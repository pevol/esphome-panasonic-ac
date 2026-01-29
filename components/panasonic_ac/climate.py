from esphome.const import (
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_DURATION,
    STATE_CLASS_MEASUREMENT,
    UNIT_CELSIUS,
    UNIT_WATT,
    UNIT_SECOND,
)
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import uart, climate, sensor, select, switch, binary_sensor

AUTO_LOAD = ["switch", "sensor", "select", "binary_sensor"]
DEPENDENCIES = ["uart"]

panasonic_ac_ns = cg.esphome_ns.namespace("panasonic_ac")
PanasonicAC = panasonic_ac_ns.class_(
    "PanasonicAC", cg.Component, uart.UARTDevice, climate.Climate
)
panasonic_ac_cnt_ns = panasonic_ac_ns.namespace("CNT")
PanasonicACCNT = panasonic_ac_cnt_ns.class_("PanasonicACCNT", PanasonicAC)
panasonic_ac_wlan_ns = panasonic_ac_ns.namespace("WLAN")
PanasonicACWLAN = panasonic_ac_wlan_ns.class_("PanasonicACWLAN", PanasonicAC)

PanasonicACSwitch = panasonic_ac_ns.class_(
    "PanasonicACSwitch", switch.Switch, cg.Component
)
PanasonicACSelect = panasonic_ac_ns.class_(
    "PanasonicACSelect", select.Select, cg.Component
)


CONF_HORIZONTAL_SWING_SELECT = "horizontal_swing_select"
CONF_VERTICAL_SWING_SELECT = "vertical_swing_select"
CONF_OUTSIDE_TEMPERATURE = "outside_temperature"
CONF_OUTSIDE_TEMPERATURE_OFFSET = "outside_temperature_offset"
CONF_CURRENT_TEMPERATURE_SENSOR = "current_temperature_sensor"
CONF_CURRENT_TEMPERATURE_OFFSET = "current_temperature_offset"
CONF_NANOEX_SWITCH = "nanoex_switch"
CONF_ECO_SWITCH = "eco_switch"
CONF_ECONAVI_SWITCH = "econavi_switch"
CONF_MILD_DRY_SWITCH = "mild_dry_switch"
CONF_CURRENT_POWER_CONSUMPTION = "current_power_consumption"
CONF_WLAN = "wlan"
CONF_CNT = "cnt"

# Cycling detection configuration keys
CONF_CYCLING_DETECTED = "cycling_detected"
CONF_CYCLE_COUNT = "cycle_count"
CONF_AVG_ON_DURATION = "avg_on_duration"
CONF_AVG_OFF_DURATION = "avg_off_duration"
CONF_CYCLING_POWER_ON_THRESHOLD = "cycling_power_on_threshold"
CONF_CYCLING_POWER_OFF_THRESHOLD = "cycling_power_off_threshold"
CONF_CYCLING_MIN_ON_DURATION = "cycling_min_on_duration"
CONF_CYCLING_MIN_OFF_DURATION = "cycling_min_off_duration"
CONF_CYCLING_TIME_WINDOW = "cycling_time_window"
CONF_CYCLING_CYCLE_THRESHOLD = "cycling_cycle_threshold"

HORIZONTAL_SWING_OPTIONS = ["auto", "left", "left_center", "center", "right_center", "right"]

VERTICAL_SWING_OPTIONS = ["swing", "auto", "up", "up_center", "center", "down_center", "down"]

SWITCH_SCHEMA = switch.switch_schema(PanasonicACSwitch).extend(cv.COMPONENT_SCHEMA)

SELECT_SCHEMA = select.select_schema(PanasonicACSelect)

