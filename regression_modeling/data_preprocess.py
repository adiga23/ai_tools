import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Import  the csv
dataset = pd.read_csv("Data.csv")
## Getting the feature variables which is the information used for machine learning
x = dataset.iloc[:,:-1].values
## Getting the dependant variable which is the output decesion
y = dataset.iloc[:,-1].values

##Fill the missing data with the mean
from sklearn.impute import SimpleImputer
imputer = SimpleImputer(missing_values=np.nan, strategy='mean')
x[:,1:3] = imputer.fit_transform(x[:,1:3])

# Encoding categorical data (This is to encode strings into numbers)
# Encoding the Independent Variable
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
# Onehot encoder is needed so that there is no numerical dependancy between these coloums
ct = ColumnTransformer(transformers=[('encoder', OneHotEncoder(), [0])], remainder='passthrough')
x = np.array(ct.fit_transform(x))

# Encoding the Dependent Variable (Convert the decision into numerical order)
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
y = le.fit_transform(y)


# Splitting the dataset into the Training set and Test set
from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 1)
print(x_train)
print(x_test)
print(y_train)
print(y_test)

# Feature Scaling should be done after Splitting because if we do this before the split,
# then mean function will do some information lekage from train to test
# Here for train we fit and transform for test we only transformers
# Meaning we get the mean and standard deviation using the fit on train
# using the above formula, we transform the test
# This is not needed for multiple linear regression model
from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
x_train[:, 3:] = sc.fit_transform(x_train[:, 3:])
x_test[:, 3:] = sc.transform(x_test[:, 3:])
print(x_train)
print(x_test)
