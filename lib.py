import json
from typing import ClassVar
from dataclasses import dataclass, asdict


@dataclass
class FJS_Buttons_State:
    Buttons_Idx_Map: ClassVar[dict[int, str]] = {
        0: 'side_stick_f1',
        1: 'side_stick_f2',
        2: 'side_stick_b1',
        3: 'side_stick_b2',
        4: 'flaps_lever_X',
        5: 'flaps_lever_A',
        6: 'flaps_lever_B',
        7: 'flaps_lever_Y',
        8: 'flaps_lever_B3',
        9: 'flaps_lever_B4',
    }

    side_stick_f1: bool
    side_stick_f2: bool
    side_stick_b1: bool
    side_stick_b2: bool

    flaps_lever_X: bool
    flaps_lever_A: bool
    flaps_lever_B: bool
    flaps_lever_Y: bool
    flaps_lever_B3: bool
    flaps_lever_B4: bool

    def to_json_str(self):
        return json.dumps(asdict(self), indent=2)


@dataclass
class FJS_Axes_State:
    Axes_Idx_Map: ClassVar[dict[int, str]] = {
        0: 'side_stick_x',
        1: 'side_stick_y',
        5: 'side_stick_z',

        2: 'flaps_lever_primary',
        7: 'flaps_lever_secondary',

        3: 'rudder_right',
        4: 'rudder_left',
        6: 'rudder_twist',
    }

    side_stick_x: float
    side_stick_y: float
    side_stick_z: float

    flaps_lever_primary: float
    flaps_lever_secondary: float

    rudder_right: float
    rudder_left: float
    rudder_twist: float

    def to_json_str(self):
        return json.dumps(asdict(self), indent=2)


@dataclass
class FJS_Hats_State:
    Hats_Idx_Map: ClassVar[dict[int, str]] = {
        0: 'side_stick_hat',
    }

    side_stick_hat: tuple[int, int]

    def to_json_str(self):
        return json.dumps(asdict(self), indent=2)


@dataclass
class FJS_State:
    timestamp_ms: int
    fjs_buttons_state: FJS_Buttons_State
    fjs_axes_state: FJS_Axes_State
    fjs_hats_state: FJS_Hats_State


@dataclass
class Plane_Commands:
    pass


def elog(msg: str):
    print('ERROR:', msg)


def dlog(msg: str):
    print('DEBUG:', msg)
