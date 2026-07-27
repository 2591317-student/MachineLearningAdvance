# Giải thích cặn kẽ: Dữ liệu & Tiền xử lý (từng bước)

> Tài liệu này để nhóm **hiểu rõ** pipeline dữ liệu và **tự viết lại bằng lời của mình**
> trong báo cáo JTE / trả lời câu hỏi của cô — **không copy nguyên văn** (cô yêu cầu tự viết).
> Toàn bộ nội dung bám sát đúng mã nguồn trong `rba_local_project/src/`
> (`features.py`, `dataset_prep.py`, `fuzzy_mamdani.py`, `config.py`).

![Sơ đồ luồng tiền xử lý dữ liệu](GiaiThich_Assets/data_pipeline.png)

*Hình — Luồng tiền xử lý: dữ liệu thô → đặc trưng → chia tập → fit CHỈ trên train → ghép thành đầu vào 39 chiều.*

---

## 1. Bộ dữ liệu

- **Nguồn:** *Login Data Set for Risk-Based Authentication* (Wiefling và cộng sự) — log đăng nhập thật đã ẩn danh. Dự án dùng một mẫu **~500.000 dòng** (`rba_sample_500k.csv`).
- **Mỗi dòng = một lượt đăng nhập.** Các cột thô chính được dùng:

| Cột thô | Ý nghĩa |
|---|---|
| `Login Timestamp` | Thời điểm đăng nhập |
| `User ID` | Mã người dùng |
| `Round-Trip Time [ms]` (RTT) | Độ trễ mạng (có thể thiếu — NaN) |
| `Country`, `City`, `ASN` | Vị trí địa lý / nhà mạng |
| `Device Type` | Loại thiết bị (desktop/mobile/…) |
| `Browser Name and Version`, `OS Name and Version` | Trình duyệt / hệ điều hành |
| `Login Successful` | Đăng nhập thành công hay không |
| **`Is Attack IP`** | **NHÃN** — lượt này đến từ IP tấn công hay không |

- **Nhãn dự đoán:** `Is Attack IP` (bài toán **phân loại nhị phân**).
- **Đặc điểm khó nhất — mất cân bằng nặng:** chỉ **~3%** là tấn công. ⇒ Không thể đánh giá bằng Accuracy, phải dùng **AUPRC / Recall / Precision**; và khi huấn luyện phải bù lệch lớp (`pos_weight`).

**Vì sao chọn nhãn `Is Attack IP`?** `Is Account Takeover` chỉ có vài mẫu dương (quá ít để học); `Login Successful` chỉ phản ánh lỗi kỹ thuật chứ không phải rủi ro bảo mật. `Is Attack IP` có ~3% dương — đủ dữ liệu và đúng bản chất bài toán chấm rủi ro.

---

## 2. `load_raw` — đọc & sắp xếp

```python
df = pd.read_csv(path)
df["Login Timestamp"] = pd.to_datetime(df["Login Timestamp"])
df = df.sort_values(["User ID", "Login Timestamp"]).reset_index(drop=True)
```

- Đổi cột thời gian sang kiểu `datetime` để tính được khoảng cách thời gian.
- **Sắp xếp theo `User ID` rồi theo thời gian.** Đây là bước **bắt buộc**: các đặc trưng "lịch sử" ở Bước 3 dùng `shift(1)` (lấy sự kiện liền trước của **cùng user**). Nếu không sắp xếp đúng thứ tự thời gian, "sự kiện trước" sẽ sai.

---

## 3. `engineer_features` — sinh 19 đặc trưng số (+ Device Type)

Chia làm 3 nhóm. **Nguyên tắc xuyên suốt:** đặc trưng lịch sử của một lượt đăng nhập **chỉ được nhìn vào quá khứ** của chính user đó, tuyệt đối không nhìn "tương lai" → tránh **rò rỉ dữ liệu (data leakage)**.

### 3a. Nhóm thời gian (tính trực tiếp từ timestamp — an toàn)
| Đặc trưng | Công thức |
|---|---|
| `hour_of_day` | giờ trong ngày (0–23) |
| `day_of_week` | thứ trong tuần (0=T2 … 6=CN) |
| `is_weekend` | 1 nếu `day_of_week ≥ 5` |
| `is_odd_hour` | 1 nếu giờ `< 6` hoặc `> 22` (giờ bất thường) |

### 3b. Nhóm RTT (độ trễ mạng)
- `rtt_missing` = 1 nếu RTT bị thiếu. **Đây là cờ "row-local"** (chỉ nhìn chính dòng đó) nên **an toàn**, tính ngay ở bước này.
- `rtt_filled` (điền giá trị thiếu) **KHÔNG** tính ở đây, vì cần *median toàn cục* → để sang Bước 5 (chỉ fit trên train).

