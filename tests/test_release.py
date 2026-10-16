"""Check the independently downloadable packages and deterministic archives."""
from pathlib import Path
import hashlib
import json
import sys
import zipfile
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from package_release import zip_paths


def test_release_zip_is_deterministic_and_order_independent(tmp_path):
    first = tmp_path / 'a.txt'; second = tmp_path / 'b.txt'
    first.write_text('readings', encoding='utf-8'); second.write_text('models', encoding='utf-8')
    zip_paths(tmp_path / 'one.zip', [second, first], 'release', tmp_path)
    zip_paths(tmp_path / 'two.zip', [first, second], 'release', tmp_path)
    assert (tmp_path / 'one.zip').read_bytes() == (tmp_path / 'two.zip').read_bytes()


def test_release_zip_rejects_files_outside_selected_root(tmp_path):
    base = tmp_path / 'site'; base.mkdir()
    private = tmp_path / 'outside.txt'; private.write_text('outside', encoding='utf-8')
    with pytest.raises(AssertionError):
        zip_paths(tmp_path / 'invalid.zip', [private], 'release', base)


def test_standalone_paclets_contain_notices_and_current_scientific_sources():
    entries = json.loads((ROOT / 'experiments/registry.json').read_text(encoding='utf-8'))['experiments']
    for entry in entries:
        package = ROOT / 'notebook/paclets' / entry['paclet']
        with zipfile.ZipFile(ROOT / entry['paclet_archive']) as archive:
            prefix = next(name.rsplit('/', 1)[0] + '/' for name in archive.namelist()
                          if name.endswith('/PacletInfo.wl'))
            for relative in ('LICENSE', 'LICENSING.md', 'THIRD_PARTY_NOTICES.md', 'LICENSES/CC-BY-4.0.txt'):
                assert archive.read(prefix + relative) == (ROOT / relative).read_bytes()
            for folder in ('Kernel', 'Notebooks', 'Tests'):
                for path in (package / folder).glob('*'):
                    if path.is_file():
                        relative = path.relative_to(package).as_posix()
                        assert hashlib.sha256(archive.read(prefix + relative)).digest() == hashlib.sha256(path.read_bytes()).digest(), (entry['id'], relative)
