"""Silla MQTT."""
from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Callable, Union

import attr

from .const import COMMAND_BACKLOG

DEBOUNCE_TIMEOUT = 1

_LOGGER = logging.getLogger(__name__)


class Timer:
    """Simple timer."""

    def __init__(self, timeout: float, callback: Callable[[], None]):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())

    async def _job(self) -> None:
        await asyncio.sleep(self._timeout)
        self._callback()

    def cancel(self) -> None:
        """Cancel the timer."""
        self._task.cancel()


PublishPayloadType = Union[str, bytes, int, float, None]
ReceivePayloadType = Union[str, bytes]