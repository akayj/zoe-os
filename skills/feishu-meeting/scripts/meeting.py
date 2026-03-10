#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "duckdb",
#     "httpx",
#     "python-dateutil",
#     "rich",
#     "typer",
# ]
# ///

"""
Feishu Meeting Manager (Python + DuckDB Edition)
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import duckdb
import httpx
import typer
from rich.console import Console
from rich.table import Table

# --- Config & Setup ---
# 支持软链接调用：通过环境变量或跟随软链接找到真实路径
if os.getenv("FEISHU_SKILL_DIR"):
    SKILL_DIR = Path(os.getenv("FEISHU_SKILL_DIR"))
else:
    # 跟随软链接找到真实脚本路径
    SCRIPT_PATH = Path(__file__).resolve()
    SCRIPT_DIR = SCRIPT_PATH.parent
    SKILL_DIR = SCRIPT_DIR.parent

DB_PATH = SKILL_DIR / "data" / "contacts.duckdb"
CONFIG_PATH = SKILL_DIR / "references" / "config.json"

console = Console()
app = typer.Typer(help="Feishu Meeting Manager with DuckDB Contacts")

# Load Config
try:
    with open(CONFIG_PATH, "r") as f:
        CONFIG = json.load(f)
except FileNotFoundError:
    console.print(f"[bold red]❌ Config not found at {CONFIG_PATH}[/]")
    sys.exit(1)

APP_ID = os.getenv("FEISHU_APP_ID") or CONFIG.get("app_id")
APP_SECRET = os.getenv("FEISHU_APP_SECRET") or CONFIG.get("app_secret")
CALENDAR_ID = os.getenv("FEISHU_CALENDAR_ID") or CONFIG.get("calendar_id")
BASE_URL = "https://open.feishu.cn/open-apis"

if not all([APP_ID, APP_SECRET, CALENDAR_ID]):
    console.print("[bold red]❌ Missing required config (APP_ID/SECRET/CALENDAR_ID)[/]")
    sys.exit(1)


# --- Database ---
def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            name VARCHAR,
            email VARCHAR,
            open_id VARCHAR PRIMARY KEY,
            alias VARCHAR,
            updated_at TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS alias_map (
            alias VARCHAR PRIMARY KEY,
            open_id VARCHAR
        );
    """)
    conn.close()


def get_contact(query: str) -> Optional[dict]:
    conn = duckdb.connect(str(DB_PATH))
    
    # 1. Try exact alias match
    res = conn.execute("SELECT open_id FROM alias_map WHERE alias = ?", [query]).fetchone()
    if res:
        open_id = res[0]
        contact = conn.execute("SELECT * FROM contacts WHERE open_id = ?", [open_id]).fetchone()
        if contact:
            return dict(zip(["name", "email", "open_id", "alias", "updated_at"], contact))

    # 2. Try name/email match
    res = conn.execute("""
        SELECT * FROM contacts 
        WHERE name = ? OR email = ? OR alias = ?
    """, [query, query, query]).fetchone()
    
    conn.close()
    if res:
        return dict(zip(["name", "email", "open_id", "alias", "updated_at"], res))
    return None


def upsert_contact(name: str, email: str, open_id: str, alias: str = None):
    conn = duckdb.connect(str(DB_PATH))
    now = datetime.now()
    
    conn.execute("""
        INSERT INTO contacts (name, email, open_id, alias, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT (open_id) DO UPDATE SET
            name = EXCLUDED.name,
            email = EXCLUDED.email,
            alias = COALESCE(EXCLUDED.alias, contacts.alias),
            updated_at = EXCLUDED.updated_at
    """, [name, email, open_id, alias, now])
    
    if alias:
        conn.execute("""
            INSERT INTO alias_map (alias, open_id) VALUES (?, ?)
            ON CONFLICT (alias) DO UPDATE SET open_id = EXCLUDED.open_id
        """, [alias, open_id])
    
    conn.close()


# --- Feishu API ---
def get_token() -> str:
    url = f"{BASE_URL}/auth/v3/tenant_access_token/internal"
    resp = httpx.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    resp.raise_for_status()
    return resp.json()["tenant_access_token"]


def resolve_user_by_email(email: str, token: str) -> Optional[dict]:
    url = f"{BASE_URL}/contact/v3/users/batch_get_id?user_id_type=open_id"
    resp = httpx.post(url, headers={"Authorization": f"Bearer {token}"}, json={"emails": [email]})
    data = resp.json()
    
    if data.get("code") == 0 and data["data"].get("user_list"):
        user = data["data"]["user_list"][0]
        if "user_id" in user:
            return {
                "open_id": user["user_id"],
                "email": email,
                "name": email.split("@")[0] # Fallback name
            }
    return None


