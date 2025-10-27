import pandas as pd
import numpy as np

def initializing():
    n = 1000
    burst = np.random.randint(low = 1,high =10,size = n) # data type = int32
    # print(type(burst))
    burst_time = np.ceil(burst).astype(int)
    # print(type(burst[0]))
    arrival_time = np.random.randint(low = 1,high =10,size = n)
    arrival_time = np.ceil(burst).astype(int)
    arrival_time = np.sort(arrival_time)
    
    process_id = np.arange(1,n+1)
    priority = process_id.copy()
    np.random.shuffle(priority)

    data = np.array([process_id,arrival_time,burst_time,priority])
    
    # print(data)
    df = pd.DataFrame(data).T.set_axis(["process_id","arrival_time","burst_time","priority"],axis="columns")
    # "T" -> transpose
    # sorted_data = df.sort_values(by = "arrival_time").reset_index(drop=False)
    df.to_csv('db/data_set.csv',index = False)
    # print(burst)
    # print(arrival_time)
    # print(process_id)
    # print(ranking)

def par_initializing(n):
    burst = np.random.randint(low = 1,high =10,size = n) # data type = int32
    # print(type(burst))
    burst_time = np.ceil(burst).astype(int)
    # print(type(burst[0]))
    arrival_time = np.random.randint(low = 1,high =10,size = n)
    arrival_time = np.ceil(burst).astype(int)
    arrival_time = np.sort(arrival_time)
    
    process_id = np.arange(1,n+1)
    priority = process_id.copy()
    np.random.shuffle(priority)

    data = np.array([process_id,arrival_time,burst_time,priority])
    
    # print(data)
    df = pd.DataFrame(data).T.set_axis(["process_id","arrival_time","burst_time","priority"],axis="columns")
    # "T" -> transpose
    # sorted_data = df.sort_values(by = "arrival_time").reset_index(drop=False)
    df.to_csv('db/data_set.csv',index = False)
    # print(burst)
    # print(arrival_time)
    # print(process_id)
    # print(ranking)

def seg_initializing(n):
    burst = np.random.randint(low = 1,high =10,size = n) # data type = int32
    # print(type(burst))
    burst_time = np.ceil(burst).astype(int)
    # print(type(burst[0]))
    arrival_time = np.random.randint(low = 1,high =10,size = n)
    arrival_time = np.ceil(burst).astype(int)
    arrival_time = np.sort(arrival_time)
    
    process_id = np.array([f"P{i}" for i in range(1, n + 1)])

    return process_id,arrival_time,burst_time
    
    
    # print(burst)
    # print(arrival_time)
    # print(process_id)
    # print(ranking)

if __name__ == '__main__':
    initializing()

