from pySC import generate_SC

SC = generate_SC('configuration.yaml', seed=1)
SC.tuning.calculate_model_orbit_response_matrix(save_as='ideal_orm.json')