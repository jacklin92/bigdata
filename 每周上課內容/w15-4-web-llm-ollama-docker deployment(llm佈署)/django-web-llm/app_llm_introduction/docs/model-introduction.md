# QwenForClassifier 模型說明與教學

## 一、模型大步驟概念介紹

本模型是基於大型語言模型（如 Qwen2.5-0.5B-instruct）的**情緒分類器**，採用**多層融合**與**QKV注意力池化**，並結合**平均池化**與**殘差連接**，最後經過多層分類器進行分類。

### 整體流程：

1. **特徵提取**：從基礎語言模型取得所有隱藏層（hidden states）。
2. **多層融合**：將最後 N 層（如 4 層）隱藏狀態進行加權融合，獲得更豐富的語義特徵。
3. **QKV 注意力池化**：將融合後的特徵進行 QKV 投影，計算自注意力，獲得序列的語義重點表示。
4. **平均池化**：對融合特徵做平均，保留全局語義。
5. **殘差連接**：將 QKV 注意力池化結果與平均池化結果相加，融合局部與全局特徵。
6. **分類器**：經過多層神經網絡，輸出最終分類結果。

---

## 二、詳細步驟說明與展示

### 1. 特徵提取與多層融合

```python
# 取得所有隱藏層
outputs = self.base_model(
    input_ids=input_ids, 
    attention_mask=attention_mask,
    output_hidden_states=True
)
hidden_states = outputs.hidden_states  # [num_layers, batch, seq_len, hidden_size]

# 取最後 N 層
last_layers = hidden_states[-self.num_fusion_layers:]  # N=4

# 層權重 softmax
layer_weights = F.softmax(self.layer_weights, dim=0)  # [num_fusion_layers]

# 加權融合
sequence_output = torch.zeros_like(last_layers[0])  # [batch, seq_len, hidden_size]
for i, layer in enumerate(last_layers):
    sequence_output += layer_weights[i].unsqueeze(-1).unsqueeze(-1) * layer
```

### 2. QKV 注意力池化

```python
# Q, K, V 線性投影
Q = self.q_proj(sequence_output)  # [batch, seq_len, hidden_size]
K = self.k_proj(sequence_output)
V = self.v_proj(sequence_output)

# 計算注意力分數
attn_scores = torch.matmul(Q, K.transpose(-2, -1)) / (Q.size(-1) ** 0.5)  # [batch, seq_len, seq_len]
attn_probs = F.softmax(attn_scores, dim=-1)  # [batch, seq_len, seq_len]

# 加權求 context 向量
context_vector_qkv = torch.matmul(attn_probs, V)  # [batch, seq_len, hidden_size]

# 池化（平均所有 token）
context_vector_qkv = context_vector_qkv.mean(dim=1)  # [batch, hidden_size]
```

### 3. 平均池化

```python
mean_pooled = torch.mean(sequence_output, dim=1)  # [batch, hidden_size]
```

### 4. 殘差連接（融合 QKV 與平均池化）

```python
combined_repr = context_vector_qkv + mean_pooled  # [batch, hidden_size]
```

### 5. 分類器預測

```python
logits = self.classifier(combined_repr)  # [batch, num_labels]
```

### 6. 損失計算（訓練時）

```python
loss = None
if labels is not None:
    loss_fct = nn.CrossEntropyLoss()
    loss = loss_fct(logits, labels)
return {"loss": loss, "logits": logits}
```

---

## 三、圖解與重點

- **多層融合**：讓模型同時利用不同層的語義特徵，提升泛化能力。
- **QKV 注意力池化**：自動學習關注序列中最重要的 token，提升語義聚焦能力。
- **平均池化**：保留全局語義，避免只聚焦於局部。
- **殘差連接**：融合局部重點與全局語義，提升模型穩定性與表達力。
- **多層分類器**：增強非線性映射能力，提升分類準確率。

---

## 四、總結

本模型結合了**多層融合**、**QKV注意力池化**、**平均池化**與**殘差連接**等現代 NLP 技術，能有效提升文本分類的準確率，適合用於教學與實務應用。