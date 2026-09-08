import time
import json
from enum import Enum
from serial import Serial
from typing import ClassVar
from dataclasses import dataclass, asdict
from ctypes import (
    CDLL,
    c_uint8,
)

from libzcom_mdbus_ffi import _libs


class V_TRIState(Enum):
    MID = 0
    UP = 1
    DOWN = 2


class R_TRIState(Enum):
    MID = 0
    CCW = 1
    CW = 2


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

    def to_json_str(self):
        return json.dumps(asdict(self), indent=2)


@dataclass
class LVDTs_State:
    LVDTs_Idx_Map: ClassVar[dict[int, str]] = {
        0: 'lv_spoiler_1',
        1: 'lv_spoiler_2',
        2: 'lv_spoiler_3',
        3: 'lv_spoiler_4',

        4: 'lv_flap_1',
        5: 'lv_flap_2',
        6: 'lv_flap_3',
        7: 'lv_flap_4',
    }

    lv_spoiler_1: float
    lv_spoiler_2: float
    lv_spoiler_3: float
    lv_spoiler_4: float

    lv_flap_1: float
    lv_flap_2: float
    lv_flap_3: float
    lv_flap_4: float

    def to_json_str(self):
        return json.dumps(asdict(self), indent=2)


@dataclass
class Limit_Switches_State:
    Limit_Switches_Idx_Map: ClassVar[dict[int, str]] = {
        0: 'limit_switch_1',
        1: 'limit_switch_2',
        2: 'limit_switch_3',
        3: 'limit_switch_4',
        4: 'limit_switch_5',
        5: 'limit_switch_6',
    }

    limit_switch_1: bool
    limit_switch_2: bool
    limit_switch_3: bool
    limit_switch_4: bool
    limit_switch_5: bool
    limit_switch_6: bool

    def to_json_str(self):
        return json.dumps(asdict(self), indent=2)


@dataclass
class Sensors_State:
    timestamp_ms: int
    lvdts_state: LVDTs_State
    limit_switches_state: Limit_Switches_State

    def to_json_str(self):
        return json.dumps(asdict(self), indent=2)


@dataclass
class Plane_Commands:
    right_ailerons: V_TRIState
    left_ailerons: V_TRIState
    elevators: V_TRIState
    flaps_deg: int
    rudder: R_TRIState
    landing_gear: V_TRIState
    spoilers_deg: tuple[int, int, int, int, int]


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

    @staticmethod
    def lvdt_map(lvdt_adc: int) -> float:
        return lvdt_adc / 0b0000_1111_1111_1111 * 10

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

        lvdts_payload = self._mdbus_read_req(0xD0, 8)
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
            lvdts_state[lvdt_name] = self.lvdt_map(lvdt_adc)

        return LVDTs_State(**lvdts_state)

    def load_limit_switches(self) -> LVDTs_State:
        if not self.serial_port:
            Plane_MDBus_Device.elog('Device is not Connected')
            return None

        limit_switches_payload = self._mdbus_read_req(0xD8, 1)
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
