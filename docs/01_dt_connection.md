# Digital Twin Environment Setup

## 1. Connect to the Digital Twin

Connect to the Elettra Digital Twin host using SSH:

```bash
ssh -Y <username>@pcl-ctrl-virt-03.elettra.trieste.it
```

Use your Elettra LDAP credentials.

After login, you should see a prompt like:

```text
<username>@pcl-ctrl-virt-03:~$
```

This confirms that you are connected to the Digital Twin host.

---

## 2. Configure the Digital Twin Environment

On the Digital Twin host, configure your shell environment by updating your `~/.bashrc`.

Add the following block at the end of the file:

```bash
HOST=$(hostname)

if [[ "$HOST" == "pcl-ctrl-virt-03" ]]; then
    export TANGO_HOST=srv-tango-ctrl-03:20000
    export LD_LIBRARY_PATH=/usr/local/tango-10.1.1/lib:/usr/local/qwt-6.3.0/lib:/runtime/lib
    export PKG_CONFIG_PATH=/usr/local/tango-10.1.1/lib/pkgconfig:/usr/local/qwt-6.3.0/lib/pkgconfig:/runtime/lib/pkgconfig
    export PATH=/runtime/bin:$PATH
    export PATH=$PATH:/usr/local/tango-10.1.1/bin
    export CUMBIA_INSTALL_ROOT=/runtime
    export QT_PLUGIN_PATH=/runtime/lib/qumbia-plugins
    export PYTHONPATH=/usr/local/lib/python3.13/site-packages:$CUMBIA_INSTALL_ROOT/lib/python3.13/site-packages

    alias qmake='qmake6'
    alias designer='designer6'
fi
```

After editing the file, reload the configuration:

```bash
source ~/.bashrc
```

To verify the setup, check:

```bash
echo $TANGO_HOST
```

It should return:

```text
srv-tango-ctrl-03:20000
```

---

## 3. Ensure the Digital Twin is Running

### Option 1 — Using Python (recommended)

Run:

```bash
python3
```

Then:

```python
import tango
dev = tango.DeviceProxy("sr/diagnostics/bpm_s")
print(dev.get_attribute_list())
```

If this returns a list of attributes, the Digital Twin is running.

---

### Option 2 — Using Astor

Start Astor:

```bash
astor
```

In the Astor GUI:
- locate the Elettra 2.0 Digital Twin group,
- verify that all servers are in the ON (green) state.

If servers are OFF, they must be started before using the DT.

---

## 4. Initialize the Digital Twin

In another terminal with the DT environment configured, the following commands can be used to initialize or reset the machine state.

### Power Supply Control

Turn ON/OFF the simulated power supplies:

```bash
pson
```

### Power Supply Noise

Enable or disable ripple/noise on all simulated power supplies:

```bash
psnoise
```

### Magnet Initialization

Set all magnets to their design strengths:

```bash
maginitstrength
```
