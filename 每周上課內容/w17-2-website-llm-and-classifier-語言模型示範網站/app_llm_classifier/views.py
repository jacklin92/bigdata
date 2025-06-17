from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json  
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch.nn.functional as F
import markdown

from .custom_qwen_model import QwenForClassifier

# If we don't use GPU, we can set the environment variable to disable it
# os.environ['CUDA_VISIBLE_DEVICES'] = '-1'


# Loading app large language model, news classifier and sentiment classifier

# Setting device on GPU if available, else CPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print('Using device:', device)


# 根據設備選擇適當的資料類型
dtype = torch.float16 if device.type == 'cuda' else torch.float32
print(f"使用資料類型: {dtype}")

# Map labels to integers
sentiment_categories=['負面','正面']
sentimentlabel_to_id = { cate : i for i, cate in enumerate(sentiment_categories)}
id_to_sentimentlabel = { i : cate for i, cate in enumerate(sentiment_categories)}

# Convert news category name ('政治','科技','運動',...) into number (0,1,2,...)
news_categories=['政治','科技','運動','證卷','產經','娛樂','生活','國際','社會','文化','兩岸']
newslabel_to_id = { cate : i for i, cate in enumerate(news_categories)}
id_to_newslabel = { i : cate for i, cate in enumerate(news_categories)}

# Tokenizer initialization
model_id = "Qwen/Qwen2.5-0.5B-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
# Model initialization
full_model = AutoModelForCausalLM.from_pretrained(model_id).to(device)
#full_model = AutoModelForCausalLM.from_pretrained(model_id,torch_dtype=dtype).to(device)
hidden_size = full_model.config.hidden_size

# Sentiment classifier model initialization
model_sentiment_classifier = QwenForClassifier(full_model.model, hidden_size, num_labels=len(sentiment_categories))
model_path_sentiment = "app_llm_classifier/trained_models/trained_sentiment_classifier_v4-5epochs-acc0.93"
model_sentiment_classifier.load_model(model_path_sentiment, device=device)
model_sentiment_classifier = model_sentiment_classifier.to(device) # 移動到設備
#model_sentiment_classifier = model_sentiment_classifier.to(device, dtype=dtype) # 移動到設備

# News classifier model initialization
model_news_classifier = QwenForClassifier(full_model.model, hidden_size, num_labels=len(news_categories))
model_path_news = "app_llm_classifier/trained_models/trained_news_classifier_v3-6epochs-acc0.90"
model_news_classifier.load_model(model_path_news, device=device)
#model_news_classifier = model_news_classifier.to(device, dtype=dtype)
model_news_classifier = model_news_classifier.to(device)

# Function to make sentiment predictions
def predict_sentiment(text):
    # Tokenize the input text
    inputs = tokenizer(
        text,
        max_length=512,
        truncation=True,
        return_tensors="pt"
    ).to(device)
    
    # Get model predictions
    with torch.no_grad():
        outputs = model_sentiment_classifier(**inputs)
    
    # Extract logits and apply softmax to get probabilities
    logits = outputs["logits"]  
    probabilities = F.softmax(logits, dim=-1)
    
    # Get the predicted class and label
    predicted_class = torch.argmax(probabilities, dim=-1).item()
    predicted_label = id_to_sentimentlabel[predicted_class]
    
    # Get the confidence score
    confidence = probabilities[0][predicted_class].item()
    
    return {
        "text": text,
        "classification": predicted_label,
        "confidence": round(confidence, 2),
        "probabilities": {
            id_to_sentimentlabel[i]: round(prob.item(), 2) for i, prob in enumerate(probabilities[0])
        }
    }

# Function to make news category predictions
def predict_news_category(text):
    # Tokenize the input text
    inputs = tokenizer(
        text,
        max_length=512,
        truncation=True,
        return_tensors="pt"
    ).to(device)
    
    # Get model predictions
    with torch.no_grad():
        outputs = model_news_classifier(**inputs)
    
    # Extract logits and apply softmax to get probabilities
    logits = outputs["logits"]
    probabilities = F.softmax(logits, dim=-1)
    
    # Get the predicted class and label
    predicted_class = torch.argmax(probabilities, dim=-1).item()
    predicted_label = id_to_newslabel[predicted_class]
    
    # Get the confidence score
    confidence = probabilities[0][predicted_class].item()
    
    return {
        "text": text,
        "classification": predicted_label,
        "confidence": round(confidence, 2),
        "probabilities": {
            id_to_newslabel[i]: round(prob.item(), 2) for i, prob in enumerate(probabilities[0])
        }
    }

# Generate text using the LLM
def generate_text(messages):
    """
    Generate response text using the model.
    """
    text_chat_template = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    print("text_chat_templte:", text_chat_template)
    
    model_inputs = tokenizer([text_chat_template], return_tensors="pt").to(device)
    prompt_length = model_inputs['input_ids'].shape[1]

    generated_ids = full_model.generate(
        model_inputs.input_ids,
        attention_mask=model_inputs.attention_mask,
        max_new_tokens=512,
        pad_token_id=tokenizer.eos_token_id
    )
    response = tokenizer.decode(generated_ids[0][prompt_length:], skip_special_tokens=True)
    return response

# Function to handle sentiment prediction
def home_sentiment(request):
    return render(request, "app_llm_classifier/home-sentiment.html")

@csrf_exempt
def api_get_sentiment(request):
    input_text = request.POST.get('input_text')
    print(input_text)
    print(request.content_type)
    print(request.body)

    sentiment_prob = predict_sentiment(input_text)
    return JsonResponse(sentiment_prob)

# Function to handle news category prediction
def home_news_category(request):
    return render(request, "app_llm_classifier/home-news-category.html")

@csrf_exempt
def api_get_news_category(request):
    input_text = request.POST.get('input_text')
    response = predict_news_category(input_text)
    return JsonResponse(response)

# Function to handle text generation using LLM
def home_chatbot(request):
    return render(request, "app_llm_classifier/home-text-generation.html")

@csrf_exempt
def api_get_llm_response(request):
    input_text = request.POST.get('input_text')
    conversation_history_json = request.POST.get('conversation_history')
    
    print("input_text", input_text)
    print("conversation_history_json", conversation_history_json)
    
    # Process conversation history if available
    conversation_history = []
    if conversation_history_json:
        try:
            conversation_history = json.loads(conversation_history_json)
        except json.JSONDecodeError:
            print("Error parsing conversation history JSON")
            conversation_history = []
    
    # Prepare messages for the model
    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    
    # Add conversation history if provided
    if conversation_history:
        messages.extend(conversation_history)
    
    # Always add the current user message
    messages.append({"role": "user", "content": input_text})
    
    print("messages:", messages)
    
    # Generate response with the prepared text
    response = generate_text(messages)
    print("response:", response)
    
    # Convert the string response into a dictionary format
    response_dict = {
        "response": response,
        "input": input_text
    }

    return JsonResponse(response_dict)


def model_introduction(request):
    # Read the markdown file
    markdown_file_path = 'app_llm_classifier/markdown-files/model-introduction.md'
    # Read the markdown file
    with open(markdown_file_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(markdown_content, extensions=['fenced_code', 'codehilite'])
    
    # Pass the HTML content to the template
    context = {
        'html_content': html_content
    }
    
    return render(request, "app_llm_classifier/model-introduction.html", context)

print("Loading app large language model, news classifier and sentiment classifier OK.")
