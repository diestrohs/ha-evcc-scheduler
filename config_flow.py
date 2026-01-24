
from homeassistant import config_entries
import voluptuous as vol

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_HOST,
    CONF_PORT,
    CONF_TOKEN,
    CONF_SSL,
    CONF_WEBSOCKET,
    CONF_WS_API,
    CONF_POLL_INTERVAL,
    DEFAULT_WEBSOCKET,
    DEFAULT_POLL_INTERVAL,
)

class EvccSchedulerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            # Verwende den vom User angegebenen Namen oder generiere einen aus Host:Port
            title = user_input.get(CONF_NAME)
            if not title:
                host = user_input.get(CONF_HOST, "EVCC")
                port = user_input.get(CONF_PORT, 7070)
                title = f"EVCC Scheduler ({host}:{port})"
            return self.async_create_entry(title=title, data=user_input)

        schema = vol.Schema({
            vol.Optional(CONF_NAME): str,
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=7070): int,
            vol.Optional(CONF_TOKEN): str,
            vol.Optional(CONF_SSL, default=False): bool,
            vol.Optional(CONF_WEBSOCKET, default=DEFAULT_WEBSOCKET): bool,
            vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL): int,
            vol.Optional(CONF_WS_API, default=False): bool,
        })

        return self.async_show_form(step_id="user", data_schema=schema)
