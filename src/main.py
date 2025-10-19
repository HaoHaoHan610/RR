import pandas as pd
from Round_robin.RR import RR
from Round_robin.CO_RR import RR_algorithm

pd.options.display.max_rows = 100
if __name__ == "__main__":
    data = pd.read_csv("db/data_set.csv")
    output = RR_algorithm(data,2)
    print(output)
    # print(type(data))
    # # print(data)
    # dic = RR(data,4)
    # print(dic)