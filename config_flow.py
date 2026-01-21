
from homeassistant import config_entries
import voluptuous as vol

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_TOKEN,
    CONF_SSL,
    CONF_TIMEOUT,
    CONF_MODE,
    CONF_WS_API,
    MODE_POLLING,
    MODE_WEBSOCKET,
)

class EvccSchedulerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="EVCC Scheduler", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=7070): int,
            vol.Optional(CONF_TOKEN): str,
            vol.Optional(CONF_SSL, default=False): bool,
            vol.Optional(CONF_TIMEOUT, default=10): int,
            vol.Required(CONF_MODE, default=MODE_WEBSOCKET): vol.In([MODE_WEBSOCKET, MODE_POLLING]),
            vol.Optional(CONF_WS_API, default=False): bool,
        })

        return self.async_show_form(step_id="user", data_schema=schema)
