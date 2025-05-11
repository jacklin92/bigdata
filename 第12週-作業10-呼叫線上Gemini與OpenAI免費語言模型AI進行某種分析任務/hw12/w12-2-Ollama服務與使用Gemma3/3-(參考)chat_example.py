import ollama
import sys
import time

# 設置 Ollama 服務器地址
ollama.host = "http://163.18.22.32:11435"

def chat_with_gemma(use_streaming=False):
    """
    簡單的與 Gemma 3-1B 指令調校模型聊天範例。
    執行此腳本前請確保 Ollama 容器已啟動。
    
    參數:
        use_streaming (bool): 是否使用串流模式，即逐字接收回應
    """
    print("與 Gemma 3-1B 聊天 (輸入 'exit' 退出)")
    print("使用模式：", "串流回應" if use_streaming else "完整回應")
    print("-" * 50)
    
    # 開始對話
    messages = []
    
    while True:
        user_input = input("\n您: ")
        if user_input.lower() == 'exit':
            break
        
        # 將用戶訊息添加到對話中
        messages.append({
            'role': 'user',
            'content': user_input
        })
        
        # 從模型獲取回應
        try:
            if use_streaming:
                # 串流模式 - 逐字接收回應
                print("\nGemma: ", end="", flush=True)
                full_response = ""
                
                for chunk in ollama.chat(
                    model='gemma3:4b',
                    messages=messages,
                    stream=True
                ):
                    content = chunk['message']['content']
                    print(content, end="", flush=True)
                    full_response += content
                    # 小延遲以模擬逐字生成效果
                    time.sleep(0.01)
                
                print()  # 換行
                
                # 將助手回應添加到對話歷史
                messages.append({
                    'role': 'assistant',
                    'content': full_response
                })
                
            else:
                # 標準模式 - 等待完整回應
                response = ollama.chat(
                    model='gemma3:4b',
                    messages=messages
                )
                
                assistant_message = response['message']['content']
                print(f"\nGemma: {assistant_message}")
                
                # 將助手回應添加到對話歷史
                messages.append({
                    'role': 'assistant',
                    'content': assistant_message
                })
            
        except Exception as e:
            print(f"錯誤: {e}")
            print("請確保 Ollama 容器正在運行。")

def generate_with_gemma(prompt, use_streaming=False):
    """
    使用 Gemma 3-1B 模型生成單次回應。
    
    參數:
        prompt (str): 提示詞
        use_streaming (bool): 是否使用串流模式
    """
    print(f"提示詞: {prompt}")
    print("-" * 50)
    
    try:
        if use_streaming:
            # 串流模式
            print("回應: ", end="", flush=True)
            for chunk in ollama.generate(
                model='gemma3:4b',
                prompt=prompt,
                stream=True
            ):
                content = chunk['response']
                print(content, end="", flush=True)
                # 小延遲以模擬逐字生成效果
                time.sleep(0.01)
            print("\n")
        else:
            # 標準模式
            response = ollama.generate(
                model='gemma3:4b',
                prompt=prompt
            )
            print(f"回應: {response['response']}\n")
            
    except Exception as e:
        print(f"錯誤: {e}")
        print("請確保 Ollama 容器正在運行。")

if __name__ == "__main__":
    print("Ollama 使用範例")
    print("=" * 50)
    print("1. 對話模式 (完整回應)")
    print("2. 對話模式 (串流回應)")
    print("3. 單次生成 (完整回應)")
    print("4. 單次生成 (串流回應)")
    print("=" * 50)
    
    try:
        choice = int(input("請選擇模式 (1-4): "))
        
        if choice == 1:
            chat_with_gemma(use_streaming=False)
        elif choice == 2:
            chat_with_gemma(use_streaming=True)
        elif choice == 3:
            prompt = input("請輸入提示詞: ")
            generate_with_gemma(prompt, use_streaming=False)
        elif choice == 4:
            prompt = input("請輸入提示詞: ")
            generate_with_gemma(prompt, use_streaming=True)
        else:
            print("無效選擇，請輸入 1-4 之間的數字。")
    except ValueError:
        print("請輸入有效的數字。")
