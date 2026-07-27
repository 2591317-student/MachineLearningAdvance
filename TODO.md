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
- **Code:** `Nhom_10-Nhan_Kien_Tuan.ipynb` — notebook Colab, code chia theo từng cell + kết quả chạy; nạp kết quả chính thức 500k từ `rba_local_project/outputs/`.
- **Báo cáo JTE:** `Nhom_10-Nhan_Kien_Tuan.docx` — nhóm tự viết, đúng định dạng JTE (lề, TNR 11, song ngữ, IMRAD, IEEE refs, tiểu sử tác giả). Đã sửa email tiểu sử tác giả 2 → 2591310. *(Đã đổi tên từ `Bao_cao_RBA_theo_mau_JTE_chinhsua.docx`; bản AI mẫu HCMUTE đã gỡ khỏi repo.)*
- **Slide:** `Nhom_10-Nhan_Kien_Tuan.pptx` — 18 trang, có ghi chú thuyết trình, cỡ chữ ≥16pt, đã ghi GVHD + Nhóm 10.

---

## ⚠️ CÒN THIẾU / CẦN LÀM

### A. Báo cáo JTE — nhóm TỰ viết (không để AI viết)
- [ ] **Ablation** (bắt buộc theo cấu trúc cô đưa, mục 4.3c): chạy + viết "MLP **không** có đặc trưng mờ" so với "MLP + Mamdani" để chứng minh phần fuzzy có đóng góp. *(Có thể nhờ hỗ trợ phần code/số; phần viết nhóm tự làm.)*
- [ ] **So sánh với phương pháp khác** (mục 4.2/4.3b): trích kết quả đã công bố (vd Wiefling và cộng sự trên cùng bộ dữ liệu) để đối chiếu.
- [ ] **Related work + tăng trích dẫn ~8** (hiện 5, chủ yếu sách/công cụ). Ưu tiên báo journal WoS/Scopus; lồng vào phần Giới thiệu. (Danh sách gợi ý: xem cuối file.)
- [ ] **Thuật toán tổng quát** dạng pseudo-code thể hiện liên kết đầu vào–đầu ra giữa các bước (mục 3).
- [ ] **Cắt tóm tắt tiếng Việt** từ 265 từ xuống **≤ 250 từ** (bản EN 183 từ đã đạt).
- [ ] **Điền email tác giả liên hệ** (đang để "[to be added]" / "[bổ sung]").

### B. File nộp — đặt tên đúng cú pháp & tránh nhầm
- [x] **Đổi tên báo cáo JTE** → `Nhom_10-Nhan_Kien_Tuan.docx` (đây là báo cáo nộp). ✅
- [x] Đã gỡ bản AI (mẫu HCMUTE) khỏi repo (còn bản sao lưu ở máy + trong lịch sử git). ✅
- [ ] Slide: nếu nộp thì giữ tên `Nhom_10-Nhan_Kien_Tuan.pptx`.

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
