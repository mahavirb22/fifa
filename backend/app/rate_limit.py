"""Rate limiter singleton — isolated to avoid circular imports.

The limiter is created once and imported by route modules that need it.
Only expensive endpoints (AI calls) are rate-limited.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
