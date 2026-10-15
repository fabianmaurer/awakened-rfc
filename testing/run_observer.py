"""Launch isolated observer runs. Python 3.9+, standard library only."""
import argparse
import configparser
import gzip
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import time

from observer_startup import SetupConfirmation

TESTING = Path(__file__).resolve().parent
ROOT = TESTING.parent
DEFAULT_EXE = Path("C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Civ4BeyondSword.exe")
SCENARIO = 'Start 1 - 3000 BC.CivBeyondSwordWBSave'
SCENARIOS = {'3000bc': SCENARIO,
             '800bc': 'Start 2 - 800 BC.CivBeyondSwordWBSave',
             '600ad': 'Start 3 - 600 AD.CivBeyondSwordWBSave',
             '840ad': 'Start 4 - 840 AD.CivBeyondSwordWBSave'}


def fingerprint(mod):
    digest = hashlib.sha256()
    manifest = {}
    files = [mod / 'Awakened RFC.ini']
    for folder in ('Assets', 'PublicMaps'):
        files += [p for p in (mod / folder).rglob('*') if p.is_file()
                  and '__pycache__' not in p.parts and not any(s.startswith('.') for s in p.relative_to(mod).parts)
                  and p.suffix.lower() not in ('.pyc', '.pyo', '.log', '.tmp', '.bak')]
    if not (mod / 'Assets/CvGameCoreDLL.dll').is_file() or not (mod / 'PublicMaps' / SCENARIO).is_file():
        raise ValueError('Missing mod DLL or 3000 BC scenario in ' + str(mod))
    for path in sorted(files):
        relative = path.relative_to(mod).as_posix()
        file_hash = hashlib.sha256(path.read_bytes()).digest()
        manifest[relative] = file_hash
        digest.update(relative.encode('utf-8') + b'\0')
        digest.update(file_hash)
    return digest.hexdigest(), manifest


def read_status(path):
    try:
        return json.loads(path.read_text(encoding='ascii'))
    except (OSError, ValueError):
        return None


def compress_recording(run):
    """Compress outside Civ4, whose bundled Python has no gzip module."""
    source = run / 'turns.jsonl'
    if not source.is_file():
        return
    destination = run / 'turns.jsonl.gz'
    temporary = run / 'turns.jsonl.gz.tmp'
    try:
        with source.open('rb') as reader, gzip.open(temporary, 'wb', compresslevel=3) as writer:
            shutil.copyfileobj(reader, writer)
        temporary.replace(destination)
        source.unlink()
    finally:
        temporary.unlink(missing_ok=True)