PANASONIC_COMMON_SCHEMA = {
    cv.Optional(CONF_HORIZONTAL_SWING_SELECT): SELECT_SCHEMA,
    cv.Optional(CONF_VERTICAL_SWING_SELECT): SELECT_SCHEMA,
    cv.Optional(CONF_OUTSIDE_TEMPERATURE): sensor.sensor_schema(
        unit_of_measurement=UNIT_CELSIUS,
        accuracy_decimals=0,
        device_class=DEVICE_CLASS_TEMPERATURE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    cv.Optional(CONF_NANOEX_SWITCH): SWITCH_SCHEMA,
    cv.Optional(CONF_OUTSIDE_TEMPERATURE_OFFSET): cv.int_range(min=-15, max=15),
}

PANASONIC_CNT_SCHEMA = {
    cv.Optional(CONF_ECO_SWITCH): SWITCH_SCHEMA,
    cv.Optional(CONF_ECONAVI_SWITCH): SWITCH_SCHEMA,
    cv.Optional(CONF_MILD_DRY_SWITCH): SWITCH_SCHEMA,
    cv.Optional(CONF_CURRENT_TEMPERATURE_SENSOR): cv.use_id(sensor.Sensor),
    cv.Optional(CONF_CURRENT_TEMPERATURE_OFFSET): cv.int_range(min=-15, max=15),
    cv.Optional(CONF_CURRENT_POWER_CONSUMPTION): sensor.sensor_schema(
        unit_of_measurement=UNIT_WATT,
        accuracy_decimals=0,
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    # Cycling detection sensors
    cv.Optional(CONF_CYCLING_DETECTED): binary_sensor.binary_sensor_schema(),
    cv.Optional(CONF_CYCLE_COUNT): sensor.sensor_schema(
        accuracy_decimals=0,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    cv.Optional(CONF_AVG_ON_DURATION): sensor.sensor_schema(
        unit_of_measurement=UNIT_SECOND,
        accuracy_decimals=0,
        device_class=DEVICE_CLASS_DURATION,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    cv.Optional(CONF_AVG_OFF_DURATION): sensor.sensor_schema(
        unit_of_measurement=UNIT_SECOND,
        accuracy_decimals=0,
        device_class=DEVICE_CLASS_DURATION,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    # Cycling detection thresholds
    cv.Optional(CONF_CYCLING_POWER_ON_THRESHOLD, default=200): cv.int_range(min=0, max=10000),
    cv.Optional(CONF_CYCLING_POWER_OFF_THRESHOLD, default=100): cv.int_range(min=0, max=10000),
    cv.Optional(CONF_CYCLING_MIN_ON_DURATION, default=30): cv.int_range(min=1, max=3600),
    cv.Optional(CONF_CYCLING_MIN_OFF_DURATION, default=30): cv.int_range(min=1, max=3600),
    cv.Optional(CONF_CYCLING_TIME_WINDOW, default=600): cv.int_range(min=60, max=7200),
    cv.Optional(CONF_CYCLING_CYCLE_THRESHOLD, default=3): cv.int_range(min=1, max=20),
}

CONFIG_SCHEMA = cv.typed_schema(
    {
        CONF_WLAN: climate.climate_schema(PanasonicACWLAN).extend(PANASONIC_COMMON_SCHEMA).extend(uart.UART_DEVICE_SCHEMA),
        CONF_CNT: climate.climate_schema(PanasonicACCNT).extend(PANASONIC_COMMON_SCHEMA).extend(PANASONIC_CNT_SCHEMA).extend(uart.UART_DEVICE_SCHEMA),
    }
)


async def to_code(config):
    var = await climate.new_climate(config)
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)

    if CONF_HORIZONTAL_SWING_SELECT in config:
        conf = config[CONF_HORIZONTAL_SWING_SELECT]
        swing_select = await select.new_select(conf, options=HORIZONTAL_SWING_OPTIONS)
        await cg.register_component(swing_select, conf)
        cg.add(var.set_horizontal_swing_select(swing_select))

    if CONF_VERTICAL_SWING_SELECT in config:
        conf = config[CONF_VERTICAL_SWING_SELECT]
        swing_select = await select.new_select(conf, options=VERTICAL_SWING_OPTIONS)
        await cg.register_component(swing_select, conf)
        cg.add(var.set_vertical_swing_select(swing_select))

    if CONF_OUTSIDE_TEMPERATURE in config:
        sens = await sensor.new_sensor(config[CONF_OUTSIDE_TEMPERATURE])
        cg.add(var.set_outside_temperature_sensor(sens))

    if CONF_OUTSIDE_TEMPERATURE_OFFSET in config:
        cg.add(var.set_outside_temperature_offset(config[CONF_OUTSIDE_TEMPERATURE_OFFSET]))

    for s in [CONF_ECO_SWITCH, CONF_NANOEX_SWITCH, CONF_MILD_DRY_SWITCH, CONF_ECONAVI_SWITCH]:
        if s in config:
            conf = config[s]
            a_switch = await switch.new_switch(conf)
            await cg.register_component(a_switch, conf)
            cg.add(getattr(var, f"set_{s}")(a_switch))

    if CONF_CURRENT_TEMPERATURE_SENSOR in config:
        sens = await cg.get_variable(config[CONF_CURRENT_TEMPERATURE_SENSOR])
        cg.add(var.set_current_temperature_sensor(sens))

    if CONF_CURRENT_TEMPERATURE_OFFSET in config:
        cg.add(var.set_current_temperature_offset(config[CONF_CURRENT_TEMPERATURE_OFFSET]))

    if CONF_CURRENT_POWER_CONSUMPTION in config:
        sens = await sensor.new_sensor(config[CONF_CURRENT_POWER_CONSUMPTION])
        cg.add(var.set_current_power_consumption_sensor(sens))

    # Cycling detection sensors
    if CONF_CYCLING_DETECTED in config:
        sens = await binary_sensor.new_binary_sensor(config[CONF_CYCLING_DETECTED])
        cg.add(var.set_cycling_detected_binary_sensor(sens))

    if CONF_CYCLE_COUNT in config:
        sens = await sensor.new_sensor(config[CONF_CYCLE_COUNT])
        cg.add(var.set_cycle_count_sensor(sens))

    if CONF_AVG_ON_DURATION in config:
        sens = await sensor.new_sensor(config[CONF_AVG_ON_DURATION])
        cg.add(var.set_avg_on_duration_sensor(sens))

    if CONF_AVG_OFF_DURATION in config:
        sens = await sensor.new_sensor(config[CONF_AVG_OFF_DURATION])
        cg.add(var.set_avg_off_duration_sensor(sens))

    # Cycling detection thresholds (always set for CNT type)
    if config.get("type") == CONF_CNT:
        cg.add(var.set_cycling_power_on_threshold(config[CONF_CYCLING_POWER_ON_THRESHOLD]))
        cg.add(var.set_cycling_power_off_threshold(config[CONF_CYCLING_POWER_OFF_THRESHOLD]))
        cg.add(var.set_cycling_min_on_duration(config[CONF_CYCLING_MIN_ON_DURATION]))
        cg.add(var.set_cycling_min_off_duration(config[CONF_CYCLING_MIN_OFF_DURATION]))
        cg.add(var.set_cycling_time_window(config[CONF_CYCLING_TIME_WINDOW]))
        cg.add(var.set_cycling_cycle_threshold(config[CONF_CYCLING_CYCLE_THRESHOLD]))
