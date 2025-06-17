from django.shortcuts import render
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import re

# (1) we can load data using read_csv()
# df is a global variable
# df = pd.read_csv('dataset/cna_news_preprocessed.csv', sep='|')

# (2) we can load data using reload_df_data() function
def reload_df_data():
    # make df be a global variable
    global  df
    df = pd.read_csv('app_user_keyword/dataset/cna_news_preprocessed_12weeks.csv', sep='|')

# We should reload df when necessary
reload_df_data() 

def home(request):
    return render(request, 'app_user_keyword/home.html')

# When POST is used, make this function be exempted from the csrf 
@csrf_exempt
def api_get_top_userkey(request):
    # (1) get keywords, category, condition, and weeks passed from frontend
    userkey = request.POST['userkey']
    cate = request.POST['cate']
    cond = request.POST['cond']
    weeks = int(request.POST['weeks'])
    key = userkey.split()
    
    # (2) make df_query global, so it can be used by other functions
    # global  df_query 

    # (3) filter dataframe
    df_query = filter_dataFrame(key, cond, cate,weeks)
    #print(len(df_query))

    # if df_query is empty, return an error message
    if len(df_query) == 0:
        return JsonResponse({'error': 'No results found for the given keywords.'})
    
    # (4) get frequency data
    key_freq_cat, key_occurrence_cat = count_keyword(df_query, key)
    print(key_occurrence_cat)
    
    # (5) get line chart data
    # key_time_freq = [
    # '{"x": "2019-03-07", "y": 2}',
    # '{"x": "2019-03-08", "y": 2}',
    # '{"x": "2019-03-09", "y": 13}']
    key_time_freq = get_keyword_time_based_freq(df_query)

    # (6) response all data to frontend home page
    response = {
    'key_occurrence_cat': key_occurrence_cat,
    'key_freq_cat': key_freq_cat,
    'key_time_freq': key_time_freq, }

    return JsonResponse(response)


# Searching keywords from "content" column
# Here this function uses df.content column, while filter_dataFrame() uses df.tokens_v2
def filter_dataFrame(user_keywords, cond, cate, weeks):

    # end date: the date of the latest record of news
    end_date = df.date.max()
    
    # start date
    start_date = (datetime.strptime(end_date, '%Y-%m-%d').date() - timedelta(weeks=weeks)).strftime('%Y-%m-%d')

    # (1) proceed filtering: a duration of a period of time
    # 期間條件
    period_condition = (df.date >= start_date) & (df.date <= end_date) 
    
    # (2) proceed filtering: news category
    # 新聞類別條件
    if (cate == "全部"):
        condition = period_condition  # "全部"類別不必過濾新聞種類
    else:
        # category新聞類別條件
        condition = period_condition & (df.category == cate)

    # (3) proceed filtering: keywords 
    # and or 條件
    if (cond == 'and'):
        # query keywords condition使用者輸入關鍵字條件and
        condition = condition & df.content.apply(lambda text: all((qk in text) for qk in user_keywords)) #寫法:all()
    elif (cond == 'or'):
        # query keywords condition使用者輸入關鍵字條件
        condition = condition & df.content.apply(lambda text: any((qk in text) for qk in user_keywords)) #寫法:any()
    # condiction is a list of True or False boolean value
    df_query = df[condition]

    return df_query



# ** How many pieces of news were the keyword(s) mentioned in?
# ** How many times were the keyword(s) mentioned?

# For the query_df, count the occurence and frequency for each category.

# (1) cate_occurence={}  被多少篇新聞報導 How many pieces of news contain the keywords.
# (2) cate_freq={}       被提到多少次? How many times are the keywords mentioned

news_categories = ['政治', '科技', '運動', '證卷', '產經', '娛樂', '生活', '國際', '社會', '文化', '兩岸', '全部']

def count_keyword(df_query, query_keywords):

    cate_occurrence = {}
    cate_freq = {}
    
    # 字典初始化
    for cate in news_categories:
        cate_occurrence[cate] = 0   # {'政治':0, '科技':0}
        cate_freq[cate] = 0
        

    for idx, row in df_query.iterrows():
        # count the number of articles各類別篇數統計
        cate_occurrence[row.category] += 1  #   {'政治':+1, '科技':0}
        cate_occurrence['全部'] += 1
        
        # count the keyword frequency各類別次數統計
        # 計算這一篇文章的content中重複含有多少個這些關鍵字(頻率)
        freq = sum([ len(re.findall(keyword, row.content, re.I)) for keyword in query_keywords] ) 
        cate_freq[row.category] += freq # 在該新聞類別中累計頻率
        cate_freq['全部'] += freq  # 在"全部"類別中累計頻率

    return cate_freq, cate_occurrence


def get_keyword_time_based_freq(df_query):
    date_samples = df_query.date
    query_freq = pd.DataFrame({'date_index': pd.to_datetime(date_samples), 'freq': [1 for _ in range(len(df_query))]})
    data = query_freq.groupby(pd.Grouper(key='date_index', freq='D')).sum()
    time_data = []
    for i, idx in enumerate(data.index):
        row = {'x': idx.strftime('%Y-%m-%d'), 'y': int(data.iloc[i].freq)}
        time_data.append(row)
    return time_data

print("app_user_keyword was loaded!")

