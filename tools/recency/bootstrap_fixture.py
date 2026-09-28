from pathlib import Path
import json
import os
import shutil
import sqlite3
import sys
import time

from codex_desktop_workflow import workflow as w


def seed(home: Path, empty: Path, server_port: int):
    home.mkdir(parents=True, exist_ok=False)
    w._seed_synthetic_tasks(home, empty)
    now = int(time.time()) - 3600
    with sqlite3.connect(home / 'state_5.sqlite') as db:
        rows = db.execute('select id,cwd,rollout_path from threads order by created_at desc').fetchall()
        fixtures = []
        for index, (tid, cwd, rollout) in enumerate(rows):
            title = ['Recency target', 'Older waiting plan', 'Recent unread'][index] if index < 3 else f'Synthetic task {index}'
            # All three prominent controls have separate, clearly named projects.
            project = home / 'synthetic-workspaces' / (['Project Alpha','Project Beta','Project Gamma'][index] if index < 3 else str(index % 12))
            project.mkdir(parents=True, exist_ok=True)
            created = now - 5000 - index
            recency = now - index
            if index == 0:
                recency = now - 900
            db.execute('update threads set name=?,title=?,preview=?,first_user_message=?,cwd=?,model_provider=?,created_at=?,created_at_ms=?,updated_at=?,updated_at_ms=?,recency_at=?,recency_at_ms=?,is_pinned=0 where id=?', (title,title,title,title,str(project),'fixture',created,created*1000,recency,recency*1000,recency,recency*1000,tid))
            p = Path(rollout)
            meta = json.loads(p.read_text().splitlines()[0])
            meta['payload']['cwd'] = str(project)
            meta['payload']['model_provider'] = 'fixture'
            p.write_text(json.dumps(meta)+'\n', encoding='utf8')
            if index < 3:
                fixtures.append({'id':tid,'title':title,'cwd':str(project),'rollout':str(p),'created':created,'recency':recency})
        db.commit()
    (home/'config.toml').write_text(f'''model_provider="fixture"
model="synthetic-local"
approval_policy="never"
sandbox_mode="danger-full-access"
[windows]
sandbox="unelevated"
[model_providers.fixture]
name="Synthetic loopback"
base_url="http://127.0.0.1:{server_port}/v1"
wire_api="responses"
requires_openai_auth=false
supports_websockets=false
''', encoding='utf8')
    (home/'auth.json').write_text(json.dumps({'auth_mode':'apikey','OPENAI_API_KEY':'synthetic-local-only-no-credentials'}), encoding='utf8')
    projects = sorted({str(p) for p in (home/'synthetic-workspaces').iterdir() if p.is_dir()})
    state = {'local-projects': projects, 'electron-persisted-atom-state': {'flat-project-sidebar-preferences-v1': {'mode':'project','chatSortMode':'priority','projectSortMode':'priority','initialized':True}, 'permission-selection-by-host-id:local':{'kind':'custom'},'pinned-sidebar-sort-mode-v1':'updated_at','electron-language':'en'}, 'desktop-first-seen-at-ms': int(time.time()*1000)-86400000}
    (home/'.codex-global-state.json').write_text(json.dumps(state), encoding='utf8')
    (home/'synthetic-fixture.json').write_text(json.dumps({'count':400,'local_only':True}),encoding='utf8')
    return fixtures
