# RBA Risk Detection — MLP + Mamdani Fuzzy Inference System

Phát hiện đăng nhập rủi ro (dự đoán `Is Attack IP`) trên bộ dữ liệu RBA
(Risk-Based Authentication), kết hợp **MLP** với **Mamdani Fuzzy Inference
System** (fuzzification → rule evaluation → aggregation (max) →
defuzzification (centroid)).

## 1. Cấu trúc thư mục

```
rba_local_project/
├── data/                        <-- ĐẶT FILE DATASET RBA VÀO ĐÂY
│   └── rba_sample_500k.csv      (hoặc tên file bạn đổi trong src/config.py)
├── src/
│   ├── config.py                # đường dẫn + hyperparameters
│   ├── features.py               # feature engineering
│   ├── fuzzy_mamdani.py          # Mamdani Fuzzy Inference System
│   ├── dataset_prep.py           # chia train/val/test + fit pipeline
│   ├── model.py                  # kiến trúc MLP + train/evaluate
│   ├── visualize.py               # vẽ biểu đồ (loss, F1, ROC, PR, confusion matrix...)
│   ├── train.py                  # *** SCRIPT CHÍNH ĐỂ CHẠY TRAINING ***
│   └── inference.py              # load model đã train, dự đoán dữ liệu mới
├── outputs/                     # model, biểu đồ, metrics sẽ được lưu ở đây
├── requirements.txt
└── README.md
```

## 2. Cài đặt

```bash
cd rba_local_project
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Đặt dữ liệu

Copy file dataset RBA của bạn (ví dụ `rba_sample_500k.csv`) vào thư mục:

```
rba_local_project/data/rba_sample_500k.csv
```

Nếu file của bạn có tên khác, mở `src/config.py` và sửa dòng:
```python
DATA_FILENAME = "rba_sample_500k.csv"   # <-- đổi thành tên file của bạn
```

Dataset cần có tối thiểu các cột: `Login Timestamp`, `User ID`,
`Round-Trip Time [ms]`, `Country`, `City`, `ASN`, `Device Type`,
`Browser Name and Version`, `OS Name and Version`, `Login Successful`,
`Is Attack IP`.

## 4. Chạy huấn luyện

```bash
cd src
python train.py
```

Script sẽ tự động:
1. Đọc dữ liệu + feature engineering
2. Chia train/val/test (70/15/15, stratified)
3. Fit Mamdani FIS + StandardScaler + OneHotEncoder trên tập train
4. Huấn luyện MLP (early stopping theo AUPRC trên tập validation)
5. Đánh giá trên tập test
6. Lưu vào thư mục `outputs/`:
   - `mlp_mamdani_model.pt` — trọng số mô hình
   - `preprocessing_pipeline.pkl` — scaler/encoder/ngưỡng fuzzy (cần cho inference)
   - `metrics.json` — các chỉ số Accuracy/Precision/Recall/F1/AUROC/AUPRC
   - `training_curves.png` — loss & AUPRC/AUROC theo epoch
   - `metrics_bar_chart.png` — biểu đồ cột các chỉ số
   - `confusion_matrix.png`
   - `roc_pr_curves.png` — ROC Curve & Precision-Recall Curve
   - `threshold_curve.png` — Precision/Recall/F1 theo ngưỡng phân loại

Có thể chỉnh số epoch, batch size, kiến trúc mạng... trong `src/config.py`.

## 5. Test / Dự đoán với dữ liệu mới (sau khi đã train)

```bash
cd src
python inference.py
```

File này load model + pipeline đã lưu (không train lại) và chạy demo với
2 kịch bản giả định (rủi ro cao / rủi ro thấp). Bạn có thể import hàm
`predict_risk()` từ `inference.py` vào script khác của mình để dự đoán
cho dữ liệu thật:

```python
from inference import load_pipeline_and_model, predict_risk

model, pipeline = load_pipeline_and_model()
result = predict_risk(your_dataframe, model, pipeline)
print(result[["attack_probability", "predicted_label"]])
```

**Lưu ý:** `your_dataframe` phải là dữ liệu đã qua bước
`features.engineer_features()` (tức đã có đủ các cột như `is_new_country`,
`user_success_rate_so_far`, `time_since_last_login_h`...), vì các đặc
trưng này phụ thuộc vào lịch sử đăng nhập trước đó của từng user.

## 6. Vì sao target là `Is Attack IP`?

- `Is Account Takeover` chỉ có ~4 mẫu dương trên 500k dòng → không đủ để train/test.
- `Login Successful` phản ánh lỗi đăng nhập kỹ thuật hơn là rủi ro bảo mật.
- `Is Attack IP` (~3% dương tính) là target chuẩn, thực tế nhất cho bài toán chấm điểm rủi ro.

Muốn đổi target, sửa `TARGET_COLUMN` trong `src/config.py`.
