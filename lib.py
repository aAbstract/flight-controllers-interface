import time
import json
from enum import IntEnum
from serial import Serial
from typing import ClassVar, Literal
from dataclasses import dataclass, asdict, field
from ctypes import (
    CDLL,
    c_uint8,
)

import conf
from libzcom_mdbus_ffi import _libs


class V_TRIState(IntEnum):
    MID = 0
    UP = 1
    DOWN = 2


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

    side_stick_f1: bool = False
    side_stick_f2: bool = False
    side_stick_b1: bool = False
    side_stick_b2: bool = False

    flaps_lever_X: bool = False
    flaps_lever_A: bool = False
    flaps_lever_B: bool = False
    flaps_lever_Y: bool = False
    flaps_lever_B3: bool = False
    flaps_lever_B4: bool = False

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

    side_stick_x: float = 0.0
    side_stick_y: float = 0.0
    side_stick_z: float = 0.0

    flaps_lever_primary: float = 0.0
    flaps_lever_secondary: float = 0.0

    rudder_right: float = 0.0
    rudder_left: float = 0.0
    rudder_twist: float = 0.0

    def to_json_str(self):
        return json.dumps(asdict(self), indent=2)


@dataclass
class FJS_Hats_State:
    Hats_Idx_Map: ClassVar[dict[int, str]] = {
        0: 'side_stick_hat',
    }

    side_stick_hat: tuple[int, int] = (0, 0)

    def to_json_str(self):
        return json.dumps(asdict(self), indent=2)


@dataclass
class FJS_State:
    timestamp_ms: int = 0
    fjs_buttons_state: FJS_Buttons_State = field(default_factory=FJS_Buttons_State)
    fjs_axes_state: FJS_Axes_State = field(default_factory=FJS_Axes_State)
    fjs_hats_state: FJS_Hats_State = field(default_factory=FJS_Hats_State)

    def to_json_str(self):
        return json.dumps(asdict(self), indent=2)


@dataclass
class LVDTs_State:
    LVDT_Max_12b: ClassVar[int] = 0b0000_0111_1101_0000
    LVDT_Max_16b: ClassVar[int] = 0b0111_1111_1111_1111

    LVDTs_Idx_Map: ClassVar[dict[int, str]] = {
        0: 'ailerons_right_lvdt',
        1: 'ailerons_left_lvdt',
        2: 'elevators_lvdt',
        3: 'flaps_right_lvdt',
        4: 'flaps_left_lvdt',
        5: 'rudder_lvdt',
        6: 'spoilers_right_lvdt',
        7: 'spoilers_left_lvdt',
    }
    LVDTs_Max_Map: ClassVar[dict[str, int]] = {
        'ailerons_right_lvdt': LVDT_Max_12b,
        'ailerons_left_lvdt': LVDT_Max_12b,
        'elevators_lvdt': LVDT_Max_12b,
        'rudder_lvdt': LVDT_Max_12b,
        'flaps_right_lvdt': LVDT_Max_16b,
        'flaps_left_lvdt': LVDT_Max_16b,
        'spoilers_right_lvdt': LVDT_Max_16b,
        'spoilers_left_lvdt': LVDT_Max_16b,
    }

    ailerons_right_lvdt: float = 0.0
    ailerons_left_lvdt: float = 0.0
    elevators_lvdt: float = 0.0
    flaps_right_lvdt: float = 0.0
    flaps_left_lvdt: float = 0.0
    rudder_lvdt: float = 0.0
    spoilers_right_lvdt: float = 0.0
    spoilers_left_lvdt: float = 0.0

    def __getattr__(self, name: str):
        if name.endswith('_norm'):
            lvdt_name = name.removesuffix('_norm') + '_lvdt'
            lvdt_max = LVDTs_State.LVDTs_Max_Map.get(lvdt_name)
            if lvdt_max is not None:
                lvdt_norm = getattr(self, lvdt_name) / lvdt_max  # normalized lvdt reading
                return lvdt_norm
            else:
                raise AttributeError(name)
        else:
            return getattr(self, name)

    def to_json_str(self):
        return json.dumps(asdict(self), indent=2)


