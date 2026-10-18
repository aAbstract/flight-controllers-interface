import sys
import time
import pygame

import conf
from lib import (
    FJS_State,
    FJS_Buttons_State,
    FJS_Axes_State,
    FJS_Hats_State,

    Sensors_State,
    Valves_State,

    Plane_MDBus_Device,
    Plane_Commands,

    V_TRIState,

    Log,
    Clock,
)


def calibrate_controls(fjs_device: pygame.joystick.JoystickType):
    def read_axes_set() -> set[float]:
        pygame.event.pump()
        axes_cnt = fjs_device.get_numaxes()
        axes_set = set([fjs_device.get_axis(x) for x in range(axes_cnt)])
        return axes_set

    while read_axes_set() == {-1}:
        Log.elog('Flight JoyStick Device is not Calibrated, Move Side Stick to Calibrate')
        time.sleep(1)
    Log.ilog('Flight JoyStick Device Calibrated')


def fjs_connect():
    if pygame.joystick.get_count() == 0 and not conf.Flight_Controllers_Emulation:
        Log.elog('No Flight JoyStick Device Detected')
        sys.exit(1)

    if not conf.Flight_Controllers_Emulation:
        fjs_device = pygame.joystick.Joystick(0)
        fjs_device.init()
        calibrate_controls(fjs_device)
        return fjs_device
    else:
        Log.ilog('Starting Flight JoyStick Device Emulation')
        return None


def capture_controls(fjs_device: pygame.joystick.JoystickType) -> FJS_State:
    if conf.Flight_Controllers_Emulation:
        return FJS_State(
            timestamp_ms=Clock.get_time_ms(),
            fjs_buttons_state=FJS_Buttons_State(),
            fjs_axes_state=FJS_Axes_State(),
            fjs_hats_state=FJS_Hats_State(),
        )

    fjs_state = {
        'timestamp_ms': Clock.get_time_ms(),
        'fjs_buttons_state': {},
        'fjs_axes_state': {},
        'fjs_hats_state': {},
    }
    pygame.event.pump()

    for btn_idx in range(fjs_device.get_numbuttons()):
        btn_name = FJS_Buttons_State.Buttons_Idx_Map.get(btn_idx)
        if not btn_name:
            continue
        fjs_state['fjs_buttons_state'][btn_name] = bool(fjs_device.get_button(btn_idx))

    for axis_idx in range(fjs_device.get_numaxes()):
        axis_name = FJS_Axes_State.Axes_Idx_Map.get(axis_idx)
        if not axis_name:
            continue
        fjs_state['fjs_axes_state'][axis_name] = fjs_device.get_axis(axis_idx)

    for hat_idx in range(fjs_device.get_numhats()):
        hat_name = FJS_Hats_State.Hats_Idx_Map.get(hat_idx)
        if not hat_name:
            continue
        fjs_state['fjs_hats_state'][hat_name] = fjs_device.get_hat(hat_idx)

    return FJS_State(
        timestamp_ms=fjs_state['timestamp_ms'],
        fjs_buttons_state=FJS_Buttons_State(**fjs_state['fjs_buttons_state']),
        fjs_axes_state=FJS_Axes_State(**fjs_state['fjs_axes_state']),
        fjs_hats_state=FJS_Hats_State(**fjs_state['fjs_hats_state']),
    )


def capture_sensors(plane_mdbus_device: Plane_MDBus_Device) -> Sensors_State:
    lvdts_state = plane_mdbus_device.load_lvdts()
    if not lvdts_state:
        return None

    limit_switches_state = plane_mdbus_device.load_limit_switches()
    if not limit_switches_state:
        return None

    # valves_state = plane_mdbus_device.load_valves()
    # if not valves_state:
    #     return None

    levers_state = plane_mdbus_device.load_levers()
    if not levers_state:
        return None

    return Sensors_State(
        timestamp_ms=Clock.get_time_ms(),
        lvdts_state=lvdts_state,
        limit_switches_state=limit_switches_state,
        # valves_state=valves_state,
        levers_state=levers_state,
    )


