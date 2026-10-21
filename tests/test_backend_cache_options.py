import os,tempfile,unittest
from pathlib import Path
from unittest import mock
from codex_desktop_workflow import backend

class CacheOptions(unittest.TestCase):
    def test_default_has_no_cache_or_reuse_override(self):
        with mock.patch.dict(os.environ,{},clear=True):
            self.assertEqual(backend._cache_options(),[])

    def test_external_source_requires_verified_cache_before_any_write(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ,{'CODEX_COMPAT_SOURCE_CACHE':d},clear=True), mock.patch.object(backend.subprocess,'run') as run:
            target=Path(d)/'output'
            with self.assertRaisesRegex(ValueError,'source_cache_requires_verified_build_cache'):
                backend.build(Path(d),target,'26.1016.6573.0')
            self.assertFalse(target.exists())
            run.assert_not_called()

    def test_missing_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ,{'CODEX_COMPAT_BUILD_CACHE':d,'CODEX_COMPAT_SOURCE_CACHE':str(Path(d)/'missing')},clear=True):
            with self.assertRaises(FileNotFoundError):backend._cache_options()

    def test_existing_inputs_retain_recipe_validation_and_toolchain_selection(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ,{
            'CODEX_COMPAT_BUILD_CACHE':d,'CODEX_COMPAT_SOURCE_CACHE':d,
            'CODEX_COMPAT_TARGET_CACHE':d,'CODEX_COMPAT_RELEASE_TARGET_CACHE':d,
            'CODEX_COMPAT_TOOLCHAIN_ROOT':d},clear=True):
            self.assertEqual(backend._cache_options(),['--reuse-verified-source','--source',str(Path(d).resolve()),'--target-cache',str(Path(d).resolve()),'--release-target-cache',str(Path(d).resolve()),'--toolchain-root',str(Path(d).resolve())])

if __name__=='__main__':unittest.main()