def game_running():
    result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq Civ4BeyondSword.exe', '/FO', 'CSV', '/NH'],
                            capture_output=True, text=True, check=True,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    return 'civ4beyondsword.exe' in result.stdout.lower()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('balance', 'diagnostics', 'performance'))
    start = parser.add_mutually_exclusive_group()
    start.add_argument('--scenario', choices=tuple(SCENARIOS))
    start.add_argument('--start', type=int, choices=range(4),
                       help='0: 3000 BC, 1: 800 BC, 2: 600 AD, 3: 840 AD')
    parser.add_argument('--games', '--runs', dest='games', type=int, default=1)
    parser.add_argument('--turns', type=int)
    parser.add_argument('--seed', type=int, default=1, help='First seed; incremented for each game')
    parser.add_argument('--observe-only', action='store_true', help='Record a human-controlled game; do not enable AI control')
    parser.add_argument('--manual-start', action='store_true', help='Leave scenario setup to the user instead of confirming it automatically')
    parser.add_argument('--exe', type=Path, default=DEFAULT_EXE)
    parser.add_argument('--output-dir', type=Path, default=TESTING / 'runs')
    parser.add_argument('--checkpoint-interval', type=int, help='Turns between saves; 0 disables saves')
    parser.add_argument('--record-interval', type=int, default=1, help='Turns between state snapshots (events are collected every turn)')
    parser.add_argument('--startup-timeout', type=int, default=300)
    parser.add_argument('--stall-timeout', type=int, default=600)
    args = parser.parse_args()
    args.scenario = args.scenario or tuple(SCENARIOS)[args.start if args.start is not None else 0]
    unattended = not args.observe_only and not args.manual_start
    scenario = SCENARIOS[args.scenario]
    if os.name != 'nt':
        parser.error('The launcher currently supports Windows only')
    config = configparser.ConfigParser()
    config.read(TESTING / 'observer.local.ini', encoding='utf-8')
    mode = args.mode or config.get('Observer', 'Mode', fallback='balance')
    turns = args.turns if args.turns is not None else config.getint('Observer', 'Turns', fallback=500)
    interval = args.checkpoint_interval
    if interval is None:
        interval = config.getint('Observer', 'CheckpointInterval', fallback=25 if mode == 'diagnostics' else 100)
    if mode == 'performance':
        interval = 0
        if args.observe_only:
            parser.error('Performance mode requires AI control')
    if mode not in ('balance', 'diagnostics', 'performance') or args.games < 1 or turns < 1 or interval < 0 or args.record_interval < 1:
        parser.error('Invalid mode, game count, turn count or checkpoint interval')
    if args.seed < 0 or args.seed + args.games > 2**32 or min(args.startup_timeout, args.stall_timeout) < 1:
        parser.error('Seeds must fit unsigned 32-bit values; timeouts must be positive')
    if not args.exe.is_file():
        parser.error('Game executable not found: ' + str(args.exe))
    if game_running():
        parser.error('Close Civ4 before starting a batch; existing games are never terminated')
    installed = args.exe.resolve().parent / 'Mods/Awakened RFC'
    if not (installed / 'PublicMaps' / scenario).is_file():
        parser.error('Scenario not found: ' + scenario)
    output_root = args.output_dir.resolve()
    if output_root.is_relative_to(installed.resolve()) or output_root.is_relative_to((ROOT / 'Awakened RFC').resolve()):
        parser.error('--output-dir must be outside both mod folders')
    try:
        runtime_hash, installed_files = fingerprint(installed)
        workspace_hash, workspace_files = fingerprint(ROOT / 'Awakened RFC')
        if runtime_hash != workspace_hash:
            differences = []
            for relative in sorted(installed_files.keys() | workspace_files.keys()):
                if relative not in workspace_files:
                    differences.append('Only installed: ' + relative)
                elif relative not in installed_files:
                    differences.append('Missing from installed mod: ' + relative)
                elif installed_files[relative] != workspace_files[relative]:
                    differences.append('Changed: ' + relative)
            detail = '\n'.join(differences[:20])
            if len(differences) > 20:
                detail += '\n... and %d more differences' % (len(differences) - 20)
            parser.error('Installed mod differs from workspace. Sync runtime files before recording.\n' + detail)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    version = subprocess.run(['git', 'describe', '--always', '--dirty', '--tags'], cwd=ROOT,
                             capture_output=True, text=True).stdout.strip() or 'unknown'
    control = 'human' if args.observe_only else 'ai'
    batch_name = '%s-%s-%s-%dgames-%dturns-seeds-%d-%d-%s-%s' % (
        mode, control, args.scenario, args.games, turns, args.seed, args.seed + args.games - 1,
        time.strftime('%Y%m%d-%H%M%S'), secrets.token_hex(3))
    batch = output_root / batch_name
    batch.mkdir(parents=True)
    print('Batch: ' + str(batch), flush=True)
    results = []
    for index in range(args.games):
        if game_running():
            raise RuntimeError('Another Civ4 process appeared; stopping batch')
        seed = args.seed + index
        run = batch / ('game-%03d-%s-%s-%dturns-seed-%d' % (index+1, mode, control, turns, seed))
        run.mkdir()
        token = secrets.token_hex(24)
        activation = run / 'observer.ini'
        env = os.environ.copy()
        env.pop('AWAKENED_RFC_PERFORMANCE_OUTPUT', None)
        if mode == 'performance':
            env['AWAKENED_RFC_PERFORMANCE_OUTPUT'] = str(run / 'performance-native.csv')
        env['AWAKENED_RFC_OBSERVER_CONFIG'] = str(activation)
        env['AWAKENED_RFC_OBSERVER_TOKEN'] = token
        settings = configparser.RawConfigParser()
        settings['Observer'] = {'Mode': mode, 'Autoplay': str(not args.observe_only),
                                'Scenario': args.scenario,
                                'Turns': str(turns), 'Seed': str(seed), 'CheckpointInterval': str(interval),
                                'RecordInterval': str(args.record_interval), 'Unattended': str(unattended),
                                'OutputDirectory': str(run), 'Token': token, 'ProcessId': '0',
                                'ModVersion': version, 'RuntimeFingerprint': runtime_hash, 'RunId': run.name}
        # Write once before launch, then bind to the exact child PID before
        # Civ4 imports Python. Token and environment exist only for this child.
        def write_activation():
            temporary = activation.with_suffix('.ini.tmp')
            with temporary.open('w', encoding='ascii') as handle:
                settings.write(handle)
            temporary.replace(activation)
        write_activation()
        command = ('"' + str(args.exe.resolve()) + '" mod="Mods\\Awakened RFC" /fxsload="'
                   + str(installed / 'PublicMaps' / scenario) + '"')
        (run / 'launch.json').write_text(json.dumps({'seed': seed, 'mode': mode, 'turns': turns,
                                                   'scenario': args.scenario,
                                                   'autoplay': not args.observe_only, 'version': version,
                                                   'unattended': unattended,
                                                   'record_interval': args.record_interval,
                                                   'runtime_fingerprint': runtime_hash, 'command': command}, indent=2))
        process = subprocess.Popen(command, cwd=args.exe.parent, env=env)
        settings['Observer']['ProcessId'] = str(process.pid)
        write_activation()
        startup = SetupConfirmation(process.pid, run) if unattended else None
        instruction = 'Scenario setup will be confirmed automatically.' if unattended else 'Confirm scenario setup if Civ4 displays it.'
        print('Game %d/%d, seed %d. %s' % (index+1, args.games, seed, instruction), flush=True)
        started = False
        last_progress = time.monotonic()
        heartbeat = None
        outcome = {'run': run.name, 'seed': seed, 'status': 'interrupted'}
        try:
            while process.poll() is None:
                complete = read_status(run / 'complete.json')
                failed = read_status(run / 'failed.json')
                if complete is not None:
                    outcome.update(status='complete', **complete)
                    break
                if failed is not None:
                    outcome.update(status='failed', details=failed)
                    print('Observer failed during: ' + failed.get('phase', 'unknown'), flush=True)
                    print(failed.get('traceback', 'No traceback recorded.'), flush=True)
                    break
                if startup is not None and not started:
                    try:
                        startup.tick(read_status(run / 'setup-ready.json'))
                    except (OSError, RuntimeError) as error:
                        outcome.update(status='startup_failed', details=str(error))
                        print('Automatic setup failed: ' + str(error), flush=True)
                        break
                if not started and (run / 'started.json').is_file():
                    started = True
                    last_progress = time.monotonic()
                current = read_status(run / 'heartbeat.json')
                if current != heartbeat:
                    heartbeat = current
                    last_progress = time.monotonic()
                timeout = args.stall_timeout if started else args.startup_timeout
                if time.monotonic() - last_progress > timeout:
                    outcome.update(status='stalled' if started else 'startup_timeout', last_heartbeat=heartbeat)
                    break
                # Respond promptly between setup screens; retain the normal
                # polling interval once the simulation is running.
                time.sleep(0.25 if startup is not None and not started else 1)
            else:
                outcome.update(status='exited', exit_code=process.returncode)
        finally:
            # Only terminate the child created for this run, never other games.
            # Recorded turns/checkpoints have already been flushed to disk.
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=30)
            activation.unlink(missing_ok=True)
            try:
                compress_recording(run)
            except OSError as error:
                # Preserve the plain recording and original run outcome.
                print('Could not compress recording; plain JSONL retained: ' + str(error), flush=True)
            results.append(outcome)
            (batch / 'batch.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
            if mode == 'performance' and ((run / 'turns.jsonl.gz').exists() or (run / 'turns.jsonl').exists()):
                from analyze_performance import summarize
                try:
                    summarize(run)
                    print('Performance report: ' + str(run / 'performance-report.md'), flush=True)
                except (OSError, ValueError, KeyError) as error:
                    print('Could not summarize performance; raw timings retained: ' + str(error), flush=True)
        print(run.name + ': ' + outcome['status'], flush=True)
        if outcome['status'] != 'complete':
            raise SystemExit('Batch stopped; inspect ' + str(run))
    analyzer = 'analyze_performance.py' if mode == 'performance' else 'analyze_observer.py'
    print('Finished. Analyse with: python testing/' + analyzer + ' "' + str(batch) + '"')


if __name__ == '__main__':
    main()
