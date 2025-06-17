from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# We don't use GPU
#import os
#os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# Load model and tokenizer from local
#model_path = "app_sentiment_bert/best-model"
#model = BertForSequenceClassification.from_pretrained(model_path, num_labels=2)
# reload our model/tokenizer. Optional, only usable when in Python files instead of notebooks
# tokenizer = BertTokenizer.from_pretrained(model_path)

# Load model and tokenizer from huggingface
# https://huggingface.co/clhuang
model = AutoModelForSequenceClassification.from_pretrained("clhuang/albert-sentiment")
tokenizer = AutoTokenizer.from_pretrained("clhuang/albert-sentiment") #from huggingface

# home
def home(request):
    return render(request, "app_sentiment_bert/home.html")

# api get sentiment score
@csrf_exempt
def api_get_sentiment(request):
    
    new_text = request.POST.get('input_text')
    #new_text = request.POST['input_text']
    print(new_text)

    # See the content_type and body從前端送過來的資料格式
    print(request.content_type)
    print(request.body) # byte format

    sentiment_prob = get_sentiment_proba(new_text)

    return JsonResponse(sentiment_prob)

# Define prediction function 
# get sentiment probability
def get_sentiment_proba(text):
    max_length=200
    # prepare our text into tokenized sequence
    inputs = tokenizer(text, padding=True, truncation=True, max_length=max_length, return_tensors="pt")
    # perform inference to our model
    outputs = model(**inputs)
    # get output probabilities by doing softmax
    probs = outputs[0].softmax(1)

    response = {'Negative': round(float(probs[0, 0]), 2), 'Positive': round(float(probs[0, 1]), 2)}
    # executing argmax function to get the candidate label
    #return probs.argmax()
    return response



print("Loading app bert sentiment classification.")
