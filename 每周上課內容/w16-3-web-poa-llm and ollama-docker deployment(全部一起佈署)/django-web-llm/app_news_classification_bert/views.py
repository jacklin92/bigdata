'''
requirements:
tensorflow==2.3
transformers==4.6 or above
'''
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


from transformers import BertTokenizer, BertTokenizerFast
from transformers import BertTokenizer, AlbertForSequenceClassification
import numpy as np
import os

# We don't use GPU

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# ----------------
# main steps and global variables

# Load our best trained model
model_path = "clhuang/albert-news-classification"
model = AlbertForSequenceClassification.from_pretrained(model_path)

# Load tokenizer
tokenizer = BertTokenizerFast.from_pretrained('bert-base-chinese')
# tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")





# Category index
news_categories=['政治','科技','運動','證卷','產經','娛樂','生活','國際','社會','文化','兩岸']
idx2cate = { i : item for i, item in enumerate(news_categories)}

# ----------------------
# Functions for Django 
# home
def home(request):
    return render(request, "app_news_classification_bert/home.html")

# api get score
@csrf_exempt
def api_get_news_category(request):
    
    new_text = request.POST.get('input_text')
    #new_text = request.POST['input_text']
    category_prob = get_category_proba(new_text)

    return JsonResponse(category_prob)

# -------------------------------------
# Code copied from jupyter notebook
# get category probability
def get_category_proba( text ):
    max_length = 250
    # prepare token sequence
    inputs = tokenizer([text], padding=True, truncation=True, max_length=max_length, return_tensors="pt")
    # perform inference
    outputs = model(**inputs)
    # get output probabilities by doing softmax
    probs = outputs[0].softmax(1)

    # executing argmax function to get the candidate label index
    label_index = probs.argmax(dim=1)[0].tolist() # convert tensor to int
    # get the label name        
    label = idx2cate[ label_index ]

    # get the label probability
    proba = round(float(probs.tolist()[0][label_index]),2)

    response = {'label': label, 'proba': proba}

    return response
 


print("Loading app bert news classification.")