@dataclass
class Limit_Switches_State:
    Limit_Switches_Idx_Map: ClassVar[dict[int, str]] = {
        0: 'landing_gear_front_limit_switch_1',
        1: 'landing_gear_front_limit_switch_2',
        2: 'landing_gear_mid_right_limit_switch_1',
        3: 'landing_gear_mid_right_limit_switch_2',
        4: 'landing_gear_mid_left_limit_switch_1',
        5: 'landing_gear_mid_left_limit_switch_2',
    }

    landing_gear_front_limit_switch_1: bool = False
    landing_gear_front_limit_switch_2: bool = False
    landing_gear_mid_right_limit_switch_1: bool = False
    landing_gear_mid_right_limit_switch_2: bool = False
    landing_gear_mid_left_limit_switch_1: bool = False
    landing_gear_mid_left_limit_switch_2: bool = False

    def to_json_str(self):
        return json.dumps(asdict(self), indent=2)


@dataclass
class Valves_State:
    Valves_Idx_Map: ClassVar[dict[int, str]] = {
        0: 'ailerons_right_valve',
        1: 'ailerons_left_valve',
        2: 'elevators_valve',
        3: 'flaps_right_valve',
        4: 'flaps_left_valve',
        5: 'rudder_valve',
        6: 'spoilers_right_valve',
        7: 'spoilers_left_valve',
        8: 'landing_gear_mid_valve',
        9: 'landing_gear_front_valve',
    }

    ailerons_right_valve: V_TRIState = V_TRIState.MID
    ailerons_left_valve: V_TRIState = V_TRIState.MID
    elevators_valve: V_TRIState = V_TRIState.MID
    flaps_right_valve: V_TRIState = V_TRIState.MID
    flaps_left_valve: V_TRIState = V_TRIState.MID
    rudder_valve: V_TRIState = V_TRIState.MID
    spoilers_right_valve: V_TRIState = V_TRIState.MID
    spoilers_left_valve: V_TRIState = V_TRIState.MID
    landing_gear_mid_valve: V_TRIState = V_TRIState.MID
    landing_gear_front_valve: V_TRIState = V_TRIState.MID

    def to_json_str(self):
        return json.dumps(asdict(self), indent=2)


@dataclass
class Levers_State:
    Levers_Idx_Map: ClassVar[dict[int, str]] = {
        0: 'landing_gear_lever',
        1: 'spoilers_lever',
    }

    landing_gear_lever: V_TRIState = V_TRIState.MID
    spoilers_lever: V_TRIState = V_TRIState.MID

    def to_json_str(self):
        return json.dumps(asdict(self), indent=2)


@dataclass
class Sensors_State:
    timestamp_ms: int = 0
    lvdts_state: LVDTs_State = field(default_factory=LVDTs_State)
    limit_switches_state: Limit_Switches_State = field(default_factory=Limit_Switches_State)
    valves_state: Valves_State = field(default_factory=Valves_State)
    levers_state: Levers_State = field(default_factory=Levers_State)

    def is_cruise(self) -> bool:
        is_cruise_flag = True
        is_cruise_flag &= self.lvdts_state.ailerons_right_norm == 0
        is_cruise_flag &= self.lvdts_state.ailerons_left_norm == 0
        is_cruise_flag &= self.lvdts_state.elevators_norm == 0
        is_cruise_flag &= self.lvdts_state.rudder_norm == 0
        return is_cruise_flag

    def is_rolling(self, rolling_dir: Literal['RIGHT', 'LEFT']) -> bool:
        if rolling_dir == 'RIGHT':
            return self.lvdts_state.ailerons_right_norm > 0 and self.lvdts_state.ailerons_left_norm < 0
        elif rolling_dir == 'LEFT':
            return self.lvdts_state.ailerons_right_norm < 0 and self.lvdts_state.ailerons_left_norm > 0

    def is_flaps_full(self) -> bool:
        flaps_right_deg = self.lvdts_state.flaps_right_norm * conf.Flaps_Max_Deg
        flaps_left_deg = self.lvdts_state.flaps_left_norm * conf.Flaps_Max_Deg
        flaps_deg = max(flaps_right_deg, flaps_left_deg)
        return flaps_deg >= 0.8 * conf.Flaps_Max_Deg

    def is_landing_gear_down(self) -> bool:
        is_landing_gear_down_flag = True
        is_landing_gear_down_flag &= not self.limit_switches_state.landing_gear_front_limit_switch_1
        is_landing_gear_down_flag &= not self.limit_switches_state.landing_gear_front_limit_switch_2
        is_landing_gear_down_flag &= not self.limit_switches_state.landing_gear_mid_right_limit_switch_1
        is_landing_gear_down_flag &= not self.limit_switches_state.landing_gear_mid_right_limit_switch_2
        is_landing_gear_down_flag &= not self.limit_switches_state.landing_gear_mid_left_limit_switch_1
        is_landing_gear_down_flag &= not self.limit_switches_state.landing_gear_mid_left_limit_switch_2
        return is_landing_gear_down_flag

    def is_landing_gear_up(self) -> bool:
        is_landing_gear_up_flag = True
        is_landing_gear_up_flag &= self.limit_switches_state.landing_gear_front_limit_switch_1
        is_landing_gear_up_flag &= self.limit_switches_state.landing_gear_front_limit_switch_2
        is_landing_gear_up_flag &= self.limit_switches_state.landing_gear_mid_right_limit_switch_1
        is_landing_gear_up_flag &= self.limit_switches_state.landing_gear_mid_right_limit_switch_2
        is_landing_gear_up_flag &= self.limit_switches_state.landing_gear_mid_left_limit_switch_1
        is_landing_gear_up_flag &= self.limit_switches_state.landing_gear_mid_left_limit_switch_2
        return is_landing_gear_up_flag

    def to_json_str(self):
        return json.dumps(asdict(self), indent=2)