def create_plane_commands(fjs_state: FJS_State, sensors_state: Sensors_State) -> Plane_Commands:
    plane_commands = Plane_Commands()

    # ailerons commands
    side_stick_x_norm = fjs_state.fjs_axes_state.side_stick_x  # [-1, 1]
    if side_stick_x_norm > -conf.Axis_Thresh and side_stick_x_norm < conf.Axis_Thresh:  # side stick: center
        plane_commands.ailerons_right_deg = 0
        plane_commands.ailerons_left_deg = 0
    else:
        ailerons_deg = side_stick_x_norm * conf.Ailerons_Max_Deg
        plane_commands.ailerons_right_deg = int(ailerons_deg)
        plane_commands.ailerons_left_deg = int(-ailerons_deg)

    # elevators commands
    side_stick_y_norm = fjs_state.fjs_axes_state.side_stick_y  # [-1, 1]
    if side_stick_y_norm > -conf.Axis_Thresh and side_stick_y_norm < conf.Axis_Thresh:  # side stick: center
        plane_commands.elevators_deg = 0
    else:
        elevators_deg = side_stick_y_norm * conf.Elevators_Max_Deg
        plane_commands.elevators_deg = int(elevators_deg)

    # flaps commands
    flaps_lever_primary_norm = fjs_state.fjs_axes_state.flaps_lever_primary  # [-1, 1]
    # flaps_lever_primary_norm = (fjs_state.fjs_axes_state.flaps_lever_primary * -1 + 1) / 2  # [0, 1]
    if flaps_lever_primary_norm > -conf.Axis_Thresh and flaps_lever_primary_norm < conf.Axis_Thresh:  # flaps_lever_primary: forward
        plane_commands.set_flaps(0)
    else:
        flaps_deg = flaps_lever_primary_norm * conf.Flaps_Max_Deg
        plane_commands.set_flaps(int(flaps_deg))

    # rudder commands
    rudder_twist_norm = fjs_state.fjs_axes_state.rudder_twist  # [-1, 1]
    if rudder_twist_norm > -conf.Axis_Thresh and rudder_twist_norm < conf.Axis_Thresh:  # rudder: center
        plane_commands.rudder_deg = 0
    else:
        rudder_deg = rudder_twist_norm * conf.Rudder_Max_Deg
        plane_commands.rudder_deg = int(rudder_deg)

    # landing gear commands
    plane_commands.landing_gear = sensors_state.levers_state.landing_gear_lever

    # spoilers commands
    # if sensors_state.is_flaps_full():
    #     plane_commands.set_spoilers(0)

    if sensors_state.levers_state.spoilers_lever == V_TRIState.DOWN:  # spoilers_lever: RET
        plane_commands.set_spoilers(0)

    elif sensors_state.levers_state.spoilers_lever == V_TRIState.UP:  # spoilers_lever: FULL
        plane_commands.set_spoilers(50)
        # if sensors_state.is_lxanding_gear_down():
        #     plane_commands.set_spoilers(50)
        # elif sensors_state.is_cruise() and sensors_state.is_lxanding_gear_up():  # cruise
        #     plane_commands.set_spoilers(40)

    elif sensors_state.levers_state.spoilers_lever == V_TRIState.MID:  # spoilers_lever: HALF
        plane_commands.set_spoilers(25)
        # if sensors_state.is_lxanding_gear_down():  # landing
        #     plane_commands.set_spoilers(25)
        # elif sensors_state.is_cruise():  # cruise
        #     plane_commands.set_spoilers(20)
        # elif sensors_state.is_rolling('RIGHT') or sensors_state.is_rolling('LEFT'):  # rolling
        #     if sensors_state.is_rolling('RIGHT'):  # left wing up
        #         plane_commands.spoiler_right_deg = 18
        #         plane_commands.spoiler_left_deg = 0
        #     elif sensors_state.is_rolling('LEFT'):  # right_wing: up
        #         plane_commands.spoiler_right_deg = 0
        #         plane_commands.spoiler_left_deg = 18

    # print(fjs_state.fjs_axes_state.to_json_str())
    # print(sensors_state.lvdts_state.to_json_str())
    # print(plane_commands.to_json_str())

    return plane_commands


