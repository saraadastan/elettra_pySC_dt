from interface import Interface
from pySC.apps import orbit_correction
from pySC import ResponseMatrix
import numpy as np
import json

APPLY_CORRECTION = True

ebs = Interface()

response_matrix = ResponseMatrix.from_json('ideal_orm.json')
mapping = json.load(open('name_mapping.json'))
response_matrix.input_names = [mapping[pySC_name] for pySC_name in response_matrix.input_names]

ref_x, ref_y = ebs.get_ref_orbit()
reference = np.concat((ref_x.flatten(order='F'), ref_y.flatten(order='F')))

n_iterations = 10

for i in range(n_iterations):
    x, y = ebs.get_orbit()
    print(f'Iter {i+1} - RMS H: {np.std(x-ref_x)*1e6:.1f} μm, V: {np.std(y-ref_y)*1e6:.1f} μm')
    orbit_correction(interface=ebs, response_matrix=response_matrix, reference=reference,
                 method='svd_cutoff', parameter=1e-3, apply=APPLY_CORRECTION, gain=0.5)
#print(trims)

x2, y2 = ebs.get_orbit()
print(f'RMS after H: {np.std(x2-ref_x)*1e6:.1f} μm, V: {np.std(y2-ref_y)*1e6:.1f} μm')

trims = orbit_correction(interface=ebs, response_matrix=response_matrix, reference=reference,
                         method='micado', parameter=1, apply=False)

x3, y3 = ebs.get_orbit()
print(f'Micado trims: {trims}')