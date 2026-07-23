# Giải thích thuật toán kèm ví dụ tính từng bước

Dự án dùng 2 thuật toán cốt lõi. Tài liệu này giải thích rõ và **tính tay từng
bước bằng số cụ thể** cho mỗi thuật toán:

- **A. Hệ suy diễn mờ Mamdani** — biến đặc trưng một lượt đăng nhập thành 1 điểm rủi ro.
- **B. Huấn luyện MLP** — cơ chế Forward Propagation & Backpropagation.

---

## A. Hệ suy diễn mờ Mamdani — ví dụ cho ra điểm 0.8391

**Mục tiêu:** từ đặc trưng của một lượt đăng nhập → một điểm rủi ro trong [0, 1].
Hệ chạy qua 4 bước: Fuzzification → Rule Evaluation → Aggregation → Defuzzification.

**Toán tử mờ:** AND = `min`, OR = `max`, NOT = `1 − μ`.

### Dữ liệu ví dụ (một lượt đăng nhập rủi ro cao)

| Đặc trưng | Giá trị / tình huống |
|---|---|
| Quốc gia | Mới (khác lần trước) → `is_new_country = 1` |
| ASN (nhà mạng) | Mới → `is_new_asn = 1`, và rất hiếm |
| Thời gian từ lần đăng nhập trước | Rất lâu (gap lớn) |
| Tỉ lệ đăng nhập thành công trước đó | Thấp |
| Số thứ thay đổi (thiết bị/trình duyệt/OS…) | Nhiều |

### Bước 1 — Fuzzification (mờ hóa)

Mỗi biến liên tục được đưa về mức độ thuộc Low/Medium/High bằng hàm tam giác
(ngưỡng học từ phân vị 20/50/80 của tập train). Với mẫu trên, ta thu được các
mức độ thuộc (μ) cần dùng:

| Mức độ thuộc | Giá trị μ |
|---|---|
| `gap_high` (lâu không đăng nhập) | 0.052 |
| `asn_rarity_high` (ASN hiếm) | 0.943 |
| `success_low` (tỉ lệ thành công thấp) | 0.629 |
| `num_changes_high` (đổi nhiều thứ) | 0.600 |
| `is_new_country`, `is_new_asn` | 1.0 ; 1.0 |

### Bước 2 — Rule Evaluation (tính độ kích hoạt từng luật)

Áp 8 luật IF-THEN, dùng min cho AND và max cho OR:

| Luật | Công thức | Tính | Kết quả (firing) | Hệ quả |
|---|---|---|---|---|
| R1 | min(is_new_country, is_new_asn, gap_high) | min(1, 1, 0.052) | **0.052** | High |
| R2 | success_low | 0.629 | **0.629** | High |
| R3 | num_changes_high | 0.600 | **0.600** | High |
| R4 | asn_rarity_high | 0.943 | **0.943** | High |
| R5 | min(NOT new_country, …) | có thừa số = 0 | 0.000 | Low |
| R6 | min(gap_low, country_rarity_low) | ≈ 0 | 0.000 | Low |
| R7 | max(changes_med, gap_med) | ≈ 0 | 0.000 | Medium |
| R8 | min(success_med, …) | ≈ 0 | 0.000 | Medium |

→ Chỉ 4 luật hệ quả **High** kích hoạt; Low và Medium đều bằng 0.

### Bước 3 — Aggregation (gộp bằng max)

Mỗi luật "cắt phẳng" tập mờ đầu ra của nó tại độ kích hoạt, rồi gộp tất cả bằng
`max`. Vì R1–R4 cùng cho **High**, tập kết quả là tập mờ `High` bị cắt ngang tại
độ kích hoạt lớn nhất:

```
mức cắt = max(0.052, 0.629, 0.600, 0.943) = 0.943
```

Tập mờ `High` là tam giác vai phải: μ(y) = (y − 0.5) / 0.5 với y ∈ [0.5, 1.0].
Cắt ngang tại μ = 0.943 nghĩa là:
- Với y ∈ [0.5 , 0.9715] : μ(y) = (y − 0.5)/0.5 (phần dốc lên)
- Với y ∈ [0.9715 , 1.0] : μ(y) = 0.943 (phần bị cắt phẳng)

