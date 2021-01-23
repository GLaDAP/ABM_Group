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

    """
    def __init__(
        self, 
        problems: dict,
        replicates: int,
        max_steps: int,
        distinct_samples: int
    ):
        """

        """
        self.problems = self.__parse_problems(problems)
        self.replicates = replicates
        self.max_steps = max_steps
        self.distinct_samples = distinct_samples

    def __parse_problems(self, problems):
        name_variables = problems.get("names", None)
        variable_bounds = problems.get("bounds", None)
        if (name_variables and variable_bounds):
            if (len(name_variables) == len(variable_bounds)):
                problems['num_vars'] = len(name_variables)
                return problems
            else:
                raise ValueError("Total variables and defined bounds are not equal!")
        else:
            raise ValueError("Problem dictionary should contain a 'names' key and 'bounds' key")

    def run_analysis(self, distinct_samples: int, model_reporters: dict):
        param_values = saltelli.sample(problem, distinct_samples)
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
        data['Run'], data['Elk'], data['Wolves'], data['Packs'], data['Killed Elks/Wolf'], data['Elks age'] = None, None, None, None, None, None

        for i in range(replicates):
            for vals in param_values: 
                # Change parameters that should be integers
                vals = list(vals)
                vals[2] = int(vals[2])
                # Transform to dict with parameter names and their values
                variable_parameters = {}
                for name, val in zip(problem['names'], vals):
                    variable_parameters[name] = val

                batch.run_iteration(variable_parameters, tuple(vals), count)
                iteration_data = batch.get_model_vars_dataframe().iloc[count]
                iteration_data['Run'] = count # Don't know what causes this, but iteration number is not correctly filled
                data.iloc[count, 0:3] = vals
                data.iloc[count, 3:6] = iteration_data
                count += 1
                print(f'{count / (len(param_values) * (replicates)) * 100:.2f}% done')

if __name__ == "__main__":
    """
    Define Sensitivity Parameters below
    """
    replicates = 10
    max_steps = 100
    distinct_samples = 500

    # Set the outputs
    model_reporters = {
        "Wolves": lambda m: m.get_wolf_breed_count(),
        "Elks": lambda m: m.schedule.get_breed_count(Elk),
        "Elks age": lambda m: m.schedule.get_average_age(Elk),
        "Killed Elks/Wolf": lambda m:
            m.schedule.get_average_kills(Wolf),
        "Packs": lambda m: m.schedule.get_breed_count(Pack)
    }

    # Define variables which should be included in the sensitivity analysis
    # with appropiate boundries.
    problem = {
        'names': ['elk_reproduce', 'wolf_reproduce', 'pack_size_threshold'],
        'bounds': [[0.01, 0.1], [0.01, 0.1], [2, 4]]
    }

    SA = SensitivityAnalysis(problem, replicates, max_steps, distinct_samples)
    SA.run_analysis(distinct_samples, model_reporters)