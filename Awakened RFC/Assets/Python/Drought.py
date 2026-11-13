"""Local directed river droughts and historical reaches. Python 2.4."""
from CvPythonExtensions import *
import cPickle as pickle
import ScenarioGeography as geo
import Consts as con
import DroughtModel as model
from IndianCivsData import HARAPPAN_DRYING

gc = CyGlobalContext()
WARNING = 2
INITIAL_PROTECTION = 20


def enabled():
    return geo.base_profile_name() == 'Earth200x110'


def setup():
    if not enabled():
        return
    world = gc.getMap()
    width, height = world.getGridWidth(), world.getGridHeight()
    flood = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
    floodTypes = tuple([gc.getInfoTypeForString(name) for name in
        ('FEATURE_FLOOD_PLAINS', 'FEATURE_FLOOD_PLAINS_DROUGHT', 'FEATURE_FLOOD_PLAINS_SEVERE_DROUGHT')])
    parents, edges = {}, []

    def corner(x, y):
        if world.isWrapX(): x %= width
        if world.isWrapY(): y %= height
        return (x, y)

    def find(node):
        if node not in parents: parents[node] = node
        while parents[node] != node:
            parents[node] = parents[parents[node]]
            node = parents[node]
        return node

    def edge(a, b, sites, index, side, flow):
        a, b = corner(*a), corner(*b)
        rootA, rootB = find(a), find(b)
        if rootA != rootB: parents[max(rootA, rootB)] = min(rootA, rootB)
        indices = []
        for x, y in sites:
            if world.isWrapX(): x %= width
            if world.isWrapY(): y %= height
            if 0 <= x < width and 0 <= y < height:
                plot = world.plot(x, y)
                if not plot.isWater(): indices.append(y * width + x)
        direction = None
        if (side == 0 and flow == 1) or (side == 1 and flow == 0): direction = (a, b)
        elif (side == 0 and flow == 3) or (side == 1 and flow == 2): direction = (b, a)
        edges.append((a, indices, (index, side), direction))

    # Civ4 stores the south edge on the plot north of it, and the east edge
    # on the plot west of it. Join actual river corners, not nearby land tiles.
    for y in range(height):
        for x in range(width):
            plot = world.plot(x, y)
            if plot.isNOfRiver(): edge((x, y), (x + 1, y), ((x, y), (x, y - 1)), y * width + x, 0, int(plot.getRiverWEDirection()))
            if plot.isWOfRiver(): edge((x + 1, y), (x + 1, y + 1), ((x, y), (x + 1, y)), y * width + x, 1, int(plot.getRiverNSDirection()))
    groups, groupEdges, groupEnds, floodBanks = {}, {}, {}, {}
    for node, sites, riverEdge, direction in edges:
        root = find(node)
        groups.setdefault(root, set()).update(sites)
        groupEdges.setdefault(root, []).append(riverEdge)
        groupEnds.setdefault(root, {})
        if direction: groupEnds[root][riverEdge] = direction
        for index in sites:
            if world.plot(index % width, index // width).getFeatureType() in floodTypes:
                floodBanks.setdefault(index, []).append(riverEdge)
    regions = []
    for root in sorted(groups.keys()):
        sites = sorted(groups[root])
        floodSites = [i for i in sites if world.plot(i % width, i // width).getFeatureType() in floodTypes]
        if not floodSites:
            continue
        anchors = sorted(set([e for index in floodSites for e in floodBanks[index]
            if e in groupEdges[root]]))
        catalogue = model.templates(groupEnds[root], anchors, gc.getGame().getSorenRandNum)
        regions.append({'sites': sites, 'flood': floodSites, 'edges': sorted(groupEdges[root]),
            'floodEdges': anchors, 'templates': catalogue, 'events': []})
    chance, expected = model.calibrate([sorted(floodBanks[i]) for i in sorted(floodBanks.keys())], regions)
    data = pickle.loads(gc.getGame().getScriptData())
    data['droughtRegions'] = regions
    data['droughtScriptLevel'] = 0
    data['droughtScriptWarned'] = False
    data['droughtLastTick'] = -1
    data['droughtChance'] = chance
    data['droughtExpectedFood'] = expected
    data['droughtFirstTick'] = geo.historyTurn(gc.getGame().getGameTurn()) + INITIAL_PROTECTION
    gc.getGame().setScriptData(pickle.dumps(data))
    # Refresh each stage through its own river-art feature, independent of latitude.
    for region in regions:
        for index in region['flood']:
            world.plot(index % width, index // width).setFeatureType(flood, 0)
    checkTurn(gc.getGame().getGameTurn())


def historicalEdges(regions):
    if geo.profile_name() != 'Earth200x110Harappa':
        return []
    width = gc.getMap().getGridWidth()
    # Include the lower junction's west bank so a healthy second edge cannot
    # shield the opening farmland. The river farther south remains a refuge.
    return sorted(set([(i, side) for region in regions for i, side in region['edges']
        if (139 <= i % width <= 145 and 60 <= i // width <= 66) or
        (i % width, i // width, side) == (138, 62, 1)]))


def historicalDrying(year):
    """Permanent retreat of selected early alluvium, independent of city owners."""
    if geo.profile_name() != 'Earth200x110Harappa':
        return
    flood = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
    floodTypes = tuple([gc.getInfoTypeForString(name) for name in
        ('FEATURE_FLOOD_PLAINS', 'FEATURE_FLOOD_PLAINS_DROUGHT', 'FEATURE_FLOOD_PLAINS_SEVERE_DROUGHT')])
    world = gc.getMap()
    dried = []
    for deadline, sites in HARAPPAN_DRYING:
        if year < deadline:
            continue
        for x, y in sites:
            plot = world.plot(x, y)
            if plot.getFeatureType() in floodTypes:
                # Preserve cities, farms, rivers and their existing ownership.
                # The desert substrate remains; recovery never recreates features.
                plot.setFeatureType(-1, 0)
                dried.append(y * world.getGridWidth() + x)
    if dried:
        notify(dried, 'TXT_KEY_DROUGHT_FLOODPLAINS_LOST')


def bankSites(edges):
    world = gc.getMap()
    width, height = world.getGridWidth(), world.getGridHeight()
    sites = set()
    for index, side in edges:
        x, y = index % width, index // width
        sites.add(index)
        if side == 0: y -= 1
        else: x += 1
        if world.isWrapX(): x %= width
        if world.isWrapY(): y %= height
        if 0 <= x < width and 0 <= y < height: sites.add(y * width + x)
    return sorted(sites)


def notify(sites, key):
    world = gc.getMap()
    width = world.getGridWidth()
    owners = {}
    floodTypes = tuple([gc.getInfoTypeForString(name) for name in
        ('FEATURE_FLOOD_PLAINS', 'FEATURE_FLOOD_PLAINS_DROUGHT', 'FEATURE_FLOOD_PLAINS_SEVERE_DROUGHT')])
    for index in sites:
        plot = world.plot(index % width, index // width)
        # Place drought warnings and markers only on affected flood plains.
        # Historical drying removes the feature before announcing its loss.
        if key != 'TXT_KEY_DROUGHT_FLOODPLAINS_LOST' and plot.getFeatureType() not in floodTypes:
            continue
        owner = plot.getOwner()
        if owner >= 0 and gc.getPlayer(owner).isHuman() and owner not in owners:
            owners[owner] = index
    for owner in sorted(owners.keys()):
        index = owners[owner]
        CyInterface().addMessage(owner, True, con.iDuration,
            CyTranslator().getText(key, ()), '', 0, '', ColorTypes(con.iOrange),
            index % width, index // width, True, True)


def advance(event, tick):
    if tick < event['due']: return True
    game = gc.getGame()
    phase = event['phase']
    if phase == 'warning':
        event['phase'], event['level'] = 'drought', 1
        event['due'] = tick + 4 + game.getSorenRandNum(4, 'Drought duration')
    else:
        return False
    return True


def checkTurn(turn):
    if not enabled() or not geo.historyBoundary(turn):
        return
    game, world = gc.getGame(), gc.getMap()
    data = pickle.loads(game.getScriptData())
    tick = geo.historyTurn(turn)
    if data['droughtLastTick'] == tick:
        return
    data['droughtLastTick'] = tick
    regions = data['droughtRegions']
    scriptEdges = historicalEdges(regions)
    year = game.getGameTurnYear()
    historicalDrying(year)
    width = world.getGridWidth()
    floodTypes = tuple([gc.getInfoTypeForString(name) for name in
        ('FEATURE_FLOOD_PLAINS', 'FEATURE_FLOOD_PLAINS_DROUGHT', 'FEATURE_FLOOD_PLAINS_SEVERE_DROUGHT')])
    # Retain river paths, but only dry edges beside currently existing flood plains.
    floodEdges = set()
    for region in regions:
        for riverEdge in region['edges']:
            for index in bankSites([riverEdge]):
                if world.plot(index % width, index // width).getFeatureType() in floodTypes:
                    floodEdges.add(riverEdge)
                    break
    scriptEdges = [edge for edge in scriptEdges if edge in floodEdges]
    scriptSites = bankSites(scriptEdges)
    scriptLevel = 0
    if scriptSites:
        # A sudden food shock leaves little time to shrink cities beforehand.
        # Recovery is quick, but the historical alluvial losses remain.
        if -2000 <= year < -1800: scriptLevel = 2
        elif -1800 <= year < -1700: scriptLevel = 1
        if year >= -2100 and year < -2000 and not data['droughtScriptWarned']:
            notify(scriptSites, 'TXT_KEY_DROUGHT_HARAPPA_WARNING')
            data['droughtScriptWarned'] = True
    data['droughtScriptLevel'] = scriptLevel
    for region in regions:
        region['events'] = [event for event in region['events'] if advance(event, tick)]
        if tick >= data['droughtFirstTick']:
            # Count each segment once, even with flood plains on both banks.
            length = len(floodEdges.intersection(region['edges']))
            weight = model.initiationWeight(length)
            chance = min(10000, int(data['droughtChance'] * weight + .5))
            if game.getSorenRandNum(10000, 'River drought') < chance:
                eligible = [i for i in range(len(region['templates']))
                    if floodEdges.intersection(region['templates'][i]['core'])]
                if not eligible:
                    continue
                shape = eligible[game.getSorenRandNum(len(eligible), 'Drought reach')]
                event = {'shape': shape, 'phase': 'warning',
                    'level': 0, 'due': tick + WARNING}
                region['events'].append(event)
                footprint = region['templates'][shape]['core'][:]
                notify(bankSites(footprint), 'TXT_KEY_DROUGHT_WARNING')
    # Combine overlapping events on each river EDGE, never on a bank tile.
    # The native tile getter then selects its healthiest bordering river.
    levels = {}
    for region in regions:
        for riverEdge in region['edges']:
            levels[riverEdge] = 0
        for event in region['events']:
            if event['level'] == 0: continue
            shape = region['templates'][event['shape']]
            for riverEdge in shape['core']:
                if riverEdge not in floodEdges: continue
                levels[riverEdge] = max(levels[riverEdge], event['level'])
    for riverEdge in scriptEdges:
        levels[riverEdge] = max(levels.get(riverEdge, 0), scriptLevel)
    byPlot = {}
    for (index, side), level in levels.items():
        byPlot.setdefault(index, [0, 0])[side] = level
    banks = bankSites(levels.keys())
    oldStages = dict([(i, world.plot(i % width, i // width).getRiverDrought()) for i in banks])
    irrigationChanged = False
    for index in sorted(byPlot.keys()):
        plot = world.plot(index % world.getGridWidth(), index // world.getGridWidth())
        south, east = byPlot[index]
        old = plot.getRiverDroughtEdges()
        if old != south + 3 * east:
            if (old % 3 == 2) != (south == 2) or (old // 3 == 2) != (east == 2):
                irrigationChanged = True
            plot.setRiverDrought(south, east)
    if irrigationChanged:
        game.refreshDroughtIrrigation()
    notices = [[], [], []]
    for index in banks:
        stage = world.plot(index % width, index // width).getRiverDrought()
        if stage != oldStages[index]: notices[stage].append(index)
    for stage, key in enumerate(('TXT_KEY_DROUGHT_END', 'TXT_KEY_DROUGHT_START', 'TXT_KEY_DROUGHT_SEVERE')):
        notify(notices[stage], key)
    game.setScriptData(pickle.dumps(data))