(0.9715 = 0.5 + 0.943 × 0.5 là điểm mà đường dốc chạm mức 0.943.)

### Bước 4 — Defuzzification (Centroid — lấy trọng tâm)

Quy tập mờ đã gộp về **một con số** bằng công thức trọng tâm, rời rạc hóa miền
[0, 1] thành lưới 51 điểm:

```
             Σ μ(y)·y
centroid = ──────────
              Σ μ(y)
```

Thay số (tính trên 51 điểm của lưới):

```
Tử số   Σ μ(y)·y = 10.8463
Mẫu số  Σ μ(y)   = 12.9260

centroid = 10.8463 / 12.9260 = 0.8391
```

→ **Điểm rủi ro = 0.839** (> 0.5) ⇒ lượt đăng nhập này **rủi ro cao**. Điểm này
(cùng 15 mức độ thuộc) được đưa vào MLP làm đặc trưng, không phải quyết định cuối.

---

## B. Huấn luyện MLP — ví dụ Forward & Backpropagation (1 mẫu)

MLP học theo 4 bước, lặp qua nhiều epoch. Dưới đây minh họa **một nơ-ron đầu ra**
với 2 đặc trưng để thấy rõ phép tính; mạng nhiều tầng lặp lại đúng nguyên lý này
và dùng quy tắc chuỗi (chain rule) để lan truyền ngược qua các tầng.

### Dữ liệu ví dụ

- Một mẫu, 2 đặc trưng (đã chuẩn hóa): **x = [1.0 , 2.0]**
- Nhãn thật: **y = 1** (là tấn công)
- Khởi tạo: **w = [0.5 , −0.3]**, **b = 0.1**, learning rate **lr = 0.1**

### B1 — Khởi tạo
Đã có w, b, lr ở trên.

### B2 — Forward Propagation (lan truyền tiến)

```
z = w·x + b = 0.5×1.0 + (−0.3)×2.0 + 0.1 = 0.5 − 0.6 + 0.1 = 0.0
ŷ = σ(z) = 1 / (1 + e^0) = 0.5          (xác suất tấn công dự đoán)
```

### B3 — Tính Loss & Gradient (Backpropagation)

```
Loss (BCE) = −[ y·ln(ŷ) + (1−y)·ln(1−ŷ) ]
           = −[ 1·ln(0.5) + 0 ] = 0.693

Sai số:  error = ŷ − y = 0.5 − 1 = −0.5

∂L/∂w = error · x = −0.5 × [1.0 , 2.0] = [−0.5 , −1.0]
∂L/∂b = error       = −0.5
```

### B4 — Cập nhật tham số (Gradient Descent)

```
w mới = w − lr·∂L/∂w = [0.5, −0.3] − 0.1×[−0.5, −1.0] = [0.55 , −0.20]
b mới = b − lr·∂L/∂b = 0.1 − 0.1×(−0.5)               = 0.15
```

### Kiểm chứng (một bước đã tiến đúng hướng)

Tính lại với tham số mới:

```
z mới = 0.55×1.0 + (−0.20)×2.0 + 0.15 = 0.30
ŷ mới = σ(0.30) = 0.574
```

Dự đoán tăng từ **0.5 → 0.574**, tiến gần nhãn thật (y = 1) ⇒ Loss giảm. Lặp lại
B2 → B3 → B4 cho tất cả mẫu, qua nhiều epoch, mô hình sẽ hội tụ.

> Ghi chú: MLP thật có 3 tầng ẩn (128 → 64 → 32) với ReLU + BatchNorm + Dropout.
> Backpropagation tính `∂L/∂z = ŷ − y` ở tầng ra rồi lan truyền ngược qua từng
> tầng bằng chain rule; hàm mất mát dùng `pos_weight` để xử lý mất cân bằng lớp.
