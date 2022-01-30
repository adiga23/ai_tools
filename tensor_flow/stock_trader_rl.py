import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pprint import pprint


# Let's use AAPL (Apple), MSI (Motorola), SBUX (Starbucks)
def get_data():
  # returns a T x 3 list of stock prices
  # each row is a different stock
  # 0 = AAPL
  # 1 = MSI
  # 2 = SBUX
  path = "/Users/ragban01/machine_learning_examples/tf2.0"
  df = pd.read_csv(f'{path}/aapl_msi_sbux.csv')
  return df.values

a = get_data()

pprint(a)


