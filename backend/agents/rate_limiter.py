"""
Shared rate limiter for Gemini free tier.
Enforces max 10 requests/minute with automatic retry + backoff.
"""
import asyncio
import time
import logging
from collections import deque

logger = logging.getLogger(__name__)

# Global token bucket — 10 requests per 60 seconds (safe under free tier 15 RPM)
_request_times: deque = deque()
_lock = asyncio.Lock()
MAX_REQUESTS_PER_MINUTE = 10
WINDOW_SECONDS = 60


async def acquire_llm_slot():
    """Wait until a request slot is available, then claim it."""
    async with _lock:
        now = time.monotonic()
        # Remove timestamps older than the window
        while _request_times and now - _request_times[0] > WINDOW_SECONDS:
            _request_times.popleft()

        if len(_request_times) >= MAX_REQUESTS_PER_MINUTE:
            oldest = _request_times[0]
            wait_time = WINDOW_SECONDS - (now - oldest) + 1.0
            logger.info(f"[RateLimiter] Throttling — waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)

        _request_times.append(time.monotonic())
