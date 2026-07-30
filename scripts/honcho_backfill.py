#!/usr/bin/env python3
"""
Honcho Historical Session Backfill Script
==========================================
Reads Hermes state.db sessions from the Agentic-rd workspace and uploads
user messages as observations to the Honcho v3 API for dialectic processing.

This script runs from the Windows host (Python 3.11+) and reads the SQLite
state.db, then POSTs to the Honcho API running in WSL2 at localhost:8000.

Usage:
    python scripts/honcho_backfill.py [--dry-run] [--limit N] [--session-id ID]
"""

import argparse
import json
import sys
import time
import sqlite3
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ── Configuration ──────────────────────────────────────────────────────────

import os, platform, shutil, tempfile

# Detect if running in WSL2 or Windows
IS_WSL = "microsoft" in platform.uname().release.lower() or "WSL" in platform.uname().release

if IS_WSL:
    STATE_DB_SOURCE = "/mnt/c/Users/carlo/AppData/Local/hermes/profiles/wsl-runtime/state.db"
else:
    STATE_DB_SOURCE = r"C:\Users\carlo\AppData\Local\hermes\profiles\wsl-runtime\state.db"

HONCHO_BASE = "http://localhost:8000"
WORKSPACE_ID = "hermes_wsl-runtime"
SESSION_NAME = "agentic-rd"
OBSERVER_PEER_ID = "hermes_wsl-runtime"
OBSERVED_PEER_ID = "user-default-carlo"

# Sessions cwd pattern to match
AGENTIC_RD_PATTERN = r"\agentic-rd"

# ── Helpers ─────────────────────────────────────────────────────────────────

def api_url(path: str) -> str:
    return f"{HONCHO_BASE}{path}"

def post_json(url: str, payload: dict, dry_run: bool = False) -> dict:
    """POST JSON payload to Honcho API. Returns parsed response or raises."""
    if dry_run:
        print(f"  [DRY RUN] POST {url}")
        print(f"  [DRY RUN] Payload: {json.dumps(payload, indent=2)[:200]}...")
        return {"status": "dry_run"}

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  HTTP {e.code}: {body[:500]}")
        raise
    except urllib.error.URLError as e:
        print(f"  Connection error: {e.reason}")
        raise


def ensure_session(dry_run: bool = False) -> str:
    """Get or create the agentic-rd session in Honcho."""
    print(f"Ensuring session '{SESSION_NAME}' exists in workspace '{WORKSPACE_ID}'...")
    url = api_url(f"/v3/workspaces/{WORKSPACE_ID}/sessions")
    payload = {"name": SESSION_NAME, "metadata": {"backfill": True}}
    resp = post_json(url, payload, dry_run=dry_run)
    sid = resp.get("id", SESSION_NAME)
    print(f"  Session ID: {sid}")
    return sid


def fetch_sessions(conn: sqlite3.Connection, limit: int | None = None,
                   session_id: str | None = None) -> list[dict]:
    """Fetch agentic-rd sessions from the state DB."""
    if session_id:
        cur = conn.execute(
            "SELECT id, title, started_at, message_count FROM sessions WHERE id = ?",
            (session_id,),
        )
    else:
        cur = conn.execute(
            """SELECT id, title, started_at, message_count 
               FROM sessions 
               WHERE cwd LIKE '%agentic-rd%'
               ORDER BY started_at ASC""",
        )
    sessions = []
    for row in cur:
        sessions.append({
            "id": row[0],
            "title": row[1] or "(no title)",
            "started_at": row[2],
            "message_count": row[3],
        })
    if limit:
        sessions = sessions[:limit]
    return sessions


def fetch_user_messages(conn: sqlite3.Connection, session_id: str) -> list[dict]:
    """Fetch user messages from a session (role='user', active=1)."""
    cur = conn.execute(
        """SELECT id, content, timestamp 
           FROM messages 
           WHERE session_id = ? AND role = 'user' AND active = 1
           ORDER BY id ASC""",
        (session_id,),
    )
    messages = []
    for row in cur:
        content = row[1]
        if content and len(content.strip()) > 10:  # Skip empty/short messages
            messages.append({
                "id": row[0],
                "content": content,
                "timestamp": row[2],
            })
    return messages


