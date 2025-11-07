import pandas as pd
from Round_robin.RR import RR
from Round_robin.CO_RR import RR_algorithm
from initializing_process import par_initializing,initializing
from pathlib import Path
# from dashboard import App

pd.options.display.max_rows = 100

def Arrival_time(data,quantum):
    output = RR_algorithm(data,quantum)
    print(output)

def Non_Arrival_time(data,quantum):
    output = RR(data,quantum)
    print(output)

if __name__ == "__main__":
    
    while(True):
        key = int(input("Key: "))
        if key == 3:
            break
        elif key == 0:
            num = int(input("An amount of processes: "))
            par_initializing(num)
        else:
            here = Path(__file__).resolve().parent
            csv_path = here / 'db' / 'data_set.csv'
            data = pd.read_csv(csv_path)
            quantum = int(input("QUANTUM: "))
            if key == 1:
                Non_Arrival_time(data=data,quantum=quantum)
            elif key == 2:
                Arrival_time(data=data,quantum=quantum)
            else:
                print("NOT THE VALID KEY")

        