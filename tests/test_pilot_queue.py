import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from research import core
from scripts.run_opus_screening import CONTROL, CONFIG, Queue, archive, screening_commands, validate_command


class QueueTests(unittest.TestCase):
    def test_plan_has_all_matched_conditions_and_explicit_development_only(self):
        commands = screening_commands()
        training = [args for _, args in commands if args[0] == 'train']
        evaluation = [args for _, args in commands if args[0] == 'evaluate']
        self.assertEqual(len(training), 5)
        self.assertEqual(len(evaluation), 6)
        self.assertEqual({a[a.index('--condition') + 1] for a in training}, set(core.CONDITIONS))
        for _, args in commands:
            validate_command(args)
            self.assertIn('screening', args[args.index('--output') + 1])
        for args in training:
            self.assertIn('--conditions', args)
            self.assertIn('--allow-unreviewed', args)
        for args in evaluation:
            self.assertEqual(args[args.index('--limit') + 1], '50')
            self.assertEqual(args[args.index('--budget') + 1], '256')
        for bad in [['freeze'], ['evaluate', '--split', 'official-test'], ['evaluate'],
                    ['evaluate', '--split', 'development', '--final-test']]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                validate_command(bad)

    def test_archive_preserves_prior_files_and_verifies_contents(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'result.txt').write_text('raw output', encoding='utf-8')
            receipt = archive(root, 'test', ['result.txt'])
            destination = root / receipt['file']
            with zipfile.ZipFile(destination) as saved:
                self.assertEqual(saved.read('result.txt'), b'raw output')
            before = destination.read_bytes()
            with self.assertRaises(FileExistsError):
                archive(root, 'test', ['result.txt'])
            self.assertEqual(destination.read_bytes(), before)

    def test_copied_config_precedes_subcommand_and_failure_stops(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / CONTROL).mkdir(parents=True)
            (root / 'configs').mkdir()
            (root / 'configs/pilot.json').write_text('{}')
            (root / CONFIG).write_text('{}')
            queue = Queue(root)
            queue.config_hash = queue.base_hash
            with patch('scripts.run_opus_screening.subprocess.run') as run:
                run.return_value.returncode = 7
                with self.assertRaises(RuntimeError):
                    queue.run('selection', ['select', '--output', 'new'], True)
                command = run.call_args.args[0]
                self.assertEqual(command[1:6], ['-m', 'research', '--config', str(CONFIG), 'select'])
                self.assertEqual(json.loads((root / CONTROL / 'status.json').read_text())['commands'][0]['exit_code'], 7)
            with self.assertRaises(FileExistsError):
                Queue(root)

    def test_config_mutation_or_busy_gpu_prevents_launch(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / CONTROL).mkdir(parents=True)
            (root / 'configs').mkdir()
            (root / 'configs/pilot.json').write_text('{}')
            queue = Queue(root)
            with patch('scripts.run_opus_screening.subprocess.check_output', return_value='123, 100 MiB'), patch('scripts.run_opus_screening.subprocess.run') as run:
                with self.assertRaises(RuntimeError):
                    queue.run('score', ['score'])
                run.assert_not_called()
            (root / 'configs/pilot.json').write_text('{"changed":true}')
            with self.assertRaises(ValueError):
                queue.run('select', ['select'])


if __name__ == '__main__':
    unittest.main()