def plane_control_loop(plane_commands: Plane_Commands, sensors_state: Sensors_State) -> Valves_State:
    valves_state = Valves_State()

    # ailerons control loop
    if plane_commands.ailerons_right_deg > -(conf.Ailerons_Max_Deg // 2) and plane_commands.ailerons_right_deg < (conf.Ailerons_Max_Deg // 2):
        valves_state.ailerons_right_valve = V_TRIState.MID
    elif plane_commands.ailerons_right_deg > (conf.Ailerons_Max_Deg // 2) and sensors_state.lvdts_state.ailerons_right_norm > conf.LVDT_Norm_Low_Thresh:
        valves_state.ailerons_right_valve = V_TRIState.UP
    elif plane_commands.ailerons_right_deg < -(conf.Ailerons_Max_Deg // 2) and sensors_state.lvdts_state.ailerons_right_norm < conf.LVDT_Norm_High_Thresh:
        valves_state.ailerons_right_valve = V_TRIState.DOWN
    else:
        valves_state.ailerons_right_valve = V_TRIState.MID
    if plane_commands.ailerons_left_deg > -(conf.Ailerons_Max_Deg // 2) and plane_commands.ailerons_left_deg < (conf.Ailerons_Max_Deg // 2):
        valves_state.ailerons_left_valve = V_TRIState.MID
    elif plane_commands.ailerons_left_deg > (conf.Ailerons_Max_Deg // 2) and sensors_state.lvdts_state.ailerons_left_norm > conf.LVDT_Norm_Low_Thresh:
        valves_state.ailerons_left_valve = V_TRIState.UP
    elif plane_commands.ailerons_left_deg < -(conf.Ailerons_Max_Deg // 2) and sensors_state.lvdts_state.ailerons_left_norm < conf.LVDT_Norm_High_Thresh:
        valves_state.ailerons_left_valve = V_TRIState.DOWN
    else:
        valves_state.ailerons_left_valve = V_TRIState.MID

    # elevators control loop
    if plane_commands.elevators_deg > -(conf.Elevators_Max_Deg // 2) and plane_commands.elevators_deg < (conf.Elevators_Max_Deg // 2):
        valves_state.elevators_valve = V_TRIState.MID
    elif plane_commands.elevators_deg > (conf.Elevators_Max_Deg // 2) and sensors_state.lvdts_state.elevators_norm > conf.LVDT_Norm_Low_Thresh:
        valves_state.elevators_valve = V_TRIState.DOWN
    elif plane_commands.elevators_deg < -(conf.Elevators_Max_Deg // 2) and sensors_state.lvdts_state.elevators_norm < conf.LVDT_Norm_High_Thresh:
        valves_state.elevators_valve = V_TRIState.UP
    else:
        valves_state.elevators_valve = V_TRIState.MID

    # flaps control loop
    if plane_commands.flaps_right_deg > -(conf.Flaps_Max_Deg // 2) and plane_commands.flaps_right_deg < (conf.Flaps_Max_Deg // 2):
        valves_state.flaps_right_valve = V_TRIState.MID
    elif plane_commands.flaps_right_deg > (conf.Flaps_Max_Deg // 2) and sensors_state.lvdts_state.flaps_right_norm < conf.LVDT_Norm_High_Thresh:
        valves_state.flaps_right_valve = V_TRIState.DOWN
    elif plane_commands.flaps_right_deg < -(conf.Flaps_Max_Deg // 2) and sensors_state.lvdts_state.flaps_right_norm > conf.LVDT_Norm_Low_Thresh:
        valves_state.flaps_right_valve = V_TRIState.UP
    else:
        valves_state.flaps_right_valve = V_TRIState.MID
    if plane_commands.flaps_left_deg > -(conf.Flaps_Max_Deg // 2) and plane_commands.flaps_left_deg < (conf.Flaps_Max_Deg // 2):
        valves_state.flaps_left_valve = V_TRIState.MID
    elif plane_commands.flaps_left_deg > (conf.Flaps_Max_Deg // 2) and sensors_state.lvdts_state.flaps_left_norm < conf.LVDT_Norm_High_Thresh:
        valves_state.flaps_left_valve = V_TRIState.DOWN
    elif plane_commands.flaps_left_deg < -(conf.Flaps_Max_Deg // 2) and sensors_state.lvdts_state.flaps_left_norm > conf.LVDT_Norm_Low_Thresh:
        valves_state.flaps_left_valve = V_TRIState.UP
    else:
        valves_state.flaps_left_valve = V_TRIState.MID

    # rudder control loop
    if plane_commands.rudder_deg > -(conf.Rudder_Max_Deg // 2) and plane_commands.rudder_deg < (conf.Rudder_Max_Deg // 2):
        valves_state.rudder_valve = V_TRIState.MID
    elif plane_commands.rudder_deg > (conf.Rudder_Max_Deg // 2) and sensors_state.lvdts_state.rudder_norm > conf.LVDT_Norm_Low_Thresh:
        valves_state.rudder_valve = V_TRIState.UP
    elif plane_commands.rudder_deg < -(conf.Rudder_Max_Deg // 2) and sensors_state.lvdts_state.rudder_norm < conf.LVDT_Norm_High_Thresh:
        valves_state.rudder_valve = V_TRIState.DOWN
    else:
        valves_state.rudder_valve = V_TRIState.MID

    # landing gear control loop
    # valves_state.landing_gear_gates = plane_commands.landing_gear
    valves_state.landing_gear_wheels = plane_commands.landing_gear

    # spoilers control loop
    if plane_commands.spoiler_right_deg == 0 and sensors_state.lvdts_state.spoilers_right_norm > conf.LVDT_Norm_Low_Thresh:
        valves_state.spoilers_right_valve = V_TRIState.DOWN
    elif plane_commands.spoiler_right_deg >= 40 and sensors_state.lvdts_state.spoilers_right_norm < conf.LVDT_Norm_High_Thresh:
        valves_state.spoilers_right_valve = V_TRIState.UP
    elif plane_commands.spoiler_right_deg in [20, 25]:
        valves_state.spoilers_right_valve = V_TRIState.MID
    else:
        valves_state.spoilers_right_valve = V_TRIState.MID
    if plane_commands.spoiler_left_deg == 0 and sensors_state.lvdts_state.spoilers_left_norm > conf.LVDT_Norm_Low_Thresh:
        valves_state.spoilers_left_valve = V_TRIState.DOWN
    elif plane_commands.spoiler_left_deg >= 40 and sensors_state.lvdts_state.spoilers_left_norm < conf.LVDT_Norm_High_Thresh:
        valves_state.spoilers_left_valve = V_TRIState.UP
    elif plane_commands.spoiler_left_deg in [20, 25]:
        valves_state.spoilers_left_valve = V_TRIState.MID
    else:
        valves_state.spoilers_left_valve = V_TRIState.MID

    # print(sensors_state.lvdts_state.ailerons_right_norm, sensors_state.lvdts_state.ailerons_left_norm)
    # print(plane_commands.ailerons_right_deg)
    # print(plane_commands.rudder_deg)
    # print(plane_commands.spoiler_right_deg, plane_commands.spoiler_left_deg)
    # print(valves_state.spoilers_right_valve, valves_state.spoilers_left_valve)

    return valves_state


def plane_send_valves(plane_mdbus_device: Plane_MDBus_Device, valves_state: Valves_State):
    plane_mdbus_device.write_valves(valves_state)


def main():
    pygame.init()
    pygame.joystick.init()
    fjs_device = fjs_connect()

    plane_mdbus_device = Plane_MDBus_Device(port_name=conf.Plane_MDBus_Port, slave_id=conf.Plane_MDBus_Slave_ID)
    plane_mdbus_device.connect()

    # set software ON indicator
    plane_mdbus_device._mdbus_write_req(4117, [1])

    while True:
        fjs_state = capture_controls(fjs_device)
        sensors_state = capture_sensors(plane_mdbus_device)
        if fjs_state == None or sensors_state == None:
            sys.exit(1)

        plane_commands = create_plane_commands(fjs_state, sensors_state)
        valves_state = plane_control_loop(plane_commands, sensors_state)
        plane_send_valves(plane_mdbus_device, valves_state)

        time.sleep(0.05)


if __name__ == "__main__":
    main()
