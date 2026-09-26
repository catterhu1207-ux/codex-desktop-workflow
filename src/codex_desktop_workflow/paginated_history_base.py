"""Single fail-closed proof for paginated rollout starting positions."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROOF_VERSION = "1.2.2"

ROLLOUT_ID_PATTERN = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)


@dataclass(frozen=True)
class HistoryInventoryEntry:
    path: Path
    archived: bool
    history_mode: str


@dataclass(frozen=True)
class HistoryBaseProof:
    start_ordinal: int
    base_offset: int | None
    kind: str
    base_thread_id: str | None
    parent_path: Path | None
    parent_sha256: str | None
    continuation_source_projection_id: str | None = None
    continuation_projection_digest: str | None = None
    lineage_parent_sha256: tuple[tuple[Path, str], ...] = ()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()


def projection_rows_digest(connection: sqlite3.Connection, projection_id: str) -> str:
    """Digest the durable source projection exactly as the recovery helper did."""
    digest = hashlib.sha256()
    ordering = {
        "thread_history_projection_state": "thread_id",
        "thread_turns": "turn_id",
        "thread_items": "turn_id, item_id",
        "thread_realtime_items": "item_id",
    }
    for table, order_by in ordering.items():
        columns = [row[1] for row in connection.execute(f'PRAGMA table_info("{table}")').fetchall()]
        if not columns:
            raise ValueError(f"Projection table is missing: {table}")
        rows = connection.execute(
            f'SELECT * FROM "{table}" WHERE thread_id = ? ORDER BY {order_by}',
            (projection_id,),
        ).fetchall()
        digest.update(table.encode("utf-8"))
        digest.update(json.dumps(columns, separators=(",", ":")).encode("utf-8"))
        for row in rows:
            digest.update(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    return digest.hexdigest()


def normalized_projection_rows_digest(
    connection: sqlite3.Connection, projection_id: str
) -> str:
    """Compare cloned visible rows without treating their immutable rollout id as content."""
    digest = hashlib.sha256()
    for table, order_by in (
        ("thread_turns", "turn_id"),
        ("thread_items", "turn_id, item_id"),
        ("thread_realtime_items", "item_id"),
    ):
        columns = [row[1] for row in connection.execute(f'PRAGMA table_info("{table}")').fetchall()]
        if "thread_id" not in columns:
            raise ValueError(f"Projection table has no thread_id: {table}")
        thread_index = columns.index("thread_id")
        digest.update(table.encode("utf-8"))
        digest.update(json.dumps(columns, separators=(",", ":")).encode("utf-8"))
        for row in connection.execute(
            f'SELECT * FROM "{table}" WHERE thread_id = ? ORDER BY {order_by}',
            (projection_id,),
        ).fetchall():
            normalized = list(row)
            normalized[thread_index] = "__projection_continuation__"
            digest.update(json.dumps(normalized, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    return digest.hexdigest()


def projection_continuation_proof(
    thread_id: str,
    first_record: dict[str, Any],
) -> HistoryBaseProof | None:
    """Validate the marker shape that distinguishes a recovered projection segment.

    The marker is intentionally narrow: it is only a statement of evidence.  The
    database and compacted-history portions are rechecked by
    ``validate_projection_continuation`` below before a bridge accepts it.
    """
    payload = first_record.get("payload")
    marker = payload.get("projection_continuation") if isinstance(payload, dict) else None
    ordinal = first_record.get("ordinal")
    if not isinstance(marker, dict):
        return None
    source_cursor = marker.get("source_cursor")
    source_id = marker.get("source_projection_id")
    digest = marker.get("source_projection_digest")
    history_digest = marker.get("replacement_history_sha256")
    if (
        first_record.get("type") != "session_meta"
        or not isinstance(ordinal, int)
        or isinstance(ordinal, bool)
        or ordinal <= 0
        or not isinstance(payload, dict)
        or payload.get("id") != thread_id
        or payload.get("history_mode") != "paginated"
        or "history_base" in payload
        or "forked_from_id" in payload
        or marker.get("strategy") != "projection_continuation_v1"
        or marker.get("source_rollout_missing") is not True
        or not isinstance(source_id, str)
        or rollout_id_from_path(Path(f"x_{source_id}.jsonl")) != source_id.lower()
        or not isinstance(source_cursor, list)
        or len(source_cursor) != 2
        or any(isinstance(value, bool) or not isinstance(value, int) for value in source_cursor)
        or source_cursor[0] <= 0
        or source_cursor[1] != ordinal
        or not isinstance(digest, str)
        or not re.fullmatch(r"[0-9a-f]{64}", digest)
        or not isinstance(history_digest, str)
        or not re.fullmatch(r"[0-9a-f]{64}", history_digest)
    ):
        raise ValueError(f"Projection continuation marker is not jointly proven for {thread_id}")
    return HistoryBaseProof(
        ordinal, None, "projection_continuation", source_id, None, None,
        source_id, digest,
    )


def validate_projection_continuation(
    thread_id: str,
    records: list[dict[str, Any]],
    rollout_id: str,
    projection_path: Path,
    projection_state: tuple[int, int] | None,
    proof: HistoryBaseProof,
    error_type: type[Exception],
) -> None:
    """Prove a recovered segment still maps exactly to its durable projection."""
    if proof.kind != "projection_continuation" or len(records) < 2:
        raise error_type(f"Projection continuation records are incomplete for {thread_id}")
    marker = records[0]["payload"]["projection_continuation"]
    compacted = records[1]
    if compacted.get("type") != "compacted" or compacted.get("ordinal") != proof.start_ordinal + 1:
        raise error_type(f"Projection continuation compacted boundary is invalid for {thread_id}")
    compacted_payload = compacted.get("payload")
    if not isinstance(compacted_payload, dict) or not isinstance(compacted_payload.get("replacement_history"), list):
        raise error_type(f"Projection continuation compacted history is invalid for {thread_id}")
    if canonical_json_sha256(compacted_payload["replacement_history"]) != marker["replacement_history_sha256"]:
        raise error_type(f"Projection continuation context digest is invalid for {thread_id}")
    if rollout_id_from_path(Path(f"x_{rollout_id}.jsonl")) != rollout_id.lower():
        raise error_type(f"Projection continuation rollout id is invalid for {thread_id}")
    if projection_state is None or projection_state[0] < 0 or projection_state[1] < proof.start_ordinal + 2:
        raise error_type(f"Projection continuation cursor is invalid for {thread_id}")
    if not projection_path.is_file():
        raise error_type(f"Projection continuation database is missing for {thread_id}")
    try:
        connection = sqlite3.connect(f"{projection_path.as_uri()}?mode=ro", uri=True)
        try:
            source_id = proof.continuation_source_projection_id
            if source_id is None:
                raise error_type(f"Projection continuation source is missing for {thread_id}")
            source_state = connection.execute(
                "SELECT next_rollout_byte_offset, next_rollout_ordinal FROM thread_history_projection_state WHERE thread_id = ?",
                (source_id,),
            ).fetchone()
            target_state = connection.execute(
                "SELECT next_rollout_byte_offset, next_rollout_ordinal FROM thread_history_projection_state WHERE thread_id = ?",
                (rollout_id,),
            ).fetchone()
            if (
                source_state is None
                or tuple(map(int, source_state)) != tuple(marker["source_cursor"])
                or target_state is None
                or tuple(map(int, target_state)) != projection_state
                or projection_rows_digest(connection, source_id) != proof.continuation_projection_digest
            ):
                raise error_type(f"Projection continuation source proof is invalid for {thread_id}")
            # The recovered rows are immutable, but the resumed segment may
            # acquire new turns. Prove its original prefix and bound every new
            # row to the appended, already ordinal-validated rollout suffix.
            for table, keys in (
                ("thread_turns", ("turn_id",)),
                ("thread_items", ("turn_id", "item_id")),
                ("thread_realtime_items", ("item_id",)),
            ):
                columns = [row[1] for row in connection.execute(f'PRAGMA table_info("{table}")')]
                compared = [name for name in columns if name != "thread_id"]
                key_match = " AND ".join(f't."{key}" IS s."{key}"' for key in keys)
                values_match = " AND ".join(f't."{name}" IS s."{name}"' for name in compared)
                missing = connection.execute(
                    f'SELECT 1 FROM "{table}" s WHERE s.thread_id = ? AND NOT EXISTS '
                    f'(SELECT 1 FROM "{table}" t WHERE t.thread_id = ? AND {key_match} AND {values_match}) LIMIT 1',
                    (source_id, rollout_id),
                ).fetchone()
                invalid_extra = connection.execute(
                    f'SELECT 1 FROM "{table}" t WHERE t.thread_id = ? AND NOT EXISTS '
                    f'(SELECT 1 FROM "{table}" s WHERE s.thread_id = ? AND {key_match}) '
                    'AND (typeof(t.rollout_ordinal) != \'integer\' OR t.rollout_ordinal < ? OR t.rollout_ordinal >= ?) LIMIT 1',
                    (rollout_id, source_id, proof.start_ordinal + 2, projection_state[1]),
                ).fetchone()
                if missing or invalid_extra:
                    raise error_type(f"Projection continuation source proof is invalid for {thread_id}: {table}")
        finally:
            connection.close()
    except sqlite3.DatabaseError as error:
        raise error_type(f"Projection continuation database is unreadable for {thread_id}: {error}") from error


def is_within(path: Path, root: Path) -> bool:
    try:
        return str(path.resolve()).casefold().startswith(
            str(root.resolve()).rstrip("\\/").casefold() + "\\"
        ) or str(path.resolve()).casefold() == str(root.resolve()).casefold()
    except OSError:
        return False


def rollout_id_from_path(path: Path) -> str | None:
    """Return the immutable rollout id encoded at the end of a canonical name."""
    matches = ROLLOUT_ID_PATTERN.findall(path.name)
    return matches[-1].lower() if matches else None


def find_rollout_path_by_id(
    rollout_id: str,
    allowed_roots: tuple[Path, ...],
    current_path: Path,
    error_type: type[Exception],
) -> Path:
    candidates: list[Path] = []
    for root in allowed_roots:
        if not root.is_dir():
            continue
        for candidate in root.rglob(f"*{rollout_id}*.jsonl*"):
            if candidate == current_path or not candidate.is_file():
                continue
            if rollout_id_from_path(candidate) == rollout_id.lower():
                candidates.append(candidate)
    unique = sorted({candidate.resolve() for candidate in candidates})
    if len(unique) != 1:
        raise error_type(
            f"Paginated history base {rollout_id} has {len(unique)} source rollouts"
        )
    return unique[0]


def validate_parent_boundary(
    thread_id: str,
    parent_path: Path,
    base_offset: int,
    start_ordinal: int,
    error_type: type[Exception],
) -> str:
    parent_bytes = parent_path.read_bytes()
    if not 0 < base_offset <= len(parent_bytes):
        raise error_type(f"History base offset is outside source rollout for {thread_id}")
    parent_identity: str | None = None
    previous_ordinal: int | None = None
    next_ordinal: int | None = None
    offset = 0
    for line_number, raw_line in enumerate(parent_bytes.splitlines(keepends=True), start=1):
        line_start = offset
        offset += len(raw_line)
        content = raw_line.rstrip(b"\r\n")
        if not content.strip():
            raise error_type(f"Blank source JSONL record for history base {thread_id}")
        try:
            value = json.loads(content)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise error_type(
                f"Invalid source JSON for history base {thread_id} at line {line_number}"
            ) from error
        if not isinstance(value, dict):
            raise error_type(f"Non-object source record for history base {thread_id}")
        if line_number == 1:
            payload = value.get("payload")
            if (
                value.get("type") != "session_meta"
                or not isinstance(payload, dict)
                or payload.get("history_mode") != "paginated"
                or not isinstance(payload.get("id"), str)
            ):
                raise error_type(f"History base source identity is not proven for {thread_id}")
            parent_identity = payload["id"]
        if offset == base_offset:
            previous_ordinal = value.get("ordinal")
        if line_start == base_offset:
            next_ordinal = value.get("ordinal")
    if previous_ordinal != start_ordinal - 1:
        raise error_type(f"History base offset is not an ordinal boundary for {thread_id}")
    if next_ordinal is not None and next_ordinal != start_ordinal:
        raise error_type(f"History base next ordinal is not proven for {thread_id}")
    assert parent_identity is not None
    return parent_identity


def _prove_inherited_fork_lineage(
    thread_id: str,
    payload: dict[str, Any],
    ordinal: int,
    base_thread_id: str,
    base_offset: int,
    parent_path: Path,
    inventory: dict[str, HistoryInventoryEntry],
    allowed_roots: tuple[Path, ...],
    current_path: Path,
    error_type: type[Exception],
) -> tuple[tuple[Path, str], ...]:
    """Prove an original fork's physical prefix belongs to its logical parent.

    Official reference-backed forks may select a turn in an inherited segment.
    The logical fork parent therefore differs from the physical history base.
    This path deliberately does not infer a legacy/reverted fork boundary.
    """
    logical_parent = payload.get("forked_from_id")
    cutoff = payload.get("forked_from_ordinal_exclusive")
    if (
        rollout_id_from_path(current_path) != thread_id.lower()
        or not isinstance(logical_parent, str)
        or ROLLOUT_ID_PATTERN.fullmatch(logical_parent) is None
        or logical_parent.lower() == thread_id.lower()
        or type(cutoff) is not int
        or cutoff != ordinal
    ):
        raise error_type(f"Inherited fork boundary is not proven for {thread_id}")
    registered = inventory.get(f"registered::{logical_parent}")
    if registered is None:
        raise error_type(f"Inherited fork logical parent is not registered for {thread_id}")
    path = registered.path
    if registered.history_mode != "paginated":
        raise error_type(f"Inherited fork logical parent mode is invalid for {thread_id}")
    seen: set[str] = {rollout_id_from_path(current_path)}
    dependencies: list[tuple[Path, str]] = []
    inherited_end: tuple[int, int] | None = None
    for depth in range(256):
        if (
            not path.is_file()
            or not any(is_within(path, root) for root in allowed_roots)
            or path.resolve() == current_path.resolve()
        ):
            raise error_type(f"Inherited fork lineage path is invalid for {thread_id}")
        rollout_id = rollout_id_from_path(path)
        if rollout_id is None or rollout_id in seen:
            raise error_type(f"Inherited fork lineage is cyclic or noncanonical for {thread_id}")
        seen.add(rollout_id)
        unique_path = find_rollout_path_by_id(
            rollout_id, allowed_roots, current_path, error_type
        )
        if unique_path.resolve() != path.resolve():
            raise error_type(f"Inherited fork lineage registration is ambiguous for {thread_id}")
        content = path.read_bytes()
        first: dict[str, Any] | None = None
        next_ordinal: int | None = None
        for line_number, raw_line in enumerate(content.splitlines(), start=1):
            try:
                record = json.loads(raw_line)
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise error_type(f"Invalid inherited fork lineage JSON for {thread_id}") from error
            if not isinstance(record, dict) or type(record.get("ordinal")) is not int:
                raise error_type(f"Invalid inherited fork lineage record for {thread_id}")
            if first is None:
                first = record
                next_ordinal = record["ordinal"]
            if record["ordinal"] != next_ordinal or record["ordinal"] < 0:
                raise error_type(f"Non-contiguous inherited fork lineage ordinal for {thread_id}")
            next_ordinal += 1
        meta = first.get("payload") if first is not None else None
        # The official filename identifies both the stable owner and physical
        # segment: <owner>.jsonl or <owner>_<rollout>.jsonl.  Checking only a
        # UUID-shaped metadata owner would allow a forged intermediate owner.
        filename_ids = list(ROLLOUT_ID_PATTERN.finditer(path.name))
        filename_owner = None
        if len(filename_ids) == 1:
            filename_owner = filename_ids[0].group().lower()
        elif (
            len(filename_ids) == 2
            and path.name[filename_ids[0].end():filename_ids[1].start()] == "_"
        ):
            filename_owner = filename_ids[0].group().lower()
        if (
            not isinstance(meta, dict)
            or first.get("type") != "session_meta"
            or meta.get("history_mode") != "paginated"
            or not isinstance(meta.get("id"), str)
            or ROLLOUT_ID_PATTERN.fullmatch(meta["id"]) is None
            or meta["id"].lower() != filename_owner
            or (depth == 0 and meta["id"] != logical_parent)
        ):
            raise error_type(f"Inherited fork lineage identity is not proven for {thread_id}")
        dependencies.append((path, hashlib.sha256(content).hexdigest()))
        if inherited_end is not None:
            end_ordinal, end_offset = inherited_end
            validate_parent_boundary(thread_id, path, end_offset, end_ordinal, error_type)
        if rollout_id == base_thread_id.lower():
            if (
                path.resolve() != parent_path.resolve()
                or inherited_end is None
                or ordinal > inherited_end[0]
                or base_offset > inherited_end[1]
            ):
                raise error_type(f"Inherited fork boundary exceeds parent history for {thread_id}")
            return tuple(dependencies)
        history_base = meta.get("history_base")
        if (
            not isinstance(history_base, dict)
            or not isinstance(history_base.get("thread_id"), str)
            or ROLLOUT_ID_PATTERN.fullmatch(history_base["thread_id"]) is None
            or type(history_base.get("end_ordinal_exclusive")) is not int
            or history_base["end_ordinal_exclusive"] != first["ordinal"]
            or type(history_base.get("end_byte_offset")) is not int
            or history_base["end_byte_offset"] <= 0
        ):
            raise error_type(f"Inherited fork history base lineage is not proven for {thread_id}")
        # A prefix ending before this segment begins cannot inherit its base.
        if inherited_end is not None and inherited_end[0] <= first["ordinal"]:
            raise error_type(f"Inherited fork lineage cutoff precedes segment for {thread_id}")
        inherited_end = (first["ordinal"], history_base["end_byte_offset"])
        path = find_rollout_path_by_id(
            history_base["thread_id"], allowed_roots, current_path, error_type
        )
    raise error_type(f"Inherited fork lineage exceeds proof depth for {thread_id}")


def validate_paginated_start(
    thread_id: str,
    first_record: dict[str, Any],
    projection_state: tuple[int, int] | None,
    rollout_size: int,
    inventory: dict[str, HistoryInventoryEntry],
    allowed_roots: tuple[Path, ...],
    error_type: type[Exception],
    current_path: Path | None = None,
) -> HistoryBaseProof:
    """Prove a zero, self, or forked paginated start without writing data."""
    ordinal = first_record.get("ordinal")
    if isinstance(ordinal, bool) or not isinstance(ordinal, int) or ordinal < 0:
        raise error_type(f"Invalid first ordinal in paginated rollout {thread_id}: {ordinal!r}")
    if ordinal == 0:
        return HistoryBaseProof(0, None, "zero", None, None, None)
    try:
        continuation = projection_continuation_proof(thread_id, first_record)
    except ValueError as error:
        raise error_type(str(error)) from error
    if continuation is not None:
        return continuation
    payload = first_record.get("payload")
    history_base = payload.get("history_base") if isinstance(payload, dict) else None
    base_offset = history_base.get("end_byte_offset") if isinstance(history_base, dict) else None
    if (
        first_record.get("type") != "session_meta"
        or not isinstance(payload, dict)
        or payload.get("id") != thread_id
        or payload.get("history_mode") != "paginated"
        or not isinstance(history_base, dict)
        or history_base.get("end_ordinal_exclusive") != ordinal
        or isinstance(base_offset, bool)
        or not isinstance(base_offset, int)
        or projection_state is None
    ):
        raise error_type(f"Non-zero paginated start is not jointly proven for {thread_id}")
    base_thread_id = history_base.get("thread_id")
    projection_offset, projection_ordinal = projection_state
    if not isinstance(base_thread_id, str) or not (0 <= projection_offset <= rollout_size and ordinal <= projection_ordinal):
        raise error_type(f"Projection cursor cannot prove paginated start for {thread_id}")
    if current_path is not None:
        current_rollout_id = rollout_id_from_path(current_path)
        if current_rollout_id is None:
            raise error_type(f"Paginated rollout filename is not canonical for {thread_id}")
        if base_thread_id.lower() == current_rollout_id:
            if base_thread_id != thread_id:
                raise error_type(f"Paginated history lineage is cyclic for {thread_id}")
            if not (0 < base_offset <= rollout_size and base_offset <= projection_offset):
                raise error_type(f"Projection cursor cannot prove paginated start for {thread_id}")
            parent_identity = validate_parent_boundary(
                thread_id, current_path, base_offset, ordinal, error_type
            )
            if parent_identity != thread_id:
                raise error_type(f"Paginated self history identity is not proven for {thread_id}")
            return HistoryBaseProof(
                ordinal,
                base_offset,
                "self",
                base_thread_id,
                current_path,
                sha256_path(current_path),
            )
        if not (0 <= projection_offset <= rollout_size and ordinal <= projection_ordinal):
            raise error_type(f"Projection cursor cannot prove paginated start for {thread_id}")
        parent_entry = inventory.get(base_thread_id)
        if (
            parent_entry is not None
            and parent_entry.path != current_path
            and parent_entry.path.is_file()
            and any(is_within(parent_entry.path, root) for root in allowed_roots)
        ):
            parent_path = parent_entry.path
        else:
            parent_path = find_rollout_path_by_id(
                base_thread_id, allowed_roots, current_path, error_type
            )
        parent_identity = validate_parent_boundary(
            thread_id, parent_path, base_offset, ordinal, error_type
        )
        if parent_identity == thread_id:
            return HistoryBaseProof(
                ordinal,
                base_offset,
                "rollover",
                base_thread_id,
                parent_path,
                sha256_path(parent_path),
            )
        registered_parent = inventory.get(f"registered::{parent_identity}")
        if registered_parent is None:
            raise error_type(
                f"Fork history base parent is not a registered session rollout for {thread_id}"
            )
        if registered_parent.path != parent_path:
            # A registered parent may have rolled over after this fork was made.
            # Accept only an exact, directly linked prior segment, with both byte
            # boundaries and the stable parent identity independently proven.
            registered_path = registered_parent.path
            if (
                registered_parent.history_mode != "paginated"
                or not registered_path.is_file()
                or not any(is_within(registered_path, root) for root in allowed_roots)
            ):
                raise error_type(f"Registered parent rollover path is invalid for {thread_id}")
            try:
                with registered_path.open("rb") as stream:
                    registered_first = json.loads(stream.readline())
                registered_payload = registered_first.get("payload", {})
                registered_base = registered_payload.get("history_base", {})
                registered_ordinal = registered_first.get("ordinal")
                registered_offset = registered_base.get("end_byte_offset")
                valid_registration = (
                    registered_first.get("type") == "session_meta"
                    and registered_payload.get("id") == parent_identity
                    and registered_payload.get("history_mode") == "paginated"
                    and registered_base.get("thread_id") == rollout_id_from_path(parent_path)
                    and type(registered_ordinal) is int
                    and registered_ordinal >= ordinal
                    and registered_base.get("end_ordinal_exclusive") == registered_ordinal
                    and type(registered_offset) is int
                    and registered_offset >= base_offset
                )
            except (OSError, ValueError, AttributeError, TypeError) as error:
                raise error_type(f"Registered parent rollover metadata is invalid for {thread_id}") from error
            if not valid_registration or validate_parent_boundary(
                thread_id, parent_path, registered_offset, registered_ordinal, error_type
            ) != parent_identity:
                raise error_type(f"Registered parent rollover lineage is not proven for {thread_id}")
        lineage_dependencies: tuple[tuple[Path, str], ...] = ()
        if payload.get("forked_from_id") not in {base_thread_id, parent_identity}:
            lineage_dependencies = _prove_inherited_fork_lineage(
                thread_id, payload, ordinal, base_thread_id, base_offset,
                parent_path, inventory, allowed_roots, current_path, error_type,
            )
        return HistoryBaseProof(
            ordinal,
            base_offset,
            "fork",
            base_thread_id,
            parent_path,
            sha256_path(parent_path),
            lineage_parent_sha256=lineage_dependencies,
        )

    # Compatibility path for older fixtures. Production callers always supply
    # current_path so self-referential lineages cannot bypass cycle detection.
    if base_thread_id == thread_id:
        if not (0 <= base_offset <= rollout_size and base_offset <= projection_offset):
            raise error_type(f"Projection cursor cannot prove paginated start for {thread_id}")
        return HistoryBaseProof(ordinal, base_offset, "self", base_thread_id, None, None)
    if payload.get("forked_from_id") != base_thread_id:
        raise error_type(f"Fork history base relationship is not proven for {thread_id}")
    parent = inventory.get(base_thread_id)
    if parent is None or parent.history_mode != "paginated" or not parent.path.is_file() or not any(is_within(parent.path, root) for root in allowed_roots):
        raise error_type(f"Fork history base parent is not a registered session rollout for {thread_id}")
    parent_bytes = parent.path.read_bytes()
    if not 0 < base_offset <= len(parent_bytes):
        raise error_type(f"Fork history base offset is outside parent rollout for {thread_id}")
    parent_identity = False
    previous_ordinal: int | None = None
    next_ordinal: int | None = None
    offset = 0
    for line_number, raw_line in enumerate(parent_bytes.splitlines(keepends=True), start=1):
        line_start = offset
        offset += len(raw_line)
        content = raw_line.rstrip(b"\r\n")
        if not content.strip():
            raise error_type(f"Blank parent JSONL record for fork history base {thread_id}")
        try:
            value = json.loads(content)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise error_type(f"Invalid parent JSON for fork history base {thread_id} at line {line_number}") from error
        if not isinstance(value, dict):
            raise error_type(f"Non-object parent record for fork history base {thread_id}")
        if line_number == 1:
            parent_payload = value.get("payload")
            parent_identity = bool(
                value.get("type") == "session_meta"
                and isinstance(parent_payload, dict)
                and parent_payload.get("id") == base_thread_id
                and parent_payload.get("history_mode") == "paginated"
            )
        if offset == base_offset:
            previous_ordinal = value.get("ordinal")
        if line_start == base_offset:
            next_ordinal = value.get("ordinal")
    if not parent_identity:
        raise error_type(f"Fork history base parent identity is not proven for {thread_id}")
    if previous_ordinal != ordinal - 1:
        raise error_type(f"Fork history base offset is not an ordinal boundary for {thread_id}")
    if next_ordinal is not None and next_ordinal != ordinal:
        raise error_type(f"Fork history base next ordinal is not proven for {thread_id}")
    return HistoryBaseProof(
        ordinal, base_offset, "fork", base_thread_id, parent.path, sha256_path(parent.path)
    )
