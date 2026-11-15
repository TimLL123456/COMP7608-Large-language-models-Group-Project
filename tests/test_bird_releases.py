"""Release migration must preserve legacy data and reject cross-release reuse."""
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from scr.datasets.bird import BirdDataset, read_annotations
from scr.datasets.bird_images import extract_database
from scr.datasets.setup_bird import setup, safe_extract_zip, verify
from tests.test_bird_setup import make_fixture


class ReleaseTests(unittest.TestCase):
    def test_current_jsonl_install_and_release_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            old_json, archive = make_fixture(base / 'fixture')
            rows = json.loads(old_json.read_text())
            for i, row in enumerate(rows):
                row['question_id'] = i
            current = base / 'current.jsonl'
            current.write_text('\n'.join(json.dumps(row) for row in rows))
            self.assertEqual(len(read_annotations(current)), 500)
            old = base / 'original'
            setup(old, archive=archive, annotations=old_json)
            old_manifest = (old / 'dataset_manifest.json').read_bytes()
            from scr.datasets.setup_bird import main
            with self.assertRaises(SystemExit) as error:
                main(['--release', 'latest', '--root', str(old), '--verify-only'])
            self.assertEqual(error.exception.code, 1)

            new = base / 'current'
            def fake_images(destination, ids):
                safe_extract_zip(archive, destination)
                return {db: 'fixture-digest' for db in ids}
            with patch('scr.datasets.bird_images.fetch_databases', side_effect=fake_images):
                result = setup(new, release='latest', annotations=current)
            self.assertEqual(result['test'], 100)
            self.assertEqual(BirdDataset(new).manifest['dataset'], 'bird-mini-dev-2026-sqlite')
            self.assertNotIn('SQL', BirdDataset(new).load_questions()[0])
            from scr.cli.evaluate_bird import run
            predictions = base / 'predictions.jsonl'
            q = BirdDataset(new).get_split('dev')[0]
            predictions.write_text(json.dumps({'question_id': q['question_id'], 'db_id': q['db_id'], 'predicted_sql': 'SELECT count(*) FROM records'}) + '\n')
            command = ['--variant', 'B0', '--split', 'dev', '--predictions', str(predictions), '--dataset-root', str(new), '--output-dir', str(base / 'scores'), '--question-ids', str(q['question_id'])]
            with self.assertRaisesRegex(ValueError, 'matching inference_manifest'):
                run(command)
            (base / 'inference_manifest.json').write_text(json.dumps({'dataset_manifest': BirdDataset(old).manifest}))
            with self.assertRaisesRegex(ValueError, 'matching inference_manifest'):
                run(command)
            (base / 'inference_manifest.json').write_text(json.dumps({'dataset_manifest': BirdDataset(new).manifest}))
            self.assertEqual(run(command), 0)

            self.assertEqual((old / 'dataset_manifest.json').read_bytes(), old_manifest)
            with self.assertRaisesRegex(ValueError, 'differs'):
                setup(new)
            with self.assertRaisesRegex(ValueError, 'differs'):
                setup(new, release='latest', revision='wrong')
            current_copy = new / 'annotations.source.jsonl'
            current_copy.write_text('tampered')
            with self.assertRaisesRegex(ValueError, 'Source annotation'):
                verify(new)
            with self.assertRaisesRegex(ValueError, 'IDs'):
                setup(base / 'bad', release='latest', annotations=old_json)

    def test_image_export_copies_only_selected_database(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            archive = base / 'export.tar'
            with tarfile.open(archive, 'w') as tar:
                for name, data in [('opt/dii/seed.sqlite', b'SQLite fixture'),
                                   ('../../outside', b'evil'),
                                   ('opt/dii/database_description/table.csv', b'name\nid')]:
                    item = tarfile.TarInfo(name)
                    item.size = len(data)
                    tar.addfile(item, io.BytesIO(data))
            extract_database(archive, base / 'output', 'demo')
            self.assertEqual((base / 'output/demo/demo.sqlite').read_bytes(), b'SQLite fixture')
            self.assertTrue((base / 'output/demo/database_description/table.csv').is_file())
            self.assertEqual(len(list((base / 'output').rglob('*'))), 4)


class RegistryTests(unittest.TestCase):
    def test_verified_documents_reject_corruption(self):
        import hashlib
        from unittest.mock import MagicMock as Mock
        from scr.datasets.bird_images import Registry
        registry = Registry.__new__(Registry)
        registry.base = 'https://example.invalid'
        registry.headers = {}
        registry.session = Mock()
        response = registry.session.get.return_value
        response.content = b'{}'
        digest = 'sha256:' + hashlib.sha256(b'{}').hexdigest()
        response.json.return_value = {}
        self.assertEqual(registry.document('manifests', digest), {})
        with self.assertRaisesRegex(ValueError, 'digest mismatch'):
            registry.document('manifests', 'sha256:' + '0' * 64)

    def test_seed_mapping_rejects_later_layers(self):
        from unittest.mock import MagicMock as Mock
        from scr.datasets.bird_images import Registry
        registry = Registry.__new__(Registry)
        manifest = {'config': {'digest': 'config'}, 'layers': [{'digest': 'seed'}]}
        config = {'history': [{'created_by': 'COPY seed.sqlite /opt/dii/seed.sqlite # buildkit'},
                              {'empty_layer': True, 'created_by': 'ENV SQLITEDB=/app/database.sqlite'}]}
        registry.document = Mock(side_effect=[manifest, config])
        self.assertEqual(registry.seed_layer('image'), ('image', {'digest': 'seed'}))
        config['history'].append({'created_by': 'RUN change-seed'})
        manifest['layers'].append({'digest': 'changed'})
        registry.document = Mock(side_effect=[manifest, config])
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            registry.seed_layer('image')

    def test_cache_is_verified_and_failed_download_is_not_installed(self):
        import hashlib
        from unittest.mock import MagicMock as Mock
        from scr.datasets.bird_images import Registry
        registry = Registry.__new__(Registry)
        registry.base = 'https://example.invalid'
        registry.headers = {}
        registry.session = Mock()
        data = b'fixture layer'
        descriptor = {'digest': 'sha256:' + hashlib.sha256(data).hexdigest(), 'size': len(data)}
        response = registry.session.get.return_value.__enter__.return_value
        response.iter_content.return_value = [data]
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp)
            target = registry.download(descriptor, cache)
            self.assertEqual(target.read_bytes(), data)
            registry.session.reset_mock()
            self.assertEqual(registry.download(descriptor, cache), target)
            registry.session.get.assert_not_called()
            target.write_bytes(b'corrupted')
            registry.session.get.return_value.__enter__.return_value.iter_content.return_value = [b'wrong']
            with self.assertRaisesRegex(ValueError, 'mismatch'):
                registry.download(descriptor, cache)
            self.assertFalse(list(cache.glob('*.part')))
