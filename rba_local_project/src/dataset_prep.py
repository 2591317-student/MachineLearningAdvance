"""
Chia train/val/test (stratified) và fit các bộ tiền xử lý (Mamdani FIS,
StandardScaler, OneHotEncoder) CHỈ trên tập train để tránh leakage.
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder

from config import TARGET_COLUMN, RANDOM_STATE, TEST_SIZE, VAL_TEST_SPLIT
from features import FEATURE_COLUMNS_NUMERIC, FEATURE_COLUMNS_CATEGORICAL
from fuzzy_mamdani import MamdaniFuzzyRiskSystem


def prepare_splits(df: pd.DataFrame):
    """Nhận df đã qua engineer_features(), trả về dict chứa X_train/val/test,
    y_train/val/test, và toàn bộ pipeline tiền xử lý đã fit (để lưu lại dùng
    cho inference sau này)."""
    y = df[TARGET_COLUMN].astype(int).values
    idx = np.arange(len(df))

    idx_train, idx_temp, y_train, y_temp = train_test_split(
        idx, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    idx_val, idx_test, y_val, y_test = train_test_split(
        idx_temp, y_temp, test_size=VAL_TEST_SPLIT, random_state=RANDOM_STATE, stratify=y_temp
    )

    df_train, df_val, df_test = df.iloc[idx_train], df.iloc[idx_val], df.iloc[idx_test]

    # ---- Mamdani FIS: fit CHỈ trên train ----
    fis = MamdaniFuzzyRiskSystem().fit(df_train)
    fz_train, fz_val, fz_test = fis.transform(df_train), fis.transform(df_val), fis.transform(df_test)

    # ---- One-hot Device Type: fit trên train ----
    ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    ohe.fit(df_train[FEATURE_COLUMNS_CATEGORICAL])
    cat_cols = list(ohe.get_feature_names_out(FEATURE_COLUMNS_CATEGORICAL))

    def make_cat(d):
        return pd.DataFrame(ohe.transform(d[FEATURE_COLUMNS_CATEGORICAL]), columns=cat_cols, index=d.index)

    cat_train, cat_val, cat_test = make_cat(df_train), make_cat(df_val), make_cat(df_test)

    # ---- StandardScaler: fit trên train ----
    scaler = StandardScaler()
    num_train = pd.DataFrame(scaler.fit_transform(df_train[FEATURE_COLUMNS_NUMERIC]),
                              columns=FEATURE_COLUMNS_NUMERIC, index=df_train.index)
    num_val = pd.DataFrame(scaler.transform(df_val[FEATURE_COLUMNS_NUMERIC]),
                            columns=FEATURE_COLUMNS_NUMERIC, index=df_val.index)
    num_test = pd.DataFrame(scaler.transform(df_test[FEATURE_COLUMNS_NUMERIC]),
                             columns=FEATURE_COLUMNS_NUMERIC, index=df_test.index)

    X_train = pd.concat([num_train, cat_train, fz_train], axis=1)
    X_val = pd.concat([num_val, cat_val, fz_val], axis=1)
    X_test = pd.concat([num_test, cat_test, fz_test], axis=1)

    pipeline = {
        "scaler": scaler,
        "ohe": ohe,
        "fis_thresholds": fis.thresholds_,
        "cat_cols": cat_cols,
        "input_columns": list(X_train.columns),
        "input_dim": X_train.shape[1],
    }

    return {
        "X": (X_train, X_val, X_test),
        "y": (y_train, y_val, y_test),
        "df_splits": (df_train, df_val, df_test),
        "pipeline": pipeline,
    }
