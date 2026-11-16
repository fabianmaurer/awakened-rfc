"""Local floodplain fertility cycles and historical Indus drying. Python 2.4."""
from CvPythonExtensions import *
import cPickle as pickle
import ScenarioGeography as geo
import Consts as con
import DroughtModel as model
from IndianCivsData import HARAPPAN_DRYING

gc = CyGlobalContext()
WARNING = 1


def featureTypes():
    return tuple([gc.getInfoTypeForString(name) for name in
        ('FEATURE_FLOOD_PLAINS', 'FEATURE_FLOOD_PLAINS_DROUGHT',
         'FEATURE_FLOOD_PLAINS_SEVERE_DROUGHT', 'FEATURE_FLOOD_PLAINS_STRONG',
         'FEATURE_FLOOD_PLAINS_EXTREME')])


def enabled():
    return geo.base_profile_name() == 'Earth200x110'


def setup():
    if not enabled():
        return
    world = gc.getMap()
    width, height = world.getGridWidth(), world.getGridHeight()
    floodTypes = featureTypes()
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
            'floodEdges': anchors, 'templates': catalogue, 'event': None,
            'ready': gc.getGame().getGameTurn() + model.INITIAL_PROTECTION})
    data = pickle.loads(gc.getGame().getScriptData())
    data['droughtRegions'] = regions
    data['droughtScriptLevel'] = 0
    data['droughtScriptWarned'] = False
    data['droughtLastTick'] = -1
    updateAverages(regions)
    gc.getGame().setScriptData(pickle.dumps(data))
    for region in regions:
        for index in region['flood']:
            world.plot(index % width, index // width).setFloodplainState(model.NORMAL)
    checkTurn(gc.getGame().getGameTurn())

def historicalEdges(regions):
    if geo.profile_name() != 'Earth200x110Harappa':
        return []
    width = gc.getMap().getGridWidth()
    # The eastern Harappan distributary joins the Indus. Select its whole
    # connected basin, rather than nearby edges of the Ganges or coastal rivers.
    anchor = (64 * width + 141, 1)
    edges = set()
    for region in regions:
        if anchor in region['edges']:
            edges.update(region['edges'])
    return sorted(edges)


def historicalDrying(year):
    """Permanent retreat of selected early alluvium, independent of city owners."""
    if geo.profile_name() != 'Earth200x110Harappa':
        return
    floodTypes = featureTypes()
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
    return dried


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
    floodTypes = featureTypes()
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

def currentSites(edges):
    world = gc.getMap()
    width = world.getGridWidth()
    floodTypes = featureTypes()
    return [i for i in bankSites(edges)
        if world.plot(i % width, i // width).getFeatureType() in floodTypes]


def updateAverages(regions):
    """Save per-tile stationary weights for DLL settlement/build planning."""
    world = gc.getMap()
    width = world.getGridWidth()
    combined = {}
    for region in regions:
        activeEdges = [e for e in region['edges'] if currentSites([e])]
        region['chance'] = model.initiationChance(len(activeEdges))
        eligible = [i for i in range(len(region['templates']))
            if currentSites(region['templates'][i]['core'])]
        region['eligible'] = eligible
        counts = {}
        for shapeID in eligible:
            shape = region['templates'][shapeID]
            for index in currentSites(shape['reach']):
                counts.setdefault(index, [0., 0.])[0] += 1.
            for index in currentSites(shape['core']):
                counts.setdefault(index, [0., 0.])[1] += 1.
        for index in sorted(counts.keys()):
            full, core = counts[index]
            weights = model.stationaryWeights(region['chance'], full / len(eligible), core / len(eligible))
            combined[index] = model.combineWeights(combined.get(index, [1., 0., 0., 0., 0.]), weights)
    for index in sorted(combined.keys()):
        weights = combined[index]
        integers = [int(weights[i] * 10000.) for i in range(5)]
        integers[0] += 10000 - sum(integers)
        world.plot(index % width, index // width).setFloodplainWeights(*integers)


def damage(states, protected):
    """Exactly one synchronized roll per initially exposed improved tile."""
    game, world = gc.getGame(), gc.getMap()
    width = world.getGridWidth()
    cottages = tuple([gc.getInfoTypeForString(name) for name in
        ('IMPROVEMENT_COTTAGE', 'IMPROVEMENT_HAMLET', 'IMPROVEMENT_VILLAGE', 'IMPROVEMENT_TOWN')])
    damaged = []
    for index in sorted(states.keys()):
        if index in protected: continue
        state = states[index]
        chance = 0
        if state == model.STRONG: chance = 5
        elif state == model.EXTREME: chance = 50
        if not chance: continue
        plot = world.plot(index % width, index // width)
        improvement = plot.getImprovementType()
        if improvement < 0: continue
        if game.getSorenRandNum(100, 'Floodplain improvement damage') >= chance: continue
        replacement = -1
        if improvement in cottages:
            replacement = gc.getImprovementInfo(improvement).getImprovementPillage()
        plot.setImprovementType(replacement)
        damaged.append(index)
    if damaged: notify(damaged, 'TXT_KEY_FLOODPLAIN_DAMAGE')


def eventStates(region, event):
    if event['phase'] == 'warning': return {}
    shape = region['templates'][event['shape']]
    kind = event['kind']
    severe = kind in (model.DROUGHT, model.EXTREME)
    mild = model.WEAK
    if kind in (model.STRONG, model.EXTREME): mild = model.STRONG
    if event['phase'] == 'recovery':
        return dict([(i, mild) for i in currentSites(shape['core'])])
    result = dict([(i, mild) for i in currentSites(shape['reach'])])
    if severe:
        for index in currentSites(shape['core']): result[index] = kind
    return result


def phaseDuration():
    return 4 + gc.getGame().getSorenRandNum(3, 'Floodplain phase duration')


def advance(region, turn, protected):
    event = region['event']
    if not event or turn < event['due']: return
    if event['phase'] == 'warning':
        event['phase'] = 'active'
        event['due'] = turn + phaseDuration()
        damage(eventStates(region, event), protected)
    elif event['phase'] == 'active' and event['kind'] in (model.DROUGHT, model.EXTREME):
        event['phase'] = 'recovery'
        event['due'] = turn + phaseDuration()
    else:
        if event['kind'] in (model.DROUGHT, model.EXTREME):
            region['ready'] = turn + model.RECOVERY_PROTECTION
        region['event'] = None



def historicalEvent(data, regions, year):
    """A prolonged, basin-wide historical drought, independent of random phases."""
    if geo.profile_name() != 'Earth200x110Harappa': return {}
    sites = currentSites(historicalEdges(regions))
    if -2100 <= year < -2000 and not data['droughtScriptWarned']:
        notify(sites, 'TXT_KEY_DROUGHT_HARAPPA_WARNING')
        data['droughtScriptWarned'] = True
    level = model.NORMAL
    if -2000 <= year < -1800: level = model.DROUGHT
    elif -1800 <= year < -1700: level = model.WEAK
    data['droughtScriptLevel'] = level
    if level == model.NORMAL: return {}
    return dict([(index, level) for index in sites])


def checkTurn(turn):
    if not enabled(): return
    game, world = gc.getGame(), gc.getMap()
    data = pickle.loads(game.getScriptData())
    if data['droughtLastTick'] == turn: return
    data['droughtLastTick'] = turn
    regions = data['droughtRegions']
    year = game.getGameTurnYear()
    width = world.getGridWidth()
    if historicalDrying(year): updateAverages(regions)
    scripted = historicalEvent(data, regions, year)
    protected = set(scripted.keys())
    levels = {}
    for region in regions:
        for index in region['sites']: levels[index] = model.NORMAL
    for region in regions:
        advance(region, turn, protected)
        if not region['event'] and turn >= region['ready'] and region['eligible']:
            if game.getSorenRandNum(10000, 'River fertility event') < region['chance']:
                kind = model.KINDS[game.getSorenRandNum(len(model.KINDS), 'River fertility kind')]
                eligible = region['eligible']
                shape = eligible[game.getSorenRandNum(len(eligible), 'River fertility reach')]
                severe = kind in (model.DROUGHT, model.EXTREME)
                phase, duration = 'warning', WARNING
                if not severe:
                    phase, duration = 'active', phaseDuration()
                event = {'shape': shape, 'kind': kind, 'phase': phase, 'due': turn + duration}
                region['event'] = event
                if severe:
                    key = 'TXT_KEY_DROUGHT_WARNING'
                    if kind == model.EXTREME: key = 'TXT_KEY_FLOODPLAIN_WARNING'
                    notify(currentSites(region['templates'][shape]['core']), key)
                else:
                    damage(eventStates(region, event), protected)
        if region['event']:
            for index, state in eventStates(region, region['event']).items():
                if model.PRIORITY[state] > model.PRIORITY[levels[index]]: levels[index] = state
    # Scripted historical stages own their footprint and suppress random damage.
    for index in sorted(scripted.keys()): levels[index] = scripted[index]
    notices = [[], [], [], [], []]
    irrigationChanged = False
    desert = gc.getInfoTypeForString('TERRAIN_DESERT')
    floodTypes = featureTypes()
    for index in sorted(levels.keys()):
        plot = world.plot(index % width, index // width)
        state = levels[index]
        if plot.getFeatureType() not in floodTypes: state = model.NORMAL
        old = plot.getRiverDrought()
        if old == state: continue
        if plot.getTerrainType() == desert and (old == model.DROUGHT or state == model.DROUGHT):
            irrigationChanged = True
        plot.setFloodplainState(state)
        notices[state].append(index)
    if irrigationChanged: game.refreshDroughtIrrigation()
    for state, key in ((model.NORMAL, 'TXT_KEY_DROUGHT_END'),
        (model.DROUGHT, 'TXT_KEY_DROUGHT_START'), (model.EXTREME, 'TXT_KEY_FLOODPLAIN_EXTREME')):
        notify(notices[state], key)
    game.setScriptData(pickle.dumps(data))
