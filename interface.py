from tango import AttributeProxy, DeviceProxy, Database
import os
import time
import numpy as np
from pathlib import Path


print("TANGO_HOST =", os.environ.get('TANGO_HOST'))
data_folder = Path('./data')
data_folder.mkdir(parents=True, exist_ok=True)

# ===== BPMs =====
HBPM = AttributeProxy('sr/diagnostics/bpm_s/HorPos')
VBPM = AttributeProxy('sr/diagnostics/bpm_s/VerPos')

# ===== RF =====
SIM_DEVICE = DeviceProxy('simulator/elettra2/sr')

# ===== Get all magnet devices =====
db = Database()
devices = db.get_device_exported("sr/magnet/*").value_string

# ===== Initialize groups =====
hst_names, vst_names, sext_names, quad_names, oct_names, antibend_names = [], [], [], [], [], []

# ===== Classify magnets =====
for dev in devices:
    name = dev.split("/")[-1]

    if name.startswith("ch_"):
        hst_names.append(name)

    elif name.startswith("cv_"):
        vst_names.append(name)

    elif name.startswith(("sf_", "sd_", "sh_")):
        sext_names.append(name)

    elif name.startswith(("qf_", "qd_")):
        quad_names.append(name)

    elif name.startswith("oct_"):
        oct_names.append(name)

    elif name.startswith("qab_"):
        antibend_names.append(name)

# ===== Sort =====
hst_names.sort()
vst_names.sort()
sext_names.sort()
quad_names.sort()
oct_names.sort()
antibend_names.sort()


class Interface:
    wait_after_set = 3.0
    quad_wait_time = 5
    rf_wait_time = 5
    orbit_wait_time = 1.01

    # ===== Reference orbit (DT → zero) =====
    def get_ref_orbit(self):
        bpm_h = HBPM.read().value
        bpm_v = VBPM.read().value

        return np.zeros_like(bpm_h) * 1e-3, np.zeros_like(bpm_v) *1e-3  # mm → m

    # ===== Orbit =====
    def get_orbit(self):
        time.sleep(self.orbit_wait_time)
        return HBPM.read().value * 1e-3, VBPM.read().value * 1e-3  # mm → m
    
    # ===== RF Frequency (TANGO: MHz, interface: Hz) =====
    def get_rf_main_frequency(self) -> float:
        return SIM_DEVICE.read_attribute('RfFrequency').value * 1e6   # MHz → Hz

    def set_rf_main_frequency(self, frequency: float):
        SIM_DEVICE.write_attribute('RfFrequency', frequency / 1e6)    # Hz → MHz
        time.sleep(self.rf_wait_time)

    # ===== RF Voltage (TANGO: MV, interface: V) =====
    def get_rf_voltage(self) -> float:
        return SIM_DEVICE.read_attribute('RfVoltage').value * 1e6     # MV → V

    def set_rf_voltage(self, voltage: float):
        SIM_DEVICE.write_attribute('RfVoltage', voltage / 1e6)        # V → MV
        time.sleep(self.rf_wait_time)

    # ===== Get single magnet =====
    def get(self, name: str) -> float:
        try:
            dev = DeviceProxy(f"sr/magnet/{name}")
            return dev.read_attribute("Strength").value
        except Exception as e:
            raise RuntimeError(f"Failed to read {name}: {e}")

    def set(self, name: str, value: float):
        try:
            dev = DeviceProxy(f"sr/magnet/{name}")
            dev.write_attribute("Strength", value)
            if name.startswith(("qf_", "qd_")):
                time.sleep(max(self.quad_wait_time, self.wait_after_set))
            else:
                time.sleep(self.wait_after_set)
        except Exception as e:
            raise RuntimeError(f"Failed to write {name}: {e}")

    # ===== Get/set many magnets =====
    def get_many(self, names: list[str]) -> dict[str, float]:
        data = {}
        for name in names:
            try:
                dev = DeviceProxy(f"sr/magnet/{name}")
                data[name] = dev.read_attribute("Strength").value
            except Exception as e:
                raise RuntimeError(f"Failed to read {name}: {e}")
        return data

    def set_many(self, data: dict[str, float]):
        wait_time = self.wait_after_set
        quad_involved = False
        for name, value in data.items():
            try:
                dev = DeviceProxy(f"sr/magnet/{name}")
                dev.write_attribute("Strength", value)
                if name.startswith(("qf_", "qd_")):
                    quad_involved = True
            except Exception as e:
                raise RuntimeError(f"Failed to write {name}: {e}")
        if quad_involved:
            wait_time = max(wait_time, self.quad_wait_time)
        time.sleep(wait_time)


class InterfaceInjection(Interface):
    tbt_wait_time = 1
    trigger_injection = False
    n_turns = 1

    def get_orbit(self):
        # switch to TBT mode
        SIM_DEVICE.write_attribute('Mode', 1)
        time.sleep(self.tbt_wait_time)

        # read TBT data: shape (168, 1000)
        tbt_h = SIM_DEVICE.read_attribute('HPositionsTbT').value
        tbt_v = SIM_DEVICE.read_attribute('VPositionsTbT').value

        # restore closed orbit mode
        SIM_DEVICE.write_attribute('Mode', 3)

        # flatten Fortran order for pySC: (n_bpms * n_turns,)
        return tbt_h[:, :self.n_turns].flatten(order='F'), tbt_v[:, :self.n_turns].flatten(order='F')
    
    def get_ref_orbit(self):
        n_bpms = len(HBPM.read().value)
        x_ref = np.zeros(n_bpms * self.n_turns)
        y_ref = np.zeros(n_bpms * self.n_turns)
        return x_ref, y_ref