from pySC import generate_SC
import json

SC = generate_SC('configuration.yaml', seed=1)

mapping = {}

for control_name in SC.magnet_settings.controls.keys():
    index = control_name.split('/')[0]
    elem = SC.lattice.design[int(index)]
    tango_name = elem.FamName.lower()
    mapping[control_name] = tango_name

json.dump(mapping, open('name_mapping.json', 'w'), indent=4)
print(f"Generated {len(mapping)} mappings")