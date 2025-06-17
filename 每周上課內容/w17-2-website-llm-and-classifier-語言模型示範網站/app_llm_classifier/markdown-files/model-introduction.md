# QwenForClassifier 類別詳解

`QwenForClassifier` 是一個用於文本分類的神經網絡模型，它利用了 Qwen 大型語言模型作為基礎，並添加了多層融合和注意力機制來提高分類效果。下面我會逐步解析這個類別的結構和工作原理。

## 1. 初始化函數 `__init__`

```python
def __init__(self, base_model, hidden_size, num_labels=11):
    super(QwenForClassifier, self).__init__()
    # 凍結 base model 的參數
    self.base_model = base_model
    
    for param in self.base_model.parameters():
        param.requires_grad = False
    # ...更多初始化代碼...
```

這個函數接收三個參數：
- `base_model`：預訓練的 Qwen 模型
- `hidden_size`：隱藏層的維度大小
- `num_labels`：分類類別數，預設為11（例如新聞類別）

**範例說明**：
假設我們使用 Qwen2.5-0.5B 模型，它的 `hidden_size` 是 1024，我們想要進行11類新聞分類：
```python
full_model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-instruct")
hidden_size = full_model.config.hidden_size  # 1024
model = QwenForClassifier(full_model.model, hidden_size, num_labels=11)
```

所有基礎模型參數被凍結（`requires_grad = False`），這表示訓練過程中不會更新這些參數，只更新自己添加的分類層參數。

## 2. 注意力池化機制

```python
# 注意力池化機制
self.attention_pooler = nn.Sequential(
    nn.Linear(hidden_size, 128),
    nn.Tanh(),
    nn.Linear(128, 1)
)
```

這部分實現了注意力機制，可以自動學習哪些詞或片段對分類更重要。

**範例說明**：
- 假設文本片段是「台積電今日股價上漲，帶動整體電子類股走強」
- 注意力機制會學習到「台積電」、「股價上漲」、「電子類股」這些詞對於判斷新聞類別（可能是「證券」類別）更為重要，給予更高的權重

## 3. 多層融合權重

```python
# 多層融合權重 (最後4層)
self.layer_weights = nn.Parameter(torch.ones(4) / 4)
```

這創建了一個可訓練的參數，用於加權融合大語言模型最後4層的表示。初始時權重均等（每層0.25）。

**範例說明**：
- 在訓練過程中，模型可能會學到最後一層權重為0.4，倒數第二層為0.3，倒數第三層為0.2，倒數第四層為0.1
- 這反映了不同層次的語義信息對分類任務的貢獻度

## 4. 增強型分類器

```python
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
```

這是一個三層的神經網絡，將高維特徵映射到類別空間：
1. 第一層：將1024維降到256維
2. 第二層：將256維降到128維
3. 第三層：將128維降到類別數

**範例說明**：
如果輸入向量的維度是1024，通過層疊的轉換：
1. 1024 → 256（還包括正規化、非線性激活和丟棄等操作）
2. 256 → 128（同上）
3. 128 → 11（最終輸出11個類別的得分）

## 5. 前向傳播函數 `forward`

```python
def forward(self, input_ids, attention_mask=None, labels=None):
    # 獲取所有隱藏層狀態
    outputs = self.base_model(
        input_ids=input_ids, 
        attention_mask=attention_mask,
        output_hidden_states=True
    )
    # ...更多前向傳播代碼...
```

這個函數處理輸入的文本（已轉換為token ID），並依次執行以下步驟：

### 5.1 獲取並融合多層表示

```python
# 獲取最後4層隱藏狀態
hidden_states = outputs.hidden_states
if hidden_states is None:
    # 使用最後一層
    sequence_output = outputs.last_hidden_state
else:
    # 融合最後4層
    last_layers = hidden_states[-4:] if len(hidden_states) >= 4 else hidden_states[1:]
    layer_weights = F.softmax(self.layer_weights[:len(last_layers)], dim=0)
    
    # 加權融合多層特徵
    sequence_output = torch.zeros_like(last_layers[0])
    for i, layer in enumerate(last_layers):
        sequence_output += layer_weights[i].unsqueeze(-1).unsqueeze(-1) * layer
```

**範例說明**：
假設模型有12層，這段代碼會：
1. 獲取最後4層（第9、10、11、12層）的輸出
2. 對這些層的輸出按學習到的權重進行加權求和
3. 例如：最終表示 = 0.3×層9 + 0.2×層10 + 0.2×層11 + 0.3×層12

### 5.2 注意力池化

```python
# 注意力池化
attention_scores = self.attention_pooler(sequence_output)
attention_probs = F.softmax(attention_scores, dim=1)
context_vector = torch.matmul(attention_probs.transpose(-1, -2), sequence_output).squeeze(1)
```

**範例說明**：
1. 對於文本「疫情影響，台北股市今日大跌」
2. 注意力機制可能會給「台北股市」、「大跌」這些對分類重要的詞賦予更高權重
3. 生成的`context_vector`會更多地反映這些重要詞的特徵

### 5.3 結合池化表示

```python
# 也計算平均池化向量
mean_pooled = torch.mean(sequence_output, dim=1)

# 結合注意力池化和平均池化 (殘差連接)
combined_repr = context_vector + mean_pooled
```

**範例說明**：
1. `mean_pooled`是對整個序列簡單平均，捕捉全局信息
2. `context_vector`是注意力加權的向量，突出重要詞彙
3. `combined_repr`結合了這兩種信息，更全面地表示文本

### 5.4 分類預測與損失計算

```python
# 分類預測
logits = self.classifier(combined_repr)

# 計算損失
loss = None
if labels is not None:
    loss_fct = nn.CrossEntropyLoss()
    loss = loss_fct(logits, labels)
    
return {"loss": loss, "logits": logits}
```

**範例說明**：
1. `logits`是對11個類別的得分，例如：[0.1, 0.2, 0.05, 0.5, ...]
2. 如果提供了標籤，例如"證券"類別（索引3），則計算交叉熵損失
3. 返回包含損失和預測得分的字典

## 實際使用情境

```python
# 預處理文本
text = "台積電今日股價大漲，帶動台股上漲20點"
inputs = tokenizer(text, return_tensors="pt", max_length=512, truncation=True).to(device)

# 模型預測
with torch.no_grad():
    outputs = model(**inputs)

# 獲取預測結果
logits = outputs["logits"]
predicted_class = torch.argmax(logits, dim=1).item()
predicted_label = id_to_label[predicted_class]  # 例如"證券"
```

這個模型設計通過結合大語言模型的多層表示、注意力機制和殘差連接，能夠更好地捕捉文本中對類別判斷重要的特徵，提高分類準確度。