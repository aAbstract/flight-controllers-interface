import sys
import time
import pygame

from lib import (
    FJS_State,
    FJS_Buttons_State,
    FJS_Axes_State,
    FJS_Hats_State,

    Sensors_State,

    Plane_MDBus_Device,

    Log,
    Clock
)


def fjs_connect():
    if pygame.joystick.get_count() == 0:
        Log.elog('No Flight JoyStick Device Detected')
        sys.exit(1)
    fjs_device = pygame.joystick.Joystick(0)
    fjs_device.init()
    return fjs_device


def capture_controls(fjs_device: pygame.joystick.JoystickType) -> FJS_State:
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
    return Sensors_State(
        timestamp_ms=Clock.get_time_ms(),
        lvdts_state=plane_mdbus_device.load_lvdts(),
        limit_switches_state=plane_mdbus_device.load_limit_switches(),
    )


def process_controls(fjs_state: FJS_State, sensors_state: Sensors_State):
    print('FJS_State:')
    print(fjs_state.to_json_str())
    print('Sensors_State:')
    print(sensors_state.to_json_str())


def send_plane_commands():
    pass


def main():
    pygame.init()
    pygame.joystick.init()
    fjs_device = fjs_connect()

    plane_mdbus_device = Plane_MDBus_Device(port_name='/dev/ttyS90', slave_id=0x01)
    plane_mdbus_device.connect()

    while True:
        fjs_state = capture_controls(fjs_device)
        sensors_state = capture_sensors(plane_mdbus_device)
        if fjs_state == None or sensors_state == None:
            sys.exit(1)

        process_controls(fjs_state, sensors_state)

        time.sleep(1)


if __name__ == "__main__":
    main()