# --- Commands ---
@app.command()
def create(
    title: str,
    time_str: str,
    duration: int = 30,
    attendees: str = "",
):
    """Create a meeting. Attendees: names, aliases, or emails (comma-separated)."""
    init_db()
    token = get_token()
    
    # 1. Resolve attendees
    attendee_ids = []
    unknown_attendees = []
    
    if attendees:
        for p in attendees.split(","):
            p = p.strip()
            if not p: continue
            
            # Check DB
            contact = get_contact(p)
            if contact:
                attendee_ids.append(contact["open_id"])
                console.print(f"[green]✓ Found '{p}': {contact['name']} ({contact['email']})[/]")
            else:
                # Try API if looks like email
                if "@" in p:
                    user = resolve_user_by_email(p, token)
                    if user:
                        attendee_ids.append(user["open_id"])
                        upsert_contact(user["name"], user["email"], user["open_id"])
                        console.print(f"[green]✓ Resolved email '{p}' -> {user['open_id']}[/]")
                    else:
                        unknown_attendees.append(p)
                else:
                    unknown_attendees.append(p)

    if unknown_attendees:
        console.print(f"[yellow]⚠️  Unknown attendees: {', '.join(unknown_attendees)}[/]")
        console.print("[dim]Tip: Add them first using `add-contact` command[/]")

    # 2. Create Event
    start_dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
    start_ts = int(start_dt.replace(tzinfo=timezone(timedelta(hours=8))).timestamp())
    end_ts = start_ts + duration * 60
    
    payload = {
        "summary": title,
        "start_time": {"timestamp": str(start_ts), "timezone": "Asia/Shanghai"},
        "end_time": {"timestamp": str(end_ts), "timezone": "Asia/Shanghai"},
        "attendee_ability": "can_see_others",
        "need_notification": True
    }
    
    resp = httpx.post(
        f"{BASE_URL}/calendar/v4/calendars/{CALENDAR_ID}/events?user_id_type=open_id",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )
    
    if resp.status_code != 200 or resp.json().get("code") != 0:
        console.print(f"[bold red]❌ Create failed: {resp.text}[/]")
        return

    event_id = resp.json()["data"]["event"]["event_id"]
    console.print(f"[bold green]✅ Meeting Created![/] ID: {event_id}")
    
    # 3. Add attendees
    if attendee_ids:
        users = [{"type": "user", "user_id": uid} for uid in attendee_ids]
        add_resp = httpx.post(
            f"{BASE_URL}/calendar/v4/calendars/{CALENDAR_ID}/events/{event_id}/attendees?user_id_type=open_id",
            headers={"Authorization": f"Bearer {token}"},
            json={"attendees": users, "need_notification": True}
        )
        if add_resp.json().get("code") == 0:
            console.print(f"[green]✓ Added {len(attendee_ids)} attendees[/]")
        else:
            console.print(f"[red]❌ Failed to add attendees: {add_resp.text}[/]")


@app.command()
def add_contact(email: str, alias: str = None, name: str = None):
    """Add a contact to local DB by email."""
    init_db()
    token = get_token()
    
    user = resolve_user_by_email(email, token)
    if user:
        final_name = name or user["name"]
        upsert_contact(final_name, email, user["open_id"], alias)
        console.print(f"[bold green]✅ Contact saved:[/]")
        console.print(f"Name: {final_name}")
        console.print(f"Email: {email}")
        console.print(f"Alias: {alias or '(none)'}")
    else:
        console.print(f"[bold red]❌ User not found for email: {email}[/]")


@app.command()
def list_contacts():
    """List all local contacts."""
    init_db()
    conn = duckdb.connect(str(DB_PATH))
    rows = conn.execute("SELECT name, email, alias FROM contacts").fetchall()
    conn.close()
    
    table = Table(title="Local Contacts")
    table.add_column("Name")
    table.add_column("Email")
    table.add_column("Alias")
    
    for row in rows:
        table.add_row(row[0], row[1], row[2] or "")
        
    console.print(table)

@app.command()
def cancel(event_id: str):
    """Cancel a meeting."""
    token = get_token()
    url = f"{BASE_URL}/calendar/v4/calendars/{CALENDAR_ID}/events/{event_id}?need_notification=true"
    resp = httpx.delete(url, headers={"Authorization": f"Bearer {token}"})
    if resp.json().get("code") == 0:
        console.print(f"[bold green]✅ Meeting canceled: {event_id}[/]")
    else:
        console.print(f"[bold red]❌ Failed: {resp.text}[/]")

if __name__ == "__main__":
    app()