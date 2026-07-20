# Tài liệu tổng quan dự án: RBA Login-Risk Detection (MLP + Mamdani Fuzzy)

> Tài liệu này được tổng hợp từ ghi chú đọc mã nguồn của 6 nhóm phân tích (config, data/features, fuzzy, model/train, inference/visualize, report/results) của dự án `rba_local_project`. Mọi con số, tên hàm, tham số đều lấy trực tiếp từ mã nguồn/ghi chú; các điểm mâu thuẫn giữa ghi chú được nêu rõ trong ngoặc.

---

## 1. Tổng quan

### 1.1. Dự án làm gì

Dự án xây dựng một hệ thống **phát hiện rủi ro cho từng lượt đăng nhập** (login-risk detection) phục vụ bài toán **RBA – Risk-Based Authentication (Xác thực dựa trên rủi ro)**. Với mỗi lượt đăng nhập, hệ thống trả về:

- `attack_probability`: xác suất lượt đăng nhập đến từ một IP tấn công (số thực trong [0, 1]).
- `predicted_label`: nhãn nhị phân (0 = bình thường, 1 = tấn công), quyết định theo ngưỡng mặc định 0.5.

### 1.2. Bài toán RBA là gì

RBA là cơ chế bảo mật trong đó mỗi lượt đăng nhập được **chấm điểm rủi ro** dựa trên ngữ cảnh: vị trí (Country/City), nhà mạng (ASN), thiết bị/trình duyệt/OS, thời điểm đăng nhập, độ trễ mạng (RTT) và lịch sử hành vi của người dùng. Nếu điểm rủi ro cao, hệ thống sẽ yêu cầu xác thực bổ sung (OTP/2FA); nếu thấp, cho đăng nhập bình thường. Đây là cách các dịch vụ lớn cân bằng giữa bảo mật và trải nghiệm người dùng.

Nhãn dự đoán của dự án là cột **`Is Attack IP`**.

### 1.3. Ý tưởng cốt lõi — vì sao kết hợp MLP + Fuzzy

Dự án dùng một **mô hình lai (hybrid) theo hướng "feature-level fusion"** (kết hợp ở tầng đặc trưng), không phải hai mô hình chạy song song rồi so sánh:

- **Hệ mờ Mamdani (Mamdani Fuzzy Inference System)** đóng vai trò **mã hóa tri thức chuyên gia** thành các luật IF-THEN (ví dụ: "đăng nhập từ quốc gia mới + ASN mới sau thời gian dài ⇒ rủi ro cao"). Đầu ra của hệ mờ (15 mức độ thuộc + 1 điểm rủi ro tổng hợp) được dùng làm **đặc trưng bổ sung**.
- **MLP (Multi-Layer Perceptron)** là bộ phân loại chính, học từ tập đặc trưng gồm: đặc trưng số đã chuẩn hóa + đặc trưng one-hot + **toàn bộ đặc trưng mờ**.

Lợi ích của cách kết hợp này: hệ mờ đưa vào tri thức miền dưới dạng có thể giải thích được, giúp MLP học nhanh hơn và tăng tính diễn giải; MLP bù lại khả năng học các tương tác phi tuyến phức tạp mà luật thủ công không nắm hết. Tên file model đầu ra `mlp_mamdani_model.pt` và các thông báo in ra ("MLP + Mamdani FIS") phản ánh trực tiếp kiến trúc lai này.

---

## 2. Kiến trúc tổng thể

### 2.1. Sơ đồ luồng dữ liệu (bằng chữ)

```
   [CSV thô: rba_sample_500k.csv]
                │
                ▼
   load_raw()  ──►  đọc CSV, ép "Login Timestamp" sang datetime,
   (features.py)     sắp xếp theo [User ID, Login Timestamp]  (bắt buộc cho
                     các feature lịch sử dùng shift/cumsum/cumcount)
                │
                ▼
   engineer_features()  ──►  sinh đặc trưng thời gian, RTT, độ hiếm toàn cục,
   (features.py)              hành vi lịch sử theo user  (19 cột số + Device Type)
                │
                ▼
   prepare_splits()  ──►  chia 70% train / 15% val / 15% test
   (dataset_prep.py)       (stratify theo nhãn, random_state=42)
                │
       ┌────────┴───────────────────────────────────────────┐
       ▼ (fit CHỈ trên train)                                ▼ (transform val/test)
   ┌────────────────────────────────────────────────────────────────────┐
   │  NHÁNH 1 (số):   StandardScaler → 19 cột số chuẩn hóa               │
   │  NHÁNH 2 (phân loại): OneHotEncoder → Device Type                  │
   │  NHÁNH 3 (mờ):   Mamdani FIS.transform → 15 membership + 1 score   │
   └────────────────────────────────────────────────────────────────────┘
                │  pd.concat([num, cat, fz], axis=1)
                ▼
   [Ma trận đầu vào X]  (input_dim = X_train.shape[1])
                │
                ▼
   ┌──────────────────────────────────────────────┐
   │  MLP: 3 tầng ẩn (128 → 64 → 32) → 1 logit     │
   └──────────────────────────────────────────────┘
                │
                ▼
   sigmoid(logit)  ──►  attack_probability  ──►  (≥ 0.5) predicted_label
```

### 2.2. Fuzzy score được dùng như thế nào (điểm quan trọng)

Điểm mấu chốt của kiến trúc: **hệ mờ Mamdani không thay thế và không chạy song song để so sánh với MLP**. Toàn bộ đầu ra của hệ mờ được **bơm thẳng vào MLP làm đặc trưng đầu vào**:

