# elettra-pySC-dt

This repository contains scripts and documentation for running pySC commissioning software on the Elettra 2.0 Digital Twin.

## Overview

The workflow is based on the [pySC](https://github.com/kparasch/pySC) framework, adapted for the Elettra 2.0 Digital Twin (DT) environment. The DT is controlled via [Tango Controls](https://www.tango-controls.org/).

The main goals are:
- Apply lattice errors to the DT using pySC
- Read and write magnets and BPMs via Tango
- Perform orbit correction and first-turn correction on the DT
- Prepare the commissioning software for use on the real Elettra 2.0 machine

## Repository Structure

```
elettra-pySC-dt/
├── docs/
│   ├── 01_dt_connection.md             # DT environment setup and connection
│   ├── 02_lattice_configuration.md     # loading lattice files into the DT
│   ├── 03_pySC_environment.md          # pySC installation and setup
│   ├── 04_pySC_commissioning.md        # running commissioning scripts
│   └── images/                         # screenshots and figures
├── configuration.yaml                  # error model and magnet family definitions
├── interface.py                        # Tango interface for DT communication
├── register.py                         # generates errored lattice and loads into DT
├── generate_name_mapping.py            # generates pySC → Tango device name mapping
├── generate_ideal_orm.py               # generates ideal closed orbit response matrix
├── generate_ideal_injection_rm.py      # generates ideal trajectory response matrices
├── correct_orbit.py                    # orbit correction script
├── correct_1st_turn.py                 # first turn correction script
└── reset_correctors.py                 # resets all correctors to zero
```

## Quick Start

1. Connect to the DT and set up the environment — see `docs/01_dt_connection.md`
2. Load the lattice file into the DT — see `docs/02_lattice_configuration.md`
3. Install pySC — see `docs/03_pySC_environment.md`
4. Run the commissioning scripts — see `docs/04_pySC_commissioning.md`

## Dependencies

- [pySC](https://github.com/kparasch/pySC)
- [PyTango](https://pytango.readthedocs.io/)
- [pyAT](https://github.com/atcollab/at)

## Status

| Step | Status |
|---|---|
| Errored lattice generation | ✅ Done |
| Tango interface (magnets, BPMs, RF) | ✅ Done |
| Orbit correction | ✅ Done |
| First turn correction | 🔄 In progress (Mode 1 TBT under investigation) |
| ORM measurement | ⏳ Not started |
| BBA | ⏳ Not started |
