# Trạng thái công việc — Báo cáo cuối kỳ RBA (MLP + Mamdani Fuzzy)

*Ghi lại: đã làm gì, tổng hợp được gì, còn cần làm gì. Cập nhật: 2026-07-20.*

---

## 0. Bối cảnh

- **Chủ đề cuối kỳ:** Kết hợp MLP (Multi-Layer Perceptron) với logic (fuzzy
  logic) trong một bài toán.
- **Dự án:** Phát hiện đăng nhập rủi ro (Risk-Based Authentication — RBA)
  bằng **MLP + Mamdani Fuzzy Inference System**.
- **Yêu cầu báo cáo:** làm xong model + **minh họa** và **giải thích** thuật toán.
- **Repo:** `MachineLearningAdvance/` (đã clone), source ở `rba_local_project/`.

---

## 1. ĐÃ CÓ SẴN trong dự án (do mình làm trước đó)

### Mã nguồn & mô hình (`rba_local_project/`)
- [x] `src/features.py` — feature engineering (19 đặc trưng số, chống leakage lịch sử user).
- [x] `src/fuzzy_mamdani.py` — hệ mờ Mamdani (5 biến, 8 luật, centroid, 16 đặc trưng mờ).
- [x] `src/dataset_prep.py` — chia 70/15/15 stratified, fit pipeline chỉ trên train.
- [x] `src/model.py` — MLP PyTorch (128→64→32→1), BCEWithLogitsLoss + pos_weight.
- [x] `src/train.py`, `src/inference.py`, `src/visualize.py`.
- [x] `outputs/` — model đã train (`mlp_mamdani_model.pt`), pipeline, `metrics.json`, 5 biểu đồ.

### Tài liệu báo cáo (gốc)
- [x] `BaoCao_CuoiKy_RBA_MLP_Fuzzy.docx` — báo cáo cuối kỳ.
- [x] `SlideThuyetTrinh_RBA_MLP_Fuzzy.pptx` — **18 slide** (6 phần: bài toán →
  kiến trúc → Mamdani → MLP → kết quả → hạn chế).
- [x] `BaoCao_Assets/` — 4 hình: kiến trúc tổng thể, membership functions,
  ví dụ Mamdani 4 bước (→0.839), kiến trúc MLP; + `rule_list.txt`.

### Kết quả model (tập Test, 75.000 dòng)
| AUROC | AUPRC | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|---|
| 0.877 | 0.219 | 0.790 | 0.112 | 0.845 | 0.197 |

---

## 2. ĐÃ LÀM THÊM (đợt đọc hiểu & tổng hợp này)

- [x] **Đọc hiểu toàn bộ mã nguồn** (8 file .py) + trích xuất nội dung báo cáo .docx.
- [x] Đối chiếu, xác minh mọi con số/tham số khớp giữa code — báo cáo — slide.
- [x] Tạo `TongHop_DuAn_RBA.md` — tổng quan toàn dự án (8 mục, kiến trúc, dữ
  liệu, hệ mờ, MLP, kết quả, cách chạy, hạn chế).
- [x] Tạo `LuatMo_SoDo_RBA.md` — giải thích chi tiết 8 luật mờ + sơ đồ kiến
  trúc + sơ đồ 4 bước Mamdani + diễn giải cách ra số 0.8391.
- [x] Tạo `BaoCao_TongHop_RBA.docx` — báo cáo Word hoàn chỉnh (gộp 2 file trên,
  nhúng 7 hình thật, có mục lục tự động). Đã verify XML hợp lệ.
- [x] `_gen_baocao_rba.js` — script sinh báo cáo Word (giữ lại để chỉnh/tạo lại).
- [x] Dọn & sắp xếp: đưa toàn bộ file phân tích vào repo; thêm `node_modules/`
  vào `.gitignore`.

### Kết luận đánh giá
Dự án **rất hoàn chỉnh**, đáp ứng đủ yêu cầu (model xong + minh họa + giải
thích). Có thể nộp/bảo vệ được ngay. Còn 3 điểm nên xử lý để chắc điểm cao
(mục 4).

---

## 3. Kiểm tra yêu cầu đề bài

