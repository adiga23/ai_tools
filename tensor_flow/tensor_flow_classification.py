from numpy import mod
import pandas as pd
import seaborn as sns
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense,Dropout
from tensorflow.python.framework.ops import colocate_with
from sklearn.metrics import mean_absolute_error,mean_squared_error
from tensorflow.keras.models import load_model
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import classification_report,confusion_matrix

path = "/Users/ragban01/learning_materials/TF2/DATA"
df = pd.read_csv(f"{path}/cancer_classification.csv")

x = df.drop("benign_0__mal_1",axis=1).values
y = df['benign_0__mal_1'].values

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 1)

scaler = StandardScaler()
x_train = scaler.fit_transform(x_train)
x_test = scaler.transform(x_test)

model = Sequential()
model.add(Dense(30,activation="relu"))
model.add(Dropout(0.5))
model.add(Dense(15,activation="relu"))
model.add(Dropout(0.5))

# Binary Classification. The output is predicting the probability of being 0/1
# Multiple classification. The output should be one hot encoded, 
# model.add(Dense(<number of classes>,activation="softmax"))
model.add(Dense(1,activation="sigmoid"))

## For multple classification use loss="categorical_crossentropy"
model.compile(optimizer="adam",loss="binary_crossentropy")

early_stop = EarlyStopping(monitor='val_loss',verbose=1,patience=25,mode='min')

model.fit(x_train,y_train,epochs=600,validation_data=(x_test,y_test),callbacks=[early_stop])

predictions = model.predict_classes(x_test)

classification_report(y_test,predictions)
confusion_matrix(y_test,predictions)