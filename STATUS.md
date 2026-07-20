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
| Giải thích thuật toán | ⚠️ Gần đủ | Mamdani rất kỹ; **phần huấn luyện MLP (forward/backprop) chưa giải thích sâu** |

---

## 4. CÒN CẦN LÀM THÊM (ưu tiên từ cao xuống thấp)

### 🔴 (1) Sửa lỗi rò rỉ dữ liệu (leakage) — QUAN TRỌNG NHẤT
- **Vấn đề:** trong `features.py`, `median RTT` và `value_counts` (country/asn
  rarity) tính trên **TOÀN BỘ df** (gồm cả val/test) vì `engineer_features`
  chạy TRƯỚC `prepare_splits`.
- **Rủi ro:** giám khảo có thể hỏi; slide 16 mới nhắc lỗi `xmin/xmax` đã sửa,
  chưa nhắc lỗi này.
- **Cần làm:** tính median/rarity **chỉ trên tập train** rồi transform cho
  val/test → train lại → cập nhật `metrics.json` + biểu đồ + báo cáo.
  *(HOẶC: giữ nguyên nhưng chuẩn bị câu trả lời "leakage nhẹ ở thống kê toàn cục".)*

### 🟡 (2) Bổ sung phần giải thích thuật toán huấn luyện MLP
- **Vấn đề:** báo cáo/slide mới mô tả *kiến trúc + chiến lược train*, chưa giải
  thích cơ chế học (Forward Propagation → Loss → Backpropagation → Gradient
  Descent, các bước B1–B4).
- **Cần làm:** thêm 1 mục vào báo cáo, tận dụng nội dung Perceptron đã có ở
  `BT-2591317-Buoi9/`.

### 🟢 (3) Xác nhận miền dữ liệu với thầy/cô
- Đề nêu ví dụ "phân loại văn bản, hình ảnh"; dự án dùng **dữ liệu bảng** (log
  đăng nhập). Dấu "..." trong đề cho phép bài toán khác → **khả năng cao OK**,
  nhưng nên xác nhận nếu đề yêu cầu chặt về text/image.

### ⚪ (tùy chọn) Chuẩn bị demo
- `python inference.py` chạy sẵn 2 kịch bản (rủi ro cao/thấp) → có thể demo
  trực tiếp lúc thuyết trình.

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
