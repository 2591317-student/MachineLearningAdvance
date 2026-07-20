"""
Kiến trúc MLP (Multi-Layer Perceptron) và vòng lặp huấn luyện/đánh giá.
"""
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import (
    roc_auc_score, average_precision_score, precision_recall_fscore_support,
    accuracy_score, confusion_matrix
)

from config import HIDDEN_DIMS, DROPOUT, EPOCHS, BATCH_SIZE, LEARNING_RATE, EARLY_STOPPING_PATIENCE


class MLPClassifier(nn.Module):
    def __init__(self, input_dim: int, hidden_dims=HIDDEN_DIMS, dropout=DROPOUT):
        super().__init__()
        layers, prev = [], input_dim
        for h in hidden_dims:
            layers += [nn.Linear(prev, h), nn.ReLU(), nn.BatchNorm1d(h), nn.Dropout(dropout)]
            prev = h
        layers += [nn.Linear(prev, 1)]
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x).squeeze(-1)  # logits


def to_tensor(df_or_arr):
    arr = df_or_arr.values if hasattr(df_or_arr, "values") else df_or_arr
    return torch.tensor(arr, dtype=torch.float32)


def train_mlp(X_train, y_train, X_val, y_val, input_dim, epochs=EPOCHS,
              batch_size=BATCH_SIZE, lr=LEARNING_RATE, seed=42, verbose=True):
    torch.manual_seed(seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = MLPClassifier(input_dim).to(device)

    Xtr_t, ytr_t = to_tensor(X_train), to_tensor(y_train)
    Xv_t, yv_t = to_tensor(X_val).to(device), to_tensor(y_val).to(device)
    loader = DataLoader(TensorDataset(Xtr_t, ytr_t), batch_size=batch_size, shuffle=True)

    n_pos = ytr_t.sum().item()
    n_neg = len(ytr_t) - n_pos
    pos_weight = torch.tensor([n_neg / max(n_pos, 1)], device=device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=2)

    best_auprc, best_state, bad = -1, None, 0
    history = {"epoch": [], "train_loss": [], "val_auprc": [], "val_auroc": []}

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            optimizer.zero_grad()
            loss = criterion(model(xb), yb)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * len(xb)
        total_loss /= len(Xtr_t)

        model.eval()
        with torch.no_grad():
            val_probs = torch.sigmoid(model(Xv_t)).cpu().numpy()
        val_auprc = average_precision_score(y_val, val_probs)
        val_auroc = roc_auc_score(y_val, val_probs)
        scheduler.step(val_auprc)

        history["epoch"].append(epoch)
        history["train_loss"].append(total_loss)
        history["val_auprc"].append(val_auprc)
        history["val_auroc"].append(val_auroc)

        if verbose:
            print(f"  Epoch {epoch:2d} | train_loss={total_loss:.4f} | "
                  f"val_AUPRC={val_auprc:.4f} | val_AUROC={val_auroc:.4f}")

        if val_auprc > best_auprc:
            best_auprc = val_auprc
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
            bad = 0
        else:
            bad += 1
            if bad >= EARLY_STOPPING_PATIENCE:
                if verbose:
                    print(f"  Early stopping tại epoch {epoch} (best val_AUPRC={best_auprc:.4f})")
                break

    model.load_state_dict(best_state)
    return model, device, history


def evaluate(model, X, y, device, threshold=0.5):
    model.eval()
    with torch.no_grad():
        probs = torch.sigmoid(model(to_tensor(X).to(device))).cpu().numpy()
    preds = (probs >= threshold).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(y, preds, average="binary", zero_division=0)
    cm = confusion_matrix(y, preds)
    return {
        "AUROC": roc_auc_score(y, probs), "AUPRC": average_precision_score(y, probs),
        "Accuracy": accuracy_score(y, preds), "Precision": precision, "Recall": recall, "F1": f1,
        "probs": probs, "y_true": np.asarray(y), "confusion_matrix": cm,
    }