@dataclass
class Plane_Commands:
    ailerons_right_deg: int = 0
    ailerons_left_deg: int = 0
    elevators_deg: int = 0
    flaps_right_deg: int = 0
    flaps_left_deg: int = 0
    rudder_deg: int = 0
    spoiler_right_deg: int = 0
    spoiler_left_deg: int = 0

    landing_gear_mid: V_TRIState = V_TRIState.MID
    landing_gear_front: V_TRIState = V_TRIState.MID

    def set_flaps(self, deg: int):
        self.flaps_right_deg = deg
        self.flaps_left_deg = deg

    def set_spoilers(self, deg: int):
        self.spoiler_right_deg = deg
        self.spoiler_left_deg = deg

    def set_landing_gear(self, pos: V_TRIState):
        self.landing_gear_mid = pos
        self.landing_gear_front = pos

    def to_json_str(self):
        return json.dumps(asdict(self), indent=2)


class Plane_MDBus_Device:
    port_name: str
    slave_id: int
    serial_port: Serial
    libzcom: CDLL

    def __init__(self, port_name: str, slave_id: int):
        self.port_name = port_name
        self.slave_id = slave_id
        self.serial_port = None
        self.libzcom = _libs['libzcom_mdbus.so']
        self.libzcom.mdbus_set_slave_id(self.slave_id)

    def connect(self):
        Plane_MDBus_Device.ilog(f"Connecting to Port: {self.port_name}...")
        try:
            self.serial_port = Serial(port=self.port_name, baudrate=115200)
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            Plane_MDBus_Device.ilog(f"Connecting to Port: {self.port_name}...OK")
        except:
            Plane_MDBus_Device.elog(f"Connecting to Port: {self.port_name}...ERR")

    @staticmethod
    def ilog(msg: str):
        Log.ilog('Plane_MDBus: ' + msg)

    @staticmethod
    def wlog(msg: str):
        Log.wlog('Plane_MDBus: ' + msg)

    @staticmethod
    def elog(msg: str):
        Log.elog('Plane_MDBus: ' + msg)

    @staticmethod
    def dlog(msg: str):
        Log.dlog('Plane_MDBus: ' + msg)

    @staticmethod
    def fmt_pkt_hex(pkt: bytes) -> str:
        return ' '.join([f"{b:02X}" for b in pkt])

    def _mdbus_read_req(self, address: int, word_cnt: int) -> bytes:
        mdbus_rreq = (c_uint8 * 8)()
        self.libzcom.mdbus_encode_read_input_regs(address, word_cnt, mdbus_rreq)
        mdbus_rreq = bytes(mdbus_rreq)
        Plane_MDBus_Device.dlog('MDBus_READ_REQ -> ' + Plane_MDBus_Device.fmt_pkt_hex(mdbus_rreq))
        self.serial_port.write(mdbus_rreq)
        mdbus_rres = self.serial_port.read(word_cnt * 2 + 5)
        Plane_MDBus_Device.dlog('MDBus_READ_RES -> ' + Plane_MDBus_Device.fmt_pkt_hex(mdbus_rres))

        data = mdbus_rres[:-2]
        target_crc = mdbus_rres[-2:]
        data_ptr = (c_uint8 * len(data)).from_buffer_copy(data)
        modbus_crc: int = self.libzcom.mdbus_rtu_crc(data_ptr, len(data))
        crc_bytes = modbus_crc.to_bytes(2, byteorder='little')
        if crc_bytes != target_crc:
            Plane_MDBus_Device.wlog('Invalid MDBus CRC')
            return None

        data_payload = mdbus_rres[3:-2]
        return data_payload

    def load_lvdts(self) -> LVDTs_State:
        if not self.serial_port:
            Plane_MDBus_Device.elog('Device is not Connected')
            return None

        lvdts_payload = self._mdbus_read_req(4096, 8)
        if not lvdts_payload:
            Plane_MDBus_Device.elog('Empty MDBus Response')
            return None

        lvdts_state = {}
        for i in range(8):
            lvdt_name = LVDTs_State.LVDTs_Idx_Map.get(i)
            if not lvdt_name:
                continue

            word = bytes([lvdts_payload[2 * i], lvdts_payload[2 * i + 1]])
            lvdt_adc = int.from_bytes(word, 'big')
            lvdts_state[lvdt_name] = lvdt_adc

        return LVDTs_State(**lvdts_state)

    def load_limit_switches(self) -> LVDTs_State:
        if not self.serial_port:
            Plane_MDBus_Device.elog('Device is not Connected')
            return None

        limit_switches_payload = self._mdbus_read_req(4104, 1)
        if not limit_switches_payload:
            Plane_MDBus_Device.elog('Empty MDBus Response')
            return None

        limit_switches_word = int.from_bytes(limit_switches_payload, 'big')
        limit_switches_bits = f"{limit_switches_word:016b}"[-6:][::-1]
        limit_switches_state = {}
        for i, b in enumerate(limit_switches_bits):
            limit_switch_name = Limit_Switches_State.Limit_Switches_Idx_Map.get(i)
            if not limit_switch_name:
                continue

            limit_switches_state[limit_switch_name] = b == '1'

        return Limit_Switches_State(**limit_switches_state)

    def load_valves(self) -> Valves_State:
        if not self.serial_port:
            Plane_MDBus_Device.elog('Device is not Connected')
            return None

        valves_payload = self._mdbus_read_req(4105, 10)
        if not valves_payload:
            Plane_MDBus_Device.elog('Empty MDBus Response')
            return None

        valves_state = {}
        for i in range(10):
            lever_name = Valves_State.Valves_Idx_Map.get(i)
            if not lever_name:
                continue

            word = bytes([valves_payload[2 * i], valves_payload[2 * i + 1]])
            valve_state = int.from_bytes(word, 'big')
            valves_state[lever_name] = V_TRIState(valve_state)

        return Valves_State(**valves_state)

    def load_levers(self) -> Levers_State:
        if not self.serial_port:
            Plane_MDBus_Device.elog('Device is not Connected')
            return None

        levers_payload = self._mdbus_read_req(4115, 2)
        if not levers_payload:
            Plane_MDBus_Device.elog('Empty MDBus Response')
            return None

        levers_state = {}
        for i in range(2):
            lever_name = Levers_State.Levers_Idx_Map.get(i)
            if not lever_name:
                continue

            word = bytes([levers_payload[2 * i], levers_payload[2 * i + 1]])
            lever_state = int.from_bytes(word, 'big')
            levers_state[lever_name] = V_TRIState(lever_state)

        return Levers_State(**levers_state)


class Log:
    DEBUG = True

    @staticmethod
    def ilog(msg: str):
        print(f"[{Clock.get_time_ms()}] [INFO]", msg)

    @staticmethod
    def wlog(msg: str):
        print(f"[{Clock.get_time_ms()}] [WARN]", msg)

    @staticmethod
    def elog(msg: str):
        print(f"[{Clock.get_time_ms()}] [ERROR]", msg)

    @staticmethod
    def dlog(msg: str):
        if Log.DEBUG:
            print(f"[{Clock.get_time_ms()}] [DEBUG]", msg)


class Clock:
    epoch_ns = time.monotonic_ns()

    def get_time_ms() -> int:
        return (time.monotonic_ns() - Clock.epoch_ns) // 1_000_000

    def get_dt_ms(t: int) -> int:
        return (t - Clock.epoch_ns) // 1_000_000
