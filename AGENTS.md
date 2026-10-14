# RFC MP Plus build notes

## Save compatibility

The user explicitly does not require compatibility with existing saves. Implement gameplay changes for new games; do not add save migrations or preserve old mechanics solely for existing saves.

## Civilization modifiers and unique powers

General civilization-specific growth, production, research and maintenance tuning is removed. Named civilization unique powers must remain active. Apply them separately from bypassed cost-tuning switches: China trains melee/gunpowder units at 1.5x speed, Maya receive their 40% research discount through the Medieval era, and Persia gains +2 stability per conquered city. When changing a broad modifier block, check for embedded unique powers before disabling it. See `docs/UniquePowersAudit.md` for the audit against the original Rhye's and Fall MP source.

## Civ4 game DLL

Use the original 32-bit VC7.1 toolchain (Microsoft Visual C++ Toolkit 2003, compiler 13.10.3077 / linker 7.10.3077). The Civilization IV DLL uses Python 2.4, Boost.Python 1.32 and the VC7.1 runtime. A modern-MSVC rebuild changes runtime dependencies and previously caused this mod to fail loading, so do not use the CMake/modern-MSVC build for the game DLL.

### Local prerequisites

The local build expects the following prerequisites under `RFC MP Plus/CvGameCoreDLL`. These downloaded/vendor toolchain files are machine-local and excluded from Git; provision them separately when setting up a fresh checkout:

- `legacy-toolchain/Microsoft Visual C++ Toolkit 2003`: VC7.1 compiler, linker and standard headers.
- `legacy-toolchain/lib`: legacy CRT libraries (`libc.lib`, `libcd.lib`, `libcmt.lib`, `libcmtd.lib`, `msvcrt.lib`, `msvcrtd.lib`, `oldnames.lib`, `oldnamesd.lib`).
- `Boost-1.32.0/libs`: DoC/Civ4 VC7.1 Boost.Python 1.32 import libraries and matching runtime DLLs.
- `Python24`: Python 2.4 headers and import library.
- Windows SDK 10.0.26100.0 x86 headers/libraries and `rc.exe`.
- Visual Studio 2022 MSBuild is only the project launcher; it invokes the legacy NMake/jom toolchain configured in `Makefile.settings`.

These paths are machine-specific and are recorded in the local `Makefile.settings`. Create it by copying `Makefile.settings.example`, then update `TOOLKIT`, `PSDK`, `RC`, and `CIV4_MOD_INSTALL_PATH`. The local settings file is ignored by Git so another checkout does not inherit this machine's paths. The SDK include/library paths and compatibility adjustments are in `Makefile` and should be retained.

### Build

Open PowerShell in `RFC MP Plus/CvGameCoreDLL`, then run:

```powershell
$vc = 'C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64'
$msbuild = 'C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe'
$env:Path = "$vc;$env:Path"
& $msbuild 'CvGameCoreDLL.vcxproj' /p:Configuration=Release /p:Platform=Win32 /verbosity:minimal /m:1
```

This invokes `nmake` for source/dependency preparation and `bin\jom build` for the actual VC7.1 compile/link. `Makefile` is configured with `YOURMOD=..`, so a successful build creates `Release\CvGameCoreDLL.dll` and copies it to `Assets\CvGameCoreDLL.dll` in this mod tree. `CIV4_MOD_INSTALL_PATH` in `Makefile.settings` points to the installed RFC MP Plus folder; after each successful build, the Makefile compares the built DLL to the installed one and copies it only when the contents differ. Keep Civ4 closed during builds so the installed DLL can be replaced. Check the MSBuild exit code and `legacy-toolchain\legacy-build.log` if output was redirected.

### Runtime and multiplayer checks

- The DLL must be x86 and link against the VC7.1-era runtime (`MSVCR71.dll`, `msvcp71.dll`), Python 2.4 and `boost_python-vc71-mt-1_32.dll`.
- Before distributing, inspect dependencies with a PE dependency viewer or `dumpbin /dependents`; do not ship a DLL that unexpectedly imports the modern VC runtime.
- All multiplayer peers need the same mod files and DLL. Tooltip/UI-only changes should not alter synchronized game state, but still require in-game load validation; gameplay changes require multiplayer validation.
- Do not add/run tests unless the user asks. The game itself is the authoritative load/runtime check.

## Text XML localization

- Every `<TEXT>` entry in every loaded text XML must contain all five language elements: `<English>`, `<French>`, `<German>`, `<Italian>`, and `<Spanish>`. Civ IV uses numeric language indexes (English 0, French 1, German 2, Italian 3, Spanish 4) and derives its available language count from the least complete text entry. One entry missing a language can therefore make menu labels disappear for that language across the entire mod, even when the XML parses successfully.
- For a new key, provide real translations where available. If a translation is not ready, copy the English wording into the other language elements; never omit an element.
- Dynamic font symbols passed through `gDLL->getText` use Civ4's `%F` placeholders (for example `%D1_Change%F2_HappyOrUn` for a signed amount and happiness/unhappiness symbol). Do not use printf's `%c`; follow the matching original game text entry. Fixed symbols can use `[ICON_HAPPY]`, `[ICON_UNHAPPY]`, etc.
- Preserve the encoding declared in each XML file when reading it. Original RFC text includes ISO-8859-1 files with literal accented characters; reading these as UTF-8 with replacement destroys the characters permanently. New/converted XML should declare UTF-8 and preferably use numeric character references (for example `&#228;` for ä). Never save lossy `?`, U+FFFD, or mojibake in translated words. `tools/inspect_text_encoding.py` reports suspicious German text; restore damaged original entries from the original mod by key and language rather than guessing lost accents.
- After changing or adding text XML, launch Civ IV while holding Shift to clear/rebuild the text cache before checking the affected language. Confirm the text files load and check the menu in a non-English language; a successful XML load alone does not catch an incomplete language set.
- Audit all loaded text XML entries for the five required language elements before finishing a text change. Do not check only the file edited: any incomplete entry can reduce the global language count.

## Related files

- `RFC MP Plus/CvGameCoreDLL/Makefile.settings`: local paths and link additions.
- `RFC MP Plus/CvGameCoreDLL/Makefile`: legacy SDK build rules and compatibility adjustments.
- `RFC MP Plus/CvGameCoreDLL/BUILDING.md`: overview and rationale.
