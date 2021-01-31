"""
GROUP:       LIMPENS (9)
DATE:        18 January 2021
AUTHOR(S):   Karlijn Limpens
             Joos Akkerman
             Guido Vaessen
             Stijn van den Berg
             David Puroja
DESCRIPTION: This class is used to run the model multiple times and to save the
             results of the model per timestep in a csv file. Parameters used
             in the constructor of WolfElk can be manipulated using a
             param dictionary which can be found in the __name__ == "__main__"
             part.
"""

import pandas as pd
import numpy as np
from wolf_elk.model import WolfElk
from matplotlib import pyplot as plt


class Runner():
    """
    Class to run the model given the amount of iterations and optional
    parameters.
    """
    def __init__(self, params):
        self.params = params

    def run(self, step_count, iterations=10):
        df_list = []

        for _ in range(iterations):
            model = WolfElk(**self.params)
            result_df = model.run_model(step_count)
            df_list.append(result_df)
        return pd.concat(df_list, ignore_index=True)


def get_statistics(dataframe, step_size):
    """
    Gets the statistics (mean and standard deviation) from the passed dataframe
    returned by the model.
    Args:
        step_size (int): The step size used by the model.
    Returns:
        Two dataframes with the mean and standard deviation.
    """
    dataframe = dataframe.set_index('step')
    by_row_index = dataframe.groupby(dataframe.index)
    df_means = by_row_index.mean()
    df_std = by_row_index.std()
    return df_means, df_std


def plot_mean_and_standard_deviation(df_mean, df_std, step_size):
    x = np.linspace(0, 200, 200)
    for col in df_mean.columns:
        _ = plt.figure(figsize=(10, 8), dpi=150)
        plt.title(
            "Mean and Standard Deviation for {} value with {} steps".format(
                col, step_size)
        )
        plt.plot(x, df_mean[col], color='teal', label='Mean of {}'.format(col))
        plt.fill_between(
            x,
            df_mean[col]-df_std[col],
            df_mean[col]+df_std[col],
            color='powderblue',
            label='error'
        )
        plt.grid(True)
        plt.legend()
        plt.show()


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
    step_count = 200
    parameters = {
        'initial_elk': 200,
        'initial_wolves': 0
    }
    runner = Runner(parameters)
    result_df = runner.run(step_count, iterations=2)
    mean, std = get_statistics(result_df, step_count)
    result_df.to_csv('model_results.csv')
