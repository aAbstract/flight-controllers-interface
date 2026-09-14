from main import create_plane_commands
from lib import (
    FJS_State,
    Sensors_State,
    V_TRIState,
    R_TRIState,
)


def test_ailerons_control():
    fjs_state = FJS_State()
    sensors_state = Sensors_State()

    fjs_state.fjs_axes_state.side_stick_x = 0.5  # side_stick: right
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.right_ailerons == V_TRIState.UP
    assert plane_commands.left_ailerons == V_TRIState.DOWN

    fjs_state.fjs_axes_state.side_stick_x = -0.5  # side_stick: left
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.right_ailerons == V_TRIState.DOWN
    assert plane_commands.left_ailerons == V_TRIState.UP

    fjs_state.fjs_axes_state.side_stick_x = 0.0  # side_stick: mid
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.right_ailerons == V_TRIState.MID
    assert plane_commands.left_ailerons == V_TRIState.MID


def test_elevators_control():
    fjs_state = FJS_State()
    sensors_state = Sensors_State()

    fjs_state.fjs_axes_state.side_stick_y = 0.5  # side_stick: pull
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.elevators == V_TRIState.UP

    fjs_state.fjs_axes_state.side_stick_y = -0.5  # side_stick: push
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.elevators == V_TRIState.DOWN

    fjs_state.fjs_axes_state.side_stick_y = 0.0  # side_stick: mid
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.elevators == V_TRIState.MID


def test_flaps_control():
    fjs_state = FJS_State()
    sensors_state = Sensors_State()

    veri_pairs = [
        (0.8, 0),   # flaps_lever: slat_1
        (0.4, 10),  # flaps_lever: slat_2
        (0.0, 15),  # flaps_lever: slat_3
        (-0.4, 20),  # flaps_lever: slat_4
        (-0.8, 35),  # flaps_lever: slat_5
    ]

    for f_pl, f_deg in veri_pairs:
        fjs_state.fjs_axes_state.flaps_lever_primary = f_pl
        plane_commands = create_plane_commands(fjs_state, sensors_state)
        assert plane_commands.flaps_deg == f_deg


def test_rudder_control():
    fjs_state = FJS_State()
    sensors_state = Sensors_State()

    fjs_state.fjs_axes_state.rudder_twist = 0.5  # rudder: right forward
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.rudder == R_TRIState.CCW

    fjs_state.fjs_axes_state.rudder_twist = -0.5  # rudder: left forward
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.rudder == R_TRIState.CW

    fjs_state.fjs_axes_state.rudder_twist = 0.0  # rudder: mid
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.rudder == R_TRIState.MID


def test_landing_gear_control():
    fjs_state = FJS_State()
    sensors_state = Sensors_State()

    sensors_state.levers_state.landing_gear_lever = V_TRIState.DOWN
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.landing_gear == V_TRIState.DOWN

    sensors_state.levers_state.landing_gear_lever = V_TRIState.UP
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.landing_gear == V_TRIState.UP


def test_spoilers_control():
    fjs_state = FJS_State()
    sensors_state = Sensors_State()

    # spoilers: RET
    sensors_state.levers_state.spoilers_lever = V_TRIState.DOWN
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.left_spoiler_deg == 0
    assert plane_commands.right_spoiler_deg == 0

    # spoilers: RET - flaps: FULL
    fjs_state.fjs_axes_state.flaps_lever_primary = -0.8  # flaps: FULL
    sensors_state.levers_state.spoilers_lever = V_TRIState.UP
    sensors_state.levers_state.landing_gear_lever = V_TRIState.DOWN
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.left_spoiler_deg == 0
    assert plane_commands.right_spoiler_deg == 0

    # spoilers: FULL - ground
    fjs_state.fjs_axes_state.flaps_lever_primary = 0.8  # flaps: RET
    sensors_state.levers_state.spoilers_lever = V_TRIState.UP
    sensors_state.levers_state.landing_gear_lever = V_TRIState.DOWN
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.left_spoiler_deg == 50
    assert plane_commands.right_spoiler_deg == 50

    # spoilers: FULL - cruise
    fjs_state.fjs_axes_state.flaps_lever_primary = 0.8  # flaps: RET
    sensors_state.levers_state.spoilers_lever = V_TRIState.UP
    sensors_state.levers_state.landing_gear_lever = V_TRIState.UP
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.left_spoiler_deg == 40
    assert plane_commands.right_spoiler_deg == 40

    # spoilers: HALF - landing
    fjs_state.fjs_axes_state.flaps_lever_primary = 0.8  # flaps: RET
    sensors_state.levers_state.spoilers_lever = V_TRIState.MID
    sensors_state.levers_state.landing_gear_lever = V_TRIState.DOWN
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.left_spoiler_deg == 25
    assert plane_commands.right_spoiler_deg == 25

    # spoilers: HALF - cruise
    fjs_state.fjs_axes_state.flaps_lever_primary = 0.8  # flaps: RET
    sensors_state.levers_state.spoilers_lever = V_TRIState.MID
    sensors_state.levers_state.landing_gear_lever = V_TRIState.UP
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.left_spoiler_deg == 20
    assert plane_commands.right_spoiler_deg == 20

    # spoilers: HALF - cruise - rolling right
    fjs_state.fjs_axes_state.flaps_lever_primary = 0.8  # flaps: RET
    fjs_state.fjs_axes_state.side_stick_x = 0.5  # rolling: right
    sensors_state.levers_state.spoilers_lever = V_TRIState.MID
    sensors_state.levers_state.landing_gear_lever = V_TRIState.UP
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.left_spoiler_deg == 0
    assert plane_commands.right_spoiler_deg == 18

    # spoilers: HALF - cruise - rolling left
    fjs_state.fjs_axes_state.flaps_lever_primary = 0.8  # flaps: RET
    fjs_state.fjs_axes_state.side_stick_x = -0.5  # rolling: left
    sensors_state.levers_state.spoilers_lever = V_TRIState.MID
    sensors_state.levers_state.landing_gear_lever = V_TRIState.UP
    plane_commands = create_plane_commands(fjs_state, sensors_state)
    assert plane_commands.left_spoiler_deg == 18
    assert plane_commands.right_spoiler_deg == 0
