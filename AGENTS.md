# Awakened RFC build notes

## Local environment instructions

Read `AGENTS.local.md` at the repository root when it exists for machine-specific
paths and build commands. Keep such details in ignored `*.local.md` files or
existing ignored configuration files; tracked instructions must use portable
commands or clearly marked path placeholders.

## Lean working workflow

- Keep work proportional to the request. Implement the agreed change and necessary integration; defer unrelated cleanup, redesign and tooling.
- Reuse context and findings already established in the conversation. Do not repeat repository discovery or reread entire documents without a concrete reason.
- Batch independent inspections. Read bounded snippets; parse minified XML to inspect selected entries instead of printing whole lines or files.
- Use existing build, audit, generation and synchronization tools. Create new helpers only when needed for the implementation or ongoing maintenance, not merely to wrap a few edits.
- Research only unresolved facts that affect the requested decision. Stop once there is sufficient evidence; do not turn routine implementation into a separate research project.
- Choose static checks that cover the changed behavior and file types; do not run every available audit routinely. Run each applicable check once after the relevant edits. Repeat only after a failure, a further relevant edit or a specific unresolved concern. The no-unrequested-tests rule below still applies.
- Update an existing relevant document briefly when needed. Avoid duplicate reports, lengthy implementation narratives and transcripts of routine verification.
- Give short progress updates about meaningful findings or blockers. Finish with the outcome, validation and any actual limitation; omit routine command inventories.
- Preserve the legacy toolchain, localization, unique-power and user-operated gameplay requirements below. Efficiency must not bypass these safeguards.

## Mod identity

The full title is **Awakened Rhye's and Fall of Civilization**. The mod folder
and matching configuration file are `Awakened RFC` and `Awakened RFC.ini`.
Scenario `ModPath` values and launch arguments must use `Mods\Awakened RFC`.
The repository is `git@github.com:fabianmaurer/awakened-rfc.git`. The checkout
directory may have a different name from the mod directory. Internal `RFCMP` XML keys,
defines and asset subdirectories remain valid identifiers.

## Save compatibility

The user explicitly does not require compatibility with existing saves. Implement gameplay changes for new games; do not add save migrations or preserve old mechanics solely for existing saves.

## Civilization modifiers and unique powers

General civilization-specific growth, production, research and maintenance tuning is removed. Named civilization unique powers must remain active. Apply them separately from bypassed cost-tuning switches: China trains melee/gunpowder units at 1.5x speed, Maya receive their 40% research discount through the Medieval era, and Persia gains +2 stability per conquered city. When changing a broad modifier block, check for embedded unique powers before disabling it. See `docs/UniquePowersAudit.md` for the audit against the original Rhye's and Fall MP source.

## Civ4 game DLL

Use the original 32-bit VC7.1 toolchain (Microsoft Visual C++ Toolkit 2003, compiler 13.10.3077 / linker 7.10.3077). The Civilization IV DLL uses Python 2.4, Boost.Python 1.32 and the VC7.1 runtime. A modern-MSVC rebuild changes runtime dependencies and previously caused this mod to fail loading, so do not use the CMake/modern-MSVC build for the game DLL.

### Local prerequisites

The local build expects the following prerequisites under `Awakened RFC/CvGameCoreDLL`. These downloaded/vendor toolchain files are machine-local and excluded from Git; provision them separately when setting up a fresh checkout:

- `legacy-toolchain/Microsoft Visual C++ Toolkit 2003`: VC7.1 compiler, linker and standard headers.
- `legacy-toolchain/lib`: legacy CRT libraries (`libc.lib`, `libcd.lib`, `libcmt.lib`, `libcmtd.lib`, `msvcrt.lib`, `msvcrtd.lib`, `oldnames.lib`, `oldnamesd.lib`).
- `Boost-1.32.0/libs`: DoC/Civ4 VC7.1 Boost.Python 1.32 import libraries and matching runtime DLLs.
- `Python24`: Python 2.4 headers and import library.
- Windows SDK x86 headers/libraries and `rc.exe`, matching the SDK version used by `Makefile`.
- Visual Studio 2022 MSBuild is only the project launcher; it invokes the legacy NMake/jom toolchain configured in `Makefile.settings`.

