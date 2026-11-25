"""One-shot continuation of the 10 November pilot, ending at human review.

Run as a module from the checkout: python -m scripts.run_opus_screening.
Step 1 must already have been launched with the recorded one-shot launcher.
Existing outputs are never resumed or replaced. A failed check stops the queue.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

from research import core
from scripts import pilot_analysis, pilot_review

CONTROL = Path('artifacts/pipeline/opus55-school-screening-20261110')
CONFIG = Path('configs/pilot-opus55.json')
CALIBRATION = Path('artifacts/scores/opus55-calibration-a2-20261110')
REPEATED = Path('artifacts/scores/opus55-calibration-first50-a8-20261110')
TRAIN = Path('artifacts/scores/opus55-train-20261110')
CONDITIONS = Path('artifacts/conditions/opus55-screening-20261110')
REVIEW = Path('artifacts/human-review/pilot-20261110')
REPORT = Path('docs/pilots/2026-11-10-opus55-screening.md')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def validate_command(args):
    if not args or args[0] not in {'score', 'select', 'train', 'evaluate', 'compare'}:
        raise ValueError('This queue only supports Steps 1-7')
    if any(a in {'freeze', 'official-test', '--final-test', '--frozen-settings'} for a in args):
        raise ValueError('Official testing is outside this queue')
    if args[0] == 'evaluate' and ('--split' not in args or args[args.index('--split') + 1] != 'development'):
        raise ValueError('Only explicit development evaluation is allowed')


def screening_commands():
    commands = []
    for condition in core.CONDITIONS:
        output = f'artifacts/runs/opus55-screening-{condition}'
        commands.append(('train-' + condition, ['train', '--conditions', str(CONDITIONS), '--condition', condition,
                                              '--allow-unreviewed', '--output', output]))
    for condition in ['unchanged', *core.CONDITIONS]:
        args = ['evaluate', '--split', 'development', '--limit', '50', '--budget', '256',
                '--output', f'artifacts/runs/opus55-screening-{condition}-eval']
        if condition != 'unchanged':
            args += ['--adapter', f'artifacts/runs/opus55-screening-{condition}/adapter']
        commands.append(('eval-' + condition, args))
    return commands


def archive(root, phase, paths):
    """Hash every member; fail before replacing a previous archive."""
    root = Path(root).resolve()
    files = set()
    for relative in paths:
        path = root / relative
        if not path.exists():
            raise FileNotFoundError(path)
        files.update(p for p in path.rglob('*') if p.is_file()) if path.is_dir() else files.add(path)
    for path in files:
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError(f'Archive path outside checkout: {path}')
    hashes = {p.relative_to(root).as_posix(): sha(p) for p in sorted(files)}
    destination = root / 'artifacts/handoff' / f'2026-11-10-opus55-school-{phase}.zip'
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, 'x', compression=zipfile.ZIP_DEFLATED) as output:
        for name in hashes:
            output.write(root / name, name)
    with zipfile.ZipFile(destination) as output:
        if output.testzip() is not None or set(output.namelist()) != set(hashes):
            raise ValueError('Archive integrity check failed')
        for name, expected in hashes.items():
            if hashlib.sha256(output.read(name)).hexdigest() != expected:
                raise ValueError(f'Archived content changed: {name}')
    receipt = {'file': destination.name, 'sha256': sha(destination), 'bytes': destination.stat().st_size,
               'files': hashes, 'created_utc': stamp()}
    core.write_json(destination.with_suffix('.manifest.json'), receipt)
    return {'file': destination.relative_to(root).as_posix(), 'sha256': receipt['sha256'], 'bytes': receipt['bytes']}


class Queue:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.control = self.root / CONTROL
        with (self.control / 'queue.pid').open('x') as destination:
            destination.write(str(os.getpid()) + '\n')
        self.state = {'status': 'running', 'started_utc': stamp(), 'stage': 'waiting for Step 1', 'commands': [], 'archives': []}
        self.base_hash = sha(self.root / 'configs/pilot.json')
        self.config_hash = None
        source_files = [*self.root.glob('research/*.py'), *self.root.glob('scripts/*.py'),
                        *self.root.glob('tests/*.py'), *self.root.glob('configs/*.json'),
                        self.root / 'requirements.txt', self.root / 'requirements-lock.txt']
        self.source_hashes = {p.relative_to(self.root).as_posix(): sha(p) for p in source_files if p.exists()}
        for relative in self.source_hashes:
            destination = self.control / 'source' / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.root / relative, destination)
        core.write_json(self.control / 'source-hashes.json', self.source_hashes)
        self.save()

    def save(self):
        self.state['updated_utc'] = stamp()
        temporary = self.control / 'status.tmp'
        temporary.write_text(json.dumps(self.state, indent=2) + '\n', encoding='utf-8')
        temporary.replace(self.control / 'status.json')

    def note(self, text):
        entry = f'\n- School pipeline {stamp()}: {text}\n'
        for filename in ['docs/EXPERIMENT_LOG.md', 'docs/TEAM_GUIDE.md']:
            with (self.root / filename).open('a', encoding='utf-8') as output:
                output.write(entry)
        print(text, flush=True)

    def run(self, name, args, copied_config=False):
        validate_command(args)
        if sha(self.root / 'configs/pilot.json') != self.base_hash:
            raise ValueError('The base config changed during the run')
        if copied_config and sha(self.root / CONFIG) != self.config_hash:
            raise ValueError('The copied series config changed during the run')
        if any(sha(self.root / path) != expected for path, expected in self.source_hashes.items()):
            raise ValueError('Source or original configuration changed while the queue was running')
        if args[0] in {'score', 'train', 'evaluate'}:
            usage = subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid,used_memory', '--format=csv,noheader'], text=True)
            if usage.strip():
                raise RuntimeError('Another GPU process is present; refusing concurrent GPU work: ' + usage.strip())
        command = [sys.executable, '-m', 'research']
        if copied_config:
            command += ['--config', str(CONFIG)]
        command += args
        self.state['stage'] = name
        record = {'stage': name, 'command': command, 'started_utc': stamp()}
        self.state['commands'].append(record)
        self.save()
        started = time.monotonic()
        with (self.control / (name + '.log')).open('x') as output:
            result = subprocess.run(command, cwd=self.root, stdout=output, stderr=subprocess.STDOUT)
        record.update(exit_code=result.returncode, elapsed_seconds=time.monotonic() - started, ended_utc=stamp())
        self.save()
        if result.returncode:
            raise RuntimeError(f'{name} exited {result.returncode}; inspect its log')

    def pack(self, phase, paths):
        item = archive(self.root, phase, [*paths, CONTROL, 'docs/EXPERIMENT_LOG.md', 'docs/TEAM_GUIDE.md'])
        self.state['archives'].append(item)
        self.save()
        self.note(f"Phase {phase} archived at `{item['file']}` (SHA-256 `{item['sha256']}`). Back this up privately; Git does not carry artifacts.")

    def check_scores(self, directory, problems, candidates, count, config):
        directory = self.root / directory
        scores = core.read_jsonl(directory / 'scored.jsonl')
        attempts = core.read_jsonl(directory / 'attempts.jsonl')
        if set(pilot_analysis.unique(scores)) != set(pilot_analysis.unique(core.read_jsonl(self.root / candidates))):
            raise ValueError('Scoring changed the input candidate keys')
        manifest = read(directory / 'manifest.json')
        if manifest['config'] != config or manifest['attempts'] != count or manifest['candidates_sha256'] != sha(self.root / candidates):
            raise ValueError('Score manifest differs from the requested configuration or inputs')
        if manifest['data_manifest'] != core.data_identity(read(self.root / 'artifacts/data/pilot/manifest.json')):
            raise ValueError('Score manifest uses different locked data')
        report = pilot_analysis.validate_scores(problems, scores, attempts, count, config['candidates_per_pool'])
        core.write_json(directory / 'verification.json', report)
        return scores, attempts, report

    def execute(self):
        future = [REPEATED, TRAIN, CONDITIONS, REVIEW, REPORT, CONFIG]
        future += [Path(args[args.index('--output') + 1]) for _, args in screening_commands()]
        if any((self.root / path).exists() for path in future):
            raise FileExistsError('A future output already exists; this queue never overwrites or resumes earlier work')
        calibration = core.read_jsonl(self.root / 'artifacts/data/pilot/calibration.jsonl')
        training = core.read_jsonl(self.root / 'artifacts/data/pilot/train.jsonl')
        config = read(self.root / 'configs/pilot.json')
        while True:
            try:
                state = read(self.control / 'step1-status.json')
            except json.JSONDecodeError:
                time.sleep(1)
                continue
            if state['status'] != 'running':
                break
            os.kill(int((self.control / 'step1.pid').read_text()), 0)
            time.sleep(30)
        if state['status'] != 'complete':
            raise RuntimeError('Step 1 failed; continuation stopped')
        # The completion record is written just before the worker process exits.
        time.sleep(2)
        self.state['step1'] = state
        scores2, attempts2, verification = self.check_scores(CALIBRATION, calibration,
            Path('artifacts/rewrites/opus55-pilot-calibration-20261110/candidates.jsonl'), 2, config)
        self.note(f'Step 1 completed: {json.dumps(verification)}. Outputs: `{CALIBRATION}`.')
        self.pack('step1', [CALIBRATION, 'artifacts/preflight/opus55-school-resume-20261110'])

        first = calibration[:50]
        subset = self.control / 'calibration-first50.jsonl'
        candidates = core.read_jsonl(self.root / 'artifacts/rewrites/opus55-pilot-calibration-20261110/candidates.jsonl')
        selected = [r for r in candidates if r['id'] in {p['id'] for p in first}]
        if len(selected) != 400:
            raise ValueError('Expected all 400 candidates for the first 50 calibration questions')
        core.write_jsonl(subset, selected)
        self.run('step2-score', ['score', '--split', 'calibration', '--attempts', '8', '--candidates', str(subset), '--output', str(REPEATED)])
        scores8, attempts8, verification = self.check_scores(REPEATED, first, subset, 8, config)
        stable = pilot_analysis.stability(first, scores2, scores8, attempts2, attempts8,
                                         config['candidates_per_pool'], config['length_penalty'])
        core.write_json(self.root / REPEATED / 'stability.json', stable)
        self.note('Step 2 completed: ' + json.dumps({k: v for k, v in stable.items() if k != 'picks'}) + f'. Evidence: `{REPEATED}`.')
        self.pack('step2', [REPEATED])

        penalty = pilot_analysis.calibrate(calibration[:100], scores2, config['candidates_per_pool'])
        core.write_json(self.root / CALIBRATION / 'penalty.json', penalty)
        config = dict(config, length_penalty=penalty['chosen_penalty'])
        core.write_json(self.root / CONFIG, config)
        self.config_hash = sha(self.root / CONFIG)
        self.state['config_sha256'] = self.config_hash
        self.note(f"Step 3 chose length_penalty={penalty['chosen_penalty']}; config `{CONFIG}` SHA-256 `{self.config_hash}`. Full table and token reductions: `{CALIBRATION}/penalty.json`.")
        self.pack('step3', [CALIBRATION / 'penalty.json', CONFIG])

        args = ['score', '--candidates', 'artifacts/rewrites/opus55-pilot-train-20261110/candidates.jsonl', '--output', str(TRAIN)]
        if stable['training_attempts'] == 4:
            args += ['--attempts', '4']
        self.run('step4-score', args, True)
        scored, _, verification = self.check_scores(TRAIN, training,
            Path('artifacts/rewrites/opus55-pilot-train-20261110/candidates.jsonl'), stable['training_attempts'], config)
        self.note(f'Step 4 completed: {json.dumps(verification)}. Evidence: `{TRAIN}`.')
        self.pack('step4', [TRAIN, CONFIG])
        self.run('step5-select', ['select', '--scored', str(TRAIN / 'scored.jsonl'), '--output', str(CONDITIONS)], True)
        groups = {name: core.read_jsonl(self.root / CONDITIONS / (name + '.jsonl')) for name in core.CONDITIONS}
        ids = [r['id'] for r in groups['original']]
        if not ids or len(ids) > 89 or any([r['id'] for r in rows] != ids for rows in groups.values()):
            raise ValueError('Selected conditions violate the matched-ID preflight constraint')
        reasons = []
        lookup = {r['id']: r for r in training}
        for excluded in core.read_jsonl(self.root / CONDITIONS / 'excluded.jsonl'):
            candidates = [r for r in scored if r['id'] == excluded['id']]
            reasons.append(dict(excluded, candidate_reasons=[{'pool': r['pool'], 'candidate': r['candidate'],
                           'validation_errors': r['validation_errors'], 'feedback_error': r.get('feedback_error')} for r in candidates],
                           source_solution=lookup[excluded['id']]['solution']))
        core.write_json(self.root / CONDITIONS / 'selection-audit.json', {'retained_ids': ids, 'excluded': reasons})
        self.note(f'Step 5 retained {len(ids)} identical IDs: {ids}. Exclusion reasons: `{CONDITIONS}/selection-audit.json`.')
        self.pack('step5', [CONDITIONS, CONFIG])
        sheets = pilot_review.prepare(self.root, self.root / CONDITIONS, self.root / REVIEW)
        self.note(f"Step 6 review sheets ready: `{REVIEW}`; unique picks: " + json.dumps({p: len(s['picks']) for p, s in sheets['sheets'].items()}) + '. No human approval was inferred.')
        self.pack('step6', [REVIEW, CONDITIONS, CONFIG])

        for name, args in screening_commands():
            self.run(name, args, True)
            directory = self.root / args[args.index('--output') + 1]
            if args[0] == 'train':
                record = read(directory / 'run.json')
                if record['status'] != 'complete' or record['training_ids'] != ids or record['config'] != config or record['smoke_check'] or not record['unreviewed_screening']:
                    raise ValueError('Training metadata violates the screening design')
            else:
                record = read(directory / 'manifest.json')
                expected = [p['id'] for p in core.read_jsonl(self.root / 'artifacts/data/pilot/development.jsonl')[:50]]
                rows = core.read_jsonl(directory / 'predictions.jsonl')
                if record['config'] != config or [r['id'] for r in rows] != expected or any(r['budget'] != 256 for r in rows):
                    raise ValueError('Evaluation did not retain all 50 matched development outputs')
            self.note(f'Step 7 {name} complete: `{directory.relative_to(self.root)}`.')
            self.pack(name, [directory.relative_to(self.root), CONFIG, CONDITIONS])
        comparisons = self.control / 'comparisons'
        comparisons.mkdir(exist_ok=False)
        pairs = [('english-' + s, 'multilingual-' + s) for s in ('shortest', 'feedback')]
        pairs += [('original', name) for name in core.CONDITIONS if name != 'original']
        pairs += [('unchanged', 'original')]
        for reference, candidate in pairs:
            self.run('compare-' + reference + '-to-' + candidate,
                     ['compare', '--reference', f'artifacts/runs/opus55-screening-{reference}-eval',
                      '--candidate', f'artifacts/runs/opus55-screening-{candidate}-eval',
                      '--output', str(comparisons / f'{reference}-to-{candidate}.json')], True)
        self.report(groups, stable, penalty, comparisons)
        self.state.update(status='awaiting_human_review', stage='Step 8: human decisions required')
        self.save()
        self.note(f'SCREENING finished. Report: `{REPORT}`; worksheets: `{REVIEW}`. STOP before Step 9 until every selected rewrite has explicit human approval. Official testing remains unopened.')
        self.pack('screening-complete', [REPORT, REVIEW, CONDITIONS, CONFIG])

    def report(self, groups, stable, penalty, comparisons):
        lines = ['# Opus 5.5 pilot — UNREVIEWED SCREENING', '',
                 'School RTX 2080 Ti, unchanged emulated-BF16 runtime. This screening establishes no final research result.', '',
                 f"Matched training questions: {len(groups['original'])}. Training attempts: {stable['training_attempts']}. Length penalty: {penalty['chosen_penalty']}.",
                 f'All compared runs use `{CONFIG}` (SHA-256 `{self.config_hash}`). First 50 development questions, budget 256; no official test.', '',
                 '| Condition | Correct / 50 | Accuracy | Mean tokens | Mean seconds | Runtime failures | Truncations | Unparseable |',
                 '|---|---:|---:|---:|---:|---:|---:|---:|']
        for name in ['unchanged', *core.CONDITIONS]:
            rows = core.read_jsonl(self.root / f'artifacts/runs/opus55-screening-{name}-eval/predictions.jsonl')
            s = core.summarize(rows)
            lines.append(f"| {name} | {s['correct']} | {s['accuracy']:.3f} | {s['mean_output_tokens']} | {s['mean_seconds']:.3f} | {s['failures']} | {s['truncated']} | {sum(r['predicted_answer'] is None for r in rows)} |")
        lines += ['', 'All failures and truncations remain in the denominator. Missing token measurements remain missing.', '',
                  '## Paired comparisons', '', '| Reference → candidate | Accuracy difference | 95% bootstrap interval | Output-token reduction |', '|---|---:|---|---:|']
        order = [('english-' + s, 'multilingual-' + s) for s in ('shortest', 'feedback')]
        order += [('original', n) for n in core.CONDITIONS if n != 'original'] + [('unchanged', 'original')]
        for left, right in order:
            r = read(comparisons / f'{left}-to-{right}.json')['results'][0]
            lines.append(f"| {left} → {right} | {r['accuracy_difference']:.3f} | {r['accuracy_difference_95_ci']} | {r['token_reduction']} |")
        lines += ['', '## Student-tokenizer measurements', '',
                  'Earlier round-1 screening found that multilingual material was not shorter under the Qwen tokenizer. The current selected-input measurements are reported separately below; word counts are not used.', '',
                  '| Strategy | English mean training tokens | Multilingual mean training tokens |', '|---|---:|---:|']
        for strategy in ('shortest', 'feedback'):
            lines.append(f"| {strategy} | {mean(r['tokens'] for r in groups['english-' + strategy]):.3f} | {mean(r['tokens'] for r in groups['multilingual-' + strategy]):.3f} |")
        elapsed = self.state['step1']['elapsed_seconds'] + sum(r['elapsed_seconds'] for r in self.state['commands'])
        lines += ['', f'Elapsed command wall time: {elapsed / 3600:.3f} hours (includes loading and CPU comparison commands; not a GPU-utilization integral).',
                  f'Raw outputs, adapters and manifests: `artifacts/runs/opus55-screening-*`. Selection exclusions: `{CONDITIONS}/selection-audit.json`.',
                  f'Stability evidence: `{REPEATED}/stability.json`. Penalty table: `{CALIBRATION}/penalty.json`.',
                  f'Human worksheets: `{REVIEW}`. No new ledger decisions or reviewed flags were inferred.',
                  'Next: collect named human A/R/U decisions, substitute rejected picks in a new selection, and obtain approval for every selected rewrite before the reviewed series.',
                  'Full development sweeps, human meaning approval, and official testing have not run. School/laptop timing is not a controlled comparison.', '']
        with (self.root / REPORT).open('x', encoding='utf-8', newline='\n') as output:
            output.write('\n'.join(lines))


def main():
    root = Path(__file__).resolve().parents[1]
    queue = Queue(root)
    try:
        queue.execute()
    except Exception as error:
        queue.state.update(status='failed', error=f'{type(error).__name__}: {error}')
        queue.save()
        queue.note(f"STOP: {queue.state['error']}. Preserve partial outputs; no automatic retry or subsequent phase was started.")
        raise
    finally:
        (queue.control / 'queue.done').write_text(stamp() + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
