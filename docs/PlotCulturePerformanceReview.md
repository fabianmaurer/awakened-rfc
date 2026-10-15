# Plot-culture performance review

Reviewed against the completed 400-turn, 3000 BC, seed-1 performance recording
`performance-ai-3000bc-1games-400turns-seeds-1-1-20261015-195134-54eb2f`.
The late-game window is engine turns 300-399. The original investigation was
independent of parallelization. The implementation follow-up below records the
subsequent changes; the measurements here describe the earlier build.

## What the recording establishes

- `CvCity::doPlotCulture` takes 156.62 seconds, or 13.89% of elapsed time in the
  last 100 turns (1.566 seconds per turn).
- Of 14,498 calls, 13,719 finish below 0.1 ms and 14,296 below 1 ms (98.61%).
  Only 147 calls reach 100 ms. Aggregate histograms do not establish precisely
  how much total time those 147 calls consume.
- The 33 native timing rows containing no calls of 100 ms or more total only
  0.587 seconds over 4,158 calls. Rows are flush aggregates, not necessarily
  unique turns. Most measured time is associated with rows containing slow calls.
- Turn 376 alone accounts for 36.79 seconds of plot-culture work. Its map turn
  takes a further 14.26 seconds; these are separate measured scopes. The prior
  turn includes a large collapse/city-transfer event. A causal connection is
  plausible but cannot be proved from state-free performance records.

## Code path

`CvCity::doPlotCulture` visits the city's culture radius in fixed coordinate
order, checks whether each tile is eligible, then adds the prescribed culture.
For ordinary owned plots in the normal city-turn call, it does not immediately
recalculate ownership: the argument is `bUpdate || !plot->isOwned()`.

For unowned plots, or callers explicitly requesting immediate updates, the path
continues through `CvPlot::setCulture`, `updateCulture`, `calculateCulturalOwner`
and `setOwner`. An unchanged owner already skips the expensive ownership body.
Changing a non-city tile's owner can trigger:

1. Old/new visibility and revelation, potentially causing network updates too.
2. Working-city changes, land/bonus accounting and revealed-owner updates.
3. Irrigation searches and yield updates.
4. Plot-group maintenance for every living player.
5. Unit validity checks, diplomacy/contact and presentation updates.

Therefore the plot-culture timer measures these downstream costs as well as
culture arithmetic. The current recording does not attribute them individually.

## Improvement candidates

### 1. Avoid unnecessary whole-network connectivity checks

This is the strongest structural suspect, not a measured attribution yet.
`CvPlot::updatePlotGroup(player)` can remove a plot and immediately call
`CvPlotGroup::recalculatePlots`. That method flood-fills the remaining connected
network to count reachable plots. Even when nothing split, discovering that
requires traversing the group. A real split additionally removes and reassigns
the group's plots, updating city resource bonuses. Multiple tile claims can
repeat this work, and visibility changes can enter the network machinery too.

A fast path that proves affected connections remain valid could avoid a full
flood fill without changing mechanics. Any such proof must account for team
trade permissions, water/river connections, revelation, and all affected edges.
A generic leaf-node shortcut is not yet demonstrated safe in this code.

Whole-city or whole-turn batching of network rebuilds has more potential but
is not a transparent optimization: intervening callbacks can observe resource
access, yields and connectivity. Preserve those observations or explicitly
treat the change as a gameplay tradeoff. The plot-group system still supplies
resource bonuses and cannot be removed merely because custom trade routes exist.

### 2. Construct irrigation search objects only when needed

`CvPlot::updateIrrigated` creates and destroys an engine pathfinder after its
initial guards even when neither branch performs a search. Lazy creation inside
the actual search branches would remove that allocation churn while retaining
the same search sequence and irrigation rules. This is a concrete, small
optimization candidate; its share of plot-culture time and resulting gain are
unmeasured. Do not assume it explains the multi-second calls.

### 3. Radius-loop and eligibility caching

Precomputed radius offsets or area-eligibility information could reduce routine
iteration. However, the call distribution suggests these are lower priority
than the expensive update cascades. Cached area pointers or eligibility also
need invalidation when terrain/areas change. Any iteration rewrite must preserve
coordinate order, map wrapping and ownership-update order.

## What to measure before a substantial change

Time actual ownership changes and distinguish ordinary city-turn culture from
explicit immediate-update calls. Within ownership changes, separate visibility,
irrigation, plot-group work and unit handling. Count plot-group connectivity
checks, their group sizes, and how often they actually split a group. Separate
the flood-fill check from resource reassignment after a split. Instrument these
relatively expensive events rather than adding a timer to every culture integer
increment or tile eligibility query.

No speedup is claimed. The entire measured culture subsystem supplies an upper
bound of 13.89% of late-game elapsed time; removing half its cost would reduce
that recording's overall elapsed time by about 6.95%. Actual eligible work and
savings require further attribution and a user-operated comparison run.

## Implementation follow-up

Implemented lazy irrigation pathfinder allocation while preserving the existing
queries and per-call reuse. Also removed the redundant second working-city
refresh when clearing a live override during tile ownership changes; the setter
already performs that refresh. Both optimizations have event counters.

Added culture-specific ownership/sight/irrigation/network timing, connectivity
check versus rebuild timing and group-size/result counters. Normal versus
explicit immediate culture calls are separated. Duration histograms now also
record seconds per bin, and reports show slow culture turns. The same expanded
400-turn launcher collects these measurements. No network checks are omitted or
batched, and no performance improvement is claimed before the comparison run.

The follow-up recording completed without errors but showed no measurable net
speedup. At the user's request, both experimental optimizations were reverted;
the diagnostic instrumentation remains. The targeted data attributed 41.82% of
late-game elapsed time to plot-group rebuilding across all callers, plus 4.30%
to connectivity checks. Retaining a connected component during a split is the
next candidate to assess, with resource accounting and component ordering as
explicit correctness constraints.

## Incremental rebuild implementation

The next implementation retains a valid, reached majority component, preserving
its plot-group ID. Membership is collected with the existing engine finder and
the same connectivity predicate, in a second pass performed only after a split.
Its count and bitmap are checked before any membership is changed. Detached
members are removed using `setPlotGroup`/`deletePlotsNode`, preserving resource
contribution and city-access bookkeeping, and reassigned using `updatePlotGroup`
in their original list order. Once reassignment starts, only local state is
used because merging may delete the retained group object.

Invalid root tiles, components no larger than half the group, or inconsistent
membership collection fall back to the prior full teardown/rebuild. No work is
deferred until the end of a city/turn. Reports distinguish membership collection,
incremental updates and full fallbacks, and count retained/detached memberships.
In-game correctness, multiplayer behavior and performance remain to be measured.
