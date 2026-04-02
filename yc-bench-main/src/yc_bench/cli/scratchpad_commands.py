from __future__ import annotations

import typer

from ..db.models.scratchpad import Scratchpad
from ..db.models.sim_state import SimState
from . import get_db, json_output, error_output

scratchpad_app = typer.Typer(help="Agent scratchpad for persistent notes.")


def _get_or_create(db, company_id) -> Scratchpad:
    row = db.query(Scratchpad).filter(Scratchpad.company_id == company_id).one_or_none()
    if row is None:
        row = Scratchpad(company_id=company_id, content="")
        db.add(row)
        db.flush()
    return row


@scratchpad_app.command("read")
def scratchpad_read():
    """Read the current scratchpad content."""
    with get_db() as db:
        sim_state = db.query(SimState).first()
        if sim_state is None:
            error_output("No simulation found. Run `yc-bench sim init` first.")
        row = _get_or_create(db, sim_state.company_id)
        json_output({"content": row.content})


@scratchpad_app.command("write")
def scratchpad_write(
    content: str = typer.Option(..., help="Text to write (replaces existing content)."),
):
    """Overwrite the scratchpad with new content."""
    with get_db() as db:
        sim_state = db.query(SimState).first()
        if sim_state is None:
            error_output("No simulation found. Run `yc-bench sim init` first.")
        row = _get_or_create(db, sim_state.company_id)
        row.content = content
        json_output({"ok": True, "content": row.content})


@scratchpad_app.command("append")
def scratchpad_append(
    content: str = typer.Option(..., help="Text to append to existing content."),
):
    """Append text to the scratchpad (adds a newline separator)."""
    with get_db() as db:
        sim_state = db.query(SimState).first()
        if sim_state is None:
            error_output("No simulation found. Run `yc-bench sim init` first.")
        row = _get_or_create(db, sim_state.company_id)
        if row.content:
            row.content = row.content + "\n" + content
        else:
            row.content = content
        json_output({"ok": True, "content": row.content})


@scratchpad_app.command("clear")
def scratchpad_clear():
    """Clear the scratchpad."""
    with get_db() as db:
        sim_state = db.query(SimState).first()
        if sim_state is None:
            error_output("No simulation found. Run `yc-bench sim init` first.")
        row = _get_or_create(db, sim_state.company_id)
        row.content = ""
        json_output({"ok": True})
