#!/bin/sh
# 使用 sh 殼程式來執行這個腳本

# 啟動 Ollama 伺服器，並在背景執行
ollama serve &

# 持續檢查直到伺服器準備好
# until curl -s http://localhost:11434 > /dev/null; do
#   echo "Waiting for Ollama server..."  # 顯示等待訊息
#   sleep 1  # 每秒檢查一次
# done

# 等待 10 秒，讓伺服器有時間啟動（因為我們沒辦法確認伺服器狀態）
echo "等待伺服器啟動中..."
sleep 10

# 當伺服器啟動完成後，自動拉取 gemma3:1b 模型
ollama pull gemma3:1b
#ollama pull gemma3:4b

# 為了讓容器保持運行，不自動結束，執行無限等待
tail -f /dev/null
