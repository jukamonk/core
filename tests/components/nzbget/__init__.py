"""Tests for the NZBGet integration."""
from homeassistant.components.nzbget.const import DOMAIN
from homeassistant.const import CONF_HOST

from tests.async_mock import patch
from tests.common import MockConfigEntry

MOCK_VERSION = "21.0"

MOCK_STATUS = {
    "ArticleCacheMB": "",
    "AverageDownloadRate": "",
    "DownloadPaused": "",
    "DownloadRate": "",
    "DownloadedSizeMB": "",
    "FreeDiskSpaceMB": "",
    "PostJobCount": "",
    "PostPaused": "",
    "RemainingSizeMB": "",
    "UpTimeSec": "",
}

MOCK_HISTORY = {}


async def init_integration(
    hass,
    *,
    status: dict = MOCK_STATUS,
    history: dict = MOCK_HISTORY,
    version: str = MOCK_VERSION,
) -> MockConfigEntry:
    """Set up the NZBGet integration in Home Assistant."""
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_HOST: "10.10.10.30"},)

    with patch(
        "homeassistant.components.nzbget.NZBGetAPI.version",
        return_value=version,
    ), patch(
        "homeassistant.components.nzbget.NZBGetAPI.status",
        return_value=status,
    ), patch(
        "homeassistant.components.nzbget.NZBGetAPI.history",
        return_value=history,
    ):
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    return entry
