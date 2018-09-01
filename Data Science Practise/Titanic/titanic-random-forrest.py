
import pandas as pd
import numpy as np
import csv as csv
from sklearn.ensemble import RandomForestClassifier



def getData(csv):
    df = pd.read_csv(csv, header=0)
    return df


def addGender(df):
    #Creates a Gender column and populates it with a 0/1 value for Male/Female.
    df['Gender'] = df['Sex'].map( {'female': 0, 'male': 1} ).astype(int)
    return df
    

def addMedianAges(df):
    #Creates AgeFill Column and populates it with Age
    df['AgeFill'] = df['Age']
    
    #Replaces NaN age values with median age for class and gender
    median_ages = np.zeros((2,3))
    for i in range(0, 2):
        for j in range(0, 3):
            median_ages[i,j] = df[(df['Gender'] == i) & (df['Pclass'] == j+1)]['Age'].dropna().median()
    
    for i in range(0, 2):
        for j in range(0, 3):
            df.loc[ (df.Age.isnull()) & (df.Gender == i) & (df.Pclass == j+1),'AgeFill'] = median_ages[i,j]
    
    #Records which rows were back filled
    df['AgeIsNull'] = pd.isnull(df.Age).astype(int)
    
    return df
        

def addFamilySize(df):
    df['FamilySize'] = df['SibSp'] + df['Parch']
    return df


def addAgeByClass(df):
    df['Age*Class'] = df.AgeFill * df.Pclass
    
    return df

def createCleanData(csv):
    
    df = getData(csv)
    df = addGender(df)
    df = addMedianAges(df)
    df = addFamilySize(df)
    df = addAgeByClass(df)
    
    return df
    
def dropNonIntegerValues(df):
    
    df = df.drop(['Name', 'Sex', 'Ticket', 'Cabin', 'Embarked','Fare','Age'], axis=1) 
    
    return df.values
    

test = createCleanData("test.csv")
train = createCleanData("train.csv")


test_data = dropNonIntegerValues(test)
train_data = dropNonIntegerValues(train)

ids = test['PassengerId'].values

print 'Training...'
forest = RandomForestClassifier(n_estimators=100)
forest = forest.fit( train_data[0::,1::], train_data[0::,0] )

print 'Predicting...'
output = forest.predict(test_data).astype(int)


predictions_file = open("myfirstforest.csv", "wb")
open_file_object = csv.writer(predictions_file)
open_file_object.writerow(["PassengerId","Survived"])
open_file_object.writerows(zip(ids, output))
predictions_file.close()
print 'Done.'




    