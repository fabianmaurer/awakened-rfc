# Optional developer instrumentation. Compatible with Civilization IV Python 2.4.
# No XML lookups, files, RNG calls or event hooks when the launcher is absent.
import os
import time
import traceback

SCHEMA = 1
CURRENT = None


def json_text(value):
    """Small ASCII JSON encoder; the embedded Python predates stdlib json."""
    if value is None:
        return 'null'
    if value is True:
        return 'true'
    if value is False:
        return 'false'
    if isinstance(value, (int, long)):
        # Boost.Python enum.__str__ may be a symbolic name, not a JSON number.
        return str(long(value))
    if isinstance(value, float):
        return str(value)
    if isinstance(value, dict):
        return '{' + ','.join([json_text(k) + ':' + json_text(value[k]) for k in sorted(value.keys())]) + '}'
    if isinstance(value, (list, tuple)):
        return '[' + ','.join([json_text(v) for v in value]) + ']'
    if not isinstance(value, unicode):
        value = unicode(str(value), 'utf-8', 'replace')
    out = []
    for char in value:
        code = ord(char)
        if char == '"' or char == '\\':
            out.append('\\' + str(char))
        elif code < 32 or code > 126:
            out.append('\\u%04x' % code)
        else:
            out.append(str(char))
    return '"' + ''.join(out) + '"'


