
from collections import deque

def RR_algorithm(data, quantum):

    pid     = data['process_id'].tolist()
    arrival = data['arrival_time'].tolist()
    burst   = data['burst_time'].tolist()

    n = len(pid)
    remain = burst[:]
    finish_time = [0]*n

    i = 0 
    t = 0
    ready = deque()
    finished = 0

    if n and t < arrival[0]:
        t = arrival[0]
    while i < n and arrival[i] <= t:
        ready.append(i)
        i += 1

    while finished < n:
        if not ready:

            if i < n:
                t = max(t, arrival[i])
                while i < n and arrival[i] <= t:
                    ready.append(i)
                    i += 1
            continue

        p = ready.popleft()
        run = min(quantum, remain[p])
        t += run
        remain[p] -= run

        while i < n and arrival[i] <= t:
            ready.append(i)
            i += 1

        if remain[p] == 0:
            finish_time[p] = t
            finished += 1
        else:
            ready.append(p)


    turnaround = [finish_time[k] - arrival[k] for k in range(n)]
    waiting    = [turnaround[k] - burst[k]     for k in range(n)]
    avg_wait   = sum(waiting)/n
    avg_turn   = sum(turnaround)/n

    return {
        "n":n,
        "avg_waiting": f"{avg_wait:.4f}",
        "avg_turn": f"{avg_turn:.4f}",
        "time": f"{t}"
    }
