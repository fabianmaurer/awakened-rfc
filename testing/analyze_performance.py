"""Summarize performance-only recordings, without loading gameplay snapshots."""
import argparse
import csv
import gzip
import json
from pathlib import Path

PATH_COUNTERS = ('calls', 'successes', 'reuse_requested', 'batches', 'distinct_destinations',
                 'repeated_destinations', 'cost_callbacks', 'valid_callbacks',
                 'successful_path_turns', 'no_callback_calls')


def path_metrics(run):
    source = run / 'performance-paths.csv'
    if not source.exists():
        return None
    callers, distances, configurations = {}, {}, {}
    def add(table, key, row):
        data = table.setdefault(key, dict.fromkeys(PATH_COUNTERS, 0))
        for field in PATH_COUNTERS:
            data[field] += int(row[field])
        for field in ('seconds', 'failed_seconds'):
            data[field] = data.get(field, 0.0) + float(row[field])
        data['max_seconds'] = max(data.get('max_seconds', 0.0), float(row['max_seconds']))
    with source.open(newline='', encoding='ascii') as handle:
        for row in csv.DictReader(handle):
            add(callers, row['caller'], row)
            add(distances, row['distance_bucket'], row)
            add(configurations, (row['caller'], int(row['domain']), int(row['flags'])), row)
    return {'callers': [dict(caller=key, **value) for key, value in sorted(callers.items(), key=lambda item: item[1]['seconds'], reverse=True)],
            'distances': [dict(distance_bucket=key, **value) for key, value in sorted(distances.items(), key=lambda item: int(item[0]))],
            'configurations': [dict(caller=key[0], domain=key[1], flags=key[2], **value)
                               for key, value in sorted(configurations.items(), key=lambda item: item[1]['seconds'], reverse=True)]}


