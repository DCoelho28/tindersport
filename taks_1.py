import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import numpy as np
import math

#data to use from the X_train.csv file
data = pd.read_csv('./X_train.csv')

print(f"data set size: {len(data)}")
# data clean up, removing the big amount of uneccessary 0.0
data_clean = data[(data['x_1'] != 0.0) | (data['y_1'] != 0.0) |
            (data['x_2'] != 0.0) | (data['y_2'] != 0.0) |
            (data['x_3'] != 0.0) | (data['y_3'] != 0.0)]
print(f"data_clean set size: {len(data_clean)}")

output_path = ('./data.csv')
# data_clean.to_csv(output_path,index=False)

# initial positions -> t=0.0
initial_positions = data_clean[(data_clean['t'] == 0.0)]
print(f"initial_positions set size: {len(initial_positions)}")

# group by positions to have unique initial positions
unique_initial_positions = initial_positions.drop_duplicates(subset=['x_1', 'y_1', 'x_2', 'y_2', 'x_3', 'y_3'])

output_path = ('./unique_initial_positions.csv')
# unique_initial_positions.to_csv(output_path,index=False)

print(f"unique_initial_positions set size: {len(unique_initial_positions)}")


comecaIndex = np.hstack((data_clean[data_clean.t == 0.0].index.values))
print(comecaIndex)
acabaIndex = np.hstack((data_clean[data_clean.t == 0.0].index.values - 1, data_clean.iloc[-1]['Id']))
print(acabaIndex)

comeca_as_DataFrame = pd.DataFrame({'comeca': comecaIndex})
# output_path = ('./comeca.csv')
comeca_as_DataFrame.to_csv(output_path,index=False)

data_clean.loc[:, ['x1_initial_position', 'y1_initial_position', 'x2_initial_position', 'y2_initial_position', 'x3_initial_position', 'y3_initial_position']] = 0.0
#completed_data = pd.DataFrame()
for j in range(comecaIndex.size):
    data_clean.loc[comecaIndex[j]:acabaIndex[j+1], ['x1_initial_position', 'y1_initial_position', 'x2_initial_position', 'y2_initial_position', 'x3_initial_position', 'y3_initial_position']] = data.loc[comecaIndex[j], ['x_1', 'y_1', 'x_2', 'y_2', 'x_3', 'y_3']].values 

#print("------------------")
print(f"data_clean set size: {len(data_clean)}")

data_clean = data_clean.drop(columns=['v_x_1', 'v_y_1', 'v_x_2', 'v_y_2', 'v_x_3', 'v_y_3'], inplace=False)
# a prof diz que t > 0.0
data_clean = data_clean[(data_clean['t'] != 0.0)]
coluna_Id = data_clean.pop('Id')
data_clean.insert(0, 'Id', coluna_Id) #Isto pq?

output_path = ('./data_clean.csv')
# data_clean.to_csv(output_path,index=False)

#80% to train, 10% to test, 10% to val
train, val = train_test_split(data_clean, test_size=0.2, random_state=42)

test = pd.read_csv('./X_test.csv')
cols = ['Id','t','x1_initial_position', 'y1_initial_position', 'x2_initial_position', 'y2_initial_position', 'x3_initial_position', 'y3_initial_position']
test.columns=cols

print(f"Train set size: {len(train)}")
print(f"Validation set size: {len(val)}")
print(f"Test set size: {len(test)}")
print(f"Total before clean =  1285002")

################################################################################################

#dados de entrada
features_X = ['x1_initial_position', 'y1_initial_position', 'x2_initial_position', 'y2_initial_position', 'x3_initial_position', 'y3_initial_position', 't']
#o que queremos prever 
y = ['x_1', 'y_1', 'x_2', 'y_2', 'x_3', 'y_3']

entry_train = train[features_X]
output_train = train[y]

entry_test  = test[features_X]
# output_test = test[y]

entry_val = val[features_X]
output_val = val[y]

#Pipeline pedida pela prof com standardscaler (padronização dos dados) e linear regression
pipeline = Pipeline([('scaler', StandardScaler()),
             ('linear_regression', LinearRegression())])

pipeline.fit(entry_train, output_train)

output_train_prediction = pipeline.predict(entry_train)
output_val_prediction = pipeline.predict(entry_val)
output_test_prediction = pipeline.predict(entry_test)

columns = ['x_1', 'y_1', 'x_2', 'y_2', 'x_3', 'y_3']
# Create a DataFrame from the predicted values
df_output = pd.DataFrame(output_test_prediction, columns=columns)
# Add a column for the 'id' values
df_output['id'] = df_output.index
# Reorder the columns to match the desired format
df_output = df_output[['id', 'x_1', 'y_1', 'x_2', 'y_2', 'x_3', 'y_3']]
#df_output = pd.DataFrame({'predicted_values': output_test_prediction})
output_path = ('./baseline-model.csv')
df_output.to_csv(output_path,index=False)
#output_path = r'C:\Users\vidcoelh\Documents\Pessoal\AA\output_test_prediction.csv'
#output_test_prediction.to_csv(output_path,index=False)

rmse_train =  math.sqrt(mean_squared_error(output_train, output_train_prediction))
rmse_val = math.sqrt(mean_squared_error(output_val, output_val_prediction))
# rmse_test = math.sqrt(mean_squared_error(output_test, output_test_prediction))

#se o MSE do dado de treino for muito menor que o MSE de validação e de treino --> modelo está a sofrer overfitting (modelo ajusta-se demasiado aos dados de treino)
print(f"Train RMSE: {rmse_train}")
print(f"Validation RMSE: {rmse_val}")
# print(f"Test RMSE: {rmse_test}")

def plot_y_yhat(y_val,y_pred, plot_title = "plot"):
    labels = ['x_1','y_1','x_2','y_2','x_3','y_3']
    MAX = 500
    if len(y_val) > MAX:
        idx = np.random.choice(len(y_val),MAX, replace=False)
    else:
        idx = np.arange(len(y_val))
    plt.figure(figsize=(10,10))
    for i in range(6):
        x0 = np.min(y_val[idx,i])
        x1 = np.max(y_val[idx,i])
        plt.subplot(3,2,i+1)
        plt.scatter(y_val[idx,i],y_pred[idx,i])
        plt.xlabel('True '+labels[i])
        plt.ylabel('Predicted '+labels[i])
        plt.plot([x0,x1],[x0,x1],color='red')
        plt.axis('square')
    plt.savefig(plot_title+'.pdf')
    plt.show()
    
    
plot_y_yhat(np.array(output_val), output_val_prediction, plot_title="y_yhat_val")
plot_y_yhat(np.array(output_train), output_train_prediction, plot_title="y_yhat_test")
