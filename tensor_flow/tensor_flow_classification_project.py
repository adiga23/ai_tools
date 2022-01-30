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
import numpy as np

def feat_info(col_name):
    print(data_info.loc[col_name]['Description'])

path = "/Users/ragban01/learning_materials/TF2/DATA"

data_info = pd.read_csv(f'{path}/lending_club_info.csv',index_col='LoanStatNew')
print(data_info.loc['revol_util']['Description'])
df = pd.read_csv(f'{path}/lending_club_loan_two.csv')

## Data analysis 
## Count plot of output classification
sns.countplot(df['loan_status'])

## Histogram of loan amount
sns.displot(df['loan_amnt'])

## Correlations
sns.heatmap(df.corr(),annot=True,cmap="viridis")

## Scatter plots to show highly correlated data
sns.scatterplot(x="installment",y="loan_amnt",data=df)

## calculate relation between loan_amount and loan_status
sns.boxplot(x="loan_status",y="loan_amnt",data=df)
df.groupby('loan_status')['loan_amnt'].describe()

## unique values in a columns
df['grade'].unique()

## Hue plots 
ordered_subgrade = sorted(df['sub_grade'].unique())
sns.countplot(x='sub_grade',data=df,order=ordered_subgrade,palette="coolwarm",hue="loan_status")

## Zooming on f and g
f_and_g = df[(df['grade'] == "F") | (df['grade'] == "G")]
ordered_subgrade = sorted(f_and_g['sub_grade'].unique())
sns.countplot(x='sub_grade',data=f_and_g,order=ordered_subgrade,palette="coolwarm",hue="loan_status")

## Convert output lable
df["loan_repaid"] = df["loan_status"].apply(lambda x : 1 if (x == "Fully Paid") else 0)

## Correlation for output variable
df.corr()['loan_repaid'].sort_values()[:-1].plot(kind="bar")

## Data Pre processing
## Missing Data
## a = df.isnull().sum() : Returns a panda series which is like a dictonary

## Remove emp_title
## Reasoning, if you do len(df['emp_title'].unique()) its almost half the data set
## which means there are a huge amount of categories, so we need to remove this feature
df = df.drop("emp_title",axis=1)

## Reasoning behind removing employment length
## Sorting employment length
## sorted(df["emp_length"].dropna().unique())
## Find out what is the percent of people repaid the loan in all categories of employment lenght
## If they are similar, then this feature really does not give much information
## loan_repaid = df[df["loan_repaid"] == 1].groupby('emp_length').count()['loan_status']
## loan_unpaid = df[df["loan_repaid"] == 1].groupby("emp_length").count()['loan_status']
## per = loan_repaid / (loan_repaid + loan_unpaid)
df = df.drop("emp_length",axis=1)

## Reasoning behind removing title
## title provides similar information as purpose so it can be removed
## Also title has 48k categories, so it does not make sense to have it
df = df.drop("title",axis=1)

## Value counts of a certain feature
## df['mort_acc'].value_counts()
## To fill in missing data of mort_acc, we know there is correlation with total_acc
## First find the mean of the mort_acc for a category of total acc
a = df.groupby('total_acc').mean()['mort_acc']
## Fill the the missing data with relation to this
df['mort_acc'] = df.apply(lambda x : a[x['total_acc']] if (np.isnan(x['mort_acc'])) else x['mort_acc'],axis=1)


## Rest of the data is small so we can just drop it
df = df.dropna()

## Selecting columns which are strings
#df.select_dtypes(['object']).columns

## Convert term into integer
df['term'] = df['term'].apply(lambda x : int(x[:3]))

## Grade can be dropped
df = df.drop('grade',axis=1)

## Creating dummies for sub_grade
a = pd.get_dummies(df['sub_grade'],drop_first=True)
df = pd.concat([df.drop('sub_grade',axis=1),a],axis=1)

a = pd.get_dummies(df['verification_status'],drop_first=True)
df = pd.concat([df.drop('verification_status',axis=1),a],axis=1)

a = pd.get_dummies(df['purpose'],drop_first=True)
df = pd.concat([df.drop('purpose',axis=1),a],axis=1)

a = pd.get_dummies(df['initial_list_status'],drop_first=True)
df = pd.concat([df.drop('initial_list_status',axis=1),a],axis=1)

a = pd.get_dummies(df['application_type'],drop_first=True)
df = pd.concat([df.drop('application_type',axis=1),a],axis=1)

## Category ANY NONE are so less, first move to other and then create a dummy
df['home_ownership'] = df['home_ownership'].replace(['ANY','NONE'],'OTHER')

a = pd.get_dummies(df['home_ownership'],drop_first=True)
df = pd.concat([df.drop('home_ownership',axis=1),a],axis=1)

df['zip_code'] = df['address'].apply(lambda x:x[-5:])
df = df.drop('address',axis=1)

a = pd.get_dummies(df['zip_code'],drop_first=True)
df = pd.concat([df.drop('zip_code',axis=1),a],axis=1)

df = df.drop('issue_d',axis=1)

df['earliest_cr_line'] = df['earliest_cr_line'].apply(lambda x:int(x[-4:]))

df = df.drop("loan_status",axis=1)

## Taking a sample of data (10% here)
# df = df.sample(frac=0.1)

x = df.drop("loan_repaid",axis=1).values
y = df['loan_repaid'].values

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 1)

scaler = StandardScaler()
x_train = scaler.fit_transform(x_train)
x_test = scaler.transform(x_test)

model = Sequential()
model.add(Dense(78,activation="relu"))
model.add(Dropout(0.2))
model.add(Dense(36,activation="relu"))
model.add(Dropout(0.2))
model.add(Dense(19,activation="relu"))
model.add(Dropout(0.2))

model.add(Dense(1,activation="sigmoid"))

model.compile(optimizer="adam",loss="binary_crossentropy")
early_stop = EarlyStopping(monitor='val_loss',verbose=1,patience=25,mode='min')

model.fit(x_train,y_train,epochs=600,validation_data=(x_test,y_test),callbacks=[early_stop],batch_size=256)