# Hệ mờ Mamdani & Sơ đồ kiến trúc — Dự án RBA (MLP + Fuzzy)

Tài liệu này giải thích chi tiết 8 luật mờ trong `src/fuzzy_mamdani.py`, kèm
sơ đồ kiến trúc tổng thể và sơ đồ 4 bước suy diễn Mamdani minh hoạ cách hệ
mờ cho ra điểm rủi ro `0.8391`.

---

## 1. Toán tử mờ dùng trong code

| Toán tử | Cài đặt | Ý nghĩa |
|---|---|---|
| **AND** | `np.minimum` / `np.minimum.reduce` | lấy min các mức thuộc — cần MỌI điều kiện đều cao |
| **OR** | `np.maximum` | lấy max — chỉ cần MỘT điều kiện cao |
| **NOT** | `1 − μ` | phần bù mờ chuẩn (vd `not_new_country = 1 − is_new_country`) |

5 biến liên tục được mờ hoá thành 3 mức Low/Med/High bằng **hàm tam giác**,
với ngưỡng học từ **percentile 20/50/80 trên tập train**. Hai biến nhị phân
`is_new_country`, `is_new_asn` dùng trực tiếp (0/1).

---

## 2. Chi tiết 8 luật mờ

Cột "độ kích hoạt" là ví dụ cho một lượt đăng nhập rủi ro (nguồn
`BaoCao_Assets/rule_list.txt`).

| Luật | Tiền đề | Toán tử | Hệ quả | Kích hoạt |
|------|---------|---------|--------|-----------|
| **R1** | `is_new_country` AND `is_new_asn` AND `gap_high` | AND (min) | **High** | 0.052 |
| **R2** | `success_rate` Low | trực tiếp | **High** | 0.629 |
| **R3** | `num_changes` High | trực tiếp | **High** | 0.600 |
| **R4** | `asn_rarity` High | trực tiếp | **High** | 0.943 |
| **R5** | NOT new_country AND NOT new_asn AND changes_low AND success_high | AND (min) | **Low** | 0.000 |
| **R6** | `gap_low` AND `country_rarity_low` | AND (min) | **Low** | 0.000 |
| **R7** | `changes_med` OR `gap_med` | OR (max) | **Medium** | 0.000 |
| **R8** | `success_med` AND (NOT new_country OR NOT new_asn) | AND lồng OR | **Medium** | 0.000 |

> Ánh xạ tên: `gap_*` ← `time_since_last_login_h`, `crare_*` ← `country_rarity`,
> `arare_*` ← `asn_rarity`, `succ_*` ← `user_success_rate_so_far`,
> `chg_*` ← `num_changes`.

### Diễn giải từng luật

**Nhóm đẩy về RỦI RO CAO (R1–R4):**

- **R1** — Đăng nhập từ *quốc gia mới* + *ASN mới* + *đã lâu không đăng nhập*.
  Chân dung điển hình của chiếm tài khoản (kẻ lạ, mạng khác, sau thời gian
  dài). Dùng AND nên cần cả 3 cùng cao → ở ví dụ chỉ kích hoạt yếu (0.052).
- **R2** — *Tỉ lệ đăng nhập thành công trong quá khứ thấp* → nghi brute-force /
  dò mật khẩu (nhiều lần fail trước đó).
- **R3** — *Nhiều thứ thay đổi cùng lúc* (thiết bị + trình duyệt + OS + thành
  phố…) → ngữ cảnh khác lạ hoàn toàn.
- **R4** — *ASN rất hiếm* (VPN/proxy/hosting lạ). Kích hoạt mạnh nhất (0.943),
  là luật kéo điểm rủi ro lên cao nhất trong ví dụ.

**Nhóm kéo về RỦI RO THẤP (R5–R6):**

- **R5** — Không đổi quốc gia + không đổi ASN + ít thay đổi + tỉ lệ thành công
  cao → mọi thứ quen thuộc, an toàn.
- **R6** — Vừa đăng nhập gần đây + quốc gia quen thuộc → an toàn.

**Nhóm giữ RỦI RO TRUNG BÌNH (R7–R8):**

- **R7** — Số thay đổi trung bình HOẶC khoảng cách thời gian trung bình (OR,
  chỉ cần 1 trong 2).
- **R8** — Tỉ lệ thành công trung bình VÀ (ít nhất quốc gia HOẶC ASN không đổi).

