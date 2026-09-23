# Application State Reset

## Description
A state management utility for safely and asynchronously flushing Redis cache namespaces.

## Architecture Overview
Redis connection pool executing cursor-based, non-blocking `SCAN` and batched `DEL` commands.

## Prerequisites
* Python 3.11+
* Redis server
* `redis-py`

## Environment Variables
* `REDIS_URL`
* `RESET_PATTERN_PREFIX`
* `SCAN_BATCH_SIZE`

## Quick Start & Usage
```bash
pip install -r requirements.txt
cp .env.example .env   # then edit REDIS_URL / RESET_PATTERN_PREFIX as needed

# Preview what would be deleted, without deleting anything
python main.py --prefix "session:*" --dry-run

# Purge a namespace (prompts for confirmation)
python main.py --prefix "session:*"

# Skip the confirmation prompt (e.g. in scripts/CI)
python main.py --prefix "cache:*" --yes
```

All options can also be set via environment variables (`REDIS_URL`, `RESET_PATTERN_PREFIX`,
`SCAN_BATCH_SIZE`); CLI flags take precedence. Deletion is cursor-based (`SCAN` + batched
`DEL`), so it never blocks the Redis event loop even on large namespaces.
