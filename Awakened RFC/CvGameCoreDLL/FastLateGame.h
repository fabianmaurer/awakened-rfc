#ifndef FAST_LATE_GAME_H
#define FAST_LATE_GAME_H

// All decisions use synchronized state; no wall clock, local-player identity or RNG.
inline bool fastLateGame() {
    return GC.getDefineINT("RFCMP_FAST_LATE_GAME") != 0 &&
        GC.getGameINLINE().getGameTurnYear() >= GC.getDefineINT("RFCMP_FAST_LATE_YEAR");
}
inline bool fastLateDue(int id, int interval) {
    return (GC.getGameINLINE().getGameTurn() + id) % interval == 0;
}
#endif