def upload_messages(session_id: str, messages: list[dict],
                    dry_run: bool = False) -> int:
    """Upload user messages as observations to the Honcho session."""
    uploaded = 0
    url = api_url(
        f"/v3/workspaces/{WORKSPACE_ID}/sessions/{session_id}/messages"
    )
    for i, msg in enumerate(messages):
        try:
            payload = {
                "messages": [{
                    "role": "user",
                    "content": msg["content"][:2000],  # Truncate very long messages
                    "peer_id": OBSERVED_PEER_ID,
                }],
            }
            post_json(url, payload, dry_run=dry_run)
            uploaded += 1
            if i % 10 == 0 and i > 0:
                print(f"  ... {i}/{len(messages)} messages uploaded")
            time.sleep(0.1)  # Rate limit
        except Exception as e:
            print(f"  Failed to upload message {msg['id']}: {e}")
    return uploaded


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Backfill Honcho memory from Hermes session history"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Print actions without uploading")
    parser.add_argument("--limit", type=int, default=None,
                        help="Max number of sessions to process")
    parser.add_argument("--session-id", type=str, default=None,
                        help="Process a single session by ID")
    parser.add_argument("--messages-per-session", type=int, default=20,
                        help="Max user messages to upload per session")
    args = parser.parse_args()

    print("=" * 60)
    print("HONCHO HISTORICAL BACKFILL")
    print(f"Platform: {'WSL2' if IS_WSL else 'Windows'}")
    print(f"State DB source: {STATE_DB_SOURCE}")
    print(f"Honcho API: {HONCHO_BASE}")
    print(f"Workspace: {WORKSPACE_ID}")
    print(f"Dry run: {args.dry_run}")
    print("=" * 60)

    # On WSL2, copy DB to temp to avoid WAL-mode boundary issues
    if IS_WSL:
        temp_db = os.path.join(tempfile.gettempdir(), "hermes_state_copy.db")
        print(f"Copying state DB to WSL2-native temp location: {temp_db}")
        shutil.copy2(STATE_DB_SOURCE, temp_db)
        # Also copy WAL and SHM if present
        for suffix in ["-wal", "-shm"]:
            src = STATE_DB_SOURCE + suffix
            if os.path.exists(src):
                shutil.copy2(src, temp_db + suffix)
        state_db = temp_db
    else:
        state_db = STATE_DB_SOURCE

    # Connect to state DB
    conn = sqlite3.connect(state_db)
    conn.row_factory = sqlite3.Row

    # Find sessions
    sessions = fetch_sessions(conn, limit=args.limit, session_id=args.session_id)
    print(f"\nFound {len(sessions)} agentic-rd sessions in state DB")

    if not sessions:
        print("No sessions found. Exiting.")
        conn.close()
        return

    # Show session summary
    print(f"\n{'Session ID':<30} | {'Title':<45} | {'Msgs':>5}")
    print("-" * 90)
    for s in sessions:
        ts = datetime.fromtimestamp(s["started_at"], tz=timezone.utc).strftime("%Y-%m-%d")
        print(f"{s['id']:<30} | {s['title'][:45]:<45} | {s['message_count']:>5}")

    # Ensure Honcho session exists
    honcho_session_id = ensure_session(dry_run=args.dry_run)

    # Process each session
    total_uploaded = 0
    for s in sessions:
        print(f"\n--- Processing: {s['title'][:50]} ({s['id'][:20]}...) ---")

        messages = fetch_user_messages(conn, s["id"])
        print(f"  Found {len(messages)} user messages")

        if len(messages) > args.messages_per_session:
            # Take a sample spread across the session
            step = max(1, len(messages) // args.messages_per_session)
            messages = messages[::step][:args.messages_per_session]
            print(f"  Sampling to {len(messages)} messages")

        if not args.dry_run and messages:
            uploaded = upload_messages(honcho_session_id, messages, dry_run=False)
            total_uploaded += uploaded
            print(f"  Uploaded {uploaded}/{len(messages)} messages")
        elif args.dry_run and messages:
            upload_messages(honcho_session_id, messages[:2], dry_run=True)
            print(f"  (Dry run — would upload {len(messages)} messages)")

    conn.close()

    print(f"\n{'=' * 60}")
    print(f"BACKFILL COMPLETE")
    print(f"Sessions processed: {len(sessions)}")
    print(f"Total messages uploaded: {total_uploaded}")
    print(f"Honcho session: {honcho_session_id}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()