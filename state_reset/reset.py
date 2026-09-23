from dataclasses import dataclass, field
from typing import Callable, Optional

import redis

ProgressCallback = Callable[[int, int], None]


@dataclass
class ResetResult:
    pattern: str
    scanned: int = 0
    deleted: int = 0
    dry_run: bool = False
    batches: list[int] = field(default_factory=list)


def reset_namespace(
    client: redis.Redis,
    pattern: str,
    scan_batch_size: int = 500,
    dry_run: bool = False,
    on_progress: Optional[ProgressCallback] = None,
) -> ResetResult:
    """Purge every key matching `pattern` using cursor-based SCAN + batched DEL.

    SCAN is used instead of KEYS so the reset never blocks the Redis event
    loop, even against large namespaces. Keys are deleted in the same
    batches they're scanned in, rather than buffering the entire matching
    keyspace in memory before deleting.
    """
    result = ResetResult(pattern=pattern, dry_run=dry_run)
    cursor = 0

    while True:
        cursor, keys = client.scan(cursor=cursor, match=pattern, count=scan_batch_size)
        result.scanned += len(keys)

        if keys:
            if dry_run:
                deleted_in_batch = 0
            else:
                deleted_in_batch = client.delete(*keys)
            result.deleted += deleted_in_batch
            result.batches.append(len(keys))

            if on_progress is not None:
                on_progress(result.scanned, result.deleted)

        if cursor == 0:
            break

    return result