| Yêu cầu | Trạng thái | Ghi chú |
|---|---|---|
| Kết hợp MLP + logic (fuzzy) | ✅ Đạt | MLP + Mamdani Fuzzy, hợp nhất ở tầng đặc trưng |
| Làm xong model | ✅ Đạt | Train xong, có metrics, inference chạy được |
| Minh họa thuật toán | ✅ Đạt | 4 sơ đồ + biểu đồ kết quả |
| Giải thích thuật toán | ✅ Đạt | Mamdani (4 bước) + MLP (Forward/Backprop, mục 5.5) đều đã giải thích |

---

## 4. TRẠNG THÁI CÁC VIỆC (cập nhật 2026-07-20)

### ✅ (1) Sửa lỗi rò rỉ dữ liệu (leakage) — ĐÃ SỬA CODE + KIỂM THỬ
- **Đã làm:** chuyển `median RTT` và độ hiếm Country/ASN sang fit **CHỈ trên train**
  — thêm `fit_global_stats()` / `apply_global_stats()` trong `features.py`; gọi
  trong `dataset_prep.prepare_splits`; lưu `global_stats` vào pipeline; áp lại
  trong `inference.predict_risk`.
- **Đã kiểm thử:** chạy toàn bộ pipeline bằng dữ liệu giả (features → split →
  train → inference) — PASS; giá trị Country/ASN lạ → rarity = 1 (đúng kỳ vọng).
- **⚠️ CÒN LẠI (cần dataset):** model/pipeline/metrics trong `outputs/` vẫn là
  của **code CŨ** (trước khi sửa) và **không tương thích** code mới (pipeline.pkl
  cũ thiếu khóa `global_stats`). Phải **chạy lại `python train.py`** với file
  `data/rba_sample_500k.csv` để tạo lại model + cập nhật `metrics.json` + biểu đồ.
  Số liệu có thể lệch nhẹ so với bản cũ (leakage vốn nhẹ).
  *(Cũng nên train lại vì pipeline cũ pickled bằng scikit-learn 1.7.2, máy hiện dùng 1.8.0.)*

### ✅ (2) Giải thích thuật toán huấn luyện MLP — ĐÃ THÊM VÀO BÁO CÁO
- Đã thêm mục **5.5 "Thuật toán huấn luyện: Forward & Backpropagation"** vào
  `BaoCao_TongHop_RBA.docx` (B1 khởi tạo → B2 forward → B3 loss + backprop →
  B4 cập nhật, kèm công thức), nối với nguyên lý Perceptron ở Buổi 9.

### 🟢 (3) Xác nhận miền dữ liệu với thầy/cô — CẦN BẠN LÀM
- Đề nêu ví dụ "phân loại văn bản, hình ảnh"; dự án dùng **dữ liệu bảng** (log
  đăng nhập). Dấu "..." cho phép bài toán khác → khả năng cao OK, nhưng nên xác nhận.

### ⚪ (4) Demo — CHỜ TRAIN LẠI
- `python inference.py` (2 kịch bản rủi ro cao/thấp) sẽ chạy được **sau khi
  train lại** (cần model + pipeline mới có `global_stats`). Đã cập nhật demo:
  kịch bản rủi ro cao dùng Country/ASN lạ để tạo độ hiếm cao đúng cách.

> **Việc DUY NHẤT còn phải làm khi có dataset:** đặt `rba_sample_500k.csv` vào
> `data/` rồi chạy `cd src && python train.py`. Mọi thứ khác đã xong.

---

## 5. Danh sách file phân tích (trong repo)

```
MachineLearningAdvance/
├── BaoCao_TongHop_RBA.docx      # báo cáo Word tổng hợp (mới)
├── TongHop_DuAn_RBA.md          # tổng quan toàn dự án (mới)
├── LuatMo_SoDo_RBA.md           # chi tiết hệ mờ + sơ đồ (mới)
├── STATUS.md                    # file này
├── _gen_baocao_rba.js           # generator báo cáo Word
├── BaoCao_CuoiKy_RBA_MLP_Fuzzy.docx / .pptx   # báo cáo & slide gốc
├── BaoCao_Assets/               # 4 hình minh họa
└── rba_local_project/           # source + model + outputs
```
