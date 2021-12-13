import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Import  the csv
dataset = pd.read_csv("Position_Salaries.csv")
## Getting the feature variables which is the information used for machine learning
x = dataset.iloc[:,1:-1].values
## Getting the dependant variable which is the output decesion
y = dataset.iloc[:,-1].values

print(x)

from sklearn.ensemble import RandomForestRegressor
regressor = RandomForestRegressor(n_estimators = 500, random_state = 0)
regressor.fit(x, y)

print(regressor.predict([[6.5]]))

x_grid = np.arange(min(x), max(x), 0.01)
x_grid = x_grid.reshape((len(x_grid), 1))
plt.scatter(x, y, color = 'red')
plt.plot(x_grid, regressor.predict(x_grid), color = 'blue')
plt.title('Truth or Bluff (Random Forest Regression)')
plt.xlabel('Position level')
plt.ylabel('Salary')
plt.show()