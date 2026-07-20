"""
Mamdani Fuzzy Inference System (FIS) cho bài toán chấm điểm rủi ro đăng nhập.

4 bước chuẩn của Mamdani FIS:
  1. Fuzzification   : mờ hoá biến đầu vào thành Low/Medium/High (hàm tam giác)
  2. Rule Evaluation  : tính firing strength của từng luật (AND=min, OR=max)
  3. Aggregation      : clip tập mờ đầu ra (Low/Med/High risk) tại firing
                        strength của từng luật, gộp tất cả luật bằng max
  4. Defuzzification  : quy tập mờ đã gộp về 1 số bằng phương pháp Centroid
"""
import numpy as np
import pandas as pd

from config import FUZZY_OUTPUT_GRID_POINTS


def triangular(x, a, b, c):
    """Hàm thành viên tam giác. Dùng float64 nội bộ để tránh mất độ chính
    xác khi so sánh x == b (trường hợp suy biến a=b=c do dữ liệu lệch)."""
    x = np.asarray(x, dtype=np.float64)
    a, b, c = float(a), float(b), float(c)
    y = np.zeros_like(x)
    if a == b == c:
        y[np.isclose(x, b)] = 1.0
        return np.clip(y, 0, 1).astype(np.float32)
    left = (x >= a) & (x <= b) & (b > a)
    y[left] = (x[left] - a) / (b - a)
    right = (x > b) & (x <= c) & (c > b)
    y[right] = (c - x[right]) / (c - b)
    y[np.isclose(x, b)] = 1.0
    return np.clip(y, 0, 1).astype(np.float32)


def low_med_high(x, p20, p50, p80):
    x = np.asarray(x, dtype=np.float64)
    xmin, xmax = float(np.min(x)), float(np.max(x))
    low = triangular(x, xmin, xmin, p50)
    med = triangular(x, p20, p50, p80)
    high = triangular(x, p50, xmax, xmax)
    return low, med, high


class MamdaniFuzzyRiskSystem:
    CONTINUOUS_VARS = [
        "time_since_last_login_h", "country_rarity", "asn_rarity",
        "user_success_rate_so_far", "num_changes",
    ]

    N_GRID = FUZZY_OUTPUT_GRID_POINTS
    Y_GRID = np.linspace(0, 1, N_GRID, dtype=np.float32)
    OUT_LOW = triangular(Y_GRID, 0.0, 0.0, 0.5)
    OUT_MED = triangular(Y_GRID, 0.2, 0.5, 0.8)
    OUT_HIGH = triangular(Y_GRID, 0.5, 1.0, 1.0)

    def fit(self, df: pd.DataFrame):
        """Fit ngưỡng percentile (20/50/80) CHỈ trên tập train."""
        self.thresholds_ = {c: np.percentile(df[c].values, [20, 50, 80]) for c in self.CONTINUOUS_VARS}
        return self

    def _fuzzify(self, df):
        return {col: low_med_high(df[col].values, *self.thresholds_[col]) for col in self.CONTINUOUS_VARS}

    def _rule_base(self, mem, df):
        """8 luật IF-THEN dạng Mamdani (hệ quả là tập mờ Low/Med/High risk)."""
        gap_low, gap_med, gap_high = mem["time_since_last_login_h"]
        crare_low, crare_med, crare_high = mem["country_rarity"]
        arare_low, arare_med, arare_high = mem["asn_rarity"]
        succ_low, succ_med, succ_high = mem["user_success_rate_so_far"]
        chg_low, chg_med, chg_high = mem["num_changes"]

        is_new_country = df["is_new_country"].values.astype(np.float32)
        is_new_asn = df["is_new_asn"].values.astype(np.float32)
        not_new_country, not_new_asn = 1.0 - is_new_country, 1.0 - is_new_asn

        return [
            (np.minimum.reduce([is_new_country, is_new_asn, gap_high]), "high"),   # R1
            (succ_low, "high"),                                                     # R2
            (chg_high, "high"),                                                     # R3
            (arare_high, "high"),                                                   # R4
            (np.minimum.reduce([not_new_country, not_new_asn, chg_low, succ_high]), "low"),  # R5
            (np.minimum(gap_low, crare_low), "low"),                                # R6
            (np.maximum(chg_med, gap_med), "med"),                                  # R7 (OR)
            (np.minimum(succ_med, np.maximum(not_new_country, not_new_asn)), "med"),  # R8
        ]

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        mem = self._fuzzify(df)
        rules = self._rule_base(mem, df)
        n = len(df)

        # ---- Bước 2 & 3: Rule Evaluation + Aggregation (max) ----
        aggregated = np.zeros((n, self.N_GRID), dtype=np.float32)
        shapes = {"low": self.OUT_LOW, "med": self.OUT_MED, "high": self.OUT_HIGH}
        for firing_strength, label in rules:
            clipped = np.minimum(shapes[label][None, :], firing_strength[:, None].astype(np.float32))
            np.maximum(aggregated, clipped, out=aggregated)

        # ---- Bước 4: Defuzzification (Centroid) ----
        numerator = aggregated @ self.Y_GRID
        denominator = aggregated.sum(axis=1)
        centroid = np.divide(numerator, denominator, out=np.full(n, 0.5, dtype=np.float32),
                              where=denominator > 1e-6)

        out = {}
        for col in self.CONTINUOUS_VARS:
            low, med, high = mem[col]
            out[f"fz_{col}_low"], out[f"fz_{col}_med"], out[f"fz_{col}_high"] = low, med, high
        out["mamdani_risk_score"] = centroid
        return pd.DataFrame(out, index=df.index)


FUZZY_FEATURE_COLUMNS = (
    [f"fz_{c}_{lvl}" for c in MamdaniFuzzyRiskSystem.CONTINUOUS_VARS for lvl in ("low", "med", "high")]
    + ["mamdani_risk_score"]
)
