from django.shortcuts import render
import ollama
import sys
import time
import argparse
import os
import requests
import json
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt

# 設置遠程 Ollama 模型的基礎 URL
REMOTE_OLLAMA_URL = "http://163.18.22.32:11435"

model_name = "gemma3:4b" # 默認模型名稱
#model_name = "llama3:latest"
#model_name = "deepseek-r1:7b"  

# 創建客戶端實例
client = ollama.Client(host=REMOTE_OLLAMA_URL)

# Function to handle text generation using LLM
def home(request):
    return render(request, "app_ollama_usage/home.html")

@csrf_exempt
def api_ollama_chat(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    input_text = request.POST.get('input_text')
    conversation_history_json = request.POST.get('conversation_history', '[]')
    stream_mode = request.POST.get('stream', 'false').lower() == 'true'
    print(f"stream_mode: {stream_mode}")
    
    try:
        # 解析對話歷史
        conversation_history = json.loads(conversation_history_json)
        
        # 將用戶新的輸入添加到對話歷史
        user_message = {
            'role': 'user',
            'content': input_text
        }
        
        # 把歷史轉換為Ollama格式的messages
        messages = []
        for msg in conversation_history:
            # 只添加已經存在的消息，新的用戶消息會在下面添加
            if msg['role'] == 'user' and msg['content'] == input_text:
                continue
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        # 添加當前的用戶消息
        messages.append({
            'role': user_message['role'],
            'content': user_message['content']
        })
        
        # 處理流模式請求
        if stream_mode:
            def generate_stream():
                if len(messages) <= 1:
                    # 如果沒有歷史對話，就使用基本的generate方法
                    for chunk in client.generate(model=model_name, prompt=input_text, stream=True):
                        if 'response' in chunk:
                            # 確保正確格式化SSE事件
                            yield f"data: {json.dumps({'response': chunk['response']})}\n\n"
                else:
                    # 使用chat方法處理有歷史的對話
                    for chunk in client.chat(model=model_name, messages=messages, stream=True):
                        if 'message' in chunk and 'content' in chunk['message']:
                            # 確保正確格式化SSE事件
                            yield f"data: {json.dumps({'response': chunk['message']['content']})}\n\n"
            
            response = StreamingHttpResponse(generate_stream(), content_type='text/event-stream')
            response['Cache-Control'] = 'no-cache'
            response['X-Accel-Buffering'] = 'no'
            return response
        else:
            # 非流模式請求
            if len(messages) <= 1:
                response = client.generate(model=model_name, prompt=input_text)
                return JsonResponse({'response': response['response']})
            else:
                response = client.chat(model=model_name, messages=messages)
                return JsonResponse({'response': response['message']['content']})
    
    except Exception as e:
        print(f"Error in Ollama chat API: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
