from __future__ import annotations

import subprocess
import argparse
import json
from pathlib import Path
import sys

import hotfix_builder

from . import workflow


def _path(value: str) -> Path:
    return Path(value)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Build and verify a supported Codex desktop workflow mod")
    sub = root.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect"); inspect.add_argument("--source", type=_path, required=True)
    build = sub.add_parser("build"); build.add_argument("--source", type=_path, required=True); build.add_argument("--target", type=_path, required=True)
    build.add_argument('--backend-mode', choices=('official','compat'), default='official'); build.add_argument('--backend-manifest', type=_path)
    backend = sub.add_parser('build-backend'); backend.add_argument('--source', type=_path, required=True); backend.add_argument('--target', type=_path, required=True)
    verify = sub.add_parser("verify"); verify.add_argument("--source", type=_path, required=True); verify.add_argument("--portable", type=_path, required=True); verify.add_argument("--runs-root", type=_path, required=True); verify.add_argument("--observe-seconds", type=float, default=60); verify.add_argument("--launches", type=int, default=2)
    copy = sub.add_parser("import-data"); copy.add_argument("--source", type=_path, required=True); copy.add_argument("--target", type=_path, required=True)
    launch = sub.add_parser("launch"); launch.add_argument("--portable", type=_path, required=True); launch.add_argument("--data", type=_path, required=True); launch.add_argument("--runs-root", type=_path, required=True)
    for name in ("status", "stop"):
        item = sub.add_parser(name); item.add_argument("--run", type=_path, required=True)
        if name == "stop": item.add_argument("--timeout", type=float, default=30)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "inspect": result = workflow.inspect(args.source)
        elif args.command == "build": result = workflow.build(args.source, args.target, args.backend_mode, args.backend_manifest)
        elif args.command == 'build-backend': result = workflow.build_backend(args.source, args.target)
        elif args.command == "verify": result = workflow.verify(args.source, args.portable, args.runs_root, args.observe_seconds, args.launches)
        elif args.command == "import-data": result = workflow.import_data(args.source, args.target)
        elif args.command == "launch": result = workflow.launch(args.portable, args.data, args.runs_root)
        elif args.command == "status": result = workflow.status(args.run)
        else: result = workflow.stop(args.run, args.timeout)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result.get("status") not in {"blocked", "backend_orphaned"} and result.get("close_status") != "timeout" else 2
    except (subprocess.CalledProcessError, workflow.WorkflowError, hotfix_builder.HotfixError, OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "blocked", "reason": str(error), "content_logged": False}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