These paths are machine-specific and are recorded in the local `Makefile.settings`. Create it by copying `Makefile.settings.example`, then update `TOOLKIT`, `PSDK`, `RC`, and `CIV4_MOD_INSTALL_PATH`. The local settings file is ignored by Git so another checkout does not inherit this machine's paths. The SDK include/library paths and compatibility adjustments are in `Makefile` and should be retained.

### Build

Rebuild the DLL only when C++ sources, headers or build inputs change, or when
explicitly requested. Python, XML, map and documentation edits alone do not
require a DLL build. Use the existing local prerequisites and settings; revisit
toolchain setup only if something is missing, a build fails, or setup changes.

Open PowerShell in `Awakened RFC/CvGameCoreDLL` with MSBuild and NMake available
on `PATH`, then run the command below. See `AGENTS.local.md`, when present,
for this machine's launcher paths and environment setup.

```powershell
MSBuild.exe 'CvGameCoreDLL.vcxproj' /p:Configuration=Release /p:Platform=Win32 /verbosity:minimal /m:1
```

This invokes `nmake` for source/dependency preparation and `bin\jom build` for the actual VC7.1 compile/link. `Makefile` is configured with `YOURMOD=..`, so a successful build creates `Release\CvGameCoreDLL.dll` and copies it to `Assets\CvGameCoreDLL.dll` in this mod tree. `CIV4_MOD_INSTALL_PATH` in `Makefile.settings` points to the installed Awakened RFC folder; after each successful build, the Makefile compares the built DLL to the installed one and copies it only when the contents differ. Keep Civ4 closed during builds so the installed DLL can be replaced. Check the MSBuild exit code and `legacy-toolchain\legacy-build.log` if output was redirected.

### Runtime and multiplayer checks

- The DLL must be x86 and link against the VC7.1-era runtime (`MSVCR71.dll`, `msvcp71.dll`), Python 2.4 and `boost_python-vc71-mt-1_32.dll`.
- Inspect DLL architecture and dependencies when changing the toolchain/link settings or preparing a release; do not repeat the inspection for ordinary builds using unchanged, already-verified settings. Do not ship a DLL that unexpectedly imports the modern VC runtime.
- All multiplayer peers need the same mod files and DLL. In-game checks are user-operated: validate affected UI/loading when requested, and validate gameplay changes in multiplayer before claiming multiplayer readiness. Unrequested runtime validation is not a prerequisite for completing an implementation; state that it remains unverified where relevant.
- For routine installed-mod synchronization, copy changed runtime files and the rebuilt DLL when applicable, and verify those copies. Reserve full runtime-manifest comparisons for release preparation, suspected workspace/install mismatches, or an explicit request. Do not synchronize documentation-only changes.
- Do not add/run tests unless the user asks. The game itself is the authoritative load/runtime check.

### Player-specific event popups

- Open a player-specific Python decision popup only on the affected player's client: check `gc.getGame().getActivePlayer() == iPlayer` before creating or launching it. `isHuman()` alone is insufficient in multiplayer because every client runs the event code for every human player.
- Keep pending decisions on every peer and synchronize their resolution. For these Python popups, retain `EventContextTypes.EVENTCONTEXT_ALL`; restrict the UI locally, but do not restrict the synchronized apply callback to the active player.
- Give each pending decision a unique ID and pass its owner and ID through `popup.setUserData`. Forward `playerID` and `netUserData` from the event manager, verify the responding player against the stored owner, and resolve each decision only once. Multiple open events must not overwrite one shared pending slot or one slot per player.
- Apply this rule to new and modified event choices. Slave revolts, refugees and slave markets in `Assets/Python/Slavery.py` are the reference implementation for this fix.

- `CyPopupInfo` uses a different delivery path: enqueue it with `addPopup(iOwner)` (or the owning `CvPlayer` in C++). A local `BUTTONPOPUP_PYTHON` click callback must not directly change synchronized game state; use a synchronized message or an acknowledgement with no gameplay effects.

