from django.http import JsonResponse
from django.shortcuts import render
import pandas as pd

def load_data_scchen():
    # Read data from csv file
    df_data = pd.read_csv('app_scchen/dataset/chen_shih_chung_data.csv',sep=',')
    global response
    response = dict(list(df_data.values))
    # get the frequency of each category
    response["categroy_frequency"] = list(zip(eval(response["category"]), eval(response["freqByCate"])))
    del df_data

# load data
load_data_scchen()


# get the frequency of each category 
# 讓前端用表格方式顯示 (使用Django Template語法)
'''
          <tbody>
            {% for category, freq in categroy_frequency %}
            <tr>
              <td>{{ category }}</td>
              <td>{{ freq }}</td>
            </tr>
            {% endfor %}
          </tbody>
'''
# print(response)

def home(request):
    return render(request,'app_scchen/home.html', response)

print('app_scchen was loaded!')