**Nhận xét thiết kế:** bất đối xứng có chủ đích — **4 luật cho High**, 2 cho
Low, 2 cho Medium. Đúng tinh thần bảo mật: nhiều "cửa" để phát hiện rủi ro.

---

## 3. Sơ đồ kiến trúc tổng thể

```
              ┌──────────────────────────────┐
              │  Dữ liệu đăng nhập (CSV ~500k) │
              │  nhãn: Is Attack IP            │
              └───────────────┬──────────────┘
                              ▼
              ┌──────────────────────────────┐
              │  Feature engineering           │
              │  19 đặc trưng số (chống leakage)│
              └──────┬──────────┬──────────┬──┘
                     ▼          ▼          ▼
          ┌───────────────┐ ┌──────────┐ ┌─────────────────────┐
          │ StandardScaler │ │ One-Hot  │ │ ★ Mamdani Fuzzy      │
          │ 19 đặc trưng số│ │Device Type│ │  16 đặc trưng rủi ro │
          └───────┬───────┘ └────┬─────┘ └──────────┬──────────┘
                  └──────────────┼──────────────────┘
                                 ▼
                  ┌──────────────────────────┐
                  │ Ghép ma trận X (~39 chiều) │
                  └─────────────┬────────────┘
                                ▼
                  ┌──────────────────────────┐
                  │ MLP (PyTorch)             │
                  │ 128 → 64 → 32 → 1 logit    │
                  └─────────────┬────────────┘
                                ▼
                  ┌──────────────────────────┐
                  │ sigmoid → xác suất tấn công│
                  │ ≥ 0.5 → nhãn 1 (tấn công)  │
                  └──────────────────────────┘

  ★ = điểm mới: hệ mờ biến tri thức chuyên gia thành đặc trưng cho MLP
      (KHÔNG chạy song song để so sánh — mà hợp nhất ở tầng đầu vào)
```

---

## 4. Sơ đồ 4 bước Mamdani — cách ra số 0.8391

```
┌───────────────┐   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│1 Fuzzification│──▶│2 Đánh giá luật│──▶│3 Gộp (max)    │──▶│4 Giải mờ      │
│ mờ hoá 5 biến │   │ 8 luật IF-THEN│   │ cắt tại firing│   │ centroid      │
│→ Low/Med/High │   │ R4 = 0.943    │   │ High cắt 0.943│   │ (lưới 51 điểm)│
└───────────────┘   └───────────────┘   └───────────────┘   └───────┬───────┘
                                                                     ▼
                          mamdani_risk_score = 0.8391  →  RỦI RO CAO
```

### Diễn giải từng bước cho lượt đăng nhập ví dụ

1. **Fuzzification** — mờ hoá 5 biến của lượt đăng nhập:
   - `asn_rarity` rất cao → mức thuộc *High ≈ 0.943*
   - `user_success_rate_so_far` thấp → *succ_low ≈ 0.629*
   - `num_changes` nhiều → *chg_high ≈ 0.600*
   - (quốc gia mới + ASN mới + gap dài → thành phần cho R1)

2. **Đánh giá luật** — tính độ kích hoạt (firing) mỗi luật:
   - R1 = 0.052, R2 = 0.629, R3 = 0.600, **R4 = 0.943** → tất cả hệ quả **High**
   - R5–R8 = 0.000 (không luật Low/Med nào kích hoạt)

3. **Gộp (Aggregation, max)** — mỗi luật "cắt phẳng" tập mờ hệ quả tại độ kích
   hoạt của nó, rồi gộp tất cả bằng `max`. Vì cả 4 luật cùng cho **High**,
   phần được giữ lại là tập mờ `OUT_HIGH` (tam giác vai phải 0.5→1.0) **bị cắt
   ngang tại 0.943** (độ kích hoạt lớn nhất). Low/Med đóng góp 0.

4. **Giải mờ Centroid** — tính trọng tâm của hình đã gộp trên lưới 51 điểm:
   ```
   centroid = Σ(μ(y)·y) / Σ(μ(y))  =  0.8391
   ```
   (Nếu không luật nào kích hoạt → gán mặc định 0.5.)

→ **0.8391 > 0.5 ⇒ rủi ro cao.** Điểm số này (cùng 15 mức thuộc mờ) được đưa
vào MLP làm đặc trưng, không phải là quyết định cuối cùng.

---

*Tài liệu đi kèm bản tổng hợp toàn dự án: `TongHop_DuAn_RBA.md`.*
