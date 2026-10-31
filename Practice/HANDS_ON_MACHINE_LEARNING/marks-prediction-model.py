import numpy as np
from sklearn.linear_model import LinearRegression

#creating the dataset

X = np.array([
    [1],
    [2],
    [3],
    [4],
    [5],
    [6],
    [7],
    [8]
])

Y = np.array([42, 48, 55, 61, 68, 74, 82, 88])

#create the model

model = LinearRegression()

#Train the model

model.fit(X, Y)

#inspect what the model learned

print("Weight: ", model.coef_[0])
print("Bias: ", model.intercept_)


#Predict a score for 5.5 study hours

prediction = model.predict(np.array([[5.5]]))

print("Predicted score: ", prediction[0])