- 15 cột mức độ thuộc mờ (`fz_<biến>_{low,med,high}` cho 5 biến liên tục), và
- 1 cột điểm rủi ro tổng hợp `mamdani_risk_score` (kết quả giải mờ centroid).

Cả 16 cột này được ghép (`pd.concat`) cùng với đặc trưng số đã scale và đặc trưng one-hot của `Device Type`. Đây là kiến trúc **"fuzzy làm bộ trích xuất đặc trưng tri thức + MLP làm bộ phân loại"**, hợp nhất ở tầng input. Khi inference, quy trình được tái lập y hệt (xem mục 7).

---

## 3. Dữ liệu & Đặc trưng

### 3.1. Dataset

- **File**: `rba_sample_500k.csv`, đặt trong thư mục `data/` (đường dẫn `DATA_PATH = data/rba_sample_500k.csv`; đổi tên qua `DATA_FILENAME` trong `config.py`).
- **Nguồn**: mẫu **500.000 dòng** trích từ bộ dữ liệu công khai "Login Data Set for Risk-Based Authentication" (Wiefling, Lo Iacono, Dürmuth — IFIP SEC 2019).
- **Lưu ý về số dòng**: con số 500k được nêu trong báo cáo `.docx`; trong mã nguồn kích thước **không hard-code** mà lấy động qua `len(df)` và `X_train.shape[1]`.
- **Các cột gốc được dùng**: `Login Timestamp`, `User ID`, `Round-Trip Time [ms]`, `Country`, `City`, `ASN`, `Device Type`, `Browser Name and Version`, `OS Name and Version`, `Login Successful`, và nhãn `Is Attack IP`.

### 3.2. Nhãn và mất cân bằng lớp

- **Nhãn**: `TARGET_COLUMN = "Is Attack IP"` (nhị phân, ép về int 0/1).
- **Lý do chọn nhãn này**:
  - `Is Account Takeover` chỉ có ~4 mẫu dương trên 500k dòng → quá ít để train/test.
  - `Login Successful` phản ánh lỗi kỹ thuật hơn là rủi ro bảo mật.
  - `Is Attack IP` có **~3% dương tính** → phù hợp nhất với bài toán chấm điểm rủi ro.
- **Mất cân bằng lớp**: dữ liệu lệch nặng về lớp âm (~3% dương). Trong khâu chuẩn bị dữ liệu, cơ chế duy nhất liên quan là `stratify=y` (giữ tỉ lệ lớp khi chia tập). **Không có oversampling/undersampling.** Việc xử lý mất cân bằng thực sự nằm ở **hàm mất mát** của MLP (`pos_weight`, xem mục 5), không nằm ở khâu dữ liệu.

### 3.3. Chia train/val/test

Trong `prepare_splits(df)` (`dataset_prep.py`):
- Thao tác trên **chỉ số** (`idx = np.arange(len(df))`), chia 2 bước bằng `train_test_split`:
  - Bước 1: tách `TEST_SIZE = 0.30` làm tập tạm (val+test).
  - Bước 2: chia đôi tập tạm bằng `VAL_TEST_SPLIT = 0.50` thành val và test.
  - Tổng thể: **70% train / 15% val / 15% test**.
- **`stratify` ở cả hai bước** (bước 2 dùng `stratify=y_temp`), `random_state = 42` (tái lập được).
- **Nguyên tắc chống leakage**: mọi bộ tiền xử lý (Mamdani FIS, OneHotEncoder, StandardScaler) đều `fit` **chỉ trên `df_train`** rồi `transform` cho val/test.

### 3.4. Danh sách đầy đủ các đặc trưng

Đặc trưng được sinh ở 2 nơi: (A) `engineer_features()` trong `features.py`, (B) `MamdaniFuzzyRiskSystem.transform()` trong `fuzzy_mamdani.py`.

#### A. Đặc trưng số/nhị phân — `FEATURE_COLUMNS_NUMERIC` (19 cột)

**Nhóm thời gian** (từ `Login Timestamp`):
| Feature | Cách tính |
|---|---|
| `hour_of_day` | `.dt.hour` (0–23) |
| `day_of_week` | `.dt.dayofweek` (0=T2 … 6=CN) |
| `is_weekend` | `day_of_week >= 5` |
| `is_odd_hour` | `(hour < 6) OR (hour > 22)` — đêm khuya/sáng sớm |

**Nhóm RTT** (từ `Round-Trip Time [ms]`):
| Feature | Cách tính |
|---|---|
| `rtt_missing` | cờ 1 nếu RTT bị thiếu (`isna().astype(int)`) |
| `rtt_filled` | RTT điền thiếu bằng **median** của cột |

**Nhóm độ hiếm toàn cục**:
| Feature | Cách tính |
|---|---|
| `country_rarity` | `1 − freq(Country)`; `freq` = `value_counts(normalize=True)`, NaN→0. Càng hiếm → càng gần 1 |
| `asn_rarity` | `1 − freq(ASN)`, cùng logic |

