"""Summarize one observer run or a batch without loading entire logs into RAM."""
import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path


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
    if not metadata:
        issues.append('Missing metadata')
    if last_turn is None:
        issues.append('Missing state snapshots')
    if complete.exists():
        try:
            completion = json.loads(complete.read_text(encoding='utf-8'))
            if completion.get('turns') != turns:
                issues.append('Completion turn count does not match the last recorded elapsed turn')
            observed_errors = sum(f.get('severity') == 'error' or f.get('kind') == 'python_exception' for f in findings)
            if completion.get('errors', observed_errors) != observed_errors:
                issues.append('Completion error count does not match recorded findings')
        except (ValueError, OSError):
            issues.append('Invalid completion marker')
    return {'run': path.parent.name, 'metadata': metadata, 'completed': complete.exists(),
            'turns': turns, 'snapshots': snapshots, 'last_turn': last_turn, 'final': list(final.values()),
            'established_players': list(established), 'spawn_checkpoints': checkpoints, 'era_entries': eras,
            'civic_player_turns': dict(civic_counts), 'events': dict(events),
            'peak_population_share': dict(maximum_share), 'findings': findings, 'recording_issues': issues}


def load_runs(folder):
    from observer_reporting import enrich
    paths = sorted(folder.rglob('turns.jsonl.gz'))
    compressed = {p.parent for p in paths}
    paths += sorted(p for p in folder.rglob('turns.jsonl') if p.parent not in compressed)
    return [enrich(analyze(p), records(p, [])) for p in paths]


def main():
    from observer_reporting import render_report, compare_runs
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path, help='Run directory or batch directory')
    parser.add_argument('--compare', type=Path, help='Baseline batch for a matched-seed comparison')
    args = parser.parse_args()
    runs = load_runs(args.folder)
    if not runs:
        parser.error('No turns.jsonl or turns.jsonl.gz recordings found')
    report = render_report(runs)
    comparison = None
    if args.compare:
        baseline = load_runs(args.compare)
        if not baseline:
            parser.error('No baseline recordings found')
        comparison = compare_runs(runs, baseline)
    output = args.folder / 'report.md'
    output.write_text(report, encoding='utf-8')
    (args.folder / 'summary.json').write_text(json.dumps(runs, indent=2, ensure_ascii=True), encoding='utf-8')
    if comparison is not None:
        (args.folder / 'comparison.md').write_text(comparison, encoding='utf-8')
    print('Wrote ' + str(output))


if __name__ == '__main__':
    main()
