from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable

from fastapi import HTTPException, Request, status


class SimpleRateLimiter:
    """Rate limiter in-memory semplice: 1 req/sec per IP, burst 10."""

    def __init__(self, requests_per_second: float = 1.0, burst: int = 10):
        self.requests_per_second = requests_per_second
        self.burst = burst
        self._requests: dict[str, list[float]] = defaultdict(list)

    def _cleanup_old(self, ip: str, now: float) -> None:
        """Rimuove richieste più vecchie di 1 secondo."""
        cutoff = now - 1.0
        self._requests[ip] = [t for t in self._requests[ip] if t > cutoff]

    def check(self, ip: str) -> bool:
        """Ritorna True se OK, False se rate limit."""
        now = time.time()
        self._cleanup_old(ip, now)

        if len(self._requests[ip]) >= self.burst:
            return False

        self._requests[ip].append(now)
        return True


_limiter = SimpleRateLimiter(requests_per_second=1.0, burst=10)


async def rate_limit_middleware(request: Request, call_next: Callable):
    """Middleware rate limiting per /api/submissions e /api/submissions/*/files."""
    path = request.url.path
    if path.startswith("/api/submissions") and request.method in ("POST", "PUT"):
        ip = request.client.host if request.client else "unknown"
        if not _limiter.check(ip):
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Troppe richieste. Attendi un momento.",
            )
    return await call_next(request)
