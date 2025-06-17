from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json  # Add this import at the top of the file

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os
from torch import nn
# from torch import functional as F # 錯誤的導入
import torch.nn.functional as F


# We don't use GPU
#import os
#os.environ['CUDA_VISIBLE_DEVICES'] = '-1'


# Loading app large language model, news classifier and sentiment classifier

# Setting device on GPU if available, else CPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print('Using device:', device)

# Map labels to integers
sentiment_categories=['負面','正面']
sentimentlabel_to_id = { cate : i for i, cate in enumerate(sentiment_categories)}
id_to_sentimentlabel = { i : cate for i, cate in enumerate(sentiment_categories)}

# Convert news category name ('政治','科技','運動',...) into number (0,1,2,...)
news_categories=['政治','科技','運動','證卷','產經','娛樂','生活','國際','社會','文化','兩岸']
newslabel_to_id = { cate : i for i, cate in enumerate(news_categories)}
id_to_newslabel = { i : cate for i, cate in enumerate(news_categories)}

class QwenForClassifier(nn.Module):
    '''
    多層融合：不僅使用最後一層，而是融合了模型最後幾層的表示，獲取更豐富的語義信息
    注意力機制：添加了注意力池化，使模型能更好識別重要詞彙和上下文
    殘差連接：結合了注意力池化和平均池化的結果，保留更全面的信息
    '''
    def __init__(self, base_model, hidden_size, num_labels=11):
        super(QwenForClassifier, self).__init__()
        # 凍結 base model 的參數
        self.base_model = base_model
        
        for param in self.base_model.parameters():
            param.requires_grad = False
            
        # 注意力池化機制
        self.attention_pooler = nn.Sequential(
            nn.Linear(hidden_size, 128),
            nn.Tanh(),
            nn.Linear(128, 1)
        )
        
        # 多層融合權重 (最後4層)
        self.layer_weights = nn.Parameter(torch.ones(4) / 4)
        
        # 增強型分類器
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size, 256),
            nn.LayerNorm(256),
            nn.GELU(),
            nn.Dropout(0.2),
            
            nn.Linear(256, 128),
            nn.LayerNorm(128),
            nn.GELU(),
            nn.Dropout(0.1),
            
            nn.Linear(128, num_labels)
        )
        
        # 保存配置
        self.config = base_model.config
        self.config.num_labels = num_labels
    
    def forward(self, input_ids, attention_mask=None, labels=None):
        # 獲取所有隱藏層狀態
        outputs = self.base_model(
            input_ids=input_ids, 
            attention_mask=attention_mask,
            output_hidden_states=True
        )
        
        # 獲取最後4層隱藏狀態
        hidden_states = outputs.hidden_states
        if hidden_states is None:
            # 如果模型沒有返回hidden_states，使用last_hidden_state
            last_hidden = outputs.last_hidden_state
            sequence_output = last_hidden
        else:
            # 融合最後4層 (或可用層數)
            last_layers = hidden_states[-4:] if len(hidden_states) >= 4 else hidden_states[1:]
            # layer_weights = torch.softmax(self.layer_weights[:len(last_layers)], dim=0)
            layer_weights = F.softmax(self.layer_weights[:len(last_layers)], dim=0)
            
            # 加權融合多層特徵
            sequence_output = torch.zeros_like(last_layers[0])
            for i, layer in enumerate(last_layers):
                sequence_output += layer_weights[i].unsqueeze(-1).unsqueeze(-1) * layer
        
        # 注意力池化
        attention_scores = self.attention_pooler(sequence_output)
        #attention_probs = torch.softmax(attention_scores, dim=1)
        attention_probs = F.softmax(attention_scores, dim=1)
        context_vector = torch.matmul(attention_probs.transpose(-1, -2), sequence_output).squeeze(1)
        
        # 也計算平均池化向量
        mean_pooled = torch.mean(sequence_output, dim=1)
        
        # 結合注意力池化和平均池化 (殘差連接)
        combined_repr = context_vector + mean_pooled
            
        # 分類預測
        logits = self.classifier(combined_repr)
        
        # 計算損失
        loss = None
        if labels is not None:
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(logits, labels)
            
        return {"loss": loss, "logits": logits}
    
    def save_model(self, output_dir=None):
        """保存分類器權重和配置"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存分類器權重
        classifier_path = os.path.join(output_dir, "classifier_weights.pt")
        model_dict = {
            'classifier': self.classifier.state_dict(),
            'attention_pooler': self.attention_pooler.state_dict(),
            'layer_weights': self.layer_weights,
            'config': {
                'num_labels': self.config.num_labels,
                'hidden_size': self.config.hidden_size
            }
        }
        torch.save(model_dict, classifier_path)
        print(f"已保存分類器權重至 {classifier_path}")
    
    def load_model(self, model_dir, device=None):
        """載入分類器權重"""
        if device is None:
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            
        classifier_path = os.path.join(model_dir, "classifier_weights.pt")
        if os.path.exists(classifier_path):
            model_dict = torch.load(classifier_path, map_location=device, weights_only=True)
            
            # 載入各組件
            self.classifier.load_state_dict(model_dict['classifier'])
            self.attention_pooler.load_state_dict(model_dict['attention_pooler'])
            self.layer_weights.data = model_dict['layer_weights'].to(device)
            
            print(f"已載入分類器權重: {classifier_path}")
            return True
        else:
            print(f"警告: 找不到分類器權重檔案 {classifier_path}")
            return False

# (1)full model initialization
model_id = "Qwen/Qwen2.5-0.5B-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
full_model = AutoModelForCausalLM.from_pretrained(model_id).to(device)
hidden_size = full_model.config.hidden_size
# (2)sentiment classifier model initialization
model_sentiment_classifier = QwenForClassifier(full_model.model, hidden_size, num_labels= len(sentiment_categories))
model_sentiment_classifier = model_sentiment_classifier.to(device)
model_path_sentiment = "trained_sentiment_classifier_v4-5epochs-acc0.93"
model_sentiment_classifier.load_model(model_path_sentiment, device=device)
# (3)news classifier model initialization
hidden_size = full_model.config.hidden_size
model_news_classifier = QwenForClassifier(full_model.model, hidden_size, num_labels= len(news_categories))
model_news_classifier = model_news_classifier.to(device)
model_path_news = "trained_news_classifier_v3-6epochs-acc0.90"
model_news_classifier.load_model(model_path_news, device=device)

def predict_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(device)
    with torch.no_grad():
        outputs = model_sentiment_classifier(**inputs)
    probs = torch.softmax(outputs['logits'], dim=1)
    prediction = id_to_sentimentlabel[ probs.argmax().item() ]
    confidence = probs.max().item()
    return prediction, confidence

def predict_news_category(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(device)
    with torch.no_grad():
        outputs = model_news_classifier(**inputs)
    probs = torch.softmax(outputs['logits'], dim=1)
    prediction = id_to_newslabel[ probs.argmax().item() ]
    confidence = probs.max().item()
    return prediction, confidence

# Function to make predictions
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
    # logits = outputs.logits
    logits = outputs["logits"]  # 取出 logits
    
    
    probabilities = torch.nn.functional.softmax(logits, dim=-1)
    
    # Get the predicted class (0: negative, 1: positive)
    predicted_class = torch.argmax(probabilities, dim=-1).item()
    
    # Get the class name using id_to_label
    predicted_label = id_to_sentimentlabel[predicted_class]
    
    # Get the confidence score
    confidence = probabilities[0][predicted_class].item()
    
    return {
        "text": text,
        "classification": predicted_label,
        "confidence": round(confidence,2),
        "probabilities": {
            id_to_sentimentlabel[i]: round(prob.item(),2) for i, prob in enumerate(probabilities[0])
        }
    }

# Function to make predictions
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
    # logits = outputs.logits
    logits = outputs["logits"]  # 取出 logits
    
    
    probabilities = torch.nn.functional.softmax(logits, dim=-1)
    
    # Get the predicted class (0: negative, 1: positive)
    predicted_class = torch.argmax(probabilities, dim=-1).item()
    
    # Get the class name using id_to_label
    predicted_label = id_to_newslabel[predicted_class]
    
    # Get the confidence score
    confidence = probabilities[0][predicted_class].item()
    
    return {
        "text": text,
        "classification": predicted_label,
        "confidence": round(confidence,2),
        "probabilities": {
            id_to_newslabel[i]: round(prob.item(),2) for i, prob in enumerate(probabilities[0])
        }
    }

from IPython.display import Markdown
def generate_text(input_prompt, conversation_history=None):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    
    # Add conversation history if provided
    if conversation_history:
        messages.extend(conversation_history)
    else:
        # If no history, just add the current user message
        messages.append({"role": "user", "content": input_prompt})
    
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(device)

    prompt_length = model_inputs['input_ids'].shape[1]

    generated_ids = full_model.generate(
        model_inputs.input_ids,
        attention_mask=model_inputs.attention_mask,  # Added as per previous fix
        max_new_tokens=512,
        pad_token_id=tokenizer.eos_token_id
    )
    response = tokenizer.decode(generated_ids[0][prompt_length:], skip_special_tokens=True)
    return response

# home
def home_sentiment(request):
    return render(request, "app_llm_classifier/home-sentiment.html")



# api get sentiment score
@csrf_exempt
def api_get_sentiment(request):
    '''
    {'text': '我覺得這個產品很好用',
    'classification': '正面',
    'confidence': 0.99,
    'probabilities': {'負面': 0.01, '正面': 0.99}}
    '''
    
    input_text = request.POST.get('input_text')
    #input_text = request.POST['input_text']
    print(input_text)

    # See the content_type and body從前端送過來的資料格式
    print(request.content_type)
    print(request.body) # byte format

    sentiment_prob = predict_sentiment(input_text)

    return JsonResponse(sentiment_prob)


def home_news_category(request):
    return render(request, "app_llm_classifier/home-news-category.html")
@csrf_exempt
def api_get_news_category(request):
    
    input_text = request.POST.get('input_text')
    #input_text = request.POST['input_text']
    response = predict_news_category(input_text)

    return JsonResponse(response)

def home_chatbot(request):
    return render(request, "app_llm_classifier/home-text-generation.html")

@csrf_exempt
def api_get_llm_response(request):
    input_text = request.POST.get('input_text')
    conversation_history_json = request.POST.get('conversation_history')
    
    print(input_text)
    
    # Process conversation history if available
    conversation_history = None
    if conversation_history_json:
        try:
            conversation_history = json.loads(conversation_history_json)
            # Don't include the latest user message as it's passed separately
            if conversation_history and len(conversation_history) > 0:
                # Remove the last message if it's from the user (we'll add it again)
                if conversation_history[-1]['role'] == 'user':
                    conversation_history.pop()
        except json.JSONDecodeError:
            print("Error parsing conversation history JSON")
            conversation_history = None
    
    # Generate response with history
    response = generate_text(input_text, conversation_history)

    # Convert the string response into a dictionary format
    response_dict = {
        "response": response,
        "input": input_text
    }

    return JsonResponse(response_dict)




print("Loading app large language model, news classifier and sentiment classifier OK.")
