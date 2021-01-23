"""
GROUP:       LIMPENS (9)
DATE:        18 January 2021
AUTHOR(S):   Karlijn Limpens
             Joos Akkerman
             Guido Vaessen
             Stijn van den Berg
             David Puroja
DESCRIPTION: Class with SOBOL sensitivity analysis functions from SALib. 
"""
import matplotlib.pyplot as plt 
from itertools import combinations
import numpy as np

from mesa.batchrunner import BatchRunner
from SALib.sample import saltelli
from SALib.analyze import sobol
import pandas as pd
import sys
from wolf_elk.agents import Elk
from wolf_elk.wolf import Wolf, Pack
from wolf_elk.model import WolfElk

class SensitivityAnalysis():
    """
    Sensitivity Analysis class which runs analysis based on SOBOL.
    """
    def __init__(
        self, 
        problems: dict,
        replicates: int,
        max_steps: int,
        distinct_samples: int
    ):
        """
        Args:
            problems (dict): Dictionary containing the model parameters to
                             analyse. This dictionary
        """
        self.problems = self.parse_problems(problems)
        self.replicates = replicates
        self.max_steps = max_steps
        self.distinct_samples = distinct_samples

    def parse_problems(self, problem_set):
        """
        Parses the dictionary so it is usable by SALib. This step is taken
        to make the dictionary more readable at setup.
        """
        problems = {
            "names": [],
            "bounds": [],
            "num_vars" : 0
        }
        print(problem_set)
        for key, value in problem_set.items():
            problems['names'].append(key)
            problems['bounds'].append(value)
            problems['num_vars'] += 1
        return problems

    def run_analysis(self, distinct_samples: int, model_reporters: dict):
        param_values = saltelli.sample(self.problems, distinct_samples, False)
        batch = BatchRunner(
            WolfElk, 
            max_steps = max_steps,
            variable_parameters = {name:[] for name in self.problems['names']},
            model_reporters = model_reporters
        )

        count = 0
        data = pd.DataFrame(
            index=range(replicates * len(param_values)), 
            columns=[
                'elk_reproduce', 'wolf_reproduce', 'pack_size_threshold', 
            ]
        )
        data['Run'] = None
        data['Elk'] = None 
        data['Wolves'] = None
        data['Packs'] = None 
        data['Killed Elks/Wolf'] = None 
        data['Elks age'] = None

        for _ in range(replicates):
            for vals in param_values: 
                # Change parameters that should be integers
                vals = list(vals)
                vals[2] = int(vals[2])
                vals[3] = int(vals[3])
                vals[4] = int(vals[4])
                vals[6] = int(vals[6])
                vals[7] = int(vals[7])
                # print(vals)
                # print(len(vals))
                # Transform to dict with parameter names and their values
                variable_parameters = {}
                for name, val in zip(self.problems['names'], vals):
                    variable_parameters[name] = val

                batch.run_iteration(variable_parameters, tuple(vals), count)
                iteration_data = batch.get_model_vars_dataframe().iloc[count]
                iteration_data['Run'] = count
                data.iloc[count, 0:len(vals)] = vals
                data.iloc[count, len(vals):5+len(vals)] = iteration_data
                # print(iteration_data)
                count += 1
                print(f'{count / (len(param_values) * (replicates)) * 100:.2f}% done')
        return data

    def plot_index(self, s, params, i, title=''):
        """
        Creates a plot for Sobol sensitivity analysis that shows the contributions
        of each parameter to the global sensitivity.

        Args:
            s (dict): dictionary {'S#': dict, 'S#_conf': dict} of dicts that hold
                the values for a set of parameters
            params (list): the parameters taken from s
            i (str): string that indicates what order the sensitivity is.
            title (str): title for the plot
        """

        if i == '2':
            p = len(params)
            params = list(combinations(params, 2))
            indices = s['S' + i].reshape((p ** 2))
            indices = indices[~np.isnan(indices)]
            errors = s['S' + i + '_conf'].reshape((p ** 2))
            errors = errors[~np.isnan(errors)]
        else:
            indices = s['S' + i]
            errors = s['S' + i + '_conf']
            plt.figure()

        l = len(indices)

        plt.title(title)
        plt.ylim([-0.2, len(indices) - 1 + 0.2])
        plt.yticks(range(l), params)
        plt.errorbar(indices, range(l), xerr=errors, linestyle='None', marker='o')
        plt.axvline(0, c='k')
        plt.grid(True)
        plt.savefig("{}.pdf".format(str(params)))

if __name__ == "__main__":
    """
    Define Sensitivity Parameters below
    """
    replicates = 10
    max_steps = 200
    distinct_samples = 500

    # Set the outputs
    model_reporters = {
        "Wolves": lambda m: m.get_wolf_breed_count(),
        "Elks": lambda m: m.schedule.get_breed_count(Elk),
        "Elks age": lambda m: m.schedule.get_average_age(Elk),
        "Killed Elks/Wolf": lambda m:
            m.schedule.get_average_kills(Wolf)
    }

    # Define variables which should be included in the sensitivity analysis
    # with appropiate boundries.
    problem_set = {
        'elk_reproduce':         [0.01, 0.10],
        'wolf_reproduce':        [0.01, 0.1],
        'pack_size_threshold':   [2, 4],
        'energy_threshold':      [5, 30],
        'wolf_territorium':      [2, 8],
        'wolf_lone_attack_prob': [0.1, 0.5],
        'elk_gain_from_food':    [4, 10],
        'wolf_gain_from_food':   [10,40]
    }

    SA = SensitivityAnalysis(problem_set, replicates, max_steps, distinct_samples)
    analysis_data = SA.run_analysis(distinct_samples, model_reporters)
    analysis_data.to_csv('sa_result.csv')

    problem = SA.parse_problems(problem_set)
    Si_elk = sobol.analyze(problem, analysis_data['Elk'].values, calc_second_order=False,print_to_console=True)
    Si_wolves = sobol.analyze(problem, analysis_data['Wolves'].values, calc_second_order=False,print_to_console=True)
    Si_pack = sobol.analyze(problem, analysis_data['Packs'].values, calc_second_order=False,print_to_console=True)
    Si_kills = sobol.analyze(problem, analysis_data['Killed Elks/Wolf'].values, calc_second_order=False,print_to_console=True)
    Si_age = sobol.analyze(problem, analysis_data['Elks age'].values, calc_second_order=False,print_to_console=True)

    # for Si in (Si_elk, Si_wolves, Si_pack, Si_kills, Si_age):
    #     # First order
    #     SA.plot_index(Si, problem['names'], '1', 'First order sensitivity')

    #     # Total order
    #     SA.plot_index(Si, problem['names'], 'T', 'Total order sensitivity')