"""Gameplay report tables. No game launches and no mutations of recordings."""
from collections import Counter, defaultdict
import json
import statistics


def median(values):
    values = list(values)
    return f'{statistics.median(values):g}' if values else 'n/a'


def label(name):
    return str(name).replace('CIVILIZATION_', '').replace('CIVIC_', '')


def errors(run):
    return [f for f in run['findings'] if f.get('severity') == 'error' or f.get('kind') == 'python_exception']


def quality(run):
    if not run['completed'] or run['recording_issues']:
        return 'incomplete/recording issues'
    return 'gameplay errors' if errors(run) else 'no recorded errors'


def enrich(run, records):
    """Stream extra observations; never turn sparse snapshots into city-turns."""
    names = {p['id']: p['civilization'] for p in run['final']}
    infos = run['metadata'].get('infos', {})
    civic_names = infos.get('civic', [])
    slavery = civic_names.index('CIVIC_SLAVERY') if 'CIVIC_SLAVERY' in civic_names else None
    spells, active, established = [], {}, set()
    food = defaultdict(Counter)
    slaves = defaultdict(Counter)
    previous_cities = {}
    timeline, collapses, scores = [], [], []
    modern = False
    apostolic_events, apostolic_last = [], None
    apostolic_counts = Counter()
    last = None

    def close(pid, turn, cause):
        for key in [k for k in active if k[0] == pid]:
            spell = active.pop(key)
            spells.append(dict(spell, end=turn, duration=turn - spell['start'], end_reason=cause))

    def open_civics(pid, civics, turn, origin):
        if pid not in names:
            return
        established.add(pid)
        for column, civic in enumerate(civics):
            key = (pid, column)
            old = active.get(key)
            if old and old['civic'] == civic:
                continue
            if old:
                spells.append(dict(old, end=turn, duration=turn - old['start'], end_reason='switch'))
            active[key] = dict(player=pid, civilization=names[pid], column=column,
                               civic=civic, start=turn, origin=origin)

    for record in records:
        if record.get('kind') not in ('initial', 'turn'):
            continue
        turn = record['turn']
        last = turn
        players = {p['id']: p for p in record['players'] if p.get('major')}
        event_list = sorted(record.get('events', []), key=lambda e: e.get('turn', turn))
        # Older first_established events omit civics. The first subsequent
        # change's before-state reconstructs the initial assignment if present.
        first_before = {}
        for event in event_list:
            if event['event'] == 'civics_changed':
                first_before.setdefault(event['player'], event['before'])
        for event in event_list:
            pid, et = event.get('player'), event.get('turn', turn)
            kind = event['event']
            if kind == 'apostolic_state':
                apostolic_last = event
                apostolic_counts['observed_turns'] += 1
                apostolic_counts['eligible_turns'] += bool(event['founding_eligible'])
                apostolic_counts['palace_active_turns'] += bool(event['palace_active'])
                apostolic_counts['crusade_active_turns'] += event['crusade_region'] >= 0
            elif kind.startswith(('papal_', 'papacy_', 'council_', 'crusade_', 'apostolic_')):
                apostolic_events.append(event)
                apostolic_counts[kind] += 1
                if kind == 'crusade_plunder':
                    apostolic_counts['plunder_gold'] += event['amount']
            if kind == 'first_established' and pid in players:
                open_civics(pid, event.get('civics', first_before.get(pid, players[pid]['civics'])), et, 'establishment')
            elif kind == 'civics_changed' and pid in established:
                open_civics(pid, event['after'], et, 'switch')
            elif kind == 'alive_changed' and pid in established:
                if not event['after']:
                    close(pid, et, 'death')
                elif event.get('civics'):
                    open_civics(pid, event['civics'], et, 'revival')
            elif kind == 'collapse_trigger':
                collapses.append(dict(event, civilization=names.get(pid, str(pid))))
            elif kind == 'labor_evaluation':
                scores.append(dict(event, civilization=names.get(pid, str(pid))))

        population = sum(p['population'] for p in players.values() if p['alive'] and p['cities'])
        points = []
        for pid, p in players.items():
            civ = p['civilization']
            if p['alive'] and p['cities']:
                if not any(k[0] == pid for k in active):
                    open_civics(pid, p['civics'], turn, 'revival_snapshot' if pid in established else 'snapshot')
                elif record.get('kind') == 'initial':
                    open_civics(pid, p['civics'], turn, 'snapshot')
            elif any(k[0] == pid for k in active):
                close(pid, turn, 'cityless_snapshot')
            if pid in established:
                points.append(dict(civilization=civ, alive=bool(p['alive'] and p['cities']),
                                   population=p['population'], cities=p['cities'], techs=p['known_techs'],
                                   population_share=p['population'] / population if population and p['cities'] else 0))
            if record['kind'] != 'turn' or not p['alive'] or not p['cities']:
                continue
            under_slavery = slavery is not None and slavery in p['civics']
            if under_slavery:
                slaves[civ]['player_samples'] += 1
            for city in p.get('city_details', []):
                key = (pid, city['id'], city['x'], city['y'])
                old = previous_cities.get(key)
                eligible = all(k in city for k in ('disorder', 'food_production', 'food_consumption', 'growth_threshold'))
                modern |= eligible
                normal = eligible and not city['disorder'] and not city.get('anarchy', False) and not city.get('occupation', 0) and not city['food_production']
                if under_slavery:
                    stats = slaves[civ]
                    stats['city_samples'] += 1
                    stats['with_slaves'] += city.get('slaves', 0) > 0
                    if 'assigned_slaves' in city and 'free_slaves' in city:
                        stats['split_samples'] += 1
                        stats['assigned'] += city['assigned_slaves']
                        stats['free'] += city['free_slaves']
                    if normal:
                        stats['normal_samples'] += 1
                        stats['normal_assigned'] += city.get('assigned_slaves', 0)
                        stats['normal_deficits'] += city['food_surplus'] < 0
                if eligible:
                    size = '1-3' if city['population'] <= 3 else '4-7' if city['population'] <= 7 else '8+'
                    stats = food[size]
                    stats['all_samples'] += 1
                    if normal:
                        stats['normal_samples'] += 1
                        for field in ('local_food', 'food_imports', 'food_exports', 'food_consumption', 'food_surplus'):
                            stats[field] += city[field]
                        stats['deficits'] += city['food_surplus'] < 0
                        stats['import_dependent'] += city['local_food'] - city['food_exports'] < city['food_consumption'] <= city['local_food'] + city['food_imports'] - city['food_exports']
                        stats['storage_fraction'] += city['food'] / max(1, city['growth_threshold'])
                        if old and old['normal']:
                            stats['population_intervals'] += 1
                            stats['population_gains'] += max(0, city['population'] - old['population'])
                            stats['population_losses'] += max(0, old['population'] - city['population'])
                    previous_cities[key] = dict(normal=normal, population=city['population'])
        current_keys = {(pid, c['id'], c['x'], c['y']) for pid, p in players.items() for c in p.get('city_details', [])}
        previous_cities = {k: v for k, v in previous_cities.items() if k in current_keys}
        # Common exact boundaries, not nearest snapshots masquerading as matches.
        elapsed = record.get('elapsed_turns', 0)
        if record['kind'] == 'turn' and (elapsed % 50 == 0 or turn == run['last_turn']):
            timeline.append(dict(turn=turn, elapsed=elapsed, year=record['year'], players=points))
    for spell in active.values():
        spells.append(dict(spell, end=last + 1, duration=last + 1 - spell['start'], end_reason='run_end_censored'))
    run['apostolic'] = dict(version=run['metadata'].get('apostolic_recording_version'),
                             counts=dict(apostolic_counts), events=apostolic_events, last_state=apostolic_last)
    run.update(civic_spells=spells, food_by_size=dict(food), slavery_usage=dict(slaves),
               timeline=timeline, collapse_triggers=collapses, labor_score_samples=scores,
               economic_context_available=modern,
               first_error_turn=min((f['turn'] for f in errors(run) if 'turn' in f), default=None))
    return run


