from __future__ import annotations

import argparse
import json
from pathlib import Path

from .ai_agent import agent
from .app import ZenvXApp
from .doctor import run_doctor


def main() -> None:
    p = argparse.ArgumentParser(prog="zenvx")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("gui")

    i = sub.add_parser("install"); i.add_argument("file"); i.add_argument("--name", default=None); i.add_argument("--allow-sudo", action="store_true")
    l = sub.add_parser("launch"); l.add_argument("app_id"); l.add_argument("--allow-sudo", action="store_true")
    sub.add_parser("list")
    r = sub.add_parser("remove"); r.add_argument("app_id"); r.add_argument("--yes", action="store_true"); r.add_argument("--allow-sudo", action="store_true")
    rep = sub.add_parser("report"); rep.add_argument("app_id")
    sub.add_parser("doctor")
    a = sub.add_parser("agent"); a.add_argument("question"); a.add_argument("--app", dest="app_id", default=None)

    args = p.parse_args()
    z = ZenvXApp()

    if args.cmd in (None, "gui"):
        from .gui import run_gui
        run_gui(); return

    if args.cmd == "doctor":
        for c in run_doctor():
            print(f"{c.status}\t{c.name}: {c.detail}" + (f" (fix: {c.fix})" if c.fix else ""))
        return

    if args.cmd == "install":
        print(z.install(Path(args.file), display_name=args.name, allow_sudo=args.allow_sudo)); return

    if args.cmd == "list":
        for rec in z.registry.list_apps():
            print(f"{rec.app_id}\t{rec.runtime_type}\t{rec.display_name}"); return

    if args.cmd == "launch":
        z.launch(args.app_id, allow_sudo=args.allow_sudo); return

    if args.cmd == "remove":
        z.remove(args.app_id, confirm=args.yes, allow_sudo=args.allow_sudo); return

    if args.cmd == "report":
        rec = z.registry.get_app(args.app_id);
        print(json.dumps(rec.__dict__ if rec else {}, indent=2, default=str)); return

    if args.cmd == "agent":
        ctx = {}
        if args.app_id:
            rec = z.registry.get_app(args.app_id); ctx = {"app": rec.__dict__ if rec else {}}
        print(json.dumps(agent.answer(args.question, ctx), indent=2)); return


if __name__ == "__main__":
    main()
