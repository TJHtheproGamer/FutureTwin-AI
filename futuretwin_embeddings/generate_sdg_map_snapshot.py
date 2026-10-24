"""Explicit offline refresh for the PostgreSQL-backed SDG map snapshot."""
from __future__ import annotations

from futuretwin_sdg_map import build_map_snapshot, save_map_snapshot


def main() -> None:
    payload = build_map_snapshot()
    save_map_snapshot(payload)
    coverage = payload["coverage"]
    print(
        "Saved SDG map snapshot "
        f"{payload['snapshot_id']}: {coverage['node_count']} nodes, "
        f"{coverage['candidate_link_count']} candidate links, "
        f"{coverage['reviewed_link_count']} reviewed links."
    )


if __name__ == "__main__":
    main()
