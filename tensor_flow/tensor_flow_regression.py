from numpy import mod
import pandas as pd
import seaborn as sns
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.python.framework.ops import colocate_with
from sklearn.metrics import mean_absolute_error,mean_squared_error
from tensorflow.keras.models import load_model

path = "/Users/ragban01/learning_materials/TF2/DATA"
df = pd.read_csv(f"{path}/kc_house_data.csv")

## Dropping of features which might not impact the outcome
df = df.drop('id',axis=1)
df = df.drop('zipcode',axis=1)

## Feature engineering extract month/year to see if they can have correlation to the price
df['date'] = pd.to_datetime(df['date'])
df['month'] = df['date'].apply(lambda date:date.month)
df['year'] = df['date'].apply(lambda date:date.year)
df = df.drop('date',axis=1)

## Remove the outliers which breaks the model accuracy
df = df.sort_values('price',ascending=False).iloc[216:,]

x = df.drop('price',axis=1).values
y = df['price'].values
y = y.reshape(-1,1)

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.3, random_state = 1)

scaler = StandardScaler()
x_train = scaler.fit_transform(x_train)
x_test = scaler.transform(x_test)

model = Sequential()
model.add(Dense(19,activation="relu"))
model.add(Dense(19,activation="relu"))
model.add(Dense(19,activation="relu"))
model.add(Dense(19,activation="relu"))
model.add(Dense(1))
model.compile(optimizer="adam",loss="mse")
## Validation_data we try to make sure we dont over fit
## At the end of the run, we can run this to check there is not overfitting
## pd.DataFrame(model.history.history).plot()
model.fit(x=x_train,y=y_train,epochs=1000,batch_size=128,validation_data=(x_test,y_test))

y_pred = model.predict(x_test)

