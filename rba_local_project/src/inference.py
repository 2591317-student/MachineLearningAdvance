"""
Load model + pipeline đã lưu (sau khi chạy train.py) để dự đoán cho dữ liệu mới,
KHÔNG cần train lại.

Cách chạy demo:
    cd src
    python inference.py

Lưu ý: nhiều đặc trưng (is_new_country, user_success_rate_so_far,
time_since_last_login_h, ...) phụ thuộc vào lịch sử đăng nhập TRƯỚC ĐÓ của
user. Để dự đoán một lượt đăng nhập mới, bạn cần cung cấp đủ các cột đặc
trưng này (xem features.FEATURE_COLUMNS_NUMERIC / FEATURE_COLUMNS_CATEGORICAL).
"""
import os
import sys
import pickle

import torch
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from model import MLPClassifier, to_tensor
from fuzzy_mamdani import MamdaniFuzzyRiskSystem
from features import FEATURE_COLUMNS_NUMERIC, FEATURE_COLUMNS_CATEGORICAL


def load_pipeline_and_model():
    if not os.path.exists(config.MODEL_PATH) or not os.path.exists(config.PIPELINE_PATH):
        raise FileNotFoundError(
            f"Chưa tìm thấy model/pipeline đã train. Hãy chạy `python train.py` trước.\n"
            f"  Model mong đợi tại : {config.MODEL_PATH}\n"
            f"  Pipeline mong đợi tại: {config.PIPELINE_PATH}"
        )
    with open(config.PIPELINE_PATH, "rb") as f:
        pipeline = pickle.load(f)

    model = MLPClassifier(pipeline["input_dim"])
    model.load_state_dict(torch.load(config.MODEL_PATH, map_location="cpu"))
    model.eval()
    return model, pipeline


def predict_risk(raw_rows: pd.DataFrame, model, pipeline, threshold: float = 0.5) -> pd.DataFrame:
    """raw_rows: DataFrame chứa các cột đặc trưng thô (đã qua engineer_features,
    TRƯỚC khi scale/one-hot/fuzzy). Trả về DataFrame gốc kèm cột
    'attack_probability' và 'predicted_label'."""
    fis = MamdaniFuzzyRiskSystem()
    fis.thresholds_ = pipeline["fis_thresholds"]
    fis.minmax_ = pipeline["fis_minmax"]
    fz = fis.transform(raw_rows)

    cat = pd.DataFrame(
        pipeline["ohe"].transform(raw_rows[FEATURE_COLUMNS_CATEGORICAL]),
        columns=pipeline["cat_cols"], index=raw_rows.index,
    )
    num = pd.DataFrame(
        pipeline["scaler"].transform(raw_rows[FEATURE_COLUMNS_NUMERIC]),
        columns=FEATURE_COLUMNS_NUMERIC, index=raw_rows.index,
    )
    X_new = pd.concat([num, cat, fz], axis=1)[pipeline["input_columns"]]

    model.eval()
    with torch.no_grad():
        probs = torch.sigmoid(model(to_tensor(X_new))).numpy()

    out = raw_rows.copy()
    out["attack_probability"] = probs
    out["predicted_label"] = (probs >= threshold).astype(int)
    return out


def _demo():
    """Demo: test model với 2 kịch bản tự tạo (rủi ro cao / rủi ro thấp).
    Chạy sau khi đã có model.pt + pipeline.pkl (tức đã chạy train.py)."""
    from features import load_raw, engineer_features

    model, pipeline = load_pipeline_and_model()

    if not os.path.exists(config.DATA_PATH):
        print(f"Không tìm thấy {config.DATA_PATH} để lấy dòng mẫu làm khuôn mẫu kịch bản demo.")
        return

    df_raw = load_raw(config.DATA_PATH)
    df = engineer_features(df_raw)
    template = df.iloc[[0]].copy()

    scenario_high_risk = template.copy()
    for col in ["is_new_country", "is_new_city", "is_new_asn", "is_new_device",
                "is_new_browser", "is_new_os", "is_odd_hour"]:
        scenario_high_risk[col] = 1
    scenario_high_risk["num_changes"] = 6
    scenario_high_risk["time_since_last_login_h"] = 5000
    scenario_high_risk["user_success_rate_so_far"] = 0.2
    scenario_high_risk["country_rarity"] = 0.99
    scenario_high_risk["asn_rarity"] = 0.99

    scenario_low_risk = template.copy()
    for col in ["is_new_country", "is_new_city", "is_new_asn", "is_new_device",
                "is_new_browser", "is_new_os", "is_odd_hour"]:
        scenario_low_risk[col] = 0
    scenario_low_risk["num_changes"] = 0
    scenario_low_risk["time_since_last_login_h"] = 24
    scenario_low_risk["user_success_rate_so_far"] = 1.0
    scenario_low_risk["country_rarity"] = 0.05
    scenario_low_risk["asn_rarity"] = 0.05

    scenarios = pd.concat([scenario_high_risk, scenario_low_risk])
    scenarios.index = ["Kịch bản: RỦI RO CAO (giả định)", "Kịch bản: RỦI RO THẤP (giả định)"]

    result = predict_risk(scenarios, model, pipeline)
    print(result[["attack_probability", "predicted_label"]])


if __name__ == "__main__":
    _demo()
