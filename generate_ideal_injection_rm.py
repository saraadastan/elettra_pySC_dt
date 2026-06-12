from pySC import generate_SC

SC = generate_SC('configuration.yaml', seed=1)
SC.tuning.calculate_model_trajectory_response_matrix(save_as='ideal_1turn_orm.json', n_turns=1)
SC.tuning.calculate_model_trajectory_response_matrix(save_as='ideal_2turn_orm.json', n_turns=2)