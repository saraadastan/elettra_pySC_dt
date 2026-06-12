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