Static review on 2026-10-18: checked all added event/decision paths for recipient routing and response synchronization. Slave revolt, refugee and slave-market choices use the corrected owner/decision IDs. Democracy announcements already use `addPopup(iPlayer)` and have no click callback that changes gameplay; conquest/relocation choices already target the conqueror and send player-scoped city tasks. Cultural uprisings and historical birth-unrest warnings use addressed messages without player choices. Embargo requests use synchronized mod-net messages. The standard XML event path also queues choices on the owning player and synchronizes responses. No additional instance of the reported popup bug was found in these paths. This is a source review, not in-game multiplayer validation; legacy RFC congress/civilization-switch systems are outside this review of added events.

## Optional AI observer

When investigating performance, flag small mechanic changes only when the
investigation reveals a concrete opportunity relevant to the measured bottleneck.
Do not perform a separate mechanics audit routinely. Explain any gameplay
tradeoff and distinguish measured gains from estimates for the user's review.

See `testing/README.md`. `testing/run_observer.py` activates recordings only in
its own child process with a token and PID; ordinary launches stay disabled.
Modes are `balance`, `diagnostics` and `performance`. Balance/diagnostics use
3000 BC; performance also supports the 600 AD scenario (turn 181, China).
Use the dedicated `setObserverAutoPlay` control, never `setAIAutoPlay` for
testing an existing civilization: the latter deletes its cities and units.
The observer control is transient, excluded from saves, and refused in
multiplayer. Recordings and `testing/observer.local.ini` are ignored local files.
Implementing the tooling does not authorize starting gameplay test runs;
the existing instruction against running unrequested tests still applies.

### User-operated testing workflow

When the user requests a particular test, prepare a standalone script file
with the requested modes, seeds, settings and run counts. Give the user the
script path and a brief description; do not execute it, launch Civ4, wait
for its completion or poll its status. The user runs the script locally.
Any progress monitoring belongs inside that script/launcher and does not
require an agent session. Analyze recordings only when the user explicitly
asks afterward. A request to prepare a test run authorizes script creation,
not execution. This applies to single runs and batches.

## Text XML localization

- Every `<TEXT>` entry in every loaded text XML must contain all five language elements: `<English>`, `<French>`, `<German>`, `<Italian>`, and `<Spanish>`. Civ IV uses numeric language indexes (English 0, French 1, German 2, Italian 3, Spanish 4) and derives its available language count from the least complete text entry. One entry missing a language can therefore make menu labels disappear for that language across the entire mod, even when the XML parses successfully.
- For a new key, provide real translations where available. If a translation is not ready, copy the English wording into the other language elements; never omit an element.
- Dynamic font symbols passed through `gDLL->getText` use Civ4's `%F` placeholders (for example `%D1_Change%F2_HappyOrUn` for a signed amount and happiness/unhappiness symbol). Do not use printf's `%c`; follow the matching original game text entry. Fixed symbols can use `[ICON_HAPPY]`, `[ICON_UNHAPPY]`, etc.
- Preserve the encoding declared in each XML file when reading it. Original RFC text includes ISO-8859-1 files with literal accented characters; reading these as UTF-8 with replacement destroys the characters permanently. New/converted XML should declare UTF-8 and preferably use numeric character references (for example `&#228;` for ä). Never save lossy `?`, U+FFFD, or mojibake in translated words. `tools/inspect_text_encoding.py` reports suspicious German text; restore damaged original entries from the original mod by key and language rather than guessing lost accents.
- When the user performs an in-game localization check, check the affected text/language. Check non-English menus when investigating language availability or menu-label problems. Do not launch Civ IV or require a menu check for every text edit; these checks do not block completion of ordinary text changes.
- For localized edits, check changed or added `<TEXT>` entries for all five required language elements and correct encoding, and confirm the edited XML files parse. If a generator rewrites whole files, check all entries in those generated files. Do not audit unrelated localization files routinely. Reserve a full localization audit for broad localization changes, suspected global language/menu problems, or an explicit user request.

## Related files

- `Awakened RFC/CvGameCoreDLL/Makefile.settings`: local paths and link additions.
- `Awakened RFC/CvGameCoreDLL/Makefile`: legacy SDK build rules and compatibility adjustments.
- `Awakened RFC/CvGameCoreDLL/BUILDING.md`: overview and rationale.
