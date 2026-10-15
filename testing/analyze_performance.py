"""Summarize performance-only recordings, without loading gameplay snapshots."""
import argparse
import csv
import gzip
import json
import statistics
from pathlib import Path

PATH_COUNTERS = ('calls', 'successes', 'reuse_requested', 'batches', 'distinct_destinations',
                 'repeated_destinations', 'cost_callbacks', 'valid_callbacks',
                 'successful_path_turns', 'no_callback_calls')

TASK_BINS = ('lt_100us', 'lt_1ms', 'lt_10ms', 'lt_100ms', 'ge_100ms')


def window_metrics(records, native_rows, runtime_rows):
    turns = {row['turn'] for row in records}
    seconds = [row['boundary_seconds'] for row in records]
    elapsed = sum(seconds)
    totals = {}
    for row in native_rows:
        if int(row['turn']) not in turns:
            continue
        name = row['calculation']
        data = totals.setdefault(name, dict(calculation=name, calls=0, inclusive_seconds=0.,
                                           exclusive_seconds=0., max_seconds=0., work_units=0.,
                                           **dict.fromkeys(TASK_BINS, 0),
                                           **dict.fromkeys((k + '_seconds' for k in TASK_BINS), 0.)))
        for key in ('calls', 'inclusive_seconds', 'exclusive_seconds', 'work_units'):
            data[key] += float(row.get(key, 0))
        data['max_seconds'] = max(data['max_seconds'], float(row['max_seconds']))
        for key in TASK_BINS:
            data[key] += int(row.get(key, 0))
            data[key + '_seconds'] += float(row.get(key + '_seconds', 0))
    for data in totals.values():
        data['exclusive_interval_percent'] = 100 * data['exclusive_seconds'] / elapsed if elapsed else 0
        data['inclusive_interval_percent'] = 100 * data['inclusive_seconds'] / elapsed if elapsed else 0
        data['mean_call_ms'] = 1000 * data['inclusive_seconds'] / max(1, data['calls'])
        data['exclusive_ms_per_turn'] = 1000 * data['exclusive_seconds'] / max(1, len(turns))
    native_exclusive = sum(r['exclusive_seconds'] for r in totals.values())
    # Runtime samples have their own explicit endpoints, unlike EndGameTurn intervals.
    # Reject samples straddling this window or an exception cutoff.
    samples = [r for r in runtime_rows if turns and
               min(turns) <= int(r['start_turn']) < int(r['end_turn']) <= max(turns) + 1]
    runtime = {key: sum(float(r[key]) for r in samples)
               for key in ('wall_seconds', 'process_cpu_seconds', 'main_thread_cpu_seconds')}
    runtime['samples'] = len(samples)
    if samples:
        runtime['main_thread_busy_percent'] = 100 * runtime['main_thread_cpu_seconds'] / max(1e-9, runtime['wall_seconds'])
        runtime['process_core_equivalents'] = runtime['process_cpu_seconds'] / max(1e-9, runtime['wall_seconds'])
        runtime['last_world_size'] = {k: int(samples[-1][k]) for k in ('cities', 'units', 'alive_players')}
    return dict(first_turn=min(turns) if turns else None, last_turn=max(turns) if turns else None,
                boundaries=len(turns), boundary_seconds=elapsed,
                mean_seconds=statistics.mean(seconds) if seconds else 0,
                median_seconds=statistics.median(seconds) if seconds else 0,
                p95_seconds=sorted(seconds)[max(0, (95 * len(seconds) + 99) // 100 - 1)] if seconds else 0,
                native_exclusive_seconds=native_exclusive,
                native_exclusive_interval_percent=100*native_exclusive/elapsed if elapsed else 0,
                runtime=runtime, calculations=sorted(totals.values(), key=lambda r: -r['exclusive_seconds']))


def window_report(title, window):
    lines = [f'## {title}', '',
             f'Turns {window["first_turn"]}-{window["last_turn"]}; {window["boundaries"]} recorded boundaries. '
             f'Mean {window["mean_seconds"]:.3f}s; median {window["median_seconds"]:.3f}s; p95 {window["p95_seconds"]:.3f}s.', '',
             'Shares use elapsed boundary intervals, not CPU time. Inclusive rows overlap; exclusive rows subtract measured children. '
             'Scopes are assigned to their entry turn and can cross a turn boundary, so percentages are approximate at window edges.', '',
             '| Calculation | Exclusive ms/turn | Exclusive % | Inclusive % | Calls | Mean call ms | Max call ms |',
             '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for row in window['calculations']:
        if row['calculation'].startswith('count.'):
            continue
        lines.append(f'| {row["calculation"]} | {row["exclusive_ms_per_turn"]:.2f} | '
                     f'{row["exclusive_interval_percent"]:.2f} | {row["inclusive_interval_percent"]:.2f} | '
                     f'{row["calls"]:.0f} | {row["mean_call_ms"]:.4f} | {1000*row["max_seconds"]:.2f} |')
    runtime = window['runtime']
    lines += ['', f'Summed native exclusive wall scopes: {window["native_exclusive_seconds"]:.3f}s '
              f'({window["native_exclusive_interval_percent"]:.2f}% of boundary intervals). '
              'This is instrumentation coverage, not CPU utilization.', '']
    if runtime['samples']:
        lines += [f'CPU accounting over {runtime["samples"]} flush intervals: wall {runtime["wall_seconds"]:.3f}s; '
                  f'main-thread CPU {runtime["main_thread_cpu_seconds"]:.3f}s '
                  f'({runtime["main_thread_busy_percent"]:.1f}% busy); '
                  f'process CPU {runtime["process_cpu_seconds"]:.3f}s '
                  f'({runtime["process_core_equivalents"]:.2f} cores on average).', '',
                  f'Final sampled world size: {runtime["last_world_size"]}.', '',
                  'CPU samples run between native timing flushes, not Python turn boundaries. They include profiling and engine work. '
                  'Wall minus thread CPU includes scheduling, I/O and waits; it does not isolate rendering. '
                  'Function timers remain wall timers and cannot be divided by CPU totals to claim exact compute shares.', '']
    else:
        lines += ['CPU accounting unavailable in this recording; rerun with the expanded DLL to measure it.', '']
    lines += ['### Task sizes and work counts', '',
              'Durations are inclusive. Tiny calls generally need batching before dispatching to workers. '
              'These distributions do not demonstrate independence or safe parallel batches.', '',
              '| Calculation | <0.1 ms | 0.1-1 ms | 1-10 ms | 10-100 ms | >=100 ms | Work units |',
              '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for row in window['calculations']:
        if sum(row[k] for k in TASK_BINS):
            lines.append('| ' + row['calculation'] + ' | ' + ' | '.join(str(row[k]) for k in TASK_BINS)
                         + f' | {row["work_units"]:.0f} |')
    if not any(sum(row[k] for k in TASK_BINS) for row in window['calculations']):
        lines += ['', 'Call-duration histograms are unavailable in this recording.']
    lines += ['', 'Work units: infrastructure search = visited queue entries; scoreAndSelect = scored eligible city candidates. '
              'AI_updateFoundValues = native tile evaluations in the full-map pass. Culture/network work units are explained below.', '',
              '### Parallel speedup ceilings', '',
              'Optimistic elapsed-time ceilings assuming the entire named subsystem is parallelizable, no overhead and unchanged gameplay. '
              'Actual eligible fractions are unknown; rows overlap and must not be added.', '',
              '| Subsystem | Inclusive interval % | Saving with 2 workers % | 4 workers % | 8 workers % |',
              '| --- | ---: | ---: | ---: | ---: |']
    candidates = {'trade.infrastructureBuild', 'trade.scoreAndSelect', 'CvCity::doTurn',
                  'CvMap::doTurn', 'unitAI.generatePath', 'CvCityAI::AI_updateBestBuild',
                  'CvCityAI::AI_chooseProduction', 'CvPlayerAI::AI_updateFoundValues'}
    for row in window['calculations']:
        if row['calculation'] in candidates:
            share = row['inclusive_interval_percent']
            lines.append(f'| {row["calculation"]} | {share:.2f} | {share/2:.2f} | {share*.75:.2f} | {share*.875:.2f} |')
    return lines + [''] + culture_report(window)


def culture_report(window):
    rows = {r['calculation']: r for r in window['calculations']}
    culture = rows.get('CvCity::doPlotCulture')
    if not culture:
        return []
    names = ['culture.normal', 'culture.immediate', 'culture.ownerChange',
             'culture.ownerOldSight', 'culture.ownerNewSight', 'culture.ownerWorkingCity',
             'culture.ownerIrrigation', 'culture.irrigation', 'culture.ownerYield',
             'culture.ownerPlotGroups', 'culture.plotGroup.recalculate',
             'culture.plotGroup.connectivityCheck', 'culture.plotGroup.collectComponent',
             'culture.plotGroup.incremental', 'culture.plotGroup.rebuild',
             'culture.ownerUnitValidation', 'culture.ownerSymbols']
    if not any(name in rows for name in names):
        return ['### Plot-culture diagnosis', '', 'Targeted culture profiling is unavailable in this recording.', '']
    lines = ['### Plot-culture diagnosis', '',
             'Only work nested under CvCity::doPlotCulture is included in culture.* timers. '
             'Normal/immediate distinguish the caller\'s requested ownership-update mode; '
             'normal mode still checks unowned tiles immediately. Inclusive stages overlap, so do not add them.', '',
             '| Culture stage | Calls | Inclusive ms/turn | % of culture time | % of turn interval | Work units |',
             '| --- | ---: | ---: | ---: | ---: | ---: |']
    for name in names:
        if name not in rows:
            continue
        r = rows[name]
        lines.append(f'| {name} | {r["calls"]:.0f} | '
                     f'{1000*r["inclusive_seconds"]/max(1,window["boundaries"]):.2f} | '
                     f'{100*r["inclusive_seconds"]/max(1e-9,culture["inclusive_seconds"]):.2f} | '
                     f'{r["inclusive_interval_percent"]:.2f} | {r["work_units"]:.0f} |')
    lines += ['', 'Work units: normal/immediate = eligible tile culture additions; '
              'recalculate = group sizes before checking; connectivityCheck = reached plots; '
              'collectComponent = plots reached on the membership pass; incremental = plots detached; '
              'rebuild = group sizes before full fallback reassignment; irrigation = path searches performed. Other timed stages report zero.', '',
              '| Event counter | Events | Total work | Mean work/event |',
              '| --- | ---: | ---: | ---: |']
    for name, r in rows.items():
        if name.startswith('count.'):
            lines.append(f'| {name} | {r["calls"]:.0f} | {r["work_units"]:.0f} | '
                         f'{r["work_units"]/max(1,r["calls"]):.2f} |')
    connected = rows.get('count.culture.plotGroup.connected', {}).get('calls', 0)
    rebuilt = rows.get('count.culture.plotGroup.rebuilt', {}).get('calls', 0)
    incremental = rows.get('count.culture.plotGroup.retained', {}).get('calls', 0)
    if connected + rebuilt + incremental:
        total = connected + rebuilt + incremental
        lines += ['', f'Culture-triggered group checks ending connected: '
                  f'{connected:.0f}/{total:.0f} ({100*connected/total:.1f}%). '
                  'A high percentage identifies a possible fast-path opportunity; it does not prove checks are unnecessary.']
        lines += ['', f'Culture incremental rebuilds: {incremental:.0f}; full fallback rebuilds: {rebuilt:.0f}.']
    for prefix in ('count.culture.plotGroup.', 'count.plotGroup.'):
        retained = rows.get(prefix + 'retained', {}).get('work_units', 0)
        detached = rows.get(prefix + 'detached', {}).get('work_units', 0)
        if retained + detached:
            lines += ['', f'{prefix} incremental work: {retained:.0f} plot memberships retained, '
                      f'{detached:.0f} detached ({100*retained/(retained+detached):.2f}% retained). '
                      'These are repeated memberships across operations, not distinct map plots.']
    lines += ['', 'allocationAvoided counts irrigation calls that previously created an unused finder; '
              'finderCreated counts calls that still allocate one. workingCityRefreshAvoided counts removed duplicate refreshes. '
              'These optimization counters cover all callers, not only culture. Plot-group counter work is group size. '
              'retained/detached counters record incremental component sizes. '
              'ownerClaimed/ownerReleased/ownerTransferred count culture-triggered changes from unowned, to unowned, or between owners.', '',
              'For before/after comparisons use plotGroup.recalculate inclusive time (culture plus other callers). '
              'The rebuild timer now measures only full fallbacks; incremental and membership-collection times are separate children.', '']
    if sum(culture[k + '_seconds'] for k in TASK_BINS):
        lines += ['| Culture call duration | Calls | Total seconds | % of culture time |',
                  '| --- | ---: | ---: | ---: |']
        for key, label in zip(TASK_BINS, ('<0.1 ms', '0.1-1 ms', '1-10 ms', '10-100 ms', '>=100 ms')):
            lines.append(f'| {label} | {culture[key]} | {culture[key + "_seconds"]:.3f} | '
                         f'{100*culture[key + "_seconds"]/max(1e-9,culture["inclusive_seconds"]):.2f} |')
        lines += ['']
    return lines


def culture_spikes(native_rows, valid_turns):
    per_turn = {}
    labels = ('CvCity::doPlotCulture', 'culture.normal', 'culture.immediate', 'culture.ownerChange',
              'culture.plotGroup.connectivityCheck', 'culture.plotGroup.collectComponent',
              'culture.plotGroup.incremental', 'culture.plotGroup.rebuild', 'culture.irrigation')
    for row in native_rows:
        turn = int(row['turn'])
        if turn in valid_turns and row['calculation'] in labels:
            data = per_turn.setdefault(turn, dict.fromkeys(labels, 0.))
            data[row['calculation']] += float(row['inclusive_seconds'])
    if not any(r['culture.normal'] or r['culture.immediate'] for r in per_turn.values()):
        return []
    lines = ['## Slowest plot-culture turns', '',
             'Inclusive seconds assigned to scope entry turns, combining all native flush rows for each turn. '
             'Columns overlap; ownership and network work are nested within culture modes.', '',
             '| Turn | Culture total | Normal | Immediate | Owner changes | Connectivity checks | Membership collection | Incremental | Full rebuild | Irrigation |',
             '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for turn, data in sorted(per_turn.items(), key=lambda item: -item[1]['CvCity::doPlotCulture'])[:10]:
        lines.append(f'| {turn} | ' + ' | '.join(f'{data[k]:.3f}' for k in labels) + ' |')
    return lines + ['']


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
    records, exceptions, native_rows, runtime_rows = [], [], [], []
    exception_cutoff = None
    pending_exception = False
    malformed_records = 0

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
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                malformed_records += 1
                continue
            if record.get('kind') == 'python_exception':
                exceptions.append(record)
                if exception_cutoff is None:
                    exception_cutoff = record.get('turn')
                    pending_exception = exception_cutoff is None
            if record.get('kind') != 'performance':
                continue
            if pending_exception:
                exception_cutoff = record['turn']
                pending_exception = False
            records.append(record)
            boundaries.append({'turn': record['turn'], 'seconds': record['boundary_seconds']})
            for name, data in record['calculations'].items():
                add('Python', name, data)
    native = run / 'performance-native.csv'
    if native.exists():
        with native.open(newline='', encoding='ascii') as handle:
            for row in csv.DictReader(handle):
                native_rows.append(row)
                add('DLL', row['calculation'], row)
    runtime_path = run / 'performance-runtime.csv'
    if runtime_path.exists():
        with runtime_path.open(newline='', encoding='ascii') as handle:
            runtime_rows = list(csv.DictReader(handle))
    valid_records = [r for r in records if exception_cutoff is None or r['turn'] < exception_cutoff]
    windows = {'before_first_exception': window_metrics(valid_records, native_rows, runtime_rows),
               'last_100_before_first_exception': window_metrics(valid_records[-100:], native_rows, runtime_rows)}
    rows = [dict(layer=layer, calculation=name, **data) for (layer, name), data in totals.items()]
    rows.sort(key=lambda row: row['exclusive_seconds'], reverse=True)
    summary = {'turn_boundaries': boundaries, 'calculations': rows,
               'pathfinding': path_metrics(run),
               'complete': (run / 'complete.json').exists(), 'native_timings_present': native.exists(),
               'exceptions': exceptions, 'first_exception_turn': exception_cutoff,
               'malformed_records': malformed_records, 'windows': windows}
    (run / 'performance-summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    lines = ['# Performance timings', '', f'Completed: {summary["complete"]}. Recorded turn boundaries: {len(boundaries)}.', '',
             'Inclusive timings contain nested calculations. Exclusive timings subtract only instrumented children in the same layer.',
             'DLL timings can contain Python callbacks; do not add the two layers together. Uninstrumented work remains in its parent.',
             'Turn-boundary times include simulation, rendering and UI waits between EndGameTurn callbacks; they are not pure CPU time.',
             'Profiling adds overhead, especially for frequently called unit and city calculations.', '']
    if exceptions:
        lines += [f'WARNING: {len(exceptions)} Python exception(s); first affected turn: {exception_cutoff}. '
                  'The window tables exclude that turn and everything afterward. The legacy full-run tables below include all recorded data.', '']
    if malformed_records:
        lines += [f'WARNING: skipped {malformed_records} malformed JSON record(s).', '']
    lines += window_report('Before the first exception', windows['before_first_exception'])
    lines += window_report('Last 100 recorded turns before the first exception', windows['last_100_before_first_exception'])
    lines += culture_spikes(native_rows, {r['turn'] for r in valid_records})
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