class Observer:
    def __init__(self):
        global CURRENT
        CURRENT = self
        self.enabled = False
        self.started = False
        self.events = []
        self.previous = {}
        self.births = {}
        self.turns = 0
        self.error_count = 0
        self.last_snapshot = 0
        self.civic_exposure = {}
        self.checkpoints_seen = set()
        self.camera_pending = False
        self.camera_elapsed = 0.0
        self.performance = {}
        self.performance_stack = []
        self.performance_boundary = None
        self.output = None
        config = os.environ.get('AWAKENED_RFC_OBSERVER_CONFIG')
        token = os.environ.get('AWAKENED_RFC_OBSERVER_TOKEN')
        if not config or not token:
            return
        try:
            import ConfigParser
            parser = ConfigParser.RawConfigParser()
            parser.read(config)
            def get(key):
                return parser.get('Observer', key)
            if get('Token') != token or int(get('ProcessId')) != os.getpid():
                return
            self.mode = get('Mode').lower()
            self.scenario = '3000bc'
            if parser.has_option('Observer', 'Scenario'):
                self.scenario = get('Scenario')
            if self.scenario not in ('3000bc', '800bc', '600ad', '840ad'):
                raise ValueError('Unsupported observer scenario/mode')
            if self.mode == 'off':
                return
            if self.mode not in ('balance', 'diagnostics', 'performance'):
                raise ValueError('Invalid observer mode')
            self.output = os.path.abspath(get('OutputDirectory'))
            self.autoplay = parser.getboolean('Observer', 'Autoplay')
            self.unattended = (parser.has_option('Observer', 'Unattended') and
                               parser.getboolean('Observer', 'Unattended'))
            self.limit = int(get('Turns'))
            self.checkpoint_interval = int(get('CheckpointInterval'))
            self.record_interval = parser.getint('Observer', 'RecordInterval')
            self.seed = int(get('Seed'))
            self.version = get('ModVersion')
            self.fingerprint = get('RuntimeFingerprint')
            self.run_id = get('RunId')
            if self.limit < 1 or self.record_interval < 1:
                raise ValueError('Turns must be positive')
            if not os.path.isdir(self.output):
                raise ValueError('Output directory must be created by launcher')
            self.path = os.path.join(self.output, 'turns.jsonl')
            if os.path.exists(self.path) or os.path.exists(self.path + '.gz'):
                raise ValueError('Refusing to append to another game recording')
            self.enabled = True
        except:
            self.fail('configuration')

    def install_before(self, manager):
        if self.enabled:
            # Before the base handler too: it otherwise queues human-only
            # introduction popups before the AI observer takes control.
            manager.EventHandlerMap['GameStart'].insert(0, self.prepare)
            manager.addEventHandler('OnLoad', self.loaded_save)

    def install_after(self, manager):
        if self.enabled:
            if self.mode == 'performance':
                # Wrap turn-system entry points, not every Python call.
                # No per-call file writes and no gameplay data collection.
                seen = set()
                for handlers in manager.EventHandlerMap.values():
                    for handler in handlers:
                        owner = getattr(handler, 'im_self', None)
                        if owner is None or owner is self:
                            continue
                        for component in getattr(owner, '__dict__', {}).values():
                            if id(component) in seen:
                                continue
                            seen.add(id(component))
                            for name in ('checkTurn', 'checkPlayerTurn', 'checkImplosion', 'endTurn', 'onEndGameTurn'):
                                method = getattr(component, name, None)
                                if callable(method):
                                    label = component.__class__.__module__ + '.' + component.__class__.__name__ + '.' + name
                                    setattr(component, name, self.timed(label, method))
                for event, handlers in manager.EventHandlerMap.items():
                    for index in range(len(handlers)):
                        handler = handlers[index]
                        if getattr(handler, 'im_self', None) is not self:
                            label = event + ':' + getattr(handler, '__module__', '') + '.' + getattr(handler, '__name__', 'handler')
                            handlers[index] = self.timed(label, handler)
            manager.addEventHandler('GameStart', self.start)
            manager.addEventHandler('EndGameTurn', self.end_turn)

    def timed(self, label, function):
        def measured(*args, **kwargs):
            if not self.enabled or not self.started:
                return function(*args, **kwargs)
            frame = [time.clock(), 0.0]
            self.performance_stack.append(frame)
            try:
                return function(*args, **kwargs)
            finally:
                elapsed = time.clock() - frame[0]
                self.performance_stack.pop()
                if self.performance_stack:
                    self.performance_stack[-1][1] += elapsed
                data = self.performance.setdefault(label, {'calls': 0, 'inclusive_seconds': 0.0,
                                                         'exclusive_seconds': 0.0, 'max_seconds': 0.0})
                data['calls'] += 1
                data['inclusive_seconds'] += elapsed
                data['exclusive_seconds'] += max(0.0, elapsed - frame[1])
                data['max_seconds'] = max(data['max_seconds'], elapsed)
        return measured

    def status(self, name, data):
        handle = open(os.path.join(self.output, name + '.json'), 'wb')
        try:
            handle.write(json_text(data))
        finally:
            handle.close()

    def write(self, data):
        # Civ4 ships a reduced Python library without gzip. Append and close
        # each JSONL record here; the external launcher compresses afterward.
        # Serialize first so an encoding error cannot write a partial record.
        record = json_text(data) + '\n'
        handle = open(self.path, 'ab')
        try:
            handle.write(record)
        finally:
            handle.close()

    def fail(self, phase):
        error = traceback.format_exc()
        print('Awakened RFC observer disabled: ' + phase + '\n' + error)
        self.enabled = False
        if self.output and os.path.isdir(self.output):
            try:
                self.status('failed', {'phase': phase, 'traceback': error})
            except:
                pass
        # Preserve an AI run on a logging failure. The owning launcher ends
        # only its own process when it sees failed.json.

    def loaded_save(self, args):
        if self.enabled:
            try:
                raise ValueError('Observer batches must start a new scenario, not load a save')
            except:
                self.fail('loaded_save')

    def prepare(self, args):
        if not self.enabled:
            return
        try:
            # Stop launcher setup input immediately, before RFC initialization.
            self.status('game-starting', {'pid': os.getpid()})
            from CvPythonExtensions import CyGlobalContext, CommerceTypes
            self.gc = CyGlobalContext()
            self.game = self.gc.getGame()
            self.research_commerce = CommerceTypes.COMMERCE_RESEARCH
            game = self.game
            if game.isGameMultiPlayer() or game.isPitboss():
                raise ValueError('Observer launcher currently supports single-player only')
            expected_turn, expected_player = {'3000bc': (0, 26), '800bc': (87, 2),
                                               '600ad': (181, 2), '840ad': (205, 2)}[self.scenario]
            if game.getStartYear() != -3000 or game.getGameTurn() != expected_turn:
                raise ValueError('Observer scenario start turn/year mismatch')
            if self.unattended:
                if self.scenario == '3000bc':
                    # Restore the early-scenario marker even if validation
                    # fails: RFC handlers still run after prepare returns.
                    self.gc.getPlayer(0).setPlayable(True)
                actual_player = game.getActivePlayer()
                setup_player = actual_player
                if (self.scenario == '3000bc' and self.autoplay and
                        actual_player == 0 and expected_player == 26):
                    # The executable can retain slot zero despite the WB
                    # selector restriction. Transfer control before RFC setup;
                    # neither operation creates/deletes cities or units.
                    if self.gc.getPlayer(26).getCivilizationType() != self.gc.getInfoTypeForString('CIVILIZATION_AMERICA'):
                        raise ValueError('Observer America slot mismatch')
                    # Change the viewpoint first, while America is still AI,
                    # then transfer the human slot without a hotseat prompt.
                    game.setActivePlayer(26, False)
                    game.switchActivePlayer(0, 26, False)
                    actual_player = game.getActivePlayer()
                actual_speed = self.gc.getGameSpeedInfo(game.getGameSpeedType()).getType()
                actual_handicap = self.gc.getHandicapInfo(game.getHandicapType()).getType()
                actual_civ = 'NO_PLAYER'
                if actual_player >= 0:
                    actual_civ = self.gc.getCivilizationInfo(self.gc.getPlayer(actual_player).getCivilizationType()).getType()
                self.status('setup-settings', {'active_player': actual_player,
                            'setup_player': setup_player,
                            'civilization': actual_civ, 'speed': actual_speed,
                            'handicap': actual_handicap, 'expected_player': expected_player})
                if (actual_player != expected_player or
                        actual_speed != 'GAMESPEED_NORMAL' or
                        actual_handicap != 'HANDICAP_PRINCE'):
                    raise ValueError('Automatic setup mismatch: player=%d (%s), expected=%d; speed=%s, expected=GAMESPEED_NORMAL; handicap=%s, expected=HANDICAP_PRINCE' %
                                     (actual_player, actual_civ, expected_player, actual_speed, actual_handicap))
            # A WorldBuilder scenario need not appear in getMapScriptName():
            # that API names the map generator, not necessarily the loaded WB
            # file. Prefer the loader's cached filename when it is available.
            import CvWBInterface
            self.map_script = self.gc.getMap().getMapScriptName()
            self.loaded_scenario = getattr(CvWBInterface, 'lastFileRead', None)
            expected = {'3000bc': 'start 1 - 3000 bc', '800bc': 'start 2 - 800 bc',
                        '600ad': 'start 3 - 600 ad', '840ad': 'start 4 - 840 ad'}[self.scenario]
            if self.loaded_scenario:
                filename = str(self.loaded_scenario).replace('\\', '/').split('/')[-1].lower()
                if not filename.startswith(expected):
                    raise ValueError('Observer scenario mismatch; WB loader reports: ' + str(self.loaded_scenario))
            elif str(self.map_script).lower().endswith('.civbeyondswordwbsave'):
                filename = str(self.map_script).replace('\\', '/').split('/')[-1].lower()
                if not filename.startswith(expected):
                    raise ValueError('Observer scenario mismatch; map reports: ' + str(self.map_script))
            # If neither API exposes a filename, the turn/year checks above
            # remain mandatory. The launcher itself selects and fingerprints
            # the exact 3000 BC scenario; record unavailable identity honestly.
            # Explicit experiment setup, separate from passive observation.
            # Happens before RFC GameStart setup; never draw from either RNG.
            if self.mode == 'performance':
                import ConfigParser
                early = ConfigParser.RawConfigParser()
                early.read(os.path.join(self.output, 'seed-initialized.ini'))
                if (early.getint('Seed', 'Value') != self.seed or
                        early.getint('Seed', 'ProcessId') != os.getpid() or
                        early.get('Seed', 'Stage') != 'CvGame.init'):
                    raise ValueError('Performance RNG seed was not applied during DLL initialization')
                self.initial_rng_state = {'map': game.getMapRand().getSeed(),
                                          'sync': game.getSorenRand().getSeed()}
            else:
                self.game.getSorenRand().init(self.seed)
                self.game.getMapRand().init(self.seed)
            if self.autoplay:
                self.game.setObserverAutoPlay(True)
            self.start_time = time.clock()
        except:
            self.fail('prepare')

    def start(self, args):
        if not self.enabled:
            return
        try:
            gc = self.gc
            game = self.game
            if self.mode == 'performance':
                native_path = os.environ.get('AWAKENED_RFC_PERFORMANCE_OUTPUT', '')
                if not native_path or not os.path.isfile(native_path):
                    raise ValueError('Native performance timings were not activated; rebuild/sync the observer DLL')
                self.started = True
                self.camera_pending = False
                self.performance_boundary = time.clock()
                self.write({'kind': 'performance_metadata', 'mode': self.mode,
                            'scenario': self.scenario, 'start_turn': game.getGameTurn(),
                            'seed': self.seed, 'runtime_fingerprint': self.fingerprint,
                            'seed_applied_at': 'CvGame.init before scenario initialization; no GameStart reseed',
                            'rng_state_before_rfc_setup': self.initial_rng_state,
                            'timer': 'Windows Python time.clock wall seconds',
                            'native_timings': 'performance-native.csv'})
                self.status('started', {'run_id': self.run_id, 'pid': os.getpid(), 'mode': self.mode})
                return
            settings = {'speed': gc.getGameSpeedInfo(game.getGameSpeedType()).getType(),
                        'handicap': gc.getHandicapInfo(game.getHandicapType()).getType(),
                        'options': [gc.getGameOptionInfo(i).getType() for i in range(gc.getNumGameOptionInfos()) if game.isOption(i)]}
            infos = {}
            for category in ('Civic', 'Unit', 'Tech', 'Building', 'Religion', 'Specialist', 'Promotion', 'Era'):
                count = getattr(gc, 'getNum' + category + 'Infos')()
                getter = getattr(gc, 'get' + category + 'Info')
                infos[category.lower()] = [getter(i).getType() for i in range(count)]
            self.write({'kind': 'metadata', 'schema': SCHEMA, 'run_id': self.run_id,
                        'mode': self.mode, 'autoplay': self.autoplay, 'seed': self.seed,
                        'seed_applied_at': 'GameStart, before RFC setup (map and initial placement already loaded)',
                        'mod_version': self.version, 'runtime_fingerprint': self.fingerprint,
                        'scenario': self.loaded_scenario, 'map_script': self.map_script,
                        'scenario_identity_available': bool(self.loaded_scenario), 'settings': settings,
                        'record_interval': self.record_interval,
                        'infos': infos, 'boundary': 'EndGameTurn after RFC implosion processing, before next-turn trade recalculation'})
            if self.mode == 'diagnostics':
                plots = []
                world = gc.getMap()
                for i in range(world.numPlots()):
                    plot = world.plotByIndex(i)
                    plots.append([plot.getX(), plot.getY(), plot.getPlotType(), plot.getTerrainType(),
                                  plot.getFeatureType(), plot.getBonusType(-1), plot.getImprovementType(),
                                  plot.getRouteType(), plot.getOwner()])
                self.write({'kind': 'initial_map', 'plots': plots})
                self.map_previous = plots
            self.started = True
            self.camera_pending = False
            self.observe_players(False)
            self.snapshot('initial')
            self.checkpoint('initial')
            self.status('started', {'run_id': self.run_id, 'pid': os.getpid(), 'mode': self.mode})
        except:
            self.fail('start')

    def cities(self, player):
        city, iterator = player.firstCity(False)
        while city and not city.isNone():
            yield city
            city, iterator = player.nextCity(iterator, False)

    def setup_camera(self, args):
        # Called by the main interface refresh; the engine's optional Update
        # event is disabled by the stock Python callback defines.
        # Smaller zoom values move inward (CvCameraControls).
        if not self.enabled or not self.started or not self.camera_pending:
            return
        self.camera_elapsed += 0.25
        if self.camera_elapsed < 1.0:
            return
        self.camera_pending = False
        try:
            from CvPythonExtensions import CyCamera
            camera = CyCamera()
            before = camera.GetZoom()
            camera.SetZoom(0.5)
            self.status('camera', {'requested_zoom': 0.5,
                                   'previous_zoom': before,
                                   'reported_zoom': camera.GetZoom()})
        except:
            # A presentation failure must not discard a valid recording.
            self.events.append({'event': 'observer_camera_error', 'traceback': traceback.format_exc()})

    def units(self, player):
        unit, iterator = player.firstUnit(False)
        while unit and not unit.isNone():
            yield unit
            unit, iterator = player.nextUnit(iterator, False)

    def observe_players(self, count_exposure):
        # Cheap per-turn tracking preserves exact civic/spawn/era dates even
        # when expensive city/unit snapshots are only written every 25 turns.
        import Consts
        gc = self.gc
        turn = self.game.getGameTurn()
        year = self.game.getGameTurnYear()
        for i in range(gc.getMAX_PLAYERS()):
            player = gc.getPlayer(i)
            if player.getCivilizationType() < 0:
                continue
            state = {'alive': player.isAlive(), 'state_religion': player.getStateReligion(),
                     'civics': [player.getCivics(c) for c in range(gc.getNumCivicOptionInfos())],
                     'era': player.getCurrentEra()}
            old = self.previous.get(i)
            if old:
                for field in ('alive', 'civics', 'state_religion', 'era'):
                    if old[field] != state[field]:
                        self.events.append({'event': field + '_changed', 'player': i, 'turn': turn, 'year': year,
                                            'before': old[field], 'after': state[field]})
            if state['alive'] and player.getNumCities() and i not in self.births:
                self.births[i] = turn
                self.events.append({'event': 'first_established', 'player': i, 'turn': turn, 'year': year})
            if i < Consts.iNumPlayers and i in self.births:
                age = turn - self.births[i]
                marker = (i, age)
                if age in (0, 10, 25, 50) and marker not in self.checkpoints_seen:
                    self.checkpoints_seen.add(marker)
                    team = gc.getTeam(player.getTeam())
                    self.events.append({'event': 'establishment_checkpoint', 'player': i,
                                        'civilization': gc.getCivilizationInfo(player.getCivilizationType()).getType(),
                                        'age': age, 'turn': turn, 'year': year, 'era': state['era'],
                                        'alive': state['alive'], 'cities': player.getNumCities(),
                                        'population': player.getTotalPopulation(), 'power': player.getPower(),
                                        'techs': sum([1 for t in range(gc.getNumTechInfos()) if team.isHasTech(t)])})
                if count_exposure and state['alive'] and player.getNumCities():
                    for civic in state['civics']:
                        key = str(civic)
                        self.civic_exposure[key] = self.civic_exposure.get(key, 0) + 1
            self.previous[i] = state

    def city_data(self, city, diagnostic):
        data = {'id': city.getID(), 'name': city.getName(), 'x': city.getX(), 'y': city.getY(),
                'population': city.getPopulation(), 'food': city.getFood(),
                'food_surplus': city.foodDifference(False), 'local_food': city.getLocalFoodYield(),
                'food_imports': city.getFoodTradeImports(), 'food_exports': city.getFoodTradeExports(),
                'production': city.getYieldRate(1), 'commerce': city.getYieldRate(2),
                'happiness': city.happyLevel() - city.unhappyLevel(0),
                'health': city.goodHealth() - city.badHealth(False)}
        slave = self.gc.getInfoTypeForString('SPECIALIST_SLAVE')
        if slave >= 0:
            data['slaves'] = city.getSpecialistCount(slave) + city.getFreeSpecialistCount(slave)
        if diagnostic:
            import Slavery
            data.update({'growth_threshold': city.growthThreshold(), 'food_export_cap': city.getFoodExportLimit(),
                         'production_stored': city.getProduction(), 'production_unit': city.getProductionUnit(),
                         'production_building': city.getProductionBuilding(),
                         'production_project': city.getProductionProject(), 'production_process': city.getProductionProcess(),
                         'occupation': city.getOccupationTimer(), 'slave_revolt_chance': Slavery.slavery.revoltChance(city, city.getOwner()),
                         'specialists': [city.getSpecialistCount(i) for i in range(self.gc.getNumSpecialistInfos())],
                         'free_specialists': [city.getFreeSpecialistCount(i) for i in range(self.gc.getNumSpecialistInfos())],
                         'buildings': [city.getNumRealBuilding(i) for i in range(self.gc.getNumBuildingInfos())],
                         'religions': [i for i in range(self.gc.getNumReligionInfos()) if city.isHasReligion(i)],
                         'city_culture_times100': [city.getCultureTimes100(i) for i in range(self.gc.getMAX_PLAYERS())],
                         'tile_culture': [city.plot().getCulture(i) for i in range(self.gc.getMAX_PLAYERS())]})
            routes = []
            for i in range(city.getTradeRoutes()):
                partner = city.getTradeCity(i)
                if partner and not partner.isNone():
                    routes.append({'owner': partner.getOwner(), 'city': partner.getID(),
                                   'profit': city.calculateTradeProfit(partner),
                                   'efficiency': city.getTradeInfrastructureEfficiency(partner),
                                   'food_net': city.getFoodTradeWith(partner)})
            data['routes'] = routes
        return data

    def snapshot(self, kind):
        gc = self.gc
        turn = self.game.getGameTurn()
        diagnostic = self.mode == 'diagnostics'
        import cPickle
        import Consts
        # Read RFC state once instead of repeatedly unpickling per player.
        script = cPickle.loads(self.game.getScriptData())
        stability = script.get('lStability', [])
        players = []
        checks = []
        imported, exported = 0, 0
        for i in range(gc.getMAX_PLAYERS()):
            player = gc.getPlayer(i)
            if player.getCivilizationType() < 0:
                continue
            team = gc.getTeam(player.getTeam())
            cities = [self.city_data(city, diagnostic) for city in self.cities(player)]
            military = 0
            army = {}
            units = []
            for unit in self.units(player):
                unit_type = unit.getUnitType()
                key = gc.getUnitInfo(unit_type).getType()
                army[key] = army.get(key, 0) + 1
                if unit.baseCombatStr() > 0:
                    military += 1
                if diagnostic:
                    units.append({'id': unit.getID(), 'type': unit_type, 'x': unit.getX(), 'y': unit.getY(),
                                  'damage': unit.getDamage(), 'xp': unit.getExperience(),
                                  'promotions': [p for p in range(gc.getNumPromotionInfos()) if unit.isHasPromotion(p)]})
            civics = [player.getCivics(c) for c in range(gc.getNumCivicOptionInfos())]
            player_stability = None
            if i < len(stability):
                player_stability = stability[i]
            data = {'id': i, 'civilization': gc.getCivilizationInfo(player.getCivilizationType()).getType(),
                    'major': i < Consts.iNumPlayers,
                    'name': player.getCivilizationDescription(0), 'team': player.getTeam(),
                    'handicap': gc.getHandicapInfo(player.getHandicapType()).getType(),
                    'alive': player.isAlive(), 'minor': player.isMinorCiv(), 'barbarian': player.isBarbarian(),
                    'cities': len(cities), 'population': player.getTotalPopulation(), 'land': player.getTotalLand(),
                    'gold': player.getGold(), 'gold_rate': player.calculateGoldRate(),
                    'research_rate': player.getCommerceRate(self.research_commerce), 'researching': player.getCurrentResearch(),
                    'era': player.getCurrentEra(), 'known_techs': sum([1 for t in range(gc.getNumTechInfos()) if team.isHasTech(t)]),
                    'civics': civics, 'state_religion': player.getStateReligion(),
                    'power': player.getPower(), 'military_units': military, 'army': army,
                    'stability': player_stability,
                    'food_imports': sum([c['food_imports'] for c in cities]),
                    'food_exports': sum([c['food_exports'] for c in cities]),
                    'slaves': sum([c.get('slaves', 0) for c in cities])}
            data['city_details'] = cities
            imported += data['food_imports']
            exported += data['food_exports']
            if i in self.births:
                data['turns_since_established'] = turn - self.births[i]
            if diagnostic:
                data['unit_details'] = units
                data['techs'] = [t for t in range(gc.getNumTechInfos()) if team.isHasTech(t)]
                for city in cities:
                    if city['food_exports'] > city['food_export_cap']:
                        checks.append({'severity': 'error', 'rule': 'food_export_cap', 'player': i, 'city': city['id']})
                    for route in city['routes']:
                        if route['efficiency'] <= 0:
                            checks.append({'severity': 'investigate', 'rule': 'zero_efficiency_route_at_boundary',
                                           'player': i, 'city': city['id'], 'route': route})
            players.append(data)
        if diagnostic and imported != exported:
            checks.append({'severity': 'error', 'rule': 'global_food_conservation', 'imports': imported, 'exports': exported})
        record = {'kind': kind, 'turn': turn, 'year': self.game.getGameTurnYear(), 'players': players,
                  'elapsed_turns': self.turns, 'span_turns': self.turns - self.last_snapshot,
                  'civic_player_turns': self.civic_exposure,
                  'events': self.events, 'checks': checks,
                  'wars': [[a,b] for a in range(gc.getMAX_TEAMS()) for b in range(a+1,gc.getMAX_TEAMS())
                           if gc.getTeam(a).isAtWar(b)]}
        if diagnostic:
            world = gc.getMap()
            changed = []
            for i in range(world.numPlots()):
                p = world.plotByIndex(i)
                row = [p.getX(), p.getY(), p.getPlotType(), p.getTerrainType(), p.getFeatureType(),
                       p.getBonusType(-1), p.getImprovementType(), p.getRouteType(), p.getOwner()]
                if row != self.map_previous[i]:
                    changed.append([i, row])
                    self.map_previous[i] = row
            record['map_changes'] = changed
            record['rng_seed'] = self.game.getSorenRand().getSeed()
        self.write(record)
        self.error_count += len([c for c in checks if c['severity'] == 'error'])
        self.last_snapshot = self.turns
        self.civic_exposure = {}
        self.events = []

    def end_turn(self, args):
        if not self.enabled or not self.started:
            return
        try:
            self.turns += 1
            if self.mode == 'performance':
                now = time.clock()
                self.write({'kind': 'performance', 'turn': self.game.getGameTurn(),
                            'elapsed_turns': self.turns,
                            'boundary_seconds': now - self.performance_boundary,
                            'calculations': self.performance})
                self.performance = {}
                self.performance_boundary = time.clock()
                self.status('heartbeat', {'turns_recorded': self.turns, 'turn': self.game.getGameTurn()})
                if self.turns >= self.limit:
                    self.game.setObserverAutoPlay(False)
                    self.status('complete', {'turns': self.turns, 'errors': self.error_count,
                                            'elapsed_seconds': time.clock() - self.start_time})
                    self.enabled = False
                return
            self.observe_players(True)
            if self.turns % self.record_interval == 0 or self.turns >= self.limit:
                self.snapshot('turn')
            if self.checkpoint_interval > 0 and self.turns % self.checkpoint_interval == 0:
                self.checkpoint('periodic')
            self.status('heartbeat', {'turns_recorded': self.turns, 'turn': self.game.getGameTurn()})
            if self.turns >= self.limit:
                self.checkpoint('final')
                self.status('complete', {'turns': self.turns, 'errors': self.error_count,
                                        'elapsed_seconds': time.clock() - self.start_time})
                self.enabled = False
                if self.autoplay:
                    self.game.setObserverAutoPlay(False)
        except:
            self.fail('end_turn')

    def checkpoint(self, label):
        if self.mode == 'performance' or self.checkpoint_interval <= 0:
            return
        folder = os.path.join(self.output, 'saves')
        if not os.path.isdir(folder):
            os.makedirs(folder)
        path = os.path.join(folder, '%s-%04d.CivBeyondSwordSave' % (label, self.game.getGameTurn()))
        self.game.saveObserverCheckpoint(path)

    def exception(self, event):
        if not self.enabled:
            return
        try:
            self.write({'kind': 'python_exception', 'event': event, 'traceback': traceback.format_exc()})
            self.error_count += 1
        except:
            self.fail('exception_recording')

    def event(self, event, args):
        if not self.enabled or not self.started:
            return
        if self.mode == 'performance':
            return
        try:
            item = {'event': event, 'turn': self.game.getGameTurn(), 'year': self.game.getGameTurnYear()}
            if event in ('cityBuilt', 'cityRazed', 'cityAcquired'):
                city = args[0]
                if event == 'cityAcquired':
                    city = args[2]
                if city.isNone():
                    return
                item.update({'name': city.getName(), 'owner': city.getOwner(), 'x': city.getX(), 'y': city.getY()})
                if event == 'cityAcquired':
                    item.update({'old_owner': args[0], 'new_owner': args[1], 'conquest': bool(args[3])})
            elif event == 'religionSpread':
                item.update({'religion': args[0], 'player': args[1], 'city': args[2].getID(),
                             'x': args[2].getX(), 'y': args[2].getY()})
            elif event in ('techAcquired', 'changeWar', 'religionFounded', 'victory', 'setPlayerAlive'):
                item['args'] = list(args)
            elif event == 'combatResult' and self.mode == 'diagnostics':
                item['winner'] = [args[0].getOwner(), args[0].getUnitType()]
                item['loser'] = [args[1].getOwner(), args[1].getUnitType()]
            else:
                return
            self.events.append(item)
        except:
            self.fail('event_' + event)
