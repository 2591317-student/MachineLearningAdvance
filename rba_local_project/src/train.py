"""
SCRIPT CHÍNH - chạy file này để huấn luyện mô hình MLP + Mamdani FIS.

Cách chạy:
    cd src
    python train.py

Yêu cầu: đã đặt file dữ liệu (vd. rba_sample_500k.csv) vào thư mục data/
ở gốc project (xem config.py để biết/đổi tên file mong đợi).

Kết quả (model, pipeline tiền xử lý, các biểu đồ, metrics.json) sẽ được
lưu vào thư mục outputs/.
"""
import json
import os
import sys
import time
import pickle

import torch
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from features import load_raw, engineer_features
from dataset_prep import prepare_splits
from model import train_mlp, evaluate
from visualize import plot_all, METRICS


def main():
    t0 = time.time()

    # ---- 0. Kiểm tra file dữ liệu tồn tại ----
    if not os.path.exists(config.DATA_PATH):
        print(f"[LỖI] Không tìm thấy file dữ liệu tại: {config.DATA_PATH}")
        print(f"      Vui lòng đặt file '{config.DATA_FILENAME}' vào thư mục: {config.DATA_DIR}")
        sys.exit(1)

    print("=" * 70)
    print("1. Đọc dữ liệu & Feature Engineering")
    print("=" * 70)
    df_raw = load_raw(config.DATA_PATH)
    print(f"Đã đọc {len(df_raw):,} dòng từ {config.DATA_PATH}")
    df = engineer_features(df_raw)

    print("\n" + "=" * 70)
    print("2. Chia Train/Val/Test + Fit Mamdani FIS + Scaler + One-Hot")
    print("=" * 70)
    data = prepare_splits(df)
    X_train, X_val, X_test = data["X"]
    y_train, y_val, y_test = data["y"]
    pipeline = data["pipeline"]
    print(f"Train/Val/Test: {len(y_train):,}/{len(y_val):,}/{len(y_test):,}")
    print(f"Tỷ lệ dương (Is Attack IP): {y_train.mean():.4f}")
    print(f"Số chiều input (bao gồm đặc trưng Mamdani FIS): {pipeline['input_dim']}")

    print("\n" + "=" * 70)
    print("3. Huấn luyện MLP + Mamdani FIS")
    print("=" * 70)
    model, device, history = train_mlp(X_train, y_train, X_val, y_val, input_dim=pipeline["input_dim"])

    print("\n" + "=" * 70)
    print("4. Đánh giá trên tập Test")
    print("=" * 70)
    results = evaluate(model, X_test, y_test, device)
    for m in METRICS:
        print(f"  {m:10s}: {results[m]:.4f}")

    print("\n" + "=" * 70)
    print("5. Lưu model, pipeline tiền xử lý, metrics và biểu đồ")
    print("=" * 70)
    torch.save(model.state_dict(), config.MODEL_PATH)
    print(f"Đã lưu model: {config.MODEL_PATH}")

    pipeline_to_save = dict(pipeline)
    with open(config.PIPELINE_PATH, "wb") as f:
        pickle.dump(pipeline_to_save, f)
    print(f"Đã lưu pipeline tiền xử lý: {config.PIPELINE_PATH}")

    with open(config.METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump({m: float(results[m]) for m in METRICS}, f, ensure_ascii=False, indent=2)
    print(f"Đã lưu metrics: {config.METRICS_PATH}")

    plot_all(results, history)

    print(f"\nHoàn tất trong {time.time() - t0:.1f}s. Xem kết quả trong: {config.OUTPUT_DIR}")


if __name__ == "__main__":
    main()
