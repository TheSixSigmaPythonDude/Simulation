import numpy as np
import pandas as pd
import simpy
import random
import itertools

class Lab:
    def __init__(self, env, lines, avg_days_to_process) -> None:
        self.env = env
        self.capacity = simpy.Resource(env, lines)
        self.avg_days_to_process = avg_days_to_process

    # This is the service time
    def cross_section(self, customer):
        # Randomly select from list of distribution of service time
        cross_section_time = np.random.normal(self.avg_days_to_process, self.avg_days_to_process*.2)
        yield self.env.timeout(cross_section_time)

# Function for defining customer 
def unit(env, unit, lab):
    global units_completed
    print(f"Unit {unit} enters queue at {env.now:.2f}!")
    with lab.capacity.request() as request:
        yield request
        print(f"Unit {unit} enters Lab at {env.now:.2f}")
        yield env.process(lab.cross_section(unit))
        print(f"Unit {unit} left Lab at {env.now:.2f}")
        units_completed += 1

# Function for defining the system       
def lab_setup(env, lines, avg_days_to_process, unit_arrival_rate):
    lab = Lab(env, lines, avg_days_to_process)
    i = 0
    while True:
        unit_interarrival_time = random.choice(interarrival_times(unit_arrival_rate,25))
        yield env.timeout(unit_interarrival_time)
        i += 1
        env.process(unit(env, i, lab))

def all_combinations(*args):
    combinations = list(itertools.product(*args))
    combinations_as_lists = [list(combination) for combination in combinations]

    return combinations_as_lists

def interarrival_times(arrival_rate, num_samples):
    interarrival_times = np.random.exponential(scale=1 / arrival_rate, size=num_samples)
    
    return interarrival_times.tolist()

def main(lines, avg_cuts_per_line, avg_cut_demand, unit_arrival_rate, days):
    avg_days_to_process = avg_cut_demand/avg_cuts_per_line
    env = simpy.Environment()
    env.process(lab_setup(env, lines, avg_days_to_process, unit_arrival_rate))
    env.run(until=days)
    #print("Units completed ", str(units_completed))
    return units_completed


if __name__ == '__main__':
    #units_completed = 0
    #main(lines=21, avg_cuts_per_line=40, avg_cut_demand=44, unit_arrival_rate=3.4,days=18)

    lines = [14,21,28]
    cut_demand = [20,28,36,44]
    unit_arrival = [1.7, 2.5, 3.4]
    days_to_complete = [18,24,36,42]
    combos = all_combinations(lines,cut_demand,unit_arrival,days_to_complete)

    df = pd.DataFrame(columns=['Lines','Average Cut Demand','Unit Arrival Rate to Lab','Timeframe to Finish DPA','Units Completed'])
    for ind,combo in enumerate(combos):
        units_completed = 0
        comp = main(combo[0], 40, combo[1], combo[2], combo[3])
        df.loc[ind] = combos[ind] + [comp]

    df.to_excel('Data.xlsx',index=False)