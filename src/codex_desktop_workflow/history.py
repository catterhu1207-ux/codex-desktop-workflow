"""Read-only paginated-history lineage checks for independent data copies."""
from pathlib import Path
from contextlib import closing
import json,sqlite3
from . import paginated_history_base as base

class HistoryError(ValueError):pass

def normalized_path(value):
    text=str(value)
    if text.startswith('\\\\?\\'):text=text[4:]
    return Path(text).resolve()

def readonly(path):return sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)

def remap_copy(source,target):
    database=target/'state_5.sqlite'
    if not database.is_file():return 0
    changed=0
    with closing(sqlite3.connect(database)) as connection:
        tables={r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if 'threads' not in tables:return 0
        for tid,value in connection.execute('SELECT id,rollout_path FROM threads').fetchall():
            if not value:continue
            original=normalized_path(value)
            if not original.is_relative_to(source.resolve()):raise HistoryError('imported_rollout_path_outside_source')
            destination=target/original.relative_to(source.resolve())
            connection.execute('UPDATE threads SET rollout_path=? WHERE id=?',(str(destination.resolve()),tid));changed+=1
        connection.commit()
    return changed

def inspect(home):
    home=home.resolve();database=home/'state_5.sqlite'
    if not database.is_file():return {'status':'passed','paginated_threads':0,'source_written':False}
    roots=tuple((home/name).resolve() for name in ('sessions','archived_sessions'))
    inventory={};registered=[];cursors={};projection=home/'thread_history_1.sqlite'
    with closing(readonly(database)) as connection:
        if 'threads' not in {r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}:
            return {'status':'passed','paginated_threads':0,'source_written':False}
        columns={r[1] for r in connection.execute('PRAGMA table_info(threads)')}
        if 'history_mode' not in columns:return {'status':'passed','paginated_threads':0,'source_written':False}
        for tid,value,archived,mode in connection.execute('SELECT id,rollout_path,archived,history_mode FROM threads'):
            if mode!='paginated':continue
            path=normalized_path(value)
            if not any(path.is_relative_to(root) for root in roots):raise HistoryError('rollout_path_outside_independent_home')
            entry=base.HistoryInventoryEntry(path,bool(archived),mode)
            inventory['registered::'+tid]=entry;inventory[tid]=entry
            registered.append((tid,entry))
    for root in roots:
        if root.exists():
            for path in root.rglob('*.jsonl'):
                rollout_id=base.rollout_id_from_path(path)
                if rollout_id:
                    existing=inventory.get(rollout_id)
                    if existing and existing.path!=path and not rollout_id.startswith('registered::'):
                        # The registered current segment wins; base lookup still detects ambiguity.
                        continue
                    inventory.setdefault(rollout_id,base.HistoryInventoryEntry(path,root.name=='archived_sessions','paginated'))
    if projection.is_file():
        with closing(readonly(projection)) as connection:
            tables={r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if 'thread_history_projection_state' in tables:
                cursors={tid:(offset,ordinal) for tid,offset,ordinal in connection.execute('SELECT thread_id,next_rollout_byte_offset,next_rollout_ordinal FROM thread_history_projection_state')}
    hashes={};deferred=0;proofs=[]
    for tid,entry in registered:
        if not entry.path.is_file():
            if entry.archived:deferred+=1;continue
            raise HistoryError('active_rollout_missing')
        raw=entry.path.read_bytes();hashes[entry.path]=base.sha256_path(entry.path)
        if not raw.endswith(b'\n'):raise HistoryError('incomplete_rollout_record')
        records=[json.loads(line) for line in raw.splitlines()]
        first=records[0]
        if first.get('type')!='session_meta' or first.get('payload',{}).get('id')!=tid:
            raise HistoryError('rollout_owner_identity_mismatch')
        proof=base.validate_paginated_start(tid,first,cursors.get(tid),len(raw),inventory,roots,HistoryError,entry.path)
        for index,record in enumerate(records):
            if type(record.get('ordinal')) is not int or record['ordinal']!=proof.start_ordinal+index:
                raise HistoryError('rollout_ordinal_discontinuity')
        cursor=cursors.get(tid)
        if cursor:
            offset=0;boundaries={0:proof.start_ordinal}
            for index,line in enumerate(raw.splitlines(keepends=True)):
                offset+=len(line);boundaries[offset]=proof.start_ordinal+index+1
            if boundaries.get(cursor[0])!=cursor[1]:raise HistoryError('projection_cursor_not_exact_record_boundary')
        if proof.kind=='projection_continuation':
            base.validate_projection_continuation(tid,records,base.rollout_id_from_path(entry.path),projection,cursor,proof,HistoryError)
        for path,digest in proof.lineage_parent_sha256:hashes[path]=digest
        if proof.parent_path:hashes[proof.parent_path]=proof.parent_sha256
        proofs.append(proof.kind)
    for path,digest in hashes.items():
        if base.sha256_path(path)!=digest:raise HistoryError('history_dependency_changed_during_validation')
    return {'status':'passed','paginated_threads':len(registered),'proved_threads':len(proofs),'archived_missing_deferred':deferred,'kinds':{kind:proofs.count(kind) for kind in set(proofs)},'source_written':False}
