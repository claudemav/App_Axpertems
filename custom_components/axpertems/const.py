"""Constantes AxpertEMS."""

DOMAIN = "axpertems"

CONF_PORT = "port"
CONF_BAUDRATE = "baudrate"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_BAUDRATE = 2400
DEFAULT_SCAN_INTERVAL = 30  # secondes

CONF_SOC_THRESHOLD = "battery_soc_threshold"
CONF_BATTERY_CRITICAL_THRESHOLD = "battery_critical_threshold"
CONF_DEFICIT_DELAY_ON = "deficit_delay_on_minutes"
CONF_DEFICIT_DELAY_OFF = "deficit_delay_off_minutes"
CONF_NIGHT_START = "night_start"

DEFAULT_OPTIONS: dict = {
    CONF_SOC_THRESHOLD: 35,
    CONF_BATTERY_CRITICAL_THRESHOLD: 20,
    CONF_DEFICIT_DELAY_ON: 10,
    CONF_DEFICIT_DELAY_OFF: 5,
    CONF_NIGHT_START: "23:00",
}