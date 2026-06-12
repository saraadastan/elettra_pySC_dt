# pySC Environment Setup on the Digital Twin

## 1. Create and Activate a Python Virtual Environment

To run pySC safely, create a dedicated Python virtual environment on the Digital Twin host.

Create the virtual environment:

```bash
python3 -m venv ~/pysc_env
```

Activate it:

```bash
source ~/pysc_env/bin/activate
```

After activation, your shell prompt should look like:

```
(pysc_env) <username>@pcl-ctrl-virt-03:~$
```

### Make PyTango Available Inside the Environment

PyTango is installed in the system Python and must be made visible inside the virtual environment. Run:

```bash
export PYTHONPATH=/usr/local/lib/python3.13/site-packages:$PYTHONPATH
```

To make this automatic, add the same line to:

```bash
~/pysc_env/bin/activate
```

---

## 2. Install pySC

Clone the pySC repository on the Digital Twin host:

```bash
git clone https://github.com/kparasch/pySC.git
```

Move into the repository:

```bash
cd pySC
```

Make sure your virtual environment is activated:

```bash
source ~/pysc_env/bin/activate
```

Install pySC in editable mode:

```bash
pip install -e .
```

### Notes on Dependencies

During installation, you may see warnings related to PyTango dependencies such as:

```
docstring_parser
psutil
```

These warnings do not prevent pySC from working. If desired, you can install them with:

```bash
pip install docstring_parser psutil
```

---

## 3. Test the Installation

After installing pySC, verify that both PyTango and pySC are working correctly.

Make sure your virtual environment is activated:

```bash
source ~/pysc_env/bin/activate
```

Start Python:

```bash
python3
```

Then run:

```python
import tango
from pySC import generate_SC
```

If no errors are raised, the setup is correct.

### Optional: Test Access to the Digital Twin

You can also verify that pySC can access the Digital Twin BPM system:

```python
import tango
dev = tango.DeviceProxy("sr/diagnostics/bpm_s")
print(dev.get_attribute_list())
```

If a list of attributes is returned, the connection to the Digital Twin is working.
