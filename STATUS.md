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
- [x] Dọn & sắp xếp: đưa toàn bộ tài liệu phân tích vào repo.

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

### ✅ (1) Sửa lỗi rò rỉ dữ liệu (leakage) — ĐÃ SỬA CODE + ĐÃ TRAIN LẠI + ĐÃ KIỂM THỬ
- **Đã làm:** chuyển `median RTT` và độ hiếm Country/ASN sang fit **CHỈ trên train**
  — thêm `fit_global_stats()` / `apply_global_stats()` trong `features.py`; gọi
  trong `dataset_prep.prepare_splits`; lưu `global_stats` vào pipeline; áp lại
  trong `inference.predict_risk`.
- **Đã train lại** với dataset thật (`data/rba_sample_500k.csv`, máy có sklearn
  1.7.2): `outputs/` (model, pipeline, metrics.json, 5 biểu đồ) giờ khớp đúng
  code mới. Metrics gần như không đổi (AUROC 0.878, AUPRC 0.218, Recall 84.3%,
  Precision 11.3%) — leakage vốn nhẹ ở quy mô batch lớn, nhưng pipeline giờ
  đúng nguyên tắc.
- **Đã kiểm thử:** `python inference.py` chạy được với pipeline mới (có khóa
  `global_stats`), 2 kịch bản rủi ro cao/thấp cho kết quả tách biệt hợp lý.

### ✅ (2) Giải thích thuật toán huấn luyện MLP — ĐÃ THÊM VÀO BÁO CÁO
- Đã thêm mục **5.5 "Thuật toán huấn luyện: Forward & Backpropagation"** vào
  `BaoCao_TongHop_RBA.docx` (B1 khởi tạo → B2 forward → B3 loss + backprop →
  B4 cập nhật, kèm công thức), nối với nguyên lý Perceptron ở Buổi 9.

### 🟢 (3) Xác nhận miền dữ liệu với thầy/cô — CẦN BẠN LÀM
- Đề nêu ví dụ "phân loại văn bản, hình ảnh"; dự án dùng **dữ liệu bảng** (log
  đăng nhập). Dấu "..." cho phép bài toán khác → khả năng cao OK, nhưng nên xác nhận.

### ✅ (4) Demo — ĐÃ CHẠY, PASS
- `python inference.py` chạy được với model/pipeline mới (có `global_stats`).
  Kịch bản rủi ro cao dùng Country/ASN lạ để tạo độ hiếm cao đúng cách.

### ✅ (5) Gộp 2 báo cáo trùng lặp — ĐÃ XỬ LÝ
- Repo từng có 2 file báo cáo Word nội dung trùng nhau
  (`BaoCao_CuoiKy_RBA_MLP_Fuzzy.docx` bản gốc và `BaoCao_TongHop_RBA.docx` bản
  tổng hợp mới hơn, có thêm mục Forward/Backprop). Đã chọn **giữ
  `BaoCao_TongHop_RBA.docx` làm báo cáo chính thức**, xóa file cũ, cập nhật số
  liệu mới nhất + thêm mục 8.2 "Lỗi đã phát hiện và khắc phục" (gộp cả 2 lỗi:
  xmin/xmax và leakage thống kê toàn cục).

> **Trạng thái hiện tại: mọi việc đã hoàn tất.** Code, model, outputs, báo cáo
> VÀ slide đều đã đồng bộ với nhau. Slide `SlideThuyetTrinh_RBA_MLP_Fuzzy.pptx`
> đã được cập nhật đúng số liệu retrain mới nhất (AUROC 87.8%, AUPRC 21.8%,
> Accuracy 79.3%, Precision 11.3%, Recall 84.3%, F1 20.0%) — đã kiểm tra không
> còn số cũ nào sót lại.

---

## 5. Danh sách file phân tích (trong repo)

```
MachineLearningAdvance/
├── BaoCao_TongHop_RBA.docx      # báo cáo Word tổng hợp (mới)
├── TongHop_DuAn_RBA.md          # tổng quan toàn dự án (mới)
├── LuatMo_SoDo_RBA.md           # chi tiết hệ mờ + sơ đồ (mới)
├── STATUS.md                    # file này
├── SlideThuyetTrinh_RBA_MLP_Fuzzy.pptx        # slide thuyết trình (18 trang)
├── BaoCao_Assets/               # 4 hình minh họa
└── rba_local_project/           # source + model + outputs
```
