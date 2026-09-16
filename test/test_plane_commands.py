from typing import Literal

import conf
from main import create_plane_commands
from lib import (
    FJS_State,
    Sensors_State,
    V_TRIState,
    LVDTs_State,
)


def test_ailerons_control():
    fjs_state = FJS_State()
    sensors_state = Sensors_State()

    stick_tilt = 0.5
    target_ailerons_deg = int(stick_tilt * conf.Ailerons_Max_Deg)

    fjs_state.fjs_axes_state.side_stick_x = stick_tilt  # side_stick: right
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.ailerons_right_deg == target_ailerons_deg
    assert plane_commands.ailerons_left_deg == -target_ailerons_deg

    fjs_state.fjs_axes_state.side_stick_x = -stick_tilt  # side_stick: left
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.ailerons_right_deg == -target_ailerons_deg
    assert plane_commands.ailerons_left_deg == target_ailerons_deg

    fjs_state.fjs_axes_state.side_stick_x = 0.0  # side_stick: mid
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.ailerons_right_deg == 0
    assert plane_commands.ailerons_left_deg == 0


def test_elevators_control():
    fjs_state = FJS_State()
    sensors_state = Sensors_State()

    stick_tilt = 0.5
    target_elevators_deg = int(stick_tilt * conf.Elevators_Max_Deg)

    fjs_state.fjs_axes_state.side_stick_y = stick_tilt  # side_stick: pull
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.elevators_deg == target_elevators_deg

    fjs_state.fjs_axes_state.side_stick_y = -stick_tilt  # side_stick: push
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.elevators_deg == -target_elevators_deg

    fjs_state.fjs_axes_state.side_stick_y = 0.0  # side_stick: mid
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.elevators_deg == 0


def test_flaps_control():
    fjs_state = FJS_State()
    sensors_state = Sensors_State()

    lever_tilt = -0.2
    target_flaps_deg = 21

    fjs_state.fjs_axes_state.flaps_lever_primary = lever_tilt  # side_stick: pull
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.flaps_right_deg == target_flaps_deg
    assert plane_commands.flaps_left_deg == target_flaps_deg


def test_rudder_control():
    fjs_state = FJS_State()
    sensors_state = Sensors_State()

    rudder_twist = 0.5
    target_rudder_deg = int(rudder_twist * conf.Rudder_Max_Deg)

    fjs_state.fjs_axes_state.rudder_twist = rudder_twist  # rudder: right forward
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.rudder_deg == target_rudder_deg

    fjs_state.fjs_axes_state.rudder_twist = -rudder_twist  # rudder: left forward
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.rudder_deg == -target_rudder_deg

    fjs_state.fjs_axes_state.rudder_twist = 0.0  # rudder: mid
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.rudder_deg == 0


def test_landing_gear_control():
    fjs_state = FJS_State()
    sensors_state = Sensors_State()

    sensors_state.levers_state.landing_gear_lever = V_TRIState.DOWN
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.landing_gear_mid == V_TRIState.DOWN
    assert plane_commands.landing_gear_front == V_TRIState.DOWN

    sensors_state.levers_state.landing_gear_lever = V_TRIState.UP
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.landing_gear_mid == V_TRIState.UP
    assert plane_commands.landing_gear_front == V_TRIState.UP


def _sensors_state_flaps_full(_sensors_state: Sensors_State) -> Sensors_State:
    _sensors_state.lvdts_state.flaps_right_lvdt = LVDTs_State.LVDT_Max_16b
    _sensors_state.lvdts_state.flaps_left_lvdt = LVDTs_State.LVDT_Max_16b
    return _sensors_state


def _sensors_state_rolling(_sensors_state: Sensors_State, rolling_dir: Literal['RIGHT', 'LEFT']) -> Sensors_State:
    if rolling_dir == 'RIGHT':
        _sensors_state.lvdts_state.ailerons_right_lvdt = LVDTs_State.LVDT_Max_12b
        _sensors_state.lvdts_state.ailerons_left_lvdt = -LVDTs_State.LVDT_Max_12b
    elif rolling_dir == 'LEFT':
        _sensors_state.lvdts_state.ailerons_right_lvdt = -LVDTs_State.LVDT_Max_12b
        _sensors_state.lvdts_state.ailerons_left_lvdt = LVDTs_State.LVDT_Max_12b
    return _sensors_state


