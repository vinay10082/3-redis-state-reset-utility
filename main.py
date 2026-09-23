#!/usr/bin/env python3
"""CLI entry point for the Redis application state reset utility.

Usage:
    python main.py --prefix "session:*"
    python main.py --prefix "cache:*" --dry-run
    python main.py --prefix "cache:*" --yes
"""
import argparse
import sys

import redis

from state_reset.client import build_client
from state_reset.config import Config, ConfigError
from state_reset.reset import reset_namespace


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Safely and asynchronously flush a Redis cache namespace.",
    )
    parser.add_argument(
        "--prefix",
        dest="pattern_prefix",
        help="Key pattern to reset, e.g. 'session:*'. "
        "Defaults to RESET_PATTERN_PREFIX env var.",
    )
    parser.add_argument(
        "--redis-url",
        dest="redis_url",
        help="Redis connection URL. Defaults to REDIS_URL env var "
        "(redis://localhost:6379/0).",
    )
    parser.add_argument(
        "--batch-size",
        dest="scan_batch_size",
        type=int,
        help="Keys per SCAN cursor iteration. Defaults to SCAN_BATCH_SIZE env var (500).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan and report matching keys without deleting anything.",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip the interactive confirmation prompt.",
    )
    return parser.parse_args(argv)


def confirm(prompt: str) -> bool:
    reply = input(f"{prompt} [y/N]: ").strip().lower()
    return reply in ("y", "yes")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        config = Config.from_env(
            overrides={
                "redis_url": args.redis_url,
                "pattern_prefix": args.pattern_prefix,
                "scan_batch_size": args.scan_batch_size,
            }
        )
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    if not args.dry_run and not args.yes:
        if not confirm(
            f"This will permanently delete all keys matching "
            f"'{config.pattern_prefix}' on {config.redis_url}. Continue?"
        ):
            print("Aborted.")
            return 1

    client = build_client(config)

    try:
        client.ping()
    except redis.exceptions.RedisError as exc:
        print(f"Could not connect to Redis at {config.redis_url}: {exc}", file=sys.stderr)
        return 1

    def on_progress(scanned: int, deleted: int) -> None:
        print(f"  scanned={scanned} deleted={deleted}", end="\r", file=sys.stderr)

    result = reset_namespace(
        client=client,
        pattern=config.pattern_prefix,
        scan_batch_size=config.scan_batch_size,
        dry_run=args.dry_run,
        on_progress=on_progress,
    )
    print(file=sys.stderr)

    mode = "Dry run: would delete" if args.dry_run else "Deleted"
    print(f"{mode} {result.scanned} key(s) matching '{result.pattern}' "
          f"in {len(result.batches)} batch(es).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
