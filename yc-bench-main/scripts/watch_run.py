"""Watch a live YC-Bench run — polls the DB every few seconds and prints funds/prestige/trust."""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from yc_bench.db.models.client import Client, ClientTrust
from yc_bench.db.models.company import Company, CompanyPrestige
from yc_bench.db.models.sim_state import SimState
from yc_bench.db.models.task import Task, TaskStatus
from yc_bench.db.session import build_engine, build_session_factory, session_scope


def snapshot(factory, company_id):
    with session_scope(factory) as db:
        sim = db.query(SimState).first()
        if not sim:
            return None
        company = db.query(Company).filter(Company.id == company_id).one()

        # Tasks
        completed = db.query(Task).filter(
            Task.company_id == company_id,
            Task.status == TaskStatus.COMPLETED_SUCCESS,
        ).count()
        failed = db.query(Task).filter(
            Task.company_id == company_id,
            Task.status == TaskStatus.COMPLETED_FAIL,
        ).count()
        active = db.query(Task).filter(
            Task.company_id == company_id,
            Task.status == TaskStatus.ACTIVE,
        ).count()

        # Prestige
        prestige_rows = db.query(CompanyPrestige).filter(
            CompanyPrestige.company_id == company_id,
        ).all()
        prestige = {
            (p.domain.value if hasattr(p.domain, "value") else str(p.domain)): round(float(p.prestige_level), 2)
            for p in prestige_rows
        }

        # Trust
        trust_rows = (
            db.query(ClientTrust, Client.name, Client.reward_multiplier)
            .join(Client, Client.id == ClientTrust.client_id)
            .filter(ClientTrust.company_id == company_id)
            .order_by(Client.name)
            .all()
        )
        trusts = [
            (name, round(float(ct.trust_level), 2), round(float(mult), 2))
            for ct, name, mult in trust_rows
        ]

        return {
            "sim_time": sim.sim_time.strftime("%Y-%m-%d %H:%M"),
            "funds": company.funds_cents,
            "completed": completed,
            "failed": failed,
            "active": active,
            "prestige": prestige,
            "trusts": trusts,
        }


def print_snapshot(snap, prev_funds=None):
    delta = ""
    if prev_funds is not None:
        d = snap["funds"] - prev_funds
        delta = f"  ({'+' if d >= 0 else ''}{d/100:,.0f})"

    print(f"\033[2J\033[H", end="")  # clear screen
    print(f"  YC-Bench Live Monitor")
    print(f"  {'='*50}")
    print(f"  Sim time:  {snap['sim_time']}")
    print(f"  Funds:     ${snap['funds']/100:>12,.0f}{delta}")
    print(f"  Tasks:     {snap['completed']} OK / {snap['failed']} fail / {snap['active']} active")
    print()
    print(f"  Prestige:")
    for domain, level in sorted(snap["prestige"].items()):
        bar = "█" * int(level * 4)
        print(f"    {domain:<20s} {level:>5.2f}  {bar}")
    print()
    print(f"  Client Trust:")
    for name, trust, mult in snap["trusts"]:
        bar = "█" * int(trust * 4)
        print(f"    {name:<20s} mult={mult:.2f}  trust={trust:>5.2f}  {bar}")
    print()
    print(f"  (polling every 5s, Ctrl+C to stop)")


def main():
    p = argparse.ArgumentParser(description="Watch a live YC-Bench run")
    p.add_argument("db_path", help="Path to the SQLite DB file")
    p.add_argument("--interval", type=float, default=5.0, help="Poll interval in seconds")
    args = p.parse_args()

    db_path = Path(args.db_path)
    if not db_path.exists():
        print(f"DB not found: {db_path}")
        sys.exit(1)

    engine = build_engine(f"sqlite:///{db_path}")
    factory = build_session_factory(engine)

    # Get company_id
    with session_scope(factory) as db:
        sim = db.query(SimState).first()
        if not sim:
            print("No simulation found in DB.")
            sys.exit(1)
        company_id = sim.company_id

    prev_funds = None
    try:
        while True:
            snap = snapshot(factory, company_id)
            if snap:
                print_snapshot(snap, prev_funds)
                prev_funds = snap["funds"]
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