**Nhóm hành vi lịch sử theo user** (`groupby("User ID", sort=False)`, chỉ dùng thông tin TRƯỚC ĐÓ để chống leakage):
| Feature | Cách tính |
|---|---|
| `time_since_last_login_h` | `(Login Timestamp − prev_timestamp)` đổi ra giờ; lần đầu (NaN) → `fillna(8760)` = 24×365 |
| `is_first_login` | 1 nếu `prev_timestamp` là NaN |
| `is_new_country` | `Country != shift(1)`; lần đầu ép = 1 |
| `is_new_city` | tương tự với `City` |
| `is_new_asn` | tương tự với `ASN` |
| `is_new_device` | tương tự với `Device Type` |
| `is_new_browser` | tương tự với `Browser Name and Version` |
| `is_new_os` | tương tự với `OS Name and Version` |
| `user_success_rate_so_far` | `cum_success / cum_count` (chỉ tính quá khứ, loại dòng hiện tại); chia 0 → NaN → `fillna(1.0)` |
| `user_login_count_so_far` | `cumcount()` — số lần đăng nhập trước đó |
| `num_changes` | tổng 6 cờ `is_new_*` theo hàng (0–6) |

#### B. Đặc trưng phân loại — `FEATURE_COLUMNS_CATEGORICAL`
- Chỉ có **`Device Type`** → one-hot encoding (`OneHotEncoder(handle_unknown="ignore", sparse_output=False)`). Giá trị lạ ở val/test → vector toàn 0.

#### C. Đặc trưng mờ (Mamdani FIS) — `FUZZY_FEATURE_COLUMNS` (16 cột)
- 15 cột mức độ thuộc: `fz_<biến>_{low,med,high}` cho 5 biến liên tục (5 × 3 = 15).
- 1 cột `mamdani_risk_score` (centroid).

#### Tổng chiều đầu vào X
```
X = [19 cột số đã scale] + [one-hot Device Type] + [16 cột fuzzy]
input_dim = X_train.shape[1]
```
Số cột one-hot phụ thuộc số giá trị `Device Type` xuất hiện trong tập train.

> **⚠️ Mâu thuẫn cần lưu ý giữa các ghi chú**: Ghi chú *data-features* (đọc trực tiếp mã) liệt kê rõ **19 cột** trong `FEATURE_COLUMNS_NUMERIC`. Báo cáo `.docx` (ghi chú *report-results*) lại mô tả đầu vào MLP là **39 chiều = "23 đặc trưng số + one-hot Device Type + 16 đặc trưng mờ"**. Cách hòa giải hợp lý nhất: **19 cột số (sau scale) + 4 cột one-hot của Device Type = 23**, cộng **16 cột mờ = 39 chiều tổng**. Nghĩa là cụm "23 đặc trưng số" trong báo cáo đã gộp cả 4 cột one-hot; con số 4 = 39 − 19 − 16, tương ứng 4 giá trị `Device Type` trong tập train. Nếu số giá trị `Device Type` khác 4, `input_dim` sẽ khác 39.

#### Xử lý thiếu dữ liệu (tóm tắt)
- RTT: cờ `rtt_missing` + điền median (`rtt_filled`).
- `time_since_last_login_h`: NaN (lần đầu) → 8760 giờ.
- `user_success_rate_so_far`: chia 0 → NaN → `fillna(1.0)`.
- `country_rarity`/`asn_rarity`: NaN → `fillna(0)` trước khi lấy `1 −`.
- One-hot: giá trị lạ → toàn 0 nhờ `handle_unknown="ignore"`.

---

## 4. Hệ mờ Mamdani (mục sâu nhất)

File `src/fuzzy_mamdani.py`, lớp chính `MamdaniFuzzyRiskSystem`, cài đặt thủ công bằng NumPy (không dùng `scikit-fuzzy`). Hệ theo đúng **4 bước chuẩn Mamdani**: Fuzzification → Rule Evaluation → Aggregation → Defuzzification.

Chu trình dùng: `fit()` (học ngưỡng percentile + min/max trên train) → `transform()` (mờ hóa + suy diễn + giải mờ).

### 4.1. Biến ngôn ngữ đầu vào

**5 biến liên tục** (`CONTINUOUS_VARS`), mỗi biến mờ hóa thành 3 tập Low / Medium / High:
1. `time_since_last_login_h` — thời gian kể từ lần đăng nhập trước (giờ)
2. `country_rarity` — độ hiếm của quốc gia
3. `asn_rarity` — độ hiếm của ASN/nhà mạng
4. `user_success_rate_so_far` — tỉ lệ đăng nhập thành công tính đến hiện tại
5. `num_changes` — số thay đổi so với lịch sử (đổi thiết bị/trình duyệt/OS…)

**2 biến nhị phân** (dùng trực tiếp làm mức thuộc): `is_new_country`, `is_new_asn` (0/1). Phần bù NOT được tính bằng `1.0 − giá_trị` (`not_new_country`, `not_new_asn`) — đây là phép **NOT mờ dạng bù chuẩn 1−μ**.

### 4.2. Hàm thuộc (Membership Functions) — tất cả đều là hàm TAM GIÁC

Hàm `triangular(x, a, b, c)`: tam giác với chân trái `a`, đỉnh `b` (μ=1), chân phải `c`.
- Nhánh lên: `(x−a)/(b−a)` khi `a ≤ x ≤ b`.
- Nhánh xuống: `(c−x)/(c−b)` khi `b < x ≤ c`.
- Xử lý suy biến `a==b==c`: chỉ điểm `x==b` có μ=1 (mẹo để dữ liệu lệch không gây lỗi chia cho 0).
- Nội bộ dùng `float64` để so sánh chính xác `x==b`, trả về `float32`, clip về [0,1].

