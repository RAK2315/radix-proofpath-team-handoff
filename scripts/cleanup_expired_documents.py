"""Private, explicitly invoked maintenance job; not an HTTP endpoint or startup action."""

import argparse
from datetime import datetime, timedelta, timezone

import httpx

from shared.integrations.auth import Identity
from shared.integrations.config import setting
from shared.integrations.documents import remove_document
from shared.integrations.store import remote_headers


def run(apply: bool = False) -> int:
    key = setting("SUPABASE_MAINTENANCE_KEY")
    if not key or setting("RADIX_STORAGE_MODE") != "supabase":
        raise RuntimeError(
            "Maintenance requires separate server-only SUPABASE_MAINTENANCE_KEY and Supabase mode"
        )
    admin = Identity("maintenance", key, True)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    # Snapshot IDs before deleting, avoiding pagination shifts.
    records = []
    offset = 0
    with httpx.Client(timeout=30) as client:
        while True:
            response = client.get(
                f"{setting('SUPABASE_URL')}/rest/v1/proofpath_records",
                headers=remote_headers(admin),
                params={
                    "kind": "eq.document",
                    "payload->>created_at": f"lt.{cutoff}",
                    "select": "owner,id",
                    "order": "owner,id",
                    "limit": 500,
                    "offset": offset,
                },
            )
            response.raise_for_status()
            batch = response.json()
            records.extend(batch)
            if len(batch) < 500:
                break
            offset += len(batch)
    for row in records:
        if apply:
            remove_document(Identity(row["owner"], key, True), row["id"])
    return len(records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Delete expired originals and dependent claims; default only counts",
    )
    args = parser.parse_args()
    print({"expired_documents": run(args.apply), "applied": args.apply})
