"""Summarize one observer run or a batch without loading entire logs into RAM."""
import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
import statistics


def records(path, issues):
    try:
        opener = gzip.open if path.suffix == '.gz' else open
        with opener(path, 'rt', encoding='ascii') as handle:
            for number, line in enumerate(handle, 1):
                try:
                    yield json.loads(line)
                except ValueError:
                    issues.append(f'{path.parent.name}: invalid JSON record {number}')
    except (EOFError, OSError) as error:
        issues.append(f'{path.parent.name}: incomplete recording ({error})')


def analyze(path):
    issues = []
    metadata = {}
    final = {}
    established = {}
    checkpoints = []
    eras = []
    civic_counts = Counter()
    events = Counter()
    findings = []
    maximum_share = defaultdict(float)
    seen_eras = set()
    turns = 0
    snapshots = 0
    last_turn = None
    for record in records(path, issues):
        kind = record.get('kind')
        if kind == 'metadata':
            metadata = record
        elif kind == 'python_exception':
            findings.append(record)
        elif kind in ('turn', 'initial'):
            if kind == 'turn':
                turns = record.get('elapsed_turns', turns + 1)
                snapshots += 1
            last_turn = record['turn']
            players = [p for p in record['players'] if p.get('major')]
            player_names = {p['id']: p['civilization'] for p in players}
            per_turn_counters = 'civic_player_turns' in record
            if per_turn_counters:
                civic_counts.update({int(k): v for k,v in record['civic_player_turns'].items()})
                for event in record['events']:
                    if event['event'] == 'establishment_checkpoint':
                        checkpoints.append(event)
                        established.setdefault(event['player'], event['turn'] - event['age'])
                        marker = (event['player'], event['era'])
                        if event['age'] == 0 and marker not in seen_eras:
                            seen_eras.add(marker)
                            eras.append({'civilization': event['civilization'], 'era': event['era'],
                                         'year': event['year'], 'turn': event['turn']})
                    elif event['event'] == 'era_changed' and event['player'] in player_names:
                        marker = (event['player'], event['after'])
                        if marker not in seen_eras:
                            seen_eras.add(marker)
                            eras.append({'civilization': player_names[event['player']], 'era': event['after'],
                                         'year': event['year'], 'turn': event['turn']})
            living = [p for p in players if p['alive'] and p['cities']]
            population = sum(p['population'] for p in living)
            for player in players:
                pid = player['id']
                final[pid] = player
                if player['cities'] and pid not in established:
                    established[pid] = record['turn']
                if pid not in established:
                    continue
                age = record['turn'] - established[pid]
                if not per_turn_counters and age in (0, 10, 25, 50) and kind == 'turn':
                    checkpoints.append({'civilization': player['civilization'], 'age': age, 'year': record['year'],
                                        'alive': player['alive'], 'cities': player['cities'],
                                        'population': player['population'], 'techs': player['known_techs'],
                                        'power': player['power']})
                if player['alive'] and player['cities']:
                    if not per_turn_counters:
                        civic_counts.update(player['civics'])
                    if len(living) >= 6 and population:
                        maximum_share[player['civilization']] = max(maximum_share[player['civilization']], player['population']/population)
                    marker = (pid, player['era'])
                    if not per_turn_counters and marker not in seen_eras:
                        seen_eras.add(marker)
                        eras.append({'civilization': player['civilization'], 'era': player['era'],
                                     'year': record['year'], 'turn': record['turn']})
            for event in record['events']:
                events[event['event']] += 1
            for finding in record['checks']:
                findings.append(dict(finding, turn=record['turn'], year=record['year']))
    complete = path.with_name('complete.json')
    return {'run': path.parent.name, 'metadata': metadata, 'completed': complete.exists(),
            'turns': turns, 'snapshots': snapshots, 'last_turn': last_turn, 'final': list(final.values()),
            'established_players': list(established), 'spawn_checkpoints': checkpoints, 'era_entries': eras,
            'civic_player_turns': dict(civic_counts), 'events': dict(events),
            'peak_population_share': dict(maximum_share), 'findings': findings, 'recording_issues': issues}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path, help='Run directory or batch directory')
    args = parser.parse_args()
    paths = sorted(args.folder.rglob('turns.jsonl.gz'))
    compressed_folders = {p.parent for p in paths}
    paths += sorted(p for p in args.folder.rglob('turns.jsonl') if p.parent not in compressed_folders)
    if not paths:
        parser.error('No turns.jsonl or turns.jsonl.gz recordings found')
    runs = [analyze(p) for p in paths]
    groups = defaultdict(list)
    for run in runs:
        m = run['metadata']
        # Do not pool different modes, builds, settings or recording lengths.
        key = json.dumps([m.get('runtime_fingerprint'), m.get('mode'), m.get('autoplay'),
                          m.get('settings'), m.get('record_interval', 1), run['last_turn']], sort_keys=True)
        groups[key].append(run)
    lines = ['# Awakened RFC observer report', '',
             f'{len(runs)} recordings; {sum(r["completed"] for r in runs)} completed.', '',
             'AI-only outcomes describe the current AI. Civic popularity is not evidence of causal strength.',
             'Incomplete games are listed individually and excluded from pooled balance statistics.', '']
    for n, group in enumerate(groups.values(), 1):
        meta = group[0]['metadata']
        complete = [r for r in group if r['completed']]
        lines += [f'## Cohort {n}', '',
                  f'Mode: {meta.get("mode")}; final turn: {group[0]["last_turn"]}; complete games: {len(complete)}.', '',
                  '| Civilization | Games established | Survived to run end | Median final population | Reached 40% population share* |',
                  '| --- | ---: | ---: | ---: | ---: |']
        civs = defaultdict(list)
        for run in complete:
            for player in run['final']:
                if player['id'] in run['established_players']:
                    civs[player['civilization']].append((run, player))
        for civ, entries in sorted(civs.items()):
            survived = sum(p['alive'] and p['cities'] > 0 for _, p in entries)
            median = statistics.median(p['population'] for _, p in entries)
            dominant = sum(r['peak_population_share'].get(civ, 0) >= .4 for r, _ in entries)
            lines.append(f'| {civ} | {len(entries)} | {survived} | {median:g} | {dominant} |')
        lines += ['', '*Measured at recorded snapshots while at least six major civilizations have cities; short-lived peaks between snapshots can be missed.', '',
                  '### Survival 50 turns after establishment', '',
                  '| Civilization | Observations | Survived | Median population |', '| --- | ---: | ---: | ---: |']
        births = defaultdict(list)
        for run in complete:
            for point in run['spawn_checkpoints']:
                if point['age'] == 50:
                    births[point['civilization']].append(point)
        for civ, points in sorted(births.items()):
            lines.append(f'| {civ} | {len(points)} | {sum(p["alive"] and p["cities"] > 0 for p in points)} | {statistics.median(p["population"] for p in points):g} |')
        lines += ['', '### Observed civic usage', '']
        counts = Counter()
        for run in complete:
            counts.update({int(k): v for k, v in run['civic_player_turns'].items()})
        names = meta.get('infos', {}).get('civic', [])
        for civic, count in counts.most_common():
            name = names[civic] if 0 <= civic < len(names) else str(civic)
            lines.append(f'- {name}: {count} established, living civilization-turns.')
        lines += ['', '### First era entries across completed games', '']
        era_years = defaultdict(list)
        for run in complete:
            first = {}
            for point in run['era_entries']:
                first[point['era']] = min(first.get(point['era'], point['year']), point['year'])
            for era, year in first.items():
                era_years[era].append(year)
        era_names = meta.get('infos', {}).get('era', [])
        for era, years in sorted(era_years.items()):
            label = era_names[era] if 0 <= era < len(era_names) else str(era)
            lines.append(f'- {label}: median year {statistics.median(years):g}, range {min(years)} to {max(years)} ({len(years)} games).')
        lines.append('')
    lines += ['## Run diagnostics', '']
    for run in runs:
        errors = [f for f in run['findings'] if f.get('severity') == 'error' or f.get('kind') == 'python_exception']
        investigations = [f for f in run['findings'] if f.get('severity') == 'investigate']
        lines += [f'### {run["run"]}', '',
                  f'{run["turns"]} turns; {run["snapshots"]} turn snapshots; {len(errors)} error observations; {len(investigations)} observations to investigate.', '']
        for issue in run['recording_issues']:
            lines.append('- ' + issue)
        for finding in run['findings'][:20]:
            lines.append('- `' + json.dumps(finding, ensure_ascii=True) + '`')
        lines.append('')
    output = args.folder / 'report.md'
    output.write_text('\n'.join(lines), encoding='utf-8')
    (args.folder / 'summary.json').write_text(json.dumps(runs, indent=2, ensure_ascii=True), encoding='utf-8')
    print('Wrote ' + str(output))


if __name__ == '__main__':
    main()
