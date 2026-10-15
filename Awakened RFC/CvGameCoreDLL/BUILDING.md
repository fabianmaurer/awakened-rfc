# Building the Awakened RFC game DLL

Build this DLL with the VC7.1 toolchain used by Civilization IV: Beyond the Sword. Modern MSVC creates different runtime dependencies and is not the supported game build here. The local build procedure, dependency layout, and multiplayer notes are documented in the repository [AGENTS.md](../../AGENTS.md).

The project launcher is Visual Studio 2022 MSBuild, but compilation and linking are performed by Microsoft Visual C++ Toolkit 2003 through NMake/jom. Required local dependencies include Python 2.4, Boost.Python 1.32 built for VC7.1, the VC7.1 CRT libraries, and the Windows SDK paths configured in `Makefile.settings`. The vendor toolchain and dependency binaries are excluded from Git and must be provisioned locally. Create the machine-specific settings file from `Makefile.settings.example` and configure the installed mod path before building.

The Release build copies the resulting DLL to `Assets/CvGameCoreDLL.dll` in the mod workspace and, when its contents differ, to the installed Awakened RFC mod folder configured by `CIV4_MOD_INSTALL_PATH` in `Makefile.settings`. Keep Civ4 closed during builds so the installed DLL can be replaced. All multiplayer participants should use the same mod files and DLL. A successful compile does not replace in-game load validation; gameplay changes also need multiplayer validation.
