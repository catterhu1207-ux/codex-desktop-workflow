import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import os

from codex_desktop_workflow.runtime_cache_transfer import transfer,restore_unlaunched,copy_ended_ssh_config


def fixture(directory):
    source=Path(directory)/('run-'+'1'*32)
    target=Path(directory)/('run-'+'2'*32)
    cache=source/'profile/.cache/codex-runtimes/codex-primary-runtime'
    (cache/'dependencies/node/bin').mkdir(parents=True)
    (cache/'dependencies/node/bin/node.exe').write_bytes(b'public-node-binary')
    (cache/'dependencies/python').mkdir()
    (cache/'dependencies/python/python.exe').write_bytes(b'public-python-binary')
    (cache/'plugins').mkdir()
    (cache/'runtime.json').write_text(json.dumps({'targetPlatform':'win32','targetArch':'x64','bundleVersion':'26.1022.11436'}))
    record={'shell_folders':'owl_fresh_profile_browser_integration_isolated',
            'main':{'pid':123,'executable':'owned/ChatGPT.exe','created':'2026-10-25T00:00:00+00:00'}}
    (source/'run.json').write_text(json.dumps(record))
    (source/'user-data').mkdir()
    (source/'user-data/private-state').write_bytes(b'must remain here')
    (target/'profile').mkdir(parents=True)
    state={'status':'exited','main':record['main'],'alive_backends':[]}
    return source,target,cache,state


class RuntimeCacheTransfer(unittest.TestCase):
    def test_owned_ssh_configuration_is_available_before_start_without_keys_or_login(self):
        with tempfile.TemporaryDirectory() as directory:
            source,target,cache,state=fixture(directory)
            config=source/'profile/.ssh/config';config.parent.mkdir();config.write_text('Host synthetic\n HostName 127.0.0.1\n')
            (config.parent/'private-key').write_text('never copy this')
            result=copy_ended_ssh_config(source,target,state)
            self.assertEqual((target/'profile/.ssh/config').read_bytes(),config.read_bytes())
            self.assertFalse((target/'profile/.ssh/private-key').exists())
            self.assertFalse(result['authentication_copied'])
            with self.assertRaises(ValueError):copy_ended_ssh_config(source,target,state)

    def test_active_or_foreign_ssh_fixture_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source,target,cache,state=fixture(directory)
            state['status']='running'
            with self.assertRaises(ValueError):copy_ended_ssh_config(source,target,state)
            self.assertFalse((target/'profile/.ssh').exists())
    def test_unlaunched_destination_restores_only_the_identical_public_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            source,target,cache,state=fixture(directory)
            transfer(source,target,state)
            result=restore_unlaunched(target,state)
            self.assertEqual(result['status'],'restored_original_run_after_unlaunched_preparation_failure')
            self.assertEqual((cache/'dependencies/node/bin/node.exe').read_bytes(),b'public-node-binary')
            self.assertEqual((source/'user-data/private-state').read_bytes(),b'must remain here')
            with self.assertRaises(ValueError):restore_unlaunched(target,state)

    def test_launched_changed_or_active_restore_is_rejected_before_move(self):
        for conflict in ('launched','changed','active'):
            with self.subTest(conflict=conflict),tempfile.TemporaryDirectory() as directory:
                source,target,cache,state=fixture(directory)
                transfer(source,target,state)
                moved=target/'profile/.cache/codex-runtimes/codex-primary-runtime'
                if conflict=='launched':(target/'run.json').write_text('{}')
                if conflict=='changed':(moved/'dependencies/node/bin/node.exe').write_bytes(b'changed')
                if conflict=='active':state['status']='running'
                with self.assertRaises(ValueError):restore_unlaunched(target,state)
                self.assertTrue(moved.exists());self.assertFalse(cache.exists())

    def test_closed_public_cache_moves_without_copying_or_moving_user_state(self):
        with tempfile.TemporaryDirectory() as directory:
            source,target,cache,state=fixture(directory)
            inode=(cache/'dependencies/node/bin/node.exe').stat().st_ino
            result=transfer(source,target,state)
            actual=target/'profile/.cache/codex-runtimes/codex-primary-runtime'
            self.assertFalse(cache.exists())
            self.assertEqual((actual/'dependencies/node/bin/node.exe').stat().st_ino,inode)
            self.assertEqual((source/'user-data/private-state').read_bytes(),b'must remain here')
            self.assertFalse((target/'user-data').exists())
            self.assertEqual(result['status'],'moved_with_native_identity_readback')
            self.assertFalse(result['user_data_moved'])

    def test_active_owner_or_reused_destination_stops_before_mutation(self):
        for conflict in ('active','destination'):
            with self.subTest(conflict=conflict),tempfile.TemporaryDirectory() as directory:
                source,target,cache,state=fixture(directory)
                if conflict=='active':state['status']='running'
                else:(target/'profile/.cache').mkdir()
                with self.assertRaises(ValueError):transfer(source,target,state)
                self.assertTrue((cache/'dependencies/node/bin/node.exe').exists())

    def test_authentication_and_configuration_cannot_be_transferred_as_runtime_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            source,target,cache,state=fixture(directory)
            (cache/'auth.json').write_text('private fixture')
            with self.assertRaisesRegex(ValueError,'not_public_dependencies'):transfer(source,target,state)
            self.assertTrue((cache/'auth.json').exists())

    def test_outside_owned_run_root_or_wrong_runtime_architecture_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source,target,cache,state=fixture(directory)
            outside=Path(directory)/'outside'/target.name
            (outside/'profile').mkdir(parents=True)
            with self.assertRaisesRegex(ValueError,'same_owned_runs_root'):transfer(source,outside,state)
            raw=json.loads((cache/'runtime.json').read_text());raw['targetArch']='arm64'
            (cache/'runtime.json').write_text(json.dumps(raw))
            with self.assertRaisesRegex(ValueError,'manifest_identity'):transfer(source,target,state)
            self.assertTrue(cache.exists())

    def test_change_during_move_preserves_intent_and_requires_readback_before_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            source,target,cache,state=fixture(directory)
            rename=os.rename
            def changed(before,after):
                rename(before,after)
                (Path(after)/'dependencies/node/bin/node.exe').write_bytes(b'changed public payload')
            with mock.patch('codex_desktop_workflow.runtime_cache_transfer.os.rename',side_effect=changed):
                with self.assertRaisesRegex(RuntimeError,'readback_differs'):transfer(source,target,state)
            receipt=json.loads((target/'runtime-cache-transfer.json').read_text())
            self.assertEqual(receipt['status'],'intent')
            with self.assertRaisesRegex(ValueError,'requires_reconciliation'):transfer(source,target,state)

if __name__=='__main__':unittest.main()
