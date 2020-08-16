"""Test the NZBGet config flow."""
from pynzbgetapi import NZBGetAPIException

from homeassistant import setup
from homeassistant.components.nzbget.const import DOMAIN
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import RESULT_TYPE_ABORT, RESULT_TYPE_CREATE_ENTRY, RESULT_TYPE_FORM
from homeassistant.setup import async_setup_component

from tests.async_mock import patch
from tests.common import MockConfigEntry

from . import MOCK_STATUS, MOCK_VERSION

CONFIG = {CONF_HOST: "10.10.10.30"}


async def test_form(hass):
    """Test we get the user initiated form."""
    await async_setup_component(hass, "persistent_notification", {})

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] == RESULT_TYPE_FORM
    assert result["errors"] == {}

    with _patch_version(), _patch_status(), _patch_async_setup() as mock_setup, _patch_async_setup_entry() as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], CONFIG,
        )

        assert result2["type"] == RESULT_TYPE_CREATE_ENTRY
        assert result2["title"] == "10.10.10.30"
        assert result2["data"] == CONFIG

        await hass.async_block_till_done()
        assert len(mock_setup.mock_calls) == 1
        assert len(mock_setup_entry.mock_calls) == 1


async def test_user_form_cannot_connect(hass):
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    with patch(
        "homeassistant.components.nzbget.NZBGetAPI.status",
        side_effect=NZBGetAPIException(),
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_HOST: "10.10.10.30"},
        )

    assert result2["type"] == RESULT_TYPE_FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_user_form_unexpected_exception(hass):
    """Test we handle unexpected exception."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "homeassistant.components.nzbget.NZBGetAPI.version",
        side_effect=Exception(),
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_HOST: "10.10.10.30"},
        )

    assert result2["type"] == RESULT_TYPE_FORM
    assert result2["errors"] == {"base": "unknown"}


async def test_user_form_duplicate(hass):
    """Test duplicate entries."""
    with _patch_version(), _patch_status():
        unique_id = "10.10.10.30:6789"
        entry = MockConfigEntry(domain=DOMAIN, unique_id=unique_id)
        await hass.config_entries.async_add(entry)

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}, data=CONFIG,
        )
        assert result["type"] == RESULT_TYPE_ABORT
        assert result["reason"] == "already_configured"


def _patch_async_setup():
    return patch("homeassistant.components.nzbget.async_setup", return_value=True)


def _patch_async_setup_entry():
    return patch(
        "homeassistant.components.nzbget.async_setup_entry", return_value=True,
    )


def _patch_status():
    return patch(
        "homeassistant.components.nzbget.NZBGetAPI.status",
        return_value=MOCK_STATUS,
    )


def _patch_version():
    return patch(
        "homeassistant.components.nzbget.NZBGetAPI.version",
        return_value=MOCK_VERSION,
    )