def cohort_key(run, build=True):
    m = run['metadata']
    return json.dumps([m.get('runtime_fingerprint') if build else None, m.get('scenario'),
                       m.get('mode'), m.get('autoplay'), m.get('settings'),
                       m.get('record_interval', 1), run['last_turn']], sort_keys=True)


def pool_counters(group, field):
    result = defaultdict(Counter)
    for run in group:
        for key, values in run[field].items():
            result[key].update(values)
    return result


def render_tables(group):
    lines = ['', '| Civilization | Established | Surviving | Median population (all / survivors) |',
             '| --- | ---: | ---: | ---: |']
    civs = defaultdict(list)
    for run in group:
        for p in run['final']:
            if p['id'] in run['established_players']:
                civs[p['civilization']].append(p)
    for civ, players in sorted(civs.items()):
        living = [p for p in players if p['alive'] and p['cities']]
        lines.append(f'| {label(civ)} | {len(players)} | {len(living)} | {median(p["population"] for p in players)} / {median(p["population"] for p in living)} |')
    lines += ['', '### Population development', '',
              'Each cell: median population share; surviving / established games. Exact elapsed boundaries only.']
    points = defaultdict(list)
    for run in group:
        for step in run['timeline']:
            for p in step['players']:
                points[(step['elapsed'], p['civilization'])].append(p)
    boundaries = sorted({elapsed for elapsed, _ in points})
    lines += ['', '| Civilization | ' + ' | '.join(f'T{t}' for t in boundaries) + ' |',
              '| --- | ' + ' | '.join('---:' for _ in boundaries) + ' |']
    for civ in sorted({civ for _, civ in points}):
        cells = []
        for elapsed in boundaries:
            values = points.get((elapsed, civ), [])
            cells.append(f'{median(100*p["population_share"] for p in values)}%; {sum(p["alive"] for p in values)}/{len(values)}' if values else 'n/a')
        lines.append('| ' + label(civ) + ' | ' + ' | '.join(cells) + ' |')
    lines += ['', '### Labor civic spells', '',
              'Durations of completed spells and right-censored spells are separate. A death is not a civic switch. '
              'Legacy revivals without civic payload start at their first observed snapshot.', '',
              '| Civilization | Labor civic | Starting spells | Later spells | Switch exits | Median completed duration | Ongoing / median observed age |',
              '| --- | --- | ---: | ---: | ---: | ---: | ---: |']
    spells = defaultdict(list)
    for run in group:
        for s in run['civic_spells']:
            if s['column'] == 2:
                names = run['metadata']['infos']['civic']
                spells[(s['civilization'], names[s['civic']])].append(s)
    for (civ, civic), values in sorted(spells.items()):
        ended = [s['duration'] for s in values if s['end_reason'] != 'run_end_censored']
        censored = [s['duration'] for s in values if s['end_reason'] == 'run_end_censored']
        lines.append(f'| {label(civ)} | {label(civic)} | {sum(s["origin"] in ("establishment", "snapshot") for s in values)} | {sum(s["origin"] not in ("establishment", "snapshot") for s in values)} | {sum(s["end_reason"] == "switch" for s in values)} | {median(ended)} | {len(censored)} / {median(censored)} |')
    transitions = Counter()
    for run in group:
        names = run['metadata']['infos']['civic']
        by_player = defaultdict(list)
        for s in run['civic_spells']:
            if s['column'] == 2:
                by_player[s['player']].append(s)
        for values in by_player.values():
            values.sort(key=lambda s: s['start'])
            for old, new in zip(values, values[1:]):
                if old['end_reason'] == 'switch' and old['end'] == new['start']:
                    transitions[(old['civilization'], names[old['civic']], names[new['civic']])] += 1
    lines += ['', 'Labor transitions:']
    lines += [f'- {label(civ)}: {label(old)} -> {label(new)}: {n}.' for (civ, old, new), n in sorted(transitions.items())] or ['- None observed.']
    lines += ['', '### Slave employment while Slavery is active', '',
              '| Civilization | Player / city samples | Cities with slaves | Mean assigned / free | Normal city samples / mean assigned | Normal deficits |',
              '| --- | ---: | ---: | ---: | ---: | ---: |']
    for civ, stats in sorted(pool_counters(group, 'slavery_usage').items()):
        n, split, normal = stats['city_samples'], stats['split_samples'], stats['normal_samples']
        mean = f'{stats["assigned"]/split:.2f} / {stats["free"]/split:.2f}' if split else 'n/a (legacy combined counts)'
        normal_mean = f'{stats["normal_assigned"]/normal:.2f}' if normal else 'n/a'
        deficits = f'{stats["normal_deficits"]}/{normal}' if normal else 'n/a'
        lines.append(f'| {label(civ)} | {stats["player_samples"]} / {n} | {stats["with_slaves"]}/{n} | {mean} | {normal} / {normal_mean} | {deficits} |')
    lines += ['', '### Food and observed population changes by city size', '',
              'Only normal city snapshots: no disorder, anarchy, occupation or food-based production. '
              'Counts are samples, not extrapolated city-turns. Population losses are not attributed to famine.', '',
              '| Size | All / normal samples | Mean local / imports / exports / consumption / surplus | Deficit samples | Import-supported samples | Mean food storage | Population intervals / gains / losses |',
              '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    food = pool_counters(group, 'food_by_size')
    for size in ('1-3', '4-7', '8+'):
        s = food[size]
        n = s['normal_samples']
        means = ' / '.join(f'{s[k]/n:.2f}' for k in ('local_food', 'food_imports', 'food_exports', 'food_consumption', 'food_surplus')) if n else 'n/a'
        storage = f'{100*s["storage_fraction"]/n:.1f}%' if n else 'n/a'
        if s['all_samples']:
            lines.append(f'| {size} | {s["all_samples"]} / {n} | {means} | {s["deficits"]}/{n} | {s["import_dependent"]}/{n} | {storage} | {s["population_intervals"]} / {s["population_gains"]} / {s["population_losses"]} |')
    if not all(r['economic_context_available'] for r in group):
        lines += ['', 'Legacy recordings lack food/disorder context; missing observations are unavailable, not zero.']
    reasons = Counter((e['civilization'], e.get('reason', 'unspecified'), e.get('outcome'), e.get('partial', False)) for r in group for e in r['collapse_triggers'])
    lines += ['', '### Explicit collapse triggers', '']
    lines += [f'- {label(civ)}: {reason}, {outcome}, partial={partial}: {n}.' for (civ, reason, outcome, partial), n in sorted(reasons.items())] or ['- No explicit triggers recorded; legacy recordings cannot identify the triggering rule.']
    score_count = sum(len(r['labor_score_samples']) for r in group)
    lines += ['', f'{score_count} sampled AI_bestCivic labor evaluations retained in summary.json. '
              'Scores are copied from actual calculations, including the current-civic inertia adjustment. '
              'An evaluation may also serve technology/diplomacy planning and is not a committed revolution. '
              'Sampling favors changes in current/best civic; frequencies do not measure preference rates.']
    margins = defaultdict(list)
    for run in group:
        names = run['metadata']['infos']['civic']
        for sample in run['labor_score_samples']:
            scores = {civic: (raw, adjusted) for civic, raw, adjusted in sample['scores']}
            current = sample['current']
            alternatives = [score for civic, score in scores.items() if civic != current]
            if current in scores and alternatives:
                margins[(sample['civilization'], names[current])].append((scores[current][0] - max(s[0] for s in alternatives), scores[current][1] - max(s[1] for s in alternatives)))
    if margins:
        lines += ['', '| Civilization | Current labor civic | Score samples | Median raw / adjusted margin over best alternative |', '| --- | --- | ---: | ---: |']
        for (civ, civic), values in sorted(margins.items()):
            lines.append(f'| {label(civ)} | {label(civic)} | {len(values)} | {median(v[0] for v in values)} / {median(v[1] for v in values)} |')
    return lines


def render_report(runs):
    lines = ['# Awakened RFC balance report', '',
             f'{len(runs)} recordings; {sum(r["completed"] for r in runs)} completed.', '',
             'Completion means the turn limit was reached. Errors and recording integrity are classified separately. '
             'AI-only outcomes do not establish human multiplayer balance.']
    groups = defaultdict(list)
    for r in runs:
        groups[(cohort_key(r), quality(r))].append(r)
    groups = dict(sorted(groups.items(), key=lambda item: (item[0][0], {'no recorded errors': 0, 'gameplay errors': 1, 'incomplete/recording issues': 2}[item[0][1]])))
    for index, ((_, status), group) in enumerate(groups.items(), 1):
        m = group[0]['metadata']
        counts = Counter(r['metadata'].get('seed') for r in group)
        duplicates = [seed for seed, n in counts.items() if n > 1]
        lines += ['', f'## Cohort {index}: {status}', '',
                  f'{len(group)} games; final engine turn {group[0]["last_turn"]}; mode {m.get("mode")}; '
                  f'scenario {m.get("scenario")}; interval {m.get("record_interval", 1)}.', '',
                  f'Seeds: {sorted(counts, key=lambda x: (0, x) if isinstance(x, int) else (1, str(x)))}. Build: `{m.get("runtime_fingerprint")}`.', '',
                  'Settings: `' + json.dumps(m.get('settings'), sort_keys=True) + '`.']
        usable = [r for r in group if r['metadata'].get('seed') not in duplicates]
        if duplicates:
            lines += ['', f'Repeated seeds {duplicates} excluded from pooled tables; they are not independent replicates.']
        if status == 'incomplete/recording issues':
            lines += ['', 'Excluded from pooled balance tables.']
        elif usable:
            if status == 'gameplay errors':
                lines += ['', '**Affected games: descriptive results only; subsequent state may be altered by exceptions.**']
            lines += render_tables(usable)
    lines += ['', '## Apostolic Palace and Crusades', '',
              'Native events retain decisions, courier delivery, weighted ballots, resolution effects, '
              'Crusade activity, rewards, settlement claims and refusal refunds in summary.json. '
              'Per-turn native state remains in recordings, including dedicated Papal/Crusader slots. '
              'Counts show observed coverage; zero occurrences do not validate an unexercised rule.', '',
              '| Run | Observed turns | Eligible / active Palace turns | Foundations / refusals / refunds | Ballots opened / results | Crusades started / ended | Settlements selected / completed | Plunder gold | Violations |',
              '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in runs:
        ap = r['apostolic']
        c = ap['counts']
        if not ap['version']:
            lines.append(f'| {r["run"]} | unavailable (older recording) | - | - | - | - | - | - | - |')
            continue
        def n(key):
            return c.get(key, 0)
        lines.append(f'| {r["run"]} | {n("observed_turns")} | {n("eligible_turns")} / {n("palace_active_turns")} | '
                     f'{n("papacy_founded")} / {sum(e["event"] == "papal_decision" and e["choice"] == 1 for e in ap["events"])} / {n("papal_penalty_cleared")} | '
                     f'{n("council_opened")} / {n("council_result")} | {n("crusade_started")} / {n("crusade_ended")} | '
                     f'{n("crusade_settlement_selected")} / {n("crusade_settlement_completed")} | {n("plunder_gold")} | {n("apostolic_violation")} |')
    lines += ['', 'Refund counts are per affected diplomatic relationship. Plunder includes combat bounties. '
              'Observer recordings cannot validate the multiplayer popup delivery path or the rendered HUD.']
    lines += ['', '## Run integrity', '', '| Run | Seed | Status | First error turn | Errors | Recording issues |',
              '| --- | ---: | --- | ---: | ---: | ---: |']
    for r in runs:
        lines.append(f'| {r["run"]} | {r["metadata"].get("seed")} | {quality(r)} | {r["first_error_turn"] if r["first_error_turn"] is not None else "-"} | {len(errors(r))} | {len(r["recording_issues"])} |')
    grouped = defaultdict(list)
    for r in runs:
        for finding in r['findings']:
            signature = (finding.get('kind'), finding.get('event'), finding.get('severity'), finding.get('rule'), finding.get('traceback', '').strip())
            grouped[signature].append((r['metadata'].get('seed'), finding))
        for issue in r['recording_issues']:
            lines.append('- ' + issue)
    lines += ['', '## Grouped diagnostics', '']
    for signature, occurrences in grouped.items():
        lines += [f'- {signature[1] or signature[3] or signature[0]}: {len(occurrences)} observations; '
                  f'seeds {sorted(set(s for s, _ in occurrences), key=str)}; '
                  f'first engine turn {min(f.get("turn", -1) for _, f in occurrences)}.']
        lines += ['```text', signature[4], '```'] if signature[4] else ['  Example: `' + json.dumps(occurrences[0][1], sort_keys=True) + '`']
    if not grouped:
        lines.append('No recorded findings.')
    lines += ['', '## Appendix: same-age checkpoints and first era entries', '',
              'Raw civic exposure, all 0/10/25/50-turn establishment checkpoints, era dates, '
              'civic spells, score samples and findings remain in summary.json. Era dates include historical starting technologies.', '',
              '| Civilization | Age | Observations | Surviving | Median population |', '| --- | ---: | ---: | ---: | ---: |']
    checkpoints = defaultdict(list)
    for r in runs:
        if quality(r) == 'no recorded errors' and sum(cohort_key(x) == cohort_key(r) and x['metadata'].get('seed') == r['metadata'].get('seed') for x in runs) == 1:
            for p in r['spawn_checkpoints']:
                if p['age'] == 50:
                    checkpoints[(cohort_key(r), p['civilization'], p['age'])].append(p)
    for (cohort, civ, age), values in sorted(checkpoints.items()):
        # Do not combine cohorts in this appendix either.
        cohort_number = next(i for i, (key, _) in enumerate(groups.items(), 1) if key == (cohort, 'no recorded errors'))
        lines.append(f'| C{cohort_number} {label(civ)} | {age} | {len(values)} | {sum(p["alive"] and p["cities"] > 0 for p in values)} | {median(p["population"] for p in values)} |')
    return '\n'.join(lines) + '\n'


def compare_runs(current, baseline):
    """Pair complete, clean, uniquely identified seeds; retain build cohorts."""
    lines = ['# Matched-seed comparison', '', 'Differences are current minus baseline. '
             'Only complete recordings without recorded errors/integrity issues are eligible. '
             'Settings, scenario, mode, interval and final engine turn must match. '
             'Every row pairs one seed and two builds; no pooling across builds.']
    def index(runs):
        out = defaultdict(list)
        for r in runs:
            if quality(r) == 'no recorded errors' and r['metadata'].get('seed') is not None:
                out[(cohort_key(r, False), r['metadata'].get('seed'))].append(r)
        return out
    new, old = index(current), index(baseline)
    deltas = defaultdict(list)
    pairs = 0
    ambiguous = 0
    for key in sorted(new.keys() & old.keys(), key=str):
        if len(new[key]) != 1 or len(old[key]) != 1:
            ambiguous += 1
            continue
        a, b = new[key][0], old[key][0]
        pairs += 1
        builds = (a['metadata'].get('runtime_fingerprint'), b['metadata'].get('runtime_fingerprint'))
        lines += ['', f'## Seed {key[1]}', '', f'Current `{builds[0]}`; baseline `{builds[1]}`.', '',
                  '| Elapsed | Civilization | Population delta | City delta | Tech-count delta |', '| ---: | --- | ---: | ---: | ---: |']
        astep = {p['elapsed']: p for p in a['timeline']}
        bstep = {p['elapsed']: p for p in b['timeline']}
        for elapsed in sorted(astep.keys() & bstep.keys()):
            ap = {p['civilization']: p for p in astep[elapsed]['players']}
            bp = {p['civilization']: p for p in bstep[elapsed]['players']}
            for civ in sorted(ap.keys() & bp.keys()):
                values = [ap[civ][field] - bp[civ][field] for field in ('population', 'cities', 'techs')]
                deltas[(key[0], builds, elapsed, civ)].append(values)
                lines.append(f'| {elapsed} | {label(civ)} | {values[0]:+d} | {values[1]:+d} | {values[2]:+d} |')
    lines += ['', f'{pairs} paired seeds; {ambiguous} ambiguous seed/settings matches excluded. '
              'Unmatched or affected games are not treated as zero-valued outcomes.', '',
              '## Paired medians and population-delta ranges', '',
              '| Current / baseline build | Elapsed | Civilization | Pairs | Median population delta [min, max] | Median cities delta | Median tech delta |',
              '| --- | ---: | --- | ---: | ---: | ---: | ---: |']
    for (_, builds, elapsed, civ), values in sorted(deltas.items(), key=lambda x: str(x[0])):
        pops = [v[0] for v in values]
        lines.append(f'| {builds[0]} / {builds[1]} | {elapsed} | {label(civ)} | {len(values)} | {median(pops)} [{min(pops)}, {max(pops)}] | {median(v[1] for v in values)} | {median(v[2] for v in values)} |')
    return '\n'.join(lines) + '\n'
