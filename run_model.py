import pandas as pd

from wolf_elk.model import WolfElk

class Runner():
    """
    Class to run the model given the amount of iterations and optional 
    parameters
    """
    def __init__(self, params):
        self.params = params

    def run(self, iterations=10):
        df_list = []

        for _ in range(iterations):
            model = WolfElk(**self.params)
            result_df = model.run_model()
            df_list.append(result_df)
        return pd.concat(df_list, ignore_index=True)

if __name__ == "__main__":
    """
    In the dictionary below, set the desired parameters.
    Options:
        height=40,
        width=40,
        initial_elk=200,
        initial_wolves=20,
        wolf_reproduce=0.03,
        wolf_gain_from_food=30,
        grass_regrowth_time=30,
        elk_gain_from_food=6,
        energy_threshold=10,
        pack_size_threshold=2,
        wolf_territorium=8,
        polynomial_degree=10,
        wolf_lone_attack_prob=0.2,
        time_per_step=1/26
    """
    parameters = { 
        'initial_elk'   : 200, 
        'initial_wolves': 20
    }
    runner = Runner(parameters)
    result_df = runner.run()

    result_df.to_csv('model_result.csv')