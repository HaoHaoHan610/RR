import pandas as pd
import numpy as np
from pathlib import Path

def initializing():
    n = 100
    burst = np.random.randint(low = 1,high =10,size = n) # data type = int32

    burst_time = np.ceil(burst).astype(int)

    arrival_time = np.random.randint(low = 1,high =10,size = n)
    arrival_time = np.ceil(burst).astype(int)
    arrival_time = np.sort(arrival_time)
    
    process_id = np.arange(1,n+1)
    priority = process_id.copy()
    np.random.shuffle(priority)

    data = np.array([process_id,arrival_time,burst_time,priority])
    

    df = pd.DataFrame(data).T.set_axis(["process_id","arrival_time","burst_time","priority"],axis="columns")
    # "T" -> transpose

    here = Path(__file__).resolve().parent
    csv_path = here / 'db' / 'data_set.csv'
    df.to_csv(csv_path,index= False)

def par_initializing(n):
    burst = np.random.randint(low = 1,high =10,size = n) # data type = int32

    burst_time = np.ceil(burst).astype(int)

    arrival_time = np.random.randint(low = 1,high =10,size = n)
    arrival_time = np.ceil(burst).astype(int)
    arrival_time = np.sort(arrival_time)
    
    process_id = np.arange(1,n+1)
    priority = process_id.copy()
    np.random.shuffle(priority)

    data = np.array([process_id,arrival_time,burst_time,priority])
    
    df = pd.DataFrame(data).T.set_axis(["process_id","arrival_time","burst_time","priority"],axis="columns")
    # "T" -> transpose
    here = Path(__file__).resolve().parent
    csv_path = here / 'db' / 'data_set.csv'
    df.to_csv(csv_path,index= False)

def seg_initializing(n):
    burst = np.random.randint(low = 1,high =10,size = n) # data type = int32
    burst_time = np.ceil(burst).astype(int)

    arrival_time = np.random.randint(low = 1,high =10,size = n)
    arrival_time = np.ceil(burst).astype(int)
    arrival_time = np.sort(arrival_time)
    
    process_id = np.array([f"P{i}" for i in range(1, n + 1)])

    return process_id,arrival_time,burst_time

if __name__ == '__main__':
    initializing()

