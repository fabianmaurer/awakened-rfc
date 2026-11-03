"""Replay captured worker decisions and compare shared Dijkstra with repeated A*.

Reads worker-path-*-queries.csv and matching -flags<N>.json graphs. Does not
launch Civ4. Native/legacy times come from paired in-game measurements; Python
replay time is not used as an estimate of DLL speed. Weighted A* rows are
exploratory candidate-ranking approximations, without an optimality guarantee.
"""
import argparse
import csv
import heapq
import json
from pathlib import Path


class Search:
    def __init__(self, graph, goal=None, weight=0):
        self.graph = graph
        self.goal = goal
        self.weight = weight
        self.origin = graph['origin']
        self.labels = {self.origin: (0, graph['moves'], 1)}
        self.closed = set()
        self.queue = [(self.heuristic(self.origin), self.origin, 0)]
        self.expanded = 0

    def heuristic(self, index):
        if self.goal is None or not self.weight:
            return 0
        width, height = self.graph['width'], self.graph['height']
        dx = abs(index % width - self.goal % width)
        dy = abs(index // width - self.goal // width)
        if self.graph['wrap_x']:
            dx = min(dx, width - dx)
        if self.graph['wrap_y']:
            dy = min(dy, height - dy)
        return self.weight * max(dx, dy) * self.graph['movement_weight']

    def query(self, goal):
        nodes = self.graph['nodes']
        if not nodes[goal][2]:
            return False, -1, -1
        if goal in self.closed:
            _, moves, turns = self.labels[goal]
            return True, turns, moves
        maximum = self.graph['max_moves']
        movement_weight = self.graph['movement_weight']
        while self.queue:
            _, index, old_cost = heapq.heappop(self.queue)
            cost, moves, turns = self.labels[index]
            if index in self.closed or cost != old_cost:
                continue
            self.closed.add(index)
            self.expanded += 1
            through = nodes[index][1 if turns > 1 or moves == 0 else 0]
            if through:
                for target, movement, diagonal in nodes[index][4]:
                    if target in self.closed:
                        continue
                    available = moves if moves else maximum
                    left = max(0, available - movement)
                    edge = movement_weight * (movement if left else available)
                    if not left:
                        edge += nodes[target][3]
                    edge += self.graph['step_weight'] + diagonal * self.graph['straight_weight']
                    candidate = cost + edge
                    if candidate >= self.labels.get(target, (float('inf'),))[0]:
                        continue
                    self.labels[target] = candidate, left, turns + (moves == 0)
                    heapq.heappush(self.queue, (candidate + self.heuristic(target), target, candidate))
            if index == goal:
                _, moves, turns = self.labels[goal]
                return True, turns, moves
        return False, -1, -1


def analyze(source):
    prefix = str(source)[:-len('-queries.csv')]
    graphs = {}
    with source.open(newline='', encoding='ascii') as handle:
        queries = list(csv.DictReader(handle))
    fields = {}
    algorithms = {name: dict(expanded=0, reachability_changes=0, arrival_changes=0,
                             later_turns=0, earlier_turns=0)
                  for name in ('shared_dijkstra', 'repeated_astar', 'weighted_astar_8', 'weighted_astar_32')}
    replay_mismatches = []
    for number, query in enumerate(queries, 1):
        flags = int(query['flags'])
        if flags not in graphs:
            graphs[flags] = json.loads(Path(prefix + f'-flags{flags}.json').read_text())
            fields[flags] = Search(graphs[flags])
        graph = graphs[flags]
        goal = int(query['y']) * graph['width'] + int(query['x'])
        expected = bool(int(query['native_success'])), int(query['native_turns']), int(query['native_moves'])
        for name, weight in (('shared_dijkstra', 0), ('repeated_astar', 1),
                             ('weighted_astar_8', 8), ('weighted_astar_32', 32)):
            search = fields[flags] if name == 'shared_dijkstra' else Search(graph, goal, weight)
            before = search.expanded
            result = search.query(goal)
            expanded = search.expanded - before
            row = algorithms[name]
            row['expanded'] += expanded
            row['reachability_changes'] += result[0] != expected[0]
            if result[0] and expected[0]:
                row['arrival_changes'] += result[1:] != expected[1:]
                row['later_turns'] += max(0, result[1] - expected[1])
                row['earlier_turns'] += max(0, expected[1] - result[1])
            if name == 'shared_dijkstra' and (result != expected or expanded != int(query['expanded'])):
                replay_mismatches.append(dict(query=number, expected=expected, replay=result,
                                              expected_expanded=int(query['expanded']), expanded=expanded))
    legacy_differences = sum(bool(int(q['native_success'])) != bool(int(q['legacy_success'])) for q in queries)
    arrival_differences = sum((q['native_turns'], q['native_moves']) != (q['legacy_turns'], q['legacy_moves'])
                              for q in queries if int(q['native_success']) and int(q['legacy_success']))
    native = sum(float(q['native_seconds']) for q in queries)
    legacy = sum(float(q['legacy_seconds']) for q in queries)
    graph = next(iter(graphs.values()))
    tasks = {}
    distances = {}
    for q in queries:
        width, height = graph['width'], graph['height']
        dx = abs(int(q['x']) - graph['origin'] % width)
        dy = abs(int(q['y']) - graph['origin'] // width)
        if graph['wrap_x']:
            dx = min(dx, width - dx)
        if graph['wrap_y']:
            dy = min(dy, height - dy)
        distance = max(dx, dy)
        bucket = next(label for limit, label in ((3, '0-3'), (8, '4-8'), (16, '9-16'), (float('inf'), '17+'))
                      if distance <= limit)
        for table, key in ((tasks, q.get('task', 'unknown')), (distances, bucket)):
            value = table.setdefault(key, dict(queries=0, native_seconds=0., legacy_seconds=0.))
            value['queries'] += 1
            value['native_seconds'] += float(q['native_seconds'])
            value['legacy_seconds'] += float(q['legacy_seconds'])
    return dict(source=str(source), turn=graph['turn'], owner=graph['owner'], unit=graph['unit'],
                queries=len(queries), flag_fields=len(graphs), native_seconds=native, legacy_seconds=legacy,
                paired_speedup=legacy / native if native else None,
                legacy_reachability_changes=legacy_differences, legacy_arrival_changes=arrival_differences,
                replay_mismatches=replay_mismatches, algorithms=algorithms, tasks=tasks, distances=distances)


def summarize(path):
    sources = [path] if path.is_file() else sorted(path.rglob('worker-path-*-queries.csv'))
    if not sources:
        raise ValueError('No worker path captures found; no sampled decision reached 4 queries or a 256-plot expansion')
    results = [analyze(source) for source in sources]
    destination = path.parent if path.is_file() else path
    (destination / 'worker-path-summary.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    lines = ['# Worker path scenario comparisons', '',
             'Times below are paired in-game candidate queries from the same worker decision. '
             'Graph export and comparison overhead make sampled turn durations unsuitable for whole-game performance comparisons. '
             'Legacy searches honor the original reuse requests; engine caches and profiling overhead still affect timings.', '',
             '| Turn | Player / unit | Queries | New seconds | Legacy seconds | Paired speedup | Reachability changes | Arrival changes |',
             '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in results:
        speedup = f'{r["paired_speedup"]:.2f}x' if r['paired_speedup'] is not None else 'unavailable'
        lines.append(f'| {r["turn"]} | {r["owner"]} / {r["unit"]} | {r["queries"]} | '
                     f'{r["native_seconds"]:.6f} | {r["legacy_seconds"]:.6f} | '
                     f'{speedup} | {r["legacy_reachability_changes"]} | {r["legacy_arrival_changes"]} |')
    lines += ['', '## Captured worker tasks', '',
              '| Turn / unit | Task | Queries | New seconds | Legacy seconds |',
              '| --- | --- | ---: | ---: | ---: |']
    for r in results:
        for name, task in r['tasks'].items():
            lines.append(f'| {r["turn"]} / {r["unit"]} | {name} | {task["queries"]} | '
                         f'{task["native_seconds"]:.6f} | {task["legacy_seconds"]:.6f} |')
    lines += ['', 'Distance-bucket timing totals are also included in the JSON summary.', '',
              '## Algorithm replay', '',
              'Expanded plots compare search work on captured terrain, permissions, danger and movement costs. '
              'Repeated A* is a reference implementation, not a replay of the proprietary engine internals. '
              'Weighted variants may change rankings and have no demonstrated quality bound in this movement-state approximation. '
              'Arrival differences below are relative to shared Dijkstra.', '',
              '| Turn / unit | Algorithm | Expanded plots | Reachability changes | Arrival changes |',
              '| --- | --- | ---: | ---: | ---: |']
    for r in results:
        for name, a in r['algorithms'].items():
            lines.append(f'| {r["turn"]} / {r["unit"]} | {name} | {a["expanded"]:,} | '
                         f'{a["reachability_changes"]} | {a["arrival_changes"]} |')
    mismatches = sum(len(r['replay_mismatches']) for r in results)
    lines += ['', f'Native/shared replay mismatches: {mismatches}. '
              'A nonzero count must be investigated before relying on algorithm comparisons.', '']
    report = destination / 'worker-path-report.md'
    report.write_text('\n'.join(lines), encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', type=Path, help='A query CSV, game folder, or batch folder')
    args = parser.parse_args()
    try:
        print(summarize(args.path))
    except ValueError as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