#### Membership đầu vào — `low_med_high(x, p20, p50, p80, xmin, xmax)`
Sinh 3 tập mờ cho mỗi biến liên tục **theo percentile học từ train** (không phải hằng số cứng):
- **Low** = `triangular(x, xmin, xmin, p50)` — tam giác vai trái, đỉnh tại `xmin`, giảm về 0 tại p50.
- **Medium** = `triangular(x, p20, p50, p80)` — tam giác cân, đỉnh tại p50.
- **High** = `triangular(x, p50, xmax, xmax)` — tam giác vai phải, tăng từ p50 lên đỉnh tại `xmax`.

Các ngưỡng học trong `fit()` **chỉ trên train**:
```python
self.thresholds_ = {c: np.percentile(df[c].values, [20, 50, 80]) for c in CONTINUOUS_VARS}
self.minmax_     = {c: (float(df[c].min()), float(df[c].max())) for c in CONTINUOUS_VARS}
```
> **Lưu ý quan trọng**: `xmin/xmax` PHẢI là giá trị toàn cục của train. Nếu tính lại từ batch nhỏ (1–2 dòng) khi inference thì `xmin=xmax=` chính giá trị mẫu đó → méo mức thuộc Low/High. Đây là lý do khi inference, `fis.thresholds_` và `fis.minmax_` được gán lại từ pipeline đã lưu chứ không gọi `fit()` lại. (Xem thêm mục 8.1 — đây từng là một lỗi đã được phát hiện và sửa.)

#### Membership đầu ra (risk score) — tham số CỐ ĐỊNH (không học từ dữ liệu)
Rời rạc hóa miền [0,1] thành `N_GRID = 51` điểm (`FUZZY_OUTPUT_GRID_POINTS = 51`):
- `Y_GRID = np.linspace(0, 1, 51)`
- `OUT_LOW  = triangular(Y_GRID, 0.0, 0.0, 0.5)` — rủi ro thấp
- `OUT_MED  = triangular(Y_GRID, 0.2, 0.5, 0.8)` — rủi ro trung bình
- `OUT_HIGH = triangular(Y_GRID, 0.5, 1.0, 1.0)` — rủi ro cao

### 4.3. Toàn bộ 8 luật mờ (`_rule_base`)

Mỗi luật là tuple `(firing_strength, nhãn_hệ_quả)`. Cột "firing mẫu" là độ kích hoạt cho một lượt đăng nhập ví dụ (từ `BaoCao_Assets/rule_list.txt`).

| Luật | Tiền đề (Antecedent) | Toán tử | Hệ quả | Firing mẫu |
|------|----------------------|---------|--------|------------|
| **R1** | `is_new_country` AND `is_new_asn` AND `gap_high` | AND=min (`np.minimum.reduce`) | **High** | 0.052 |
| **R2** | `success_rate` Low (`succ_low`) | trực tiếp | **High** | 0.629 |
| **R3** | `num_changes` High (`chg_high`) | trực tiếp | **High** | 0.600 |
| **R4** | `asn_rarity` High (`arare_high`) | trực tiếp | **High** | 0.943 |
| **R5** | NOT `new_country` AND NOT `new_asn` AND `changes_low` AND `success_high` | AND=min | **Low** | 0.000 |
| **R6** | `gap_low` AND `country_rarity_low` | AND=min | **Low** | 0.000 |
| **R7** | `changes_med` OR `gap_med` | OR=max (`np.maximum`) | **Medium** | 0.000 |
| **R8** | `success_med` AND (NOT `new_country` OR NOT `new_asn`) | `min(succ_med, max(not_new_country, not_new_asn))` | **Medium** | 0.000 |

Ánh xạ biến trong code: `gap_*` ← `time_since_last_login_h`; `crare_*` ← `country_rarity`; `arare_*` ← `asn_rarity`; `succ_*` ← `user_success_rate_so_far`; `chg_*` ← `num_changes`.

**Ngữ nghĩa**: R1–R4 đẩy điểm về **High** (quốc gia+ASN mới sau thời gian dài; tỉ lệ thành công thấp; nhiều thay đổi; ASN rất hiếm). R5–R6 kéo về **Low** (mọi thứ quen thuộc, ít thay đổi, tỉ lệ thành công cao). R7–R8 giữ ở **Medium**.

### 4.4. Cơ chế suy diễn chi tiết (`transform`)

**Bước 1 — Fuzzification** (`_fuzzify`): với mỗi biến liên tục gọi `low_med_high(...)` → dict `mem[col] = (low, med, high)`, mỗi phần tử là mảng mức thuộc theo từng dòng.

**Bước 2 — Rule Evaluation**: tính firing strength mỗi luật. AND = `np.minimum`/`np.minimum.reduce`; OR = `np.maximum`; NOT = `1 − μ`.

**Bước 3 — Aggregation** (Mamdani min-clip + max-aggregation): mỗi luật "cắt phẳng" tập mờ hệ quả (Low/Med/High) tại firing strength, rồi gộp tất cả luật bằng max:
```python
clipped = np.minimum(shapes[label][None,:], firing_strength[:,None])   # cắt ngọn tại firing
np.maximum(aggregated, clipped, out=aggregated)                        # gộp các luật bằng MAX
```
Kết quả `aggregated` có kích thước `n × 51`.

**Bước 4 — Defuzzification bằng Centroid** (trọng tâm rời rạc trên lưới 51 điểm):
```python
numerator   = aggregated @ Y_GRID     # Σ μ(y)·y
denominator = aggregated.sum(axis=1)   # Σ μ(y)
centroid    = numerator / denominator  # Σ(μ·y) / Σμ
```
Khi mẫu số ≈ 0 (`denominator ≤ 1e-6`, không luật nào kích hoạt) → gán mặc định **0.5** (rủi ro trung tính). Giá trị `centroid` chính là `mamdani_risk_score`.

**Ví dụ minh họa** (Hình 3 báo cáo): quốc gia mới + ASN mới + ~500h không đăng nhập + success 35% + 4 thay đổi → **centroid = 0.8391** (rủi ro cao). Đóng góp mạnh nhất là R4 (firing 0.943) và R2 (firing 0.629).

### 4.5. Fuzzy score được dùng thế nào
Như đã nêu ở mục 2.2: 15 mức thuộc + `mamdani_risk_score` (16 cột) được ghép làm đặc trưng đầu vào MLP. Đây là fuzzy feature engineering → neural network, không phải hai hệ độc lập.

---

## 5. Mô hình MLP & Huấn luyện

### 5.1. Kiến trúc (`model.py`, lớp `MLPClassifier(nn.Module)`)

Xây dựng động qua vòng lặp `hidden_dims`. Mỗi tầng ẩn `h` gồm khối 4 lớp **theo đúng thứ tự**:
```
nn.Linear(prev, h) → nn.ReLU() → nn.BatchNorm1d(h) → nn.Dropout(dropout)
```
> Lưu ý thứ tự đặc biệt: **ReLU đặt TRƯỚC BatchNorm1d**, Dropout ở cuối khối.

Với `HIDDEN_DIMS = (128, 64, 32)` (3 tầng ẩn):
```
Input(input_dim)
  → Linear(input_dim, 128) → ReLU → BatchNorm1d(128) → Dropout(0.3)
  → Linear(128, 64)        → ReLU → BatchNorm1d(64)  → Dropout(0.3)
  → Linear(64, 32)         → ReLU → BatchNorm1d(32)  → Dropout(0.3)
  → Linear(32, 1)          # tầng ra, KHÔNG activation → logits thô
```
`forward` trả về `self.net(x).squeeze(-1)` (logits, chưa sigmoid). `input_dim` truyền từ ngoài vào (`pipeline["input_dim"] = X_train.shape[1]`), gồm số cột numeric đã scale + one-hot Device Type + 16 đặc trưng Mamdani.

### 5.2. Loss & xử lý mất cân bằng

- **CÓ xử lý mất cân bằng** qua trọng số lớp dương trong loss:
  ```python
  n_pos = ytr_t.sum(); n_neg = len(ytr_t) - n_pos
  pos_weight = torch.tensor([n_neg / max(n_pos, 1)])   # tỉ lệ âm/dương
  criterion  = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
  ```
- Dùng `BCEWithLogitsLoss` (nhận logits trực tiếp). **Không dùng Focal Loss.**

### 5.3. Optimizer, LR, scheduler, epoch, batch

| Thành phần | Giá trị |
|---|---|
| Optimizer | `Adam(lr=1e-3, weight_decay=1e-5)` (có L2 regularization) |
| Learning rate | `LEARNING_RATE = 1e-3` |
| LR scheduler | `ReduceLROnPlateau(mode="max", factor=0.5, patience=2)` theo dõi `val_auprc` (giảm nửa LR nếu AUPRC val không cải thiện 2 epoch) |
| Epochs | `EPOCHS = 30` (tối đa) |
| Batch size | `BATCH_SIZE = 4096`, `DataLoader(shuffle=True)` |
| Early stopping | `EARLY_STOPPING_PATIENCE = 5` — dừng khi `bad >= 5` epoch không cải thiện `val_auprc` |
| Seed | `torch.manual_seed(42)` |
| Device | `"cuda" if torch.cuda.is_available() else "cpu"` |

### 5.4. Vòng lặp huấn luyện & chọn model tốt nhất

- Mỗi epoch: `model.train()` → lặp mini-batch → `zero_grad → loss.backward → optimizer.step`. Train loss trung bình theo mẫu.
- Đánh giá val: `model.eval()` + `torch.no_grad()`, `val_probs = torch.sigmoid(model(Xv_t))`; tính `val_auprc = average_precision_score(...)` và `val_auroc = roc_auc_score(...)`.
- **Tiêu chí chọn model tốt nhất = AUPRC trên validation** (không phải loss, không phải AUROC) — phù hợp dữ liệu mất cân bằng. Khi `val_auprc > best_auprc` thì lưu `best_state` (bản sao state_dict) và reset `bad=0`.
- Sau vòng lặp: `model.load_state_dict(best_state)` — khôi phục trọng số của epoch có AUPRC val cao nhất.

### 5.5. Chọn threshold phân loại

- **Không có bước tự tối ưu threshold ở quyết định cuối.** Hàm `evaluate(model, X, y, device, threshold=0.5)` dùng **ngưỡng cứng 0.5**: `preds = (probs >= 0.5).astype(int)`. Trong `train.py`, `evaluate` được gọi không truyền threshold → dùng đúng 0.5.
- Các metric phụ thuộc ngưỡng (Precision/Recall/F1 qua `precision_recall_fscore_support(average="binary", zero_division=0)`, Accuracy, confusion_matrix) đều tính ở 0.5. AUROC/AUPRC độc lập ngưỡng (tính trên `probs`).
- Dù mất cân bằng được xử lý ở loss (`pos_weight`), **ngưỡng quyết định vẫn giữ 0.5** — không hạ ngưỡng theo tỉ lệ dương hay tối ưu F1.
- Riêng `visualize.plot_threshold_curve` có tính và **in ra** ngưỡng cho F1 cao nhất (qua `argmax` trên đường F1), nhưng chỉ để tham khảo/vẽ biểu đồ, **không** được dùng để tạo ra `metrics.json`.

---

## 6. Kết quả

### 6.1. Bảng metrics đầy đủ (tập Test, 75.000 dòng — nguồn `outputs/metrics.json`)

| Chỉ số | Giá trị | Làm tròn | Ý nghĩa |
|---|---|---|---|
| **AUROC** | 0.8773947125732673 | **0.8774** | Khả năng phân biệt tổng quát 2 lớp (1.0 = hoàn hảo) — khá tốt |
| **AUPRC** | 0.21876371741746312 | **0.2188** | Đáng tin hơn AUROC khi dữ liệu mất cân bằng (~3% dương) |
| **Accuracy** | 0.7896266666666667 | **0.7896** | Tỉ lệ dự đoán đúng — dễ gây hiểu nhầm với dữ liệu lệch lớp |
| **Precision** | 0.1117382790001152 | **0.1117** | Trong các cảnh báo tấn công, ~11% là đúng thật |
| **Recall** | 0.8449477351916377 | **0.8449** | Trong các tấn công thật, bắt được ~84% |
| **F1** | 0.19737511445721845 | **0.1974** | Điều hòa giữa Precision và Recall |

Tất cả tính ở ngưỡng mặc định 0.5.

**Số liệu bổ sung (chỉ có trong text `.docx`, KHÔNG có trong `metrics.json`)**: nếu chuyển sang **ngưỡng tối ưu F1 = 0.829** thì Precision tăng lên **27.8%**, F1 = **0.327**, đổi lại Recall giảm còn **39.8%**.

### 6.2. Diễn giải ý nghĩa trong bối cảnh RBA

- **Recall cao (84.5%) + Precision thấp (11.2%)** là một sự đánh đổi *có chủ đích và hợp lý* cho bài toán bảo mật:
  - **Recall cao** nghĩa là hệ thống **bắt được phần lớn tấn công thật** — điều tối quan trọng, vì bỏ sót một IP tấn công (false negative) là rủi ro bảo mật nghiêm trọng.
  - **Precision thấp** nghĩa là có **nhiều báo động giả** (false positive): cứ ~9 cảnh báo thì chỉ ~1 là tấn công thật. Trong RBA, hệ quả của báo động giả "chỉ" là yêu cầu người dùng xác thực thêm (OTP/2FA) — gây phiền nhưng không nguy hiểm. Nguyên nhân trực tiếp: lớp dương chỉ ~3% + ngưỡng cứng 0.5 + loss có `pos_weight` đẩy mô hình thiên về phát hiện dương.
- **AUPRC (0.219) quan trọng hơn Accuracy/AUROC**: với dữ liệu lệch ~3% dương, một mô hình đoán "tất cả âm" đã đạt Accuracy ~97%, nên Accuracy 0.79 không phản ánh chất lượng thực. AUROC 0.877 trông đẹp nhưng cũng bị "thổi phồng" bởi lớp âm áp đảo. AUPRC 0.219 (so với baseline ngẫu nhiên ~0.03) mới cho thấy mô hình thực sự học được tín hiệu hữu ích.
- **Kết luận thực tiễn**: mô hình phù hợp làm tầng sàng lọc rủi ro đầu tiên (ưu tiên không bỏ sót), sau đó dùng ngưỡng linh hoạt theo chi phí thực tế để cân bằng phiền toái người dùng.

---

## 7. Cấu trúc thư mục & cách chạy

### 7.1. Cây thư mục

```
rba_local_project/
├── README.md
├── requirements.txt
├── data/
│   └── rba_sample_500k.csv          # dataset (tự đặt vào)
├── src/
│   ├── config.py                    # mọi hằng số/đường dẫn/hyperparameter
│   ├── features.py                  # load_raw(), engineer_features()
│   ├── fuzzy_mamdani.py             # MamdaniFuzzyRiskSystem (hệ mờ)
│   ├── dataset_prep.py              # prepare_splits() — chia dữ liệu + fit pipeline
│   ├── model.py                     # MLPClassifier, train_mlp(), evaluate()
│   ├── train.py                     # script huấn luyện chính
│   ├── inference.py                 # dự đoán không train lại + demo
│   └── visualize.py                 # vẽ biểu đồ
└── outputs/                         # tạo tự động khi import config
    ├── mlp_mamdani_model.pt         # trọng số MLP (~73.5 KB)
    ├── preprocessing_pipeline.pkl   # pipeline tiền xử lý (~2.8 KB)
    ├── metrics.json                 # 6 chỉ số (~202 B)
    ├── training_curves.png
    ├── metrics_bar_chart.png
    ├── confusion_matrix.png
    ├── roc_pr_curves.png
    └── threshold_curve.png

BaoCao_Assets/                       # tài nguyên báo cáo
├── hinh1_kien_truc_tong_the.png
├── hinh2_membership_functions.png
├── hinh3_vidu_mamdani_4buoc.png
├── hinh4_kien_truc_mlp.png
└── rule_list.txt                    # 8 luật + firing + centroid 0.8391
BaoCao_CuoiKy_RBA_MLP_Fuzzy.docx     # báo cáo cuối kỳ
```

**Các đường dẫn trong `config.py`** đều tính tương đối theo vị trí `config.py` (`os.path.abspath(__file__)`), nên data/outputs luôn trỏ đúng về `rba_local_project/` bất kể thư mục hiện hành. Dòng cuối `config.py` có side effect: `os.makedirs(OUTPUT_DIR, exist_ok=True)` — thư mục `outputs/` được tạo ngay khi import module.

### 7.2. Thư viện phụ thuộc (`requirements.txt`)

| Thư viện | Vai trò |
|---|---|
| `numpy>=1.24` | tính toán mảng nền tảng; **cài đặt Mamdani FIS thủ công** (không dùng scikit-fuzzy) |
| `pandas>=2.0` | đọc CSV, xử lý DataFrame, feature engineering |
| `scikit-learn>=1.3` | `train_test_split` (stratified), `StandardScaler`, `OneHotEncoder`, các metric, `roc_curve`, `precision_recall_curve` |
| `torch>=2.0` | xây dựng & huấn luyện MLP |
| `matplotlib>=3.7` | vẽ biểu đồ (loss, AUPRC/AUROC, ROC, PR, confusion matrix, threshold curve) |

### 7.3. Cài đặt

```bash
cd rba_local_project
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
Đặt dữ liệu: copy dataset vào `rba_local_project/data/rba_sample_500k.csv` (hoặc đổi `DATA_FILENAME`).

### 7.4. Thứ tự chạy

**Bước 1 — Huấn luyện:**
```bash
cd src
python train.py
```
`train.py` tự động: đọc dữ liệu + feature engineering → chia 70/15/15 stratified → fit Mamdani FIS + StandardScaler + OneHotEncoder **trên train** → train MLP (early stopping theo AUPRC val) → đánh giá test → lưu ra `outputs/`: `mlp_mamdani_model.pt`, `preprocessing_pipeline.pkl`, `metrics.json` và 5 biểu đồ PNG.

**Bước 2 — Dự đoán (không train lại):**
```bash
cd src
python inference.py
```
Load model + pipeline đã lưu, chạy demo 2 kịch bản (rủi ro cao / thấp). Có thể import dùng lại:
```python
from inference import load_pipeline_and_model, predict_risk
model, pipeline = load_pipeline_and_model()
result = predict_risk(your_dataframe, model, pipeline)
print(result[["attack_probability", "predicted_label"]])
```

**Chi tiết `inference.py`:**
- `load_pipeline_and_model()`: kiểm tra tồn tại `MODEL_PATH` + `PIPELINE_PATH` (thiếu → `FileNotFoundError`), load pipeline bằng pickle, tạo `MLPClassifier(pipeline["input_dim"])`, load trọng số (`map_location="cpu"`), `model.eval()`.
- `predict_risk(raw_rows, model, pipeline, threshold=0.5)`: tái lập y hệt lúc train — (1) dựng lại FIS bằng `pipeline["fis_thresholds"]`/`["fis_minmax"]` rồi `transform`; (2) one-hot bằng `pipeline["ohe"]`; (3) scale bằng `pipeline["scaler"]`; (4) `concat([num, cat, fz])[pipeline["input_columns"]]` (sắp đúng thứ tự cột); (5) `sigmoid(model(X))` → `attack_probability`, và `predicted_label = (probs >= 0.5)`.
- `_demo()`: dùng dòng đầu của `rba_sample_500k.csv` làm khuôn mẫu, chỉnh tay tạo 2 kịch bản. **Không có file CSV mẫu riêng cho inference.**

**Pipeline được lưu** (`preprocessing_pipeline.pkl`) là dict gồm: `scaler`, `ohe`, `fis_thresholds` (percentile 20/50/80), `fis_minmax` (min/max toàn cục), `cat_cols`, `input_columns`, `input_dim`. Lưu ý: pipeline lưu **tham số đã fit** của FIS chứ không lưu trực tiếp object `MamdaniFuzzyRiskSystem` — khi inference tái dựng FIS từ hai dict `thresholds_`/`minmax_`.

> **Cảnh báo về input inference**: `your_dataframe` phải đã qua `features.engineer_features()` — tức đã có sẵn các cột như `is_new_country`, `user_success_rate_so_far`, `time_since_last_login_h`… Các đặc trưng này phụ thuộc lịch sử đăng nhập trước đó của từng user, **không thể tính từ một dòng đơn lẻ tách rời**.

### 7.5. Các biểu đồ xuất ra (`visualize.py`, đều lưu `outputs/`, `dpi=150`)

| Hàm | File | Nội dung |
|---|---|---|
| `plot_training_curves` | `training_curves.png` | Train loss (BCE) + val AUPRC/AUROC theo epoch |
| `plot_metrics_bar` | `metrics_bar_chart.png` | Bar chart 6 chỉ số (ylim 0–1) |
| `plot_confusion_matrix` | `confusion_matrix.png` | Ma trận nhầm lẫn 2×2 (Blues) |
| `plot_roc_pr_curves` | `roc_pr_curves.png` | ROC (kèm AUROC) + PR (kèm AP, baseline = tỉ lệ dương) |
| `plot_threshold_curve` | `threshold_curve.png` | Precision/Recall/F1 theo ngưỡng; đánh dấu ngưỡng F1 tốt nhất + in ra console |

Hàm tổng hợp `plot_all(results, history)` gọi cả 5.

---

## 8. Nhận xét, hạn chế & hướng phát triển

### 8.1. Điểm mạnh

- **Kiến trúc lai có tính giải thích**: 8 luật Mamdani mã hóa tri thức chuyên gia một cách minh bạch, đóng vai trò tầng đặc trưng bổ trợ giúp MLP dễ học và dễ diễn giải.
- **Chống data leakage bài bản ở phần lớn pipeline**: đặc trưng lịch sử user chỉ dùng thông tin quá khứ (shift/cumsum/cumcount); Mamdani FIS, `StandardScaler`, `OneHotEncoder` đều fit **chỉ trên train**; chia dữ liệu stratified có seed cố định (tái lập được).
- **Chọn nhãn/metric phù hợp bối cảnh mất cân bằng**: dùng `Is Attack IP` (~3% dương) thay vì các cột không khả thi; early stopping và chọn model theo **AUPRC** thay vì accuracy; xử lý mất cân bằng qua `pos_weight`.
- **Đã phát hiện & sửa một lỗi thực**: hàm `low_med_high()` từng tính lại `xmin/xmax` từ batch truyền vào `transform()` thay vì dùng giá trị toàn cục lúc `fit()`. Với batch lớn ảnh hưởng không đáng kể, nhưng khi inference 1–2 dòng đơn lẻ thì `xmin=xmax=` giá trị mẫu → méo mức thuộc Low/High (bị đẩy về 1.0 giả tạo). **Đã sửa**: `fit()` lưu `self.minmax_` toàn cục của train; `transform()`/`_fuzzify()` dùng cố định; lưu `minmax_` vào pipeline để inference khôi phục đúng. Đã huấn luyện lại (kết quả mục 6 là sau sửa). Kiểm chứng inference: kịch bản "rủi ro cao" → **76.9%** (dự đoán 1), "rủi ro thấp" → **26.3%** (dự đoán 0).

### 8.2. Điểm yếu / rủi ro trong code

- **Precision thấp (11.2%) ở ngưỡng 0.5**: nhiều báo động giả; chưa tối ưu ngưỡng ở khâu quyết định cuối.
- **Ngưỡng quyết định cứng 0.5**: dù đã xử lý mất cân bằng ở loss, mã không hạ/tối ưu ngưỡng theo F1 hay theo chi phí thực tế khi sinh `metrics.json` (ngưỡng F1 tối ưu 0.829 chỉ được nêu trong báo cáo, không áp dụng trong code đánh giá).
- **8 luật fuzzy thiết kế thủ công theo trực giác**: chưa được tối ưu/học tự động.
- **Rò rỉ thống kê toàn cục tinh vi (chưa xử lý trong code)**: trong `engineer_features()`, **median RTT** và **`value_counts` cho country/asn rarity** được tính trên **toàn bộ df** (vì `engineer_features` chạy *trước* `prepare_splits`), tức bao gồm cả val/test. Chỉ FIS/OHE/Scaler mới nghiêm ngặt fit-trên-train. Đây là dạng leakage nhẹ ở đặc trưng thống kê toàn cục — nên tính median/rarity chỉ trên train.
- **Không ghim phiên bản chính xác** (`requirements.txt` dùng `>=`): có thể lệch hành vi giữa các phiên bản thư viện. Không khai báo phiên bản Python tối thiểu.
- **Đầu vào inference nặng phụ thuộc lịch sử**: khó dùng cho một lượt đăng nhập đơn lẻ nếu không có ngữ cảnh lịch sử của user (demo phải tự chế kịch bản).
- **Ghi chú của chính báo cáo**: cần kiểm tra lại DOI/đường dẫn Zenodo của các trích dẫn tham khảo (được ghi từ trí nhớ).

### 8.3. Hướng phát triển

- **Xử lý mất cân bằng nâng cao**: thử **Focal Loss** hoặc tinh chỉnh `pos_weight` để cải thiện Precision mà không hy sinh Recall quá nhiều.
- **Chọn ngưỡng theo chi phí thực tế**: cân bằng giữa chi phí bỏ sót tấn công (false negative) và chi phí làm phiền người dùng (false positive) — chọn ngưỡng theo ma trận chi phí thay vì cố định 0.5.
- **Tối ưu/học tự động hệ mờ**: mở rộng bộ luật hoặc dùng **ANFIS** (Adaptive Neuro-Fuzzy Inference System) / thuật toán tiến hóa để tự học tham số hàm thành viên và luật thay vì thiết kế thủ công.
- **Khắc phục leakage thống kê toàn cục**: tính median RTT và tần suất rarity chỉ trên tập train rồi transform cho val/test.
- **Ghim phiên bản thư viện** để đảm bảo tái lập kết quả.

### 8.4. Kết luận

Dự án đã xây dựng thành công một hệ lai **MLP + Mamdani Fuzzy** trên ~500.000 lượt đăng nhập cho bài toán RBA. Hệ mờ mã hóa tri thức chuyên gia (8 luật IF-THEN) thành đặc trưng bổ sung giải thích được, ghép cùng đặc trưng số/one-hot làm đầu vào cho MLP 3 tầng ẩn (128→64→32). Kết quả test (AUROC 0.877, AUPRC 0.219, Recall 84.5%, Precision 11.2% ở ngưỡng 0.5) cho thấy mô hình bắt được phần lớn tấn công — phù hợp mục tiêu bảo mật — dù tỉ lệ báo động giả còn cao, một đánh đổi chấp nhận được trong bối cảnh RBA và có thể tinh chỉnh qua ngưỡng. Quá trình rà soát mã còn phát hiện và sửa một lỗi thực trong hệ mờ (xmin/xmax batch-local).