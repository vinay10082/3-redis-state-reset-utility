import os
from dataclasses import dataclass


class ConfigError(ValueError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Config:
    redis_url: str
    pattern_prefix: str
    scan_batch_size: int

    @classmethod
    def from_env(cls, overrides: dict | None = None) -> "Config":
        overrides = overrides or {}

        redis_url = overrides.get("redis_url") or os.environ.get(
            "REDIS_URL", "redis://localhost:6379/0"
        )

        pattern_prefix = overrides.get("pattern_prefix") or os.environ.get(
            "RESET_PATTERN_PREFIX"
        )
        if not pattern_prefix:
            raise ConfigError(
                "A pattern prefix is required. Set RESET_PATTERN_PREFIX or pass --prefix."
            )

        raw_batch_size = overrides.get("scan_batch_size") or os.environ.get(
            "SCAN_BATCH_SIZE", "500"
        )
        try:
            scan_batch_size = int(raw_batch_size)
        except (TypeError, ValueError) as exc:
            raise ConfigError(
                f"SCAN_BATCH_SIZE must be an integer, got {raw_batch_size!r}"
            ) from exc
        if scan_batch_size <= 0:
            raise ConfigError("SCAN_BATCH_SIZE must be a positive integer.")

        return cls(
            redis_url=redis_url,
            pattern_prefix=pattern_prefix,
            scan_batch_size=scan_batch_size,
        )
