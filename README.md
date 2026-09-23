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
Provide a target namespace prefix to the CLI tool to initiate a non-blocking cache purge.

## Testing & CI
Integration tests require an active local Redis instance mapped via Docker to validate deletion atomicity.
