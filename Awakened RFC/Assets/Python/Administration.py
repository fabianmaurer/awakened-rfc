"""Administration UI and synchronized city autonomy. Compatible with Python 2.4."""
from CvPythonExtensions import *
import cPickle as pickle
import Consts as con
import ScenarioGeography as geo
from Reporting import ENABLED as REPORTING_ENABLED

gc = CyGlobalContext()
MESSAGE = 19002
CAPACITY, EFFORT, OVERLOAD, STABILITY, PRODUCTION, UPKEEP, CIVIC, TRAVEL, CITY_EFFORT, LOCAL = range(10)
PAUSED = 10
CONNECTED, GOVERNOR, RESIDENCE_COST = 14, 15, 16
REMOVE_MESSAGE = 19003
releaseContext = None


def symbol():
    return unichr(gc.getGame().getSymbolID(FontSymbols.MAP_CHAR))


def number(value):
    sign = u''
    if value < 0:
        sign = u'-'
    value = abs(value)
    return sign + u"%d.%02d" % (value // 100, value % 100)


def points(value):
    return unicode((value + 99) // 100)


def cost(value):
    return u'%d.%d' % (value // 100, (value % 100) // 10)


def value(player, kind, city=-1):
    return gc.getPlayer(player).getAdministrationValue(kind, city)


def isolation(city):
    data = pickle.loads(gc.getGame().getScriptData())
    key = (city.getOwner(), city.getID(), city.getGameTurnFounded())
    return data.get('administrationIsolation', {}).get(key, (-1, 0))[1]


def requestRelease(city, target):
    owner = city.getOwner()
    if gc.getGame().getActivePlayer() != owner:
        return
    CyMessageControl().sendModNetMessage(MESSAGE, owner, city.getID(), city.getGameTurnFounded(), target)


def requestRemoveResidence(city):
    owner = city.getOwner()
    if gc.getGame().getActivePlayer() == owner:
        CyMessageControl().sendModNetMessage(REMOVE_MESSAGE, owner, city.getID(), city.getGameTurnFounded(), 0)


def applyRemoveResidence(owner, cityID, founded):
    if owner < 0 or owner >= con.iNumMajorPlayers:
        return
    player = gc.getPlayer(owner)
    city = player.getCity(cityID)
    if city.isNone() or city.getOwner() != owner or city.getGameTurnFounded() != founded:
        return
    observation = None
    if REPORTING_ENABLED:
        observation = releaseObservation(owner, city, 'residence_removed')
    if player.removeAdministrationResidence(cityID) and REPORTING_ENABLED and observation is not None:
        import GameObserver
        observation.update({'effort100_after': value(owner, EFFORT), 'overload100_after': value(owner, OVERLOAD)})
        GameObserver.record_mechanic('administration_residence_removed', owner, observation)


def releaseObservation(owner, city, reason):
    observer = None
    try:
        import GameObserver
        observer = GameObserver.CURRENT
        if observer is None or not observer.enabled or not observer.started or observer.mode == 'performance':
            return None
        return {'city': city.getID(), 'founded': city.getGameTurnFounded(), 'name': city.getName(),
                'x': city.getX(), 'y': city.getY(), 'population': city.getPopulation(), 'reason': reason,
                'city_effort100': value(owner, CITY_EFFORT, city.getID()),
                'travel_time100': value(owner, TRAVEL, city.getID()), 'isolation_turns': isolation(city),
                'capacity100': value(owner, CAPACITY), 'effort100_before': value(owner, EFFORT),
                'overload100_before': value(owner, OVERLOAD)}
    except:
        if observer is not None:
            observer.exception('administration_release_observation')
        return None


def recordRelease(owner, details):
    try:
        if details is None:
            return
        import GameObserver
        city = gc.getMap().plot(details['x'], details['y']).getPlotCity()
        details.update({'new_owner': city.getOwner(), 'effort100_after': value(owner, EFFORT),
                        'overload100_after': value(owner, OVERLOAD),
                        'recipient_capacity100': value(city.getOwner(), CAPACITY),
                        'recipient_effort100': value(city.getOwner(), EFFORT)})
        GameObserver.record_mechanic('administration_city_released', owner, details)
    except:
        import GameObserver
        if GameObserver.CURRENT is not None:
            GameObserver.CURRENT.exception('administration_release_recording')


def applyRelease(owner, cityID, founded, target, reason='manual'):
    global releaseContext
    if owner < 0 or owner >= con.iNumMajorPlayers:
        return
    player = gc.getPlayer(owner)
    city = player.getCity(cityID)
    if city.isNone() or city.getOwner() != owner or city.getGameTurnFounded() != founded:
        return
    if target != -2 and player.getAdministrationReleaseTarget(cityID) != target:
        return
    if target < 0 and target != -2:
        return
    wasAlive = True
    if target >= 0:
        wasAlive = gc.getPlayer(target).isAlive()
    observation = None
    if REPORTING_ENABLED:
        observation = releaseObservation(owner, city, reason)
    previousContext = releaseContext
    releaseContext = (owner, city.getX(), city.getY())
    try:
        released = player.releaseAdministrationCity(cityID, target == -2)
    finally:
        releaseContext = previousContext
    if released and target >= 0 and not wasAlive:
        import RFCUtils
        utils = RFCUtils.RFCUtils()
        utils.setStability(target, 5)
        utils.setBaseStabilityLastTurn(target, 0)
    if REPORTING_ENABLED and released:
        recordRelease(owner, observation)


def beginTurn(turn, owner):
    if owner < 0 or owner >= con.iNumMajorPlayers:
        return
    player = gc.getPlayer(owner)
    if not player.isAlive():
        return
    data = pickle.loads(gc.getGame().getScriptData())
    previous = data.get('administrationIsolation', {})
    current = dict([(key, item) for key, item in previous.items() if key[0] != owner])
    paused = value(owner, PAUSED)
    releases = []
    city, iterator = player.firstCity(False)
    limit = 5
    if geo.turns(1) == 2:
        limit = 10
    while city and not city.isNone():
        key = (owner, city.getID(), city.getGameTurnFounded())
        if not value(owner, CONNECTED, city.getID()):
            last, count = previous.get(key, (-1, 0))
            if last != turn and not paused:
                count += 1
            current[key] = (turn, count)
            if count >= limit and not paused:
                releases.append((city.getID(), city.getName()))
        city, iterator = player.nextCity(iterator, False)
    data['administrationIsolation'] = current
    gc.getGame().setScriptData(pickle.dumps(data))
    for cityID, name in releases:
        observation = None
        if REPORTING_ENABLED:
            observation = releaseObservation(owner, player.getCity(cityID), 'distance')
        if player.releaseAdministrationCity(cityID, True):
            if REPORTING_ENABLED:
                recordRelease(owner, observation)
            CyInterface().addMessage(owner, True, con.iDuration, CyTranslator().getText('TXT_KEY_ADMIN_LOST', (name,)), '', 0, '', ColorTypes(gc.getInfoTypeForString('COLOR_RED')), -1, -1, False, False)
    if not player.isHuman():
        manageAI(turn, owner)
    # Keep the DLL's intelligence snapshot consistent with the live stability value.
    import RFCUtils
    player.setIntelligenceStability(RFCUtils.RFCUtils().getStability(owner))


def manageAI(turn, owner):
    """Release one peripheral city after sustained pressure, on every peer."""
    player = gc.getPlayer(owner)
    data = pickle.loads(gc.getGame().getScriptData())
    records = data.setdefault('administrationAI', {})
    tick = geo.historyTurn(turn)
    # Review at most one candidate periodically; the DLL calculates its real
    # removal effect without mutating buildings during the preview.
    if (tick + owner) % 5 == 0:
        candidate, nearest = None, 1000000
        city, iterator = player.firstCity(False)
        while city and not city.isNone():
            if value(owner, RESIDENCE_COST, city.getID()):
                distance = value(owner, 13, city.getID())
                if distance < nearest:
                    candidate, nearest = city, distance
            city, iterator = player.nextCity(iterator, False)
        if candidate is not None and value(owner, 20, candidate.getID()) > 0:
            applyRemoveResidence(owner, candidate.getID(), candidate.getGameTurnFounded())
    since, last = records.get(owner, (-1, -1000))
    overload = value(owner, OVERLOAD)
    if overload < 2500 or player.getNumCities() < 3:
        since = -1
    elif since < 0:
        since = tick
    records[owner] = (since, last)
    gc.getGame().setScriptData(pickle.dumps(data))
    if since < 0 or tick - since < 3 or tick - last < 5:
        return
    best, bestTarget, bestScore = None, -1, 0
    city, iterator = player.firstCity(False)
    capacity = value(owner, CAPACITY)
    effort = value(owner, EFFORT)
    while city and not city.isNone():
        target = player.getAdministrationReleaseTarget(city.getID())
        # Independence is a costlier fallback, reserved for severe overload.
        if target < 0 and overload >= 5000:
            target = -2
        travel = value(owner, TRAVEL, city.getID())
        if ((target >= 0 or target == -2) and not city.isCapital() and not city.isHolyCity()
                and city.getNumWorldWonders() == 0 and value(owner, CONNECTED, city.getID())):
            # Prefer remote or recently acquired cities; protect established centres.
            recent = tick - geo.historyTurn(city.getGameTurnAcquired()) < 20
            if travel >= 300 or recent or city.calculateCulturePercent(owner) < 50:
                relief = value(owner, CITY_EFFORT, city.getID())
                recipientEffort = 0
                recipientCapacity = capacity
                if target >= 0:
                    recipient = gc.getPlayer(target)
                    if recipient.isAlive():
                        recipientEffort = value(target, EFFORT)
                        recipientCapacity = value(target, CAPACITY)
                # Do not merely pass a severe administration crisis to the vassal.
                if target == -2 or recipientEffort + relief <= recipientCapacity * 11 // 10:
                    useful = min(relief, max(0, effort - capacity))
                    output = city.getYieldRate(YieldTypes.YIELD_PRODUCTION) + city.getYieldRate(YieldTypes.YIELD_COMMERCE)
                    score = useful * (100 + travel // 5) // max(10, 10 + output)
                    if target == -2:
                        score //= 2
                    if relief >= capacity // 20 and score > bestScore:
                        best, bestTarget, bestScore = city, target, score
        city, iterator = player.nextCity(iterator, False)
    if best is None:
        return
    cityID, founded = best.getID(), best.getGameTurnFounded()
    applyRelease(owner, cityID, founded, bestTarget, 'ai_overload')
    # Re-read after applyRelease: initializing a revived player updates script data.
    if player.getCity(cityID).isNone():
        data = pickle.loads(gc.getGame().getScriptData())
        data.setdefault('administrationAI', {})[owner] = (tick, tick)
        gc.getGame().setScriptData(pickle.dumps(data))
