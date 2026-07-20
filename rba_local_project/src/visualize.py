"""
Vẽ các biểu đồ đánh giá học máy: training curves, bar chart metrics,
confusion matrix, ROC, Precision-Recall, Precision/Recall/F1 theo threshold.
Tất cả biểu đồ được lưu vào thư mục outputs/.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, precision_recall_curve

from config import OUTPUT_DIR

METRICS = ["AUROC", "AUPRC", "Accuracy", "Precision", "Recall", "F1"]


def plot_training_curves(history, save_name="training_curves.png"):
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    axes[0].plot(history["epoch"], history["train_loss"], marker="o", color="#2563eb")
    axes[0].set_xlabel("Epoch"); axes[0].set_ylabel("Train Loss (BCE)")
    axes[0].set_title("Training Loss theo Epoch")

    axes[1].plot(history["epoch"], history["val_auprc"], marker="o", label="Validation AUPRC", color="#16a34a")
    axes[1].plot(history["epoch"], history["val_auroc"], marker="s", label="Validation AUROC", color="#dc2626")
    axes[1].set_xlabel("Epoch"); axes[1].set_ylabel("Score")
    axes[1].set_title("Validation AUPRC & AUROC theo Epoch")
    axes[1].legend()

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, save_name)
    plt.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Đã lưu: {path}")


def plot_metrics_bar(results, save_name="metrics_bar_chart.png"):
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["#2563eb", "#16a34a", "#f59e0b", "#dc2626", "#7c3aed", "#0891b2"]
    values = [results[m] for m in METRICS]
    bars = ax.bar(METRICS, values, color=colors)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Điểm số")
    ax.set_title("Các chỉ số đánh giá mô hình MLP + Mamdani FIS (Test set)")
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.02, f"{v:.3f}", ha="center", fontsize=9)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, save_name)
    plt.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Đã lưu: {path}")


def plot_confusion_matrix(results, save_name="confusion_matrix.png"):
    cm = results["confusion_matrix"]
    fig, ax = plt.subplots(figsize=(5.5, 5))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(["Dự đoán: Bình thường", "Dự đoán: Tấn công"])
    ax.set_yticklabels(["Thực tế: Bình thường", "Thực tế: Tấn công"])
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{cm[i, j]:,}", ha="center", va="center",
                     color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=13, fontweight="bold")
    ax.set_title("Confusion Matrix (Test set)")
    plt.colorbar(im, ax=ax, fraction=0.046)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, save_name)
    plt.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Đã lưu: {path}")


def plot_roc_pr_curves(results, save_name="roc_pr_curves.png"):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fpr, tpr, _ = roc_curve(results["y_true"], results["probs"])
    axes[0].plot(fpr, tpr, color="#2563eb", label=f"MLP + Mamdani FIS (AUC={results['AUROC']:.3f})")
    axes[0].plot([0, 1], [0, 1], "k--", alpha=0.3)
    axes[0].set_xlabel("False Positive Rate"); axes[0].set_ylabel("True Positive Rate")
    axes[0].set_title("ROC Curve"); axes[0].legend()

    prec, rec, _ = precision_recall_curve(results["y_true"], results["probs"])
    baseline_rate = results["y_true"].mean()
    axes[1].plot(rec, prec, color="#16a34a", label=f"MLP + Mamdani FIS (AP={results['AUPRC']:.3f})")
    axes[1].axhline(baseline_rate, color="k", linestyle="--", alpha=0.3, label=f"Random baseline ({baseline_rate:.3f})")
    axes[1].set_xlabel("Recall"); axes[1].set_ylabel("Precision")
    axes[1].set_title("Precision-Recall Curve"); axes[1].legend()

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, save_name)
    plt.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Đã lưu: {path}")


def plot_threshold_curve(results, save_name="threshold_curve.png"):
    prec_arr, rec_arr, thresh_arr = precision_recall_curve(results["y_true"], results["probs"])
    f1_arr = 2 * prec_arr[:-1] * rec_arr[:-1] / np.maximum(prec_arr[:-1] + rec_arr[:-1], 1e-9)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(thresh_arr, prec_arr[:-1], label="Precision", color="#2563eb")
    ax.plot(thresh_arr, rec_arr[:-1], label="Recall", color="#dc2626")
    ax.plot(thresh_arr, f1_arr, label="F1", color="#16a34a")
    best_idx = int(np.argmax(f1_arr))
    ax.axvline(thresh_arr[best_idx], color="gray", linestyle="--",
               label=f"Ngưỡng F1 tốt nhất = {thresh_arr[best_idx]:.3f}")
    ax.set_xlabel("Ngưỡng phân loại (threshold)"); ax.set_ylabel("Điểm số")
    ax.set_title("Precision / Recall / F1 theo ngưỡng phân loại")
    ax.legend()
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, save_name)
    plt.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Đã lưu: {path}")

    print(f"Ngưỡng cho F1 tốt nhất: {thresh_arr[best_idx]:.3f} -> "
          f"Precision={prec_arr[best_idx]:.3f}, Recall={rec_arr[best_idx]:.3f}, F1={f1_arr[best_idx]:.3f}")


def plot_all(results, history):
    plot_training_curves(history)
    plot_metrics_bar(results)
    plot_confusion_matrix(results)
    plot_roc_pr_curves(results)
    plot_threshold_curve(results)
