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


@attr.s(slots=True, frozen=True)
class PublishMessage:
    """MQTT Message."""

    topic: str = attr.ib()
    payload: PublishPayloadType = attr.ib()
    qos: int | None = attr.ib()
    retain: bool | None = attr.ib()


@attr.s(slots=True, frozen=True)
class ReceiveMessage:
    """MQTT Message."""

    topic: str = attr.ib()
    payload: ReceivePayloadType = attr.ib()
    qos: int = attr.ib()
    retain: bool = attr.ib()

class SillaMQTTClient:
    """Helper class to sue an external MQTT client."""

    def __init__(
        self,
        publish: Callable[[str, PublishPayloadType, int | None, bool | None], None],
        subscribe: Callable[[dict | None, dict], Awaitable[dict]],
        unsubscribe: Callable[[dict | None], Awaitable[dict]],
    ):
        """Initialize."""
        self._pending_messages: dict[PublishMessage, Timer] = {}
        self._publish = publish
        self._subscribe = subscribe
        self._unsubscribe = unsubscribe

    def publish(
        self,
        topic: str,
        payload: PublishPayloadType,
        qos: int | None = None,
        retain: bool | None = None,
    ) -> None:
        """Publish a message."""
        return self._publish(topic, payload, qos, retain)

    def publish_debounced(
        self,
        topic: str,
        payload: PublishPayloadType,
        qos: int | None = None,
        retain: bool | None = None,
    ) -> None:
        """Publish a message, with debounce."""
        msg = PublishMessage(topic, payload, qos, retain)

        def publish_callback() -> None:
            _LOGGER.debug("publish_debounced: publishing %s", msg)
            self._pending_messages.pop(msg)
            self.publish(msg.topic, msg.payload, qos=msg.qos, retain=msg.retain)

        if msg in self._pending_messages:
            timer = self._pending_messages.pop(msg)
            timer.cancel()
        timer = Timer(DEBOUNCE_TIMEOUT, publish_callback)
        self._pending_messages[msg] = timer

    async def subscribe(self, sub_state: dict | None, topics: dict) -> dict:
        """Subscribe to topics."""
        return await self._subscribe(sub_state, topics)

    async def unsubscribe(self, sub_state: dict | None) -> dict:
        """Unsubscribe from topics."""
        return await self._unsubscribe(sub_state)


def send_commands(
    mqtt_client: SillaMQTTClient,
    command_topic: str,
    commands: list[tuple[str, str | float]],
) -> None:
    """Send a sequence of commands."""
    backlog_topic = command_topic + COMMAND_BACKLOG
    backlog = ";".join(["NoDelay;%s %s" % command for command in commands])
    mqtt_client.publish(backlog_topic, backlog)