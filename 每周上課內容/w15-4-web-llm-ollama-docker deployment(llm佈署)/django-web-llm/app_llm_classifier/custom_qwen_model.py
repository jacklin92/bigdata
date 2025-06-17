import torch
import os
import torch.nn.functional as F
from torch import nn

class QwenForClassifier(nn.Module):
    def __init__(self, base_model, hidden_size, num_labels, num_fusion_layers=4):
        super(QwenForClassifier, self).__init__()
        # 指定基礎模型 來自於外部指定的模型
        self.base_model = base_model
        
        # 融合權重多少層 (可調整層數)
        self.num_fusion_layers = num_fusion_layers
        # 保存config配置
        self.config = base_model.config
        self.config.num_labels = num_labels
        
        # 凍結 base model 的參數
        for param in self.base_model.parameters():
            param.requires_grad = False
        
        # 多層融合權重 (最後4層)
        # 初始值是0.25，訓練後模型可能會學到最後一層權重為0.4，倒數第二層為0.3，倒數第三層為0.2，倒數第四層為0.1
        self.layer_weights = nn.Parameter(torch.ones(num_fusion_layers) / num_fusion_layers)
            
        # 新增 QKV 線性層
        self.q_proj = nn.Linear(hidden_size, hidden_size)
        self.k_proj = nn.Linear(hidden_size, hidden_size)
        self.v_proj = nn.Linear(hidden_size, hidden_size)
        
        # 增強型分類器
        # 這是一個三層的神經網絡，將高維特徵映射到類別空間：
        #     1. 第一層：將1024維降到256維
        #     2. 第二層：將256維降到128維
        #     3. 第三層：將128維降到類別數量
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
        
    
    def forward(self, input_ids, attention_mask=None, labels=None):
        # 獲取所有隱藏層狀態
        outputs = self.base_model(
            input_ids=input_ids, 
            attention_mask=attention_mask,
            output_hidden_states=True # 設置為True以獲取所有隱藏層狀態
        )
        
        # outputs 是一個包含多個元素的元組
        hidden_states = outputs.hidden_states # 有24層的隱藏狀態 維度是
        # 獲取最後4層隱藏狀態
        
        last_layers = hidden_states[-self.num_fusion_layers:] # 取得最後4層的隱藏狀態 維度是 (batch_size, seq_len, hidden_size) 
        layer_weights = F.softmax(self.layer_weights, dim=0) # 將權重轉換為概率分佈 維度是 (num_fusion_layers,)
        # 加權融合最後4層特徵
        sequence_output = torch.zeros_like(last_layers[0]) # 初始化為0，維度是 (batch_size, seq_len, hidden_size)
        for i, layer in enumerate(last_layers):
            sequence_output += layer_weights[i].unsqueeze(-1).unsqueeze(-1) * layer # 將權重擴展到 (batch_size, seq_len, hidden_size)
    
        # ===== QKV Attention Pooling =====
        # [batch, seq_len, hidden_size]
        Q = self.q_proj(sequence_output)
        K = self.k_proj(sequence_output)
        V = self.v_proj(sequence_output)
        # Attention scores: [batch, seq_len, seq_len]
        attn_scores = torch.matmul(Q, K.transpose(-2, -1)) / (Q.size(-1) ** 0.5)
        attn_probs = F.softmax(attn_scores, dim=-1)
        # Context vector: [batch, seq_len, hidden_size]
        context_vector_qkv = torch.matmul(attn_probs, V).mean(dim=1)  # [batch, hidden_size]

        # ===== mean pooling =====
        mean_pooled = torch.mean(sequence_output, dim=1)

        # ===== 融合 QKV context 與 mean_pooled =====
        combined_repr = context_vector_qkv + mean_pooled

        # 分類預測
        logits = self.classifier(combined_repr) # 維度是 (batch_size, num_labels)
        
        # 計算損失
        loss = None
        if labels is not None:
            loss_fct = nn.CrossEntropyLoss() # 計算交叉熵損失
            loss = loss_fct(logits, labels)
            
        return {"loss": loss, "logits": logits}
    
    def save_model(self, output_dir=None):
        """保存分類器權重和配置"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存分類器權重與QKV權重
        classifier_path = os.path.join(output_dir, "classifier_weights.pt")
        model_dict = {
            'classifier': self.classifier.state_dict(),
            'layer_weights': self.layer_weights,
            'q_proj': self.q_proj.state_dict(),
            'k_proj': self.k_proj.state_dict(),
            'v_proj': self.v_proj.state_dict(),
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
            self.layer_weights.data = model_dict['layer_weights'].to(device)
            self.q_proj.load_state_dict(model_dict['q_proj'])
            self.k_proj.load_state_dict(model_dict['k_proj'])
            self.v_proj.load_state_dict(model_dict['v_proj'])
            
            print(f"已載入分類器權重: {classifier_path}")
            return True
        else:
            print(f"警告: 找不到分類器權重檔案 {classifier_path}")
            return False