def path_report(metrics):
    if metrics is None:
        return []
    lines = ['## Pathfinding opportunities', '',
             'These are observational opportunities, not validated cache hits. Contiguous batches share group, origin, caller, flags, reuse request, turn slice, head unit, head movement points and group size.',
             'Other state changes can invalidate reuse within a batch. Explicit path resets and turn flushes end batches; destination sets are capped at 4096.',
             'Callback counts measure cost/validity evaluations, not exact expanded nodes. Reuse requested is not proof the engine reused a search; zero callbacks can also mean trivial rejection.',
             'Detailed measurements add overhead. Compare time shares within this recording before attributing differences from older builds.', '',
             '| Caller | Calls | Seconds | Failed seconds | Failure % | Distinct targets / batch | Repeat % | Cost callbacks / call |',
             '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for row in metrics['callers']:
        calls = max(1, row['calls'])
        lines.append(f'| {row["caller"]} | {row["calls"]:,} | {row["seconds"]:.3f} | {row["failed_seconds"]:.3f} | '
                     f'{100*(row["calls"]-row["successes"])/calls:.1f} | {row["distinct_destinations"]/max(1,row["batches"]):.1f} | '
                     f'{100*row["repeated_destinations"]/calls:.1f} | {row["cost_callbacks"]/calls:.1f} |')
    lines += ['', '| Caller | Reuse requested % | No callbacks % | Validity callbacks / call | Mean successful path turns |',
              '| --- | ---: | ---: | ---: | ---: |']
    for row in metrics['callers']:
        calls = max(1, row['calls'])
        lines.append(f'| {row["caller"]} | {100*row["reuse_requested"]/calls:.1f} | {100*row["no_callback_calls"]/calls:.1f} | '
                     f'{row["valid_callbacks"]/calls:.1f} | {row["successful_path_turns"]/max(1,row["successes"]):.1f} |')
    lines += ['', '| Straight-line step distance | Calls | Seconds | Failed seconds |', '| --- | ---: | ---: | ---: |']
    labels = {'3': '0-3', '8': '4-8', '16': '9-16', '17': '17+'}
    for row in metrics['distances']:
        lines.append(f'| {labels[row["distance_bucket"]]} | {row["calls"]:,} | {row["seconds"]:.3f} | {row["failed_seconds"]:.3f} |')
    lines += ['', 'High distinct-target counts per batch suggest one-to-many searches; repeated targets suggest short-lived caching.',
              'Expensive long-distance searches suggest hierarchy; expensive failures suggest connectivity/reachability rejection.',
              'The JSON configurations split callers by numeric unit domain and movement flags to identify queries that cannot safely share results.', '']
    return lines


def summarize(run):
    totals = {}
    boundaries = []

    def add(layer, name, row):
        data = totals.setdefault((layer, name), dict(calls=0, inclusive_seconds=0.0,
                                                    exclusive_seconds=0.0, max_seconds=0.0))
        for key in ('calls', 'inclusive_seconds', 'exclusive_seconds'):
            data[key] += float(row[key])
        data['max_seconds'] = max(data['max_seconds'], float(row['max_seconds']))

    source = run / 'turns.jsonl.gz'
    opener = gzip.open
    if not source.exists():
        source = run / 'turns.jsonl'
        opener = open
    with opener(source, 'rt', encoding='ascii') as handle:
        for line in handle:
            record = json.loads(line)
            if record.get('kind') != 'performance':
                continue
            boundaries.append({'turn': record['turn'], 'seconds': record['boundary_seconds']})
            for name, data in record['calculations'].items():
                add('Python', name, data)
    native = run / 'performance-native.csv'
    if native.exists():
        with native.open(newline='', encoding='ascii') as handle:
            for row in csv.DictReader(handle):
                add('DLL', row['calculation'], row)
    rows = [dict(layer=layer, calculation=name, **data) for (layer, name), data in totals.items()]
    rows.sort(key=lambda row: row['exclusive_seconds'], reverse=True)
    summary = {'turn_boundaries': boundaries, 'calculations': rows,
               'pathfinding': path_metrics(run),
               'complete': (run / 'complete.json').exists(), 'native_timings_present': native.exists()}
    (run / 'performance-summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    lines = ['# Performance timings', '', f'Completed: {summary["complete"]}. Recorded turn boundaries: {len(boundaries)}.', '',
             'Inclusive timings contain nested calculations. Exclusive timings subtract only instrumented children in the same layer.',
             'DLL timings can contain Python callbacks; do not add the two layers together. Uninstrumented work remains in its parent.',
             'Turn-boundary times include simulation, rendering and UI waits between EndGameTurn callbacks; they are not pure CPU time.',
             'Profiling adds overhead, especially for frequently called unit and city calculations.', '']
    if not native.exists():
        lines += ['Native timing file is missing: DLL profiling was not activated.', '']
    if boundaries:
        seconds = [row['seconds'] for row in boundaries]
        lines += [f'Mean boundary interval: {sum(seconds)/len(seconds):.3f}s. Slowest: {max(seconds):.3f}s.', '',
                  '## Slowest turn boundaries', '', '| Game turn | Seconds |', '| --- | ---: |']
        lines += [f'| {row["turn"]} | {row["seconds"]:.3f} |' for row in sorted(boundaries, key=lambda row: row['seconds'], reverse=True)[:10]]
        lines += ['']
    for layer in ('DLL', 'Python'):
        lines += [f'## {layer} calculations', '', '| Calculation | Calls | Inclusive seconds | Exclusive seconds | Max call seconds |',
                  '| --- | ---: | ---: | ---: | ---: |']
        for row in rows:
            if row['layer'] == layer:
                lines.append('| {calculation} | {calls:.0f} | {inclusive_seconds:.3f} | {exclusive_seconds:.3f} | {max_seconds:.3f} |'.format(**row))
        lines += ['']
    lines += path_report(summary['pathfinding'])
    (run / 'performance-report.md').write_text('\n'.join(lines), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', type=Path)
    args = parser.parse_args()
    runs = [args.path] if (args.path / 'launch.json').exists() else sorted(args.path.glob('game-*'))
    for run in runs:
        summarize(run)
        print('Performance report: ' + str(run / 'performance-report.md'))


if __name__ == '__main__':
    main()
