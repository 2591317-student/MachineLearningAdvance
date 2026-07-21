"""
Feature engineering cho dataset RBA.
Mọi đặc trưng "lịch sử người dùng" chỉ dùng thông tin TRƯỚC ĐÓ của cùng
user (shift/cumsum theo timestamp) để tránh Data Leakage.
"""
import numpy as np
import pandas as pd

from config import TARGET_COLUMN

FEATURE_COLUMNS_NUMERIC = [
    "hour_of_day", "day_of_week", "is_weekend", "is_odd_hour",
    "rtt_filled", "rtt_missing",
    "country_rarity", "asn_rarity",
    "time_since_last_login_h", "is_first_login",
    "is_new_country", "is_new_city", "is_new_asn",
    "is_new_device", "is_new_browser", "is_new_os",
    "user_success_rate_so_far", "user_login_count_so_far",
    "num_changes",
]

FEATURE_COLUMNS_CATEGORICAL = ["Device Type"]


def load_raw(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Login Timestamp"] = pd.to_datetime(df["Login Timestamp"])
    df = df.sort_values(["User ID", "Login Timestamp"]).reset_index(drop=True)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # ---- Thời gian ----
    df["hour_of_day"] = df["Login Timestamp"].dt.hour
    df["day_of_week"] = df["Login Timestamp"].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["is_odd_hour"] = ((df["hour_of_day"] < 6) | (df["hour_of_day"] > 22)).astype(int)

    # ---- RTT ----
    # rtt_missing là row-local (an toàn). rtt_filled cần median toàn cục nên
    # được tính ở fit_global_stats/apply_global_stats — CHỈ trên train, chống leakage.
    df["rtt_missing"] = df["Round-Trip Time [ms]"].isna().astype(int)

    # ---- Độ hiếm Country/ASN ----
    # value_counts là thống kê toàn cục; nếu tính trên cả df sẽ rò rỉ thông tin
    # val/test. Vì vậy country_rarity, asn_rarity (và rtt_filled) được thêm ở
    # apply_global_stats() SAU khi đã fit trên tập train (xem dataset_prep.py).

    # ---- Hành vi lịch sử theo user ----
    g = df.groupby("User ID", sort=False)
    df["prev_timestamp"] = g["Login Timestamp"].shift(1)
    df["time_since_last_login_h"] = (
        (df["Login Timestamp"] - df["prev_timestamp"]).dt.total_seconds() / 3600.0
    )
    df["is_first_login"] = df["prev_timestamp"].isna().astype(int)
    df["time_since_last_login_h"] = df["time_since_last_login_h"].fillna(24 * 365)

    for col, new_col in [
        ("Country", "is_new_country"), ("City", "is_new_city"), ("ASN", "is_new_asn"),
        ("Device Type", "is_new_device"), ("Browser Name and Version", "is_new_browser"),
        ("OS Name and Version", "is_new_os"),
    ]:
        prev = g[col].shift(1)
        df[new_col] = (df[col] != prev).astype(int)
        df.loc[df["is_first_login"] == 1, new_col] = 1

    success_int = df["Login Successful"].astype(int)
    cum_success = success_int.groupby(df["User ID"]).cumsum() - success_int
    cum_count = df.groupby("User ID").cumcount()
    df["user_success_rate_so_far"] = (cum_success / cum_count.replace(0, np.nan)).fillna(1.0)
    df["user_login_count_so_far"] = cum_count

    change_cols = ["is_new_country", "is_new_city", "is_new_asn",
                   "is_new_device", "is_new_browser", "is_new_os"]
    df["num_changes"] = df[change_cols].sum(axis=1)

    return df


def fit_global_stats(df_train: pd.DataFrame) -> dict:
    """Học thống kê toàn cục CHỈ trên tập train (chống data leakage):
    median RTT và tần suất xuất hiện của Country/ASN."""
    return {
        "rtt_median": float(df_train["Round-Trip Time [ms]"].median()),
        "country_freq": df_train["Country"].value_counts(normalize=True),
        "asn_freq": df_train["ASN"].value_counts(normalize=True),
    }


def apply_global_stats(df: pd.DataFrame, stats: dict) -> pd.DataFrame:
    """Áp thống kê đã fit (trên train) để tạo rtt_filled, country_rarity,
    asn_rarity cho một tập bất kỳ (train/val/test hoặc dữ liệu inference).
    Giá trị Country/ASN lạ (không có trong train) → rarity = 1 (rất hiếm)."""
    df = df.copy()
    df["rtt_filled"] = df["Round-Trip Time [ms]"].fillna(stats["rtt_median"])
    df["country_rarity"] = 1 - df["Country"].map(stats["country_freq"]).fillna(0)
    df["asn_rarity"] = 1 - df["ASN"].map(stats["asn_freq"]).fillna(0)
    return df


if __name__ == "__main__":
    from config import DATA_PATH
    df = load_raw(DATA_PATH)
    df = engineer_features(df)
    df = apply_global_stats(df, fit_global_stats(df))  # demo: fit trên chính df
    print(df[FEATURE_COLUMNS_NUMERIC + FEATURE_COLUMNS_CATEGORICAL + [TARGET_COLUMN]].head())
    print("Shape:", df.shape)
