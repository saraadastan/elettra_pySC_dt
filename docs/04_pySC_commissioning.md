# pySC Commissioning Scripts on the Digital Twin

## 1. Prepare the Working Directory

Create a working directory for the pySC commissioning scripts:

```bash
mkdir ~/pysc_env/elettra_dt
cd ~/pysc_env/elettra_dt
```

Copy the following files into this directory:

```
elettra_dt/
├── configuration.yaml              # error model and magnet family definitions
├── interface.py                    # Tango interface for DT communication
├── register.py                     # generates errored lattice and loads into DT
├── generate_name_mapping.py        # generates pySC → Tango device name mapping
├── generate_ideal_orm.py           # generates ideal closed orbit response matrix
├── generate_ideal_injection_rm.py  # generates ideal trajectory response matrices
├── correct_orbit.py                # orbit correction script
├── correct_1st_turn.py             # first turn correction script
└── reset_correctors.py             # resets all correctors to zero
```

---

## 2. Run register.py — Generate and Load the Errored Lattice

`register.py` reads the ideal lattice from the DT, applies errors defined in `configuration.yaml`, and saves the errored lattice back to the DT directory.

Make sure the DT is running and the ideal lattice is loaded (see `02_lattice_configuration.md`).

Run:

```bash
python3 register.py --configuration configuration.yaml --seed 1
```

This will:

- Read `/etc/dt/lattice/phase1_lattice.m` from the DT
- Convert it to `phase1_lattice.mat` for pySC
- Apply errors (misalignment, roll) from `configuration.yaml`
- Save the errored lattice locally as `phase1_lattice_error.m`
- Save the errored lattice to `/etc/dt/lattice/phase1_lattice_error.m` for the DT to load

After running, reload the DT with the errored lattice by updating the `RingFile` property in Jive (see `02_lattice_configuration.md`).

### Notes on Errors

The following errors are currently applied:

| Error type | Value |
|---|---|
| Magnet misalignment (dx, dy) | 30 μm |
| Magnet roll | 50 μrad |
| Dipole misalignment (dx, dy) | 50 μm |
| Dipole roll | 100 μrad |
| BPM misalignment (dx, dy) | 150 μm |
| BPM roll | 150 μrad |

The following errors are excluded because they cause the DT to go into an error state:

- Girder errors
- Field calibration errors

---

## 3. Run generate_name_mapping.py — Build the Name Mapping

`generate_name_mapping.py` builds a mapping between pySC internal control names (index-based, e.g. `94/B1L`) and DT Tango device names (e.g. `ch_s01.01`). This mapping is required by all correction scripts.

Run once (no DT connection required):

```bash
python3 generate_name_mapping.py
```

This produces `name_mapping.json` in the working directory.

Example entries:

```json
{
    "94/B1L": "ch_s01.01",
    "95/A1L": "cv_s01.01",
    "66/B2L": "qf_s01.01",
    "12/B1L": "sd_s01.01"
}
```

---

## 4. Run generate_ideal_orm.py — Generate the Ideal ORM

`generate_ideal_orm.py` computes the ideal closed orbit response matrix from the design lattice. This matrix is used by `correct_orbit.py` to compute corrector kicks.

Run once (no DT connection required):

```bash
python3 generate_ideal_orm.py
```

This produces `data/ideal_orm.json`.

The ORM has shape `(336, 480)` — 336 BPM readings (168 H + 168 V) and 480 corrector controls.

---

## 5. Run generate_ideal_injection_rm.py — Generate the Trajectory Response Matrices

`generate_ideal_injection_rm.py` computes the ideal trajectory response matrices for first and second turn correction.

Run once (no DT connection required):

```bash
python3 generate_ideal_injection_rm.py
```

This produces:

- `data/ideal_1turn_orm.json` — used by `correct_1st_turn.py`
- `data/ideal_2turn_orm.json` — used for 2-turn correction

---

## 6. Run correct_orbit.py — Orbit Correction on the DT

`correct_orbit.py` reads the closed orbit from the DT BPMs, computes corrector kicks using the ideal ORM and SVD cutoff method, and applies them to the DT magnets iteratively.

Make sure:

- The DT is running with the errored lattice loaded
- All correctors are at zero (or a known state)
- `name_mapping.json` and `data/ideal_orm.json` exist

Run:

```bash
python3 correct_orbit.py
```

Expected output:

```
Iter 1 - RMS H: 992.9 μm, V: 929.0 μm
Iter 2 - RMS H: 922.8 μm, V: 780.4 μm
Iter 3 - RMS H: 894.4 μm, V: 717.9 μm
...
Final RMS H: xxx μm, V: xxx μm
```

### Resetting Correctors

If the DT goes into an error state during correction, reset all correctors to zero before restarting:

```python
from interface import Interface
from tango import Database

ebs = Interface()
db = Database()
devices = db.get_device_exported("sr/magnet/*").value_string

for dev in devices:
    name = dev.split("/")[-1]
    if name.startswith(("ch_", "cv_")):
        ebs.set(name, 0.0)

print("All correctors reset to zero")
```

---

## 7. Run correct_1st_turn.py — First Turn Correction on the DT

`correct_1st_turn.py` reads the turn-by-turn trajectory from the DT in Mode 1 (injection mode) and applies corrector kicks to improve first-turn transmission.

> **Note:** This script requires the DT injection mode (Mode 1) to be configured correctly. Currently under investigation with the DT team.

Run:

```bash
python3 correct_1st_turn.py
```

---

## Notes on BPM Units

The DT BPM device (`sr/diagnostics/bpm_s`) returns positions in **mm**. The pySC interface converts these to **meters** automatically:

```python
return HBPM.read().value * 1e-3, VBPM.read().value * 1e-3  # mm → m
```

This conversion is applied in `interface.py` and does not need to be handled manually.

---

## Notes on Magnet Attributes

Each magnet device (`sr/magnet/<name>`) exposes the following relevant attributes:

| Attribute | Description |
|---|---|
| `DesignStrength` | Nominal design value (read-only) |
| `CorrectionStrength` | Correction applied on top of design |
| `Strength` | Total = DesignStrength + CorrectionStrength |

The interface reads and writes `Strength` for all magnets, which is consistent with how pySC stores and restores magnet settings.
