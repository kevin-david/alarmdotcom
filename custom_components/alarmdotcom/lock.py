"""Interfaces with Alarm.com alarm control panels."""
import logging
import re


import homeassistant.components.lock as lock

try:
    from homeassistant.components.lock import LockEntity
except ImportError:
    from homeassistant.components.lock import (
        Lock as LockEntity,
    )

from homeassistant.components.lock import PLATFORM_SCHEMA

from homeassistant.const import (
    STATE_JAMMED,
    STATE_LOCKED,
    STATE_LOCKING,
    STATE_UNLOCKED,
    STATE_UNLOCKING,
    STATE_UNKNOWN
)
_LOGGER = logging.getLogger(__name__)

class AlarmDotComLock(LockEntity):
    """Representation of an Alarm.com status."""

    def __init__(
        self,
        lock_id,
        name,
        code,
        alarm_com
    ):
        self._lock_id = lock_id
        self._name = name
        self._code = code if code else None
        self._alarmdotcom = alarm_com

    async def async_update(self):
        """Fetch the latest state."""
        await self._alarmdotcom.async_update("lock")
        return self._alarmdotcom.state

    @property
    def name(self):
        """Return the name of the alarm."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._lock_id

    @property
    def code_format(self):
        """Return one or more digits/characters."""
        if self._code is None:
            return None
        if isinstance(self._code, str) and re.search("^\\d+$", self._code):
            return "number"
        return "text"

    @property
    def state(self):
        """Return the state of the device."""
        if self._alarmdotcom.state[self._lock_id].lower() == "unlocked":
            return STATE_UNLOCKED
        if self._alarmdotcom.state[self._lock_id].lower() == "locked":
            return STATE_LOCKED
        return STATE_UNKNOWN

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {"sensor_status": self._alarmdotcom.sensor_status}

    async def async_lock(self, code=None):
        """Send lock command."""
        if self._validate_code(code):
            await self._alarmdotcom.async_lock()

    async def async_unlock(self, code=None):
        """Send unlock command."""
        if self._validate_code(code):
            await self._alarmdotcom.async_unlock()

    def _validate_code(self, code):
        """Validate given code."""
        check = self._code is None or code == self._code
        if not check:
            _LOGGER.warning("Wrong code entered")
        return check
