from timeit import default_timer as timer

CPU_TIME_UNIT = None

def calculate():
    start = timer()
    temp = sum(range(1_000_000))
    end = timer()

    return end-start # Benchmark


def get_cpu_time_unit():
    global CPU_TIME_UNIT
    if not CPU_TIME_UNIT:
        CPU_TIME_UNIT = calculate()
    return CPU_TIME_UNIT