### 3c. Nhóm lịch sử người dùng (dùng `groupby("User ID")` + `shift`/`cumsum`)
```python
g = df.groupby("User ID", sort=False)
df["prev_timestamp"] = g["Login Timestamp"].shift(1)   # thời điểm đăng nhập TRƯỚC ĐÓ
```
| Đặc trưng | Cách tính | Ghi chú chống leakage |
|---|---|---|
| `time_since_last_login_h` | (giờ hiện tại − lần trước) tính theo giờ | lần đầu = NaN → điền `24*365 = 8760h` (coi như "rất lâu rồi") |
| `is_first_login` | 1 nếu không có lần trước | |
| `is_new_country/city/asn/device/browser/os` | 1 nếu giá trị hiện tại **khác** lần trước; lần đầu = 1 (mọi thứ đều "mới") | dùng `shift(1)` → chỉ so với quá khứ |
| `user_success_rate_so_far` | tỉ lệ đăng nhập thành công **trước** lượt này | `cumsum(success) − success_hiện_tại` (trừ chính nó ra); lần đầu → điền 1.0 |
| `user_login_count_so_far` | số lần đăng nhập **trước** lượt này | `cumcount()` (đếm từ 0) |
| `num_changes` | tổng của 6 cờ `is_new_*` | càng nhiều thứ đổi cùng lúc càng đáng ngờ |

> **Điểm mấu chốt để trả lời cô:** vì `shift(1)` và `cumsum − current` chỉ lấy **thông tin đã xảy ra trước** thời điểm t, nên mô hình không bao giờ "thấy trước" tương lai của user → không rò rỉ.

Kết thúc Bước 3 ta có **19 đặc trưng số** + cột phân loại `Device Type`.

---

## 4. Chia Train / Val / Test — **Stratified 70/15/15**

```python
# tách 30% ra làm (val+test), giữ tỉ lệ nhãn
idx_train, idx_temp = train_test_split(idx, test_size=0.30, stratify=y, random_state=42)
# 30% đó chia đôi -> 15% val, 15% test
idx_val,  idx_test  = train_test_split(idx_temp, test_size=0.50, stratify=y_temp, random_state=42)
```
- **Stratified** = giữ nguyên tỉ lệ ~3% dương trong **cả 3 tập**. Nếu chia ngẫu nhiên thường, tập test có thể "hên xui" quá ít mẫu tấn công → đánh giá không đáng tin.
- `random_state=42` để **tái lập được** kết quả.
- Tỉ lệ 70/15/15: 70% để học; 15% val để **chọn mô hình tốt nhất + dừng sớm**; 15% test **chỉ dùng đúng 1 lần** để báo cáo.

---

## 5. Fit các bộ tiền xử lý — **CHỈ TRÊN TRAIN**, rồi áp cho Val/Test

Đây là phần quan trọng nhất về mặt phương pháp. **Mọi thứ "học từ dữ liệu" đều chỉ được học trên tập train**, sau đó *áp lại* (transform) cho val/test. Nếu học trên cả val/test → rò rỉ phân phối của tập kiểm tra vào mô hình → điểm số ảo.

### 5a. Thống kê toàn cục (`fit_global_stats` → `apply_global_stats`)
Fit trên train:
- `rtt_median` = trung vị RTT của train → dùng để điền `rtt_filled`.
- `country_freq`, `asn_freq` = tần suất xuất hiện của mỗi Country/ASN trong train.

Áp cho mọi tập:
- `rtt_filled` = RTT, chỗ thiếu điền bằng `rtt_median`.
- `country_rarity = 1 − freq(country)`, `asn_rarity = 1 − freq(asn)` → **càng hiếm càng gần 1**.
- Country/ASN **lạ** (không có trong train) → `freq = 0` → **rarity = 1** (rất hiếm) — hợp lý vì địa điểm lạ thường rủi ro.

> *(Đây chính là lỗi leakage đã sửa: trước kia median RTT và tần suất Country/ASN tính trên **toàn bộ** dữ liệu; nay chỉ tính trên train.)*

### 5b. Hệ mờ Mamdani (`MamdaniFuzzyRiskSystem`)
- **Fit trên train:** với 5 biến liên tục (`time_since_last_login_h`, `country_rarity`, `asn_rarity`, `user_success_rate_so_far`, `num_changes`) → học **ngưỡng phân vị 20/50/80** và **min/max** của mỗi biến.
- **Transform:** mờ hóa mỗi biến thành Low/Med/High (hàm tam giác) → **15 mức độ thuộc** + **1 điểm rủi ro Centroid** = **16 đặc trưng mờ**.
- Vì sao min/max phải lấy từ train (không tính lại từng batch): nếu suy luận 1 dòng đơn lẻ mà tính min/max ngay trên dòng đó thì min=max=chính giá trị đó → hàm thuộc bị méo. *(Đây là lỗi xmin/xmax đã sửa.)*
- Chi tiết 8 luật + cách ra số 0.839: xem `GiaiThich_ThuatToan_ViDu.md`.

