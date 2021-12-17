from matplotlib.pyplot import yscale
import numpy as np
import pandas as pd
from scipy.sparse import data
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from pprint import pprint
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score

def conv_to_frame(x):
    x_frame = pd.DataFrame(x)
    x_frame = x_frame.iloc[:,:].values
    return(x_frame)

def read_matrix_from_csv(file=""):
    if file != "":
        dataset = pd.read_csv(file)
    else:
        dataset = None
    return(dataset)

def train_split(x,y,test_size=0.2):
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = test_size, random_state = 1)
    return((x_train,x_test,y_train,y_test))

class regression_models():
    def __init__(self,type="linear"):
        self.model = None
        self.type = type
        self.x_scaler = None
        self.y_scaler = None
        self.poly_model = None

    ## This function encodes the independent variables using 1 hot encoder
    ## This will be usefull if independant variables are strings for example
    def encode_indep_var(self,x,col=[]):
        if self.type != "indep_encoder":
            return(x)
        if self.model==None:
            self.model = ColumnTransformer(transformers=[('encoder', OneHotEncoder(), col)], remainder='passthrough')
            x_t = np.array(self.model.fit_transform(x))
        else:
            x_t = np.array(self.model.transform(x))
        return(x_t)

    ## This function encodes the dependant variable into integers
    ## This will be useful if dependant variable is a string
    def encode_dep_var(self,y):
        if self.type != "dep_encoder":
            return(y)
        if self.model==None:
            self.model = LabelEncoder()
            y_tran = self.model.fit_transform(y)
        else:
            y_tran = self.model.transform(y)
        return(y_tran)

    ## This function would be used to fill the missing data
    def fill_missing_data(self,x):
        if self.type != "filler":
            return(x)  
        if self.model==None:
            self.model = SimpleImputer(missing_values=np.nan, strategy='mean')
            x_tran = self.model.fit_transform(x)
        else:
            x_tran = self.model.transform(x)
        return(x_tran)


    ## This function would be used for scale the data using standard scaler
    def scale(self,x):
        if self.type != "scaler":
            return(x)
        if self.model==None:
            self.model = StandardScaler()
            x_tran = self.model.fit_transform(x)
        else:
            x_tran = self.model.transform(x)
        return(x_tran)

    ## This function is used to inverse scale the data which was scaled using
    ## Standard scaler
    def inv_scale(self,x):
        if self.type != "scaler":
            return(x)
        if self.model == None:
            return (x)
        x_tran=self.model.inverse_transform(x)
        return(x_tran)

    ## This function is use to score the regression model using r2 score
    def score(self,y_test,y_pred):
        return(r2_score(y_test, y_pred))

    ## This functions is used to split the data into train and test set
    def train_split(self,x,y,test_size=0.2):
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = test_size, random_state = 0)
        return((x_train,x_test,y_train,y_test))

    ## This function is used to train the chosen regression model
    def train(self,x,y):
        if self.type not in ["linear","polynomial","svr","tree","forest"]:
            return(None)

        if self.type=="linear":
            self.model = LinearRegression()
            self.model.fit(x, y)
        elif self.type=="polynomial":
            self.poly_model = PolynomialFeatures(degree = 4)
            x_poly = self.poly_model.fit_transform(x)
            self.model = LinearRegression()
            self.model.fit(x_poly, y)
        elif self.type=="svr":
            self.x_scaler = StandardScaler()
            self.y_scaler = StandardScaler()
            x_scale = self.x_scaler.fit_transform(x)
            y_scale = self.y_scaler.fit_transform(y.reshape(len(y),1))
            self.model = SVR(kernel = 'rbf')
            y_scale = y_scale.flatten()
            self.model.fit(x_scale, y_scale)

        elif self.type=="tree":
            self.model = DecisionTreeRegressor(random_state = 0)
            self.model.fit(x, y)
        elif self.type=="forest ":
            self.model = RandomForestRegressor(n_estimators = 10, random_state = 0)
            self.model.fit(x, y)

    ## This function is used to predict the data using the chosen trained model
    def predict(self,x):
        if self.type=="polynomial":
            x_poly = self.poly_model.transform(x)
            y_pred = self.model.predict(x_poly)
        elif self.type=="svr":
            x_scale = self.x_scaler.transform(x)
            y_pred = self.model.predict(x_scale)
            y_pred = self.y_scaler.inverse_transform(y_pred.reshape(-1,1))
        else:
            y_pred = self.model.predict(x)
        return(y_pred)

    ## Chooses the best regressor based on R2 score
    def choose_regressor(self,x,y,test_size=0.2):
        (x_train,x_test,y_train,y_test) = self.train_split(x,y,test_size)
        types = ["linear","polynomial","svr","tree","forest"]
        score = 0
        chosen_type = ""
        for type in types:
            self.type = type
            self.train(x_train,y_train)
            y_pred = self.predict(x_test)
            curr_score = self.score(y_test,y_pred)
            print(f"regression {type} has score of {curr_score}")
            if curr_score > score:
                score = curr_score
                chosen_type = type
                print(f"Choosing {type}")

        self.type = chosen_type
        self.train(x_train,y_train)


dataset = read_matrix_from_csv("Data.csv")
x = dataset.iloc[:,:-1].values
y = dataset.iloc[:,-1].values

x = conv_to_frame([1,2,3,4,5,6,7,8,9,10])
y = conv_to_frame([1,4,9,16,25,36,49,64,81,100])


regressor = regression_models()
regressor.choose_regressor(x,y)
y_test = conv_to_frame([12,13,14,20])
pprint(regressor.predict(y_test))

# (cm,a_tran) = encode_categorical_data(a,[0])
# (cm,b_tran) = encode_categorical_data(b,[],cm)

# pprint(a_tran)
# pprint(b_tran)