def _sensors_state_landing_gear_up(_sensors_state: Sensors_State) -> Sensors_State:
    _sensors_state.limit_switches_state.landing_gear_front_limit_switch_1 = True
    _sensors_state.limit_switches_state.landing_gear_front_limit_switch_2 = True
    _sensors_state.limit_switches_state.landing_gear_mid_right_limit_switch_1 = True
    _sensors_state.limit_switches_state.landing_gear_mid_right_limit_switch_2 = True
    _sensors_state.limit_switches_state.landing_gear_mid_left_limit_switch_1 = True
    _sensors_state.limit_switches_state.landing_gear_mid_left_limit_switch_2 = True
    return _sensors_state


def _sensors_state_landing_gear_down(_sensors_state: Sensors_State) -> Sensors_State:
    _sensors_state.limit_switches_state.landing_gear_front_limit_switch_1 = False
    _sensors_state.limit_switches_state.landing_gear_front_limit_switch_2 = False
    _sensors_state.limit_switches_state.landing_gear_mid_right_limit_switch_1 = False
    _sensors_state.limit_switches_state.landing_gear_mid_right_limit_switch_2 = False
    _sensors_state.limit_switches_state.landing_gear_mid_left_limit_switch_1 = False
    _sensors_state.limit_switches_state.landing_gear_mid_left_limit_switch_2 = False
    return _sensors_state


def test_spoilers_control():
    fjs_state = FJS_State()

    # spoilers: sensors_state.is_flaps_full()
    sensors_state = Sensors_State()
    sensors_state = _sensors_state_flaps_full(sensors_state)
    sensors_state.levers_state.spoilers_lever = V_TRIState.UP
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.spoiler_right_deg == 0
    assert plane_commands.spoiler_left_deg == 0

    # spoilers_lever: RET
    sensors_state = Sensors_State()
    sensors_state.levers_state.spoilers_lever = V_TRIState.DOWN
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.spoiler_right_deg == 0
    assert plane_commands.spoiler_left_deg == 0

    # spoilers: FULL, sensors_state.is_landing_gear_down()
    sensors_state = Sensors_State()
    sensors_state = _sensors_state_landing_gear_down(sensors_state)
    sensors_state.levers_state.spoilers_lever = V_TRIState.UP
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.spoiler_right_deg == 50
    assert plane_commands.spoiler_left_deg == 50

    # spoilers: FULL, sensors_state.is_cruise()
    sensors_state = Sensors_State()
    sensors_state = _sensors_state_landing_gear_up(sensors_state)
    sensors_state.levers_state.spoilers_lever = V_TRIState.UP
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.spoiler_right_deg == 40
    assert plane_commands.spoiler_left_deg == 40

    # spoilers: HALF, sensors_state.is_landing_gear_down()
    sensors_state = Sensors_State()
    sensors_state = _sensors_state_landing_gear_down(sensors_state)
    sensors_state.levers_state.spoilers_lever = V_TRIState.MID
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.spoiler_right_deg == 25
    assert plane_commands.spoiler_left_deg == 25

    # spoilers: HALF, sensors_state.is_cruise()
    sensors_state = Sensors_State()
    sensors_state = _sensors_state_landing_gear_up(sensors_state)
    sensors_state.levers_state.spoilers_lever = V_TRIState.MID
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.spoiler_right_deg == 20
    assert plane_commands.spoiler_left_deg == 20

    # spoilers: HALF, sensors_state.is_rolling('RIGHT')
    sensors_state = Sensors_State()
    sensors_state = _sensors_state_landing_gear_up(sensors_state)
    sensors_state = _sensors_state_rolling(sensors_state, 'RIGHT')
    sensors_state.levers_state.spoilers_lever = V_TRIState.MID
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.spoiler_right_deg == 18
    assert plane_commands.spoiler_left_deg == 0

    # spoilers: HALF, sensors_state.is_rolling('LEFT')
    sensors_state = Sensors_State()
    sensors_state = _sensors_state_landing_gear_up(sensors_state)
    sensors_state = _sensors_state_rolling(sensors_state, 'LEFT')
    sensors_state.levers_state.spoilers_lever = V_TRIState.MID
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.spoiler_right_deg == 0
    assert plane_commands.spoiler_left_deg == 18
