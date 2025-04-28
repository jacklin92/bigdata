from django.http import JsonResponse
from django.shortcuts import render
import pandas as pd


def load_data():
    # Read data from csv file
    df_data = pd.read_csv("app_person_fan/dataset/Trump_data.csv", sep=",")
    global response
    response = dict(list(df_data.values))
    del df_data


# load pk data
load_data()


def home(request):
    return render(request,'app_person_fan/home.html', response)



print("app_person_fan was loaded!")
