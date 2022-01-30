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



def train_split(x,y,test_size=0.2):
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = test_size, random_state = 1)
    return((x_train,x_test,y_train,y_test))


# ## creates a tensor a which is a constant
# a = tf.constant(20)
# ## Creates a 4*4 matrix with value 10
# a = tf.fill((4,4),10)

# ## Creats a 4*4 matrix with zeros
# a = tf.zeros((4,4))

# ## Creates a 4*4 matrix with ones
# b = tf.ones((4,4))

# ## Creates a 4*4 matrix with mean = 0 and standard deviation =1
# c = tf.random.normal((4,4))

# ## Matrix multiplication 
# d = tf.matmul(b,c)

## Finding missing data in an input
## pd.isnull().sum().tolist()

## Distribution plot for example house prices
## sns.distplot(df['price'])

## Count plot for example counting number of bedrooms
## sns.countplot(df['bedrooms'])

## Finding out hot spots of price for example in lat and long
## sns.scatterplot(x="long",y="lat",data=df,hue="price",edgecolor=None,alpha=0.2,palette='RdYlGn')

## Sorting data frame using price (Get top 20)
## df.sort_values('price',ascending=False).head(20)

## Filter out top 1% of houses which prices are outliers 
## df.sort_values('price',ascending=False).iloc[<based on len of data frame find starting point>:]

## dropping a coloumn from the data frame
## df.drop('id',axis=1)

## Converte data time
## df['date'] = pd.to_datetime(df['date'])

## feature engineer 
## df['month'] = df['date'].appy(lambda date:date.month)

## pd group by and mean
## Groups the entries by month and find the mean of the price
## df.groupby('month').mean()['price']

## Drop based on certain conditions
## df.drop(df['age'] > 21)

## Correlation plots with respect to a output
## df.corr()['benign_0__mal_1'].sort_values().plot(kind="bar")

## Correlation with everything to everything 
## sns.heatmap(df.corr())

path = "/Users/ragban01/learning_materials/TF2/DATA"

df = pd.read_csv(f"{path}/kc_house_data.csv")
x = df.iloc[:,1:3].values
y = df.iloc[:,0].values



(x_train,x_test,y_train,y_test) = train_split(x,y)

model = StandardScaler()
x_train = model.fit_transform(x_train)
x_test = model.transform(x_test)



model = Sequential()
model.add(Dense(4,activation="relu"))
model.add(Dense(4,activation="relu"))
model.add(Dense(4,activation="relu"))
model.add(Dense(1))

model.compile(optimizer="rmsprop",loss="mse")
model.fit(x=x_train,y=y_train,epochs=250,verbose=0)

model.evaluate(x_test,y_test)

y_pred = model.predict(x_test)
y_pred = pd.DataFrame(y_pred,columns=["Pred"])
y_test = pd.DataFrame(y_test,columns=["Test"])
plot_data = pd.concat([y_test,y_pred],axis=1)
sns.scatterplot(x="Test",y="Pred",data=plot_data)
plt.show()

mean_absolute_error(y_test,y_pred)
mean_squared_error(y_test,y_pred)

model.save("fake_model")
model1 = load_model("fake_model")