"""Package the playable mod. Uses Python 3's standard library only.

    python tools/package_release.py
    python tools/package_release.py --version v0.1.0

Uses the existing Assets/CvGameCoreDLL.dll; does not compile or publish.
"""
import argparse
from pathlib import Path
import re
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'Awakened RFC'
SKIP_DIRS = {'__pycache__', '.git', '.svn', '.vs', '_rollback-backup'}
SKIP_SUFFIXES = {'.pyc', '.pyo', '.pdb', '.obj', '.pch', '.ilk', '.idb',
                 '.log', '.tmp', '.bak', '.orig', '.rej'}
REPORTING_FILES = {'Assets/Python/GameObserver.py', 'Assets/Python/ObserverStartup.py',
                   'Assets/XML/Text/CIV4GameText_Observer.xml'}
INSTALL = """Awakened Rhye's and Fall of Civilization
======================================

Requires Civilization IV: Beyond the Sword, patched to 3.19.

1. Extract the entire "Awakened RFC" folder into Beyond the Sword's Mods folder.
   Example for Steam:
   .../Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Mods/
2. Keep the folder named "Awakened RFC". Do not nest it inside another folder.
3. Start Beyond the Sword and choose Advanced > Load a Mod > Awakened RFC.
4. Choose one of the included scenarios: 3000 BC, 800 BC, 600 AD or 1453 AD.

When updating, replace the previous Awakened RFC folder rather than merging
files. Changes are
intended for new games; compatibility with older saves is not guaranteed.
All multiplayer participants must use the same release.

No compiler, separate Python installation or original RFC mod is required
to play. The compiled game DLL, scripts and assets are included.

Repository and releases: https://github.com/fabianmaurer/awakened-rfc
Asset credits and licenses are retained inside the mod's Assets folder.
"""


def runtime_files(include_reporting=False):
    """Allowlist runtime roots so new development folders cannot leak in."""
    config = MOD / 'Awakened RFC.ini'
    required = (config, MOD / 'Assets/CvGameCoreDLL.dll')
    for path in required:
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError('Missing or empty runtime file: ' + str(path))
    dll = (MOD / 'Assets/CvGameCoreDLL.dll').read_bytes()
    expected = b'AWAKENED_RFC_REPORTING=' + (b'1' if include_reporting else b'0')
    other = b'AWAKENED_RFC_REPORTING=' + (b'0' if include_reporting else b'1')
    if expected not in dll or other in dll:
        raise ValueError('DLL reporting mode does not match package mode; rebuild with '
                         'ARFC_ENABLE_REPORTING=' + ('1' if include_reporting else '0'))
    for folder in ('Assets', 'PublicMaps'):
        if not (MOD / folder).is_dir():
            raise ValueError('Missing runtime directory: ' + str(MOD / folder))
    if not any((MOD / 'PublicMaps').glob('*.CivBeyondSwordWBSave')):
        raise ValueError('No playable scenarios found in PublicMaps.')
    paths = [config]
    for folder in ('Assets', 'PublicMaps'):
        for path in (MOD / folder).rglob('*'):
            relative = path.relative_to(MOD)
            if not include_reporting and relative.as_posix() in REPORTING_FILES:
                continue
            if (not path.is_file() or any(p.startswith('.') or p in SKIP_DIRS
                                         for p in relative.parts)
                    or path.suffix.lower() in SKIP_SUFFIXES
                    or path.name.endswith('~')):
                continue
            # Do not accidentally package linked files from outside the mod.
            if path.is_symlink() or not path.resolve().is_relative_to(MOD.resolve()):
                raise ValueError('Runtime asset points outside the mod: ' + str(path))
            paths.append(path)
    return sorted(paths, key=lambda p: p.relative_to(MOD).as_posix())


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--version', help='Optional filename label, e.g. v0.1.0')
    parser.add_argument('--include-reporting', action='store_true',
                        help='Development package; requires ARFC_ENABLE_REPORTING=1 DLL')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'dist',
                        help='Destination directory (default: workspace/dist)')
    args = parser.parse_args()
    if args.version and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', args.version):
        parser.error('--version must contain only letters, digits, dots, underscores or hyphens')
    output_dir = args.output_dir.resolve()
    if output_dir.is_relative_to(MOD.resolve()):
        parser.error('--output-dir must be outside the mod folder')
    try:
        paths = runtime_files(args.include_reporting)
    except ValueError as error:
        parser.error(str(error))
    name = ('Awakened-RFC' + ('-' + args.version if args.version else '')
            + ('-reporting' if args.include_reporting else '') + '.zip')
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / name
    # Finish the new archive before replacing any previous package.
    with tempfile.NamedTemporaryFile(dir=output_dir, suffix='.tmp', delete=False) as handle:
        temporary = Path(handle.name)
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED,
                             compresslevel=6) as archive:
            for path in paths:
                archive.write(path, (Path(MOD.name) / path.relative_to(MOD)).as_posix())
            archive.writestr('INSTALL.txt', INSTALL)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    size = destination.stat().st_size / (1024 * 1024)
    print('Created: ' + str(destination))
    print(f'{len(paths)} mod files + INSTALL.txt; {size:.1f} MiB compressed')
    print('Development reporting package.' if args.include_reporting else
          'Uses the existing compiled gameplay DLL. Ready to attach to a GitHub release.')


if __name__ == '__main__':
    main()
