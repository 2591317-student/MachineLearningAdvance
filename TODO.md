# VIỆC CÒN THIẾU — Nộp đồ án cuối kỳ (Nhóm 10)

> Hạn nộp: **17h Chủ nhật 02/08/2026** trên **UTEXLMS**.
> Ngày cập nhật: 2026-07-27.

## Bối cảnh nộp bài
- **GVHD:** TS. Phan Thị Huyền Trang.
- **Nhóm 10:** Lê Phú Nhân (2591317) · Phạm Trung Kiên (2591310) · Nguyễn Minh Tuấn (2591325).
- **Báo cáo phải theo template tạp chí JTE** và **tự viết** — cô nói rõ: *"để AI sinh ra là cô sẽ yêu cầu viết lại"*. ⇒ Không dùng AI viết nội dung báo cáo.
- **Bộ file nộp:** Báo cáo (JTE) + Code (notebook Colab/GitHub) + Slide + Video báo cáo 10–15 phút.
- **Quy trình test cuối kỳ:** nộp video trước → cô ra câu hỏi → hôm báo cáo mỗi nhóm 15 phút trả lời câu hỏi vào giấy. Thứ tự nhóm 10: Phạm Trung Kiên số 3 — **Thứ 3, 04/08, 19h10–19h40**.

---

## ✅ Đã xong
- **Code:** `Nhom_10-Nhan_Kien_Tuan.ipynb` — notebook Colab nhóm chạy thực tế (23 bước, có ablation), chia theo từng cell + kết quả chạy, 0 lỗi. **Chạy trên TOÀN BỘ 500.000 dòng** (train 350.000 / val 75.000 / test 75.000).
- **Báo cáo JTE:** `Nhom_10-Nhan_Kien_Tuan.docx` — nhóm tự viết, đúng định dạng JTE (lề, TNR 11, song ngữ, IMRAD, IEEE refs, tiểu sử tác giả). Đã sửa email tiểu sử tác giả 2 → 2591310. *(Đã đổi tên từ `Bao_cao_RBA_theo_mau_JTE_chinhsua.docx`; bản AI mẫu HCMUTE đã gỡ khỏi repo.)*
- **Slide:** `Nhom_10-Nhan_Kien_Tuan.pptx` — 19 trang (có slide ablation), ghi chú thuyết trình đầy đủ, cỡ chữ ≥16pt, đã ghi GVHD + Nhóm 10.
- **Tài liệu học/hiểu (để tự viết lại, KHÔNG copy vào báo cáo):**
  - `GiaiThich_ThuatToan_ViDu.md` — Mamdani + MLP kèm ví dụ tính tay.
  - `GiaiThich_Data_TienXuLy.md` — dữ liệu + tiền xử lý từng bước, có sơ đồ luồng + ví dụ tính tay 3 lượt đăng nhập.

---

## ⚠️ CÒN THIẾU / CẦN LÀM

### A. Báo cáo JTE — nhóm TỰ viết (không để AI viết)
- [x] **Ablation** (mục 3.3 + Bảng 3): đã có, số liệu khớp đúng notebook (full 500k): fuzzy cải thiện MỌI chỉ số, rõ nhất Recall +0,0144 và AUPRC +0,0100. ✅
- [x] **Thuật toán tổng quát** (mục 2.4, pseudo-code Algorithm 1). ✅
- [x] **Trích dẫn 5 → 8** (thêm [6] Freeman, [7] Saito, [8] Jang ANFIS). ✅
- [x] **Điền email tác giả liên hệ** (đủ 3 email SV). ✅
- [~] **So sánh với phương pháp khác** (mục 4.2/4.3b): đã lồng trích dẫn Wiefling/Freeman + baseline trong prose; *có thể* thêm 1 bảng đối chiếu số nếu muốn mạnh hơn.
- [—] **Cắt tóm tắt tiếng Việt ≤250 từ**: nhóm quyết định **giữ nguyên 265 từ** (bỏ qua).
- [x] **Đồng bộ kết quả về FULL 500k** (28/07, nhóm gửi notebook chạy lại toàn bộ dữ liệu): Bảng 2/3 + abstract (EN/VI) + thảo luận + confusion + cỡ test (75.000) + Hình 5 + slide + biểu đồ + outputs/ + README/STATUS/TongHop đều dùng số mới → khớp 100% với code. Kết quả: AUROC 0,877 · AUPRC 0,216 · Accuracy 0,795 · Precision 0,114 · Recall 0,843 · F1 0,201. ✅

### B. File nộp — đặt tên đúng cú pháp & tránh nhầm
- [x] **Đổi tên báo cáo JTE** → `Nhom_10-Nhan_Kien_Tuan.docx`. ✅
- [x] Đã gỡ bản AI (mẫu HCMUTE) khỏi repo. ✅
- [x] Chốt **1 notebook** duy nhất `Nhom_10-Nhan_Kien_Tuan.ipynb` (+ header nhóm). ✅
- [x] **Slide ablation**: đã thêm slide 15 (Δ có/không fuzzy) + ghi chú thuyết trình; slide đánh số lại (19 trang). ✅

### C. Video & nộp
- [ ] **Quay video báo cáo 10–15 phút** → đặt tên `Nhom_10-Nhan_Kien_Tuan.mp4` (nặng thì up Google Drive, gửi link cho cô).
- [ ] **Đẩy code lên GitHub/Colab** và kiểm tra link chạy được, hiển thị đủ cell + output.
- [ ] **Nộp UTEXLMS** trước 17h CN 02/08/2026 (đủ: báo cáo + link code + slide + video/link video).

---

## Gợi ý tài liệu tham khảo (nhóm tự đọc & tự trích dẫn — nhớ kiểm tra lại vol/no/trang/DOI)
- S. Wiefling, M. Dürmuth, L. Lo Iacono — *"What's in Score for Website Users…"* — Financial Cryptography (FC), 2021.
- D. Freeman và cộng sự — *"Who Are You? A Statistical Approach to Measuring User Authenticity"* — NDSS, 2016.
- J.-S. R. Jang — *"ANFIS: Adaptive-Network-Based Fuzzy Inference System"* — IEEE Trans. SMC, 1993.
- P. V. de Campos Souza — *"Fuzzy neural networks and neuro-fuzzy networks: A review"* — Applied Soft Computing, 2020.
- T. Saito, M. Rehmsmeier — *"The Precision-Recall Plot Is More Informative than the ROC Plot…"* — PLOS ONE, 2015.
- N. V. Chawla và cộng sự — *"SMOTE…"* — JAIR, 2002.
- T.-Y. Lin và cộng sự — *"Focal Loss for Dense Object Detection"* — ICCV 2017 / IEEE TPAMI 2020.