### 5c. One-Hot Encoding cho `Device Type`
- `OneHotEncoder(handle_unknown="ignore")` fit trên train → ví dụ 4 loại thiết bị → **4 cột 0/1**.
- Thiết bị lạ khi suy luận → mã hóa thành toàn 0 (không lỗi).

### 5d. Chuẩn hóa số (`StandardScaler`)
- Fit trên train → mỗi đặc trưng số về **trung bình 0, độ lệch chuẩn 1**: `z = (x − μ_train) / σ_train`.
- Giúp MLP hội tụ nhanh, không để đặc trưng thang đo lớn (như `time_since_last_login_h`) lấn át.

---

## 6. Ghép đặc trưng → đầu vào MLP (39 chiều)

```
X = [ 19 đặc trưng số đã chuẩn hóa ] + [ 4 one-hot Device Type ] + [ 16 đặc trưng mờ Mamdani ]
  = 39 chiều
```
Toàn bộ bộ tiền xử lý (scaler, ohe, global_stats, ngưỡng Mamdani, danh sách cột) được **lưu lại thành pipeline** để lúc suy luận (`inference.py`) áp **đúng y hệt** cho dữ liệu mới.

---

## 7. Ví dụ tính tay — một user có 3 lượt đăng nhập

Giả sử user U đăng nhập 3 lần (đã sắp xếp theo thời gian):

| # | Thời gian | Country | ASN | Device | RTT | Success |
|---|---|---|---|---|---|---|
| L1 | T7 01/02 09:00 | VN | AS1 | desktop | 100 | 1 |
| L2 | T7 01/02 23:30 | VN | AS1 | desktop | *(thiếu)* | 1 |
| L3 | T4 05/02 03:00 | US | AS9 | mobile | 500 | 0 |

**Đặc trưng thời gian & RTT:**

| | hour | day_of_week | is_weekend | is_odd_hour | rtt_missing |
|---|---|---|---|---|---|
| L1 | 9 | 5 (T7) | 1 | 0 | 0 |
| L2 | 23 | 5 (T7) | 1 | 1 (giờ >22) | 1 (thiếu RTT) |
| L3 | 3 | 2 (T4) | 0 | 1 (giờ <6) | 0 |

**Đặc trưng lịch sử (chỉ nhìn quá khứ của U):**

| | time_since_last_login_h | is_first_login | is_new_country | is_new_asn | is_new_device | num_changes | success_rate_so_far | login_count_so_far |
|---|---|---|---|---|---|---|---|---|
| L1 | 8760 (điền, lần đầu) | 1 | 1 | 1 | 1 | 6 (mọi thứ mới) | 1.0 (điền) | 0 |
| L2 | 14.5 | 0 | 0 (VN=VN) | 0 | 0 | 0 | 1.0 (L1 thành công) | 1 |
| L3 | 75.5 | 0 | 1 (US≠VN) | 1 (AS9≠AS1) | 1 (mobile≠desktop) | 6 | 1.0 (L1,L2 đều thành công) | 2 |

→ **L3 rất đáng ngờ**: quốc gia/ASN/thiết bị đều mới, đăng nhập lúc 03:00, cách lần trước 75 giờ. Đây đúng kiểu lượt mà hệ thống cần chấm rủi ro cao.

**Sau Bước 5 (giả sử train có `freq(VN)=0.40`, `freq(US)=0.05`, `rtt_median=90`):**
- L2 `rtt_filled = 90` (điền median).
- L3 `country_rarity = 1 − 0.05 = 0.95` (rất hiếm) ; L1/L2 `= 1 − 0.40 = 0.60`.
- 5 biến liên tục của mỗi dòng → đưa qua Mamdani → 16 đặc trưng mờ (điểm rủi ro của L3 sẽ cao).
- `Device Type`: L1 desktop → `[1,0,0,0]`, L3 mobile → `[0,1,0,0]`.
- 19 đặc trưng số → StandardScaler.

**Ghép lại:** mỗi dòng thành vector **39 chiều** → đưa vào MLP.

---

## 8. Tóm tắt "vì sao" (dễ bị hỏi khi báo cáo)
1. **Sắp xếp theo user + thời gian** → để `shift(1)` lấy đúng "lần trước".
2. **Đặc trưng lịch sử chỉ dùng quá khứ** (`shift`, `cumsum − current`) → chống leakage.
3. **Chia stratified** → giữ tỉ lệ 3% dương ở cả 3 tập.
4. **Fit mọi bộ tiền xử lý CHỈ trên train** (median RTT, rarity, ngưỡng Mamdani, scaler, one-hot) → val/test chỉ được *transform*, không được *fit*.
5. **rarity của Country/ASN lạ = 1** → phản ánh đúng "địa điểm lạ ⇒ rủi ro".
6. **min/max Mamdani lấy từ train** → suy luận 1 dòng vẫn đúng, không méo hàm thuộc.
7. Kết quả: đầu vào **39 chiều = 19 số + 4 one-hot + 16 mờ**.
