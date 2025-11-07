import pandas as pd
#from timer import get_cpu_time_unit
import time
def get_cpu_time_unit():
    return time.process_time()
import numpy as np
ilb = 0 # the time of CPU in rest

def waiting_time(processes, n, burst_t, waiting_t, quantum):
    global ilb
    t = 0
    remain = burst_t.copy()

    while True:
        finish = True
        for i in range(n):
            if remain[i] > 0:
                finish = False
                if remain[i] > quantum:
                    remain[i] -= quantum
                    t += quantum
                else:
                    t += remain[i]
                    waiting_t[i] = t - burst_t[i]
                    remain[i] = 0

            if waiting_t[i] < 0:
                ilb += abs(waiting_t[i])
                waiting_t[i] = 0

        if finish:
            break

def turnaround_time(processes, n, burst_time, waiting, turnaround, quantum):
   for i in range(n):
       turnaround[i] = burst_time[i] + waiting[i]
       
def response_time(n,burst_time,quantum):
    # response = 0
    # list_responses = []
    # for i in range(1,n):
    #     if quantum > 
    pass
        

def RR(data,quantum):
    processes = data['process_id']
    burst_time = data['burst_time']
    n = len(processes)
    waiting_t = [0] * n
    turn_around_t = [0] * n
    
    waiting_time(processes, n, burst_time, waiting_t, quantum)
    turnaround_time(processes, n, burst_time, waiting_t, turn_around_t,quantum)

    total_waiting_time = sum(waiting_t)
    total_run_around_t = sum(turn_around_t)
    total_burst_time = sum(burst_time)

    
    average_waiting_time = total_waiting_time*get_cpu_time_unit()/n
    average_turnarounf_time = total_run_around_t*get_cpu_time_unit()/n

    return{
        'n':str(n),
        'awt': "%.4f" % average_waiting_time,
        'avtat':"%.4f" % average_turnarounf_time,
        'ilb':ilb
    }

