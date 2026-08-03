# Kịch bản thuyết trình — 5 slide đầu (Phần mở đầu + Phần 1: Bài toán)

> Tài liệu để **luyện nói**, không phải học thuộc từng chữ. Đọc kỹ vài lần, hiểu vì sao
> từng câu tồn tại, rồi diễn đạt lại bằng giọng của bạn khi quay video/báo cáo.
> Đối chiếu nguồn: `GiaiThich_Data_TienXuLy.md` (giải thích kỹ thuật) và
> `QA_Data_TienXuLy.md` (câu hỏi hay gặp).

---

## SLIDE 1 — Trang bìa

**Trên slide:** tên đề tài, tên 3 thành viên, Nhóm 10, Lớp KHMT 2025B, GVHD.

**Nói (10–15 giây, không hơn):**
> "Xin chào cô và các bạn. Nhóm 10 xin trình bày đồ án cuối kỳ môn Học Máy Nâng Cao,
> đề tài: Phát hiện đăng nhập rủi ro bằng cách kết hợp mạng nơ-ron đa tầng MLP với
> hệ suy diễn mờ Mamdani. Nhóm gồm Phạm Trung Kiên, Nguyễn Minh Tuấn và Lê Phú Nhân,
> lớp KHMT 2025B, dưới sự hướng dẫn của cô Phan Thị Huyền Trang."

**Lưu ý:** Đi thẳng vào, không giải thích thêm gì — mọi nội dung để dành cho slide 3 trở đi.

---

## SLIDE 2 — Mục lục (6 phần)

**Trên slide:** 6 phần — Bài toán RBA / Kiến trúc hệ thống / Mamdani Fuzzy Logic / Mạng MLP / Kết quả thực nghiệm / Hạn chế & Kết luận.

**Nói (10–15 giây):**
> "Bài trình bày gồm 6 phần: đầu tiên là bài toán Risk-Based Authentication, sau đó
> kiến trúc hệ thống lai, đi sâu vào hệ mờ Mamdani, kiến trúc mạng MLP, kết quả
> thực nghiệm, và cuối cùng là hạn chế cùng hướng phát triển."

**Lưu ý:** Đây là slide "bản đồ" — nói một lượt, không dừng lại giải thích từng mục.
Ghi chú sẵn trong pptx cũng nhắc: "đi nhanh slide này."

---

## SLIDE 3 — Risk-Based Authentication là gì?

**Trên slide:** định nghĩa RBA + sơ đồ Đăng nhập → Chấm điểm rủi ro → An toàn/Rủi ro
+ mục tiêu đồ án (dự đoán xác suất một lượt đăng nhập đến từ IP tấn công, trên
500.000 dòng log thật).

**Nói (45–60 giây):**
> "Thông thường, hệ thống đăng nhập chỉ kiểm tra một điều: mật khẩu đúng hay sai.
> Risk-Based Authentication đi xa hơn — với MỖI lượt đăng nhập, dù mật khẩu đúng,
> hệ thống vẫn chấm một điểm rủi ro dựa trên nhiều tín hiệu ngữ cảnh: người này đăng
> nhập từ đâu, bằng thiết bị gì, qua nhà mạng nào, vào thời điểm nào, và trước đây họ
> thường đăng nhập ra sao.
>
> Ví dụ dễ hình dung: một tài khoản luôn đăng nhập từ Việt Nam, ban ngày, cùng một
> chiếc điện thoại quen thuộc. Nếu đột nhiên có một lượt đăng nhập lúc 3 giờ sáng,
> từ một quốc gia lạ, qua một nhà mạng chưa từng thấy — dù mật khẩu vẫn đúng — hệ
> thống RBA sẽ chấm điểm rủi ro cao và yêu cầu xác thực thêm, ví dụ mã OTP.
>
> Mục tiêu của đồ án là xây dựng một mô hình dự đoán xác suất một lượt đăng nhập đến
> từ IP tấn công, huấn luyện và đánh giá trên khoảng 500.000 dòng dữ liệu log đăng
> nhập thật."

**Điểm cần nhấn:** RBA là sự **cân bằng** giữa an toàn (bắt được tấn công) và trải
nghiệm người dùng (không làm phiền người dùng thật bằng xác thực thêm không cần thiết).
Ghi chú pptx cũng nhấn đúng điểm này.

**Câu hỏi có thể gặp:** "RBA khác 2FA/OTP thông thường ở điểm nào?" → Trả lời: 2FA
bắt mọi người xác thực thêm mọi lúc; RBA chỉ yêu cầu xác thực thêm khi điểm rủi ro
cao, nên trải nghiệm người dùng tốt hơn mà vẫn an toàn.

---

## SLIDE 4 — Bộ dữ liệu

**Trên slide:** 500.000 lượt đăng nhập / ~3% là tấn công / 16 cột đặc trưng thô;
nguồn Wiefling và cộng sự; các nhóm cột (thời gian, RTT; vị trí; thiết bị; nhãn).

**Nói (45–60 giây):**
> "Dữ liệu nhóm dùng là 'Login Data Set for Risk-Based Authentication' do Wiefling,
> Lo Iacono và Dürmuth công bố — đây là log đăng nhập thật đã được ẩn danh hóa, không
> phải dữ liệu giả lập. Bộ dữ liệu có khoảng 500.000 dòng, mỗi dòng là một lượt đăng
> nhập, với 16 cột thô: thời gian đăng nhập, mã người dùng, độ trễ mạng, vị trí địa
> lý gồm quốc gia/thành phố/nhà mạng, loại thiết bị/trình duyệt/hệ điều hành, và các
> cột nhãn.
>
> Điểm quan trọng nhất của bộ dữ liệu này: chỉ khoảng 3% các lượt đăng nhập là tấn
> công — tức là dữ liệu mất cân bằng lớp rất nặng. Con số 3% này ảnh hưởng đến toàn
> bộ phần còn lại của đồ án: nó là lý do nhóm không thể dùng Accuracy để đánh giá mô
> hình — vì chỉ cần đoán 'không phải tấn công' cho mọi dòng, mô hình cũng đạt gần 97%
> Accuracy mà không phát hiện được tấn công nào. Vì vậy nhóm ưu tiên các chỉ số nhạy
> với lớp thiểu số như AUPRC và Recall, điều này sẽ nói rõ hơn ở phần kết quả."

**Điểm cần nhấn:** Câu cuối là **cầu nối chủ động** sang phần 5 (Kết quả) — nói trước
để giám khảo không bất ngờ khi thấy Accuracy không phải chỉ số chính ở phần sau.

**Câu hỏi có thể gặp:** "Vì sao không cân bằng lại dữ liệu (SMOTE/undersampling)?"
→ Có thể trả lời: nhóm xử lý mất cân bằng ở tầng loss (`pos_weight` trong
BCEWithLogitsLoss) thay vì resampling dữ liệu, và nêu SMOTE là một hướng có thể thử
thêm (đã liệt kê trong tài liệu tham khảo [Chawla và cộng sự]).

---

## SLIDE 5 — Vì sao chọn nhãn "Is Attack IP"?

**Trên slide:** 3 lựa chọn — `Is Account Takeover` (✗), `Login Successful` (✗),
`Is Attack IP` (✓ đã chọn).

**Nói (45–60 giây, đây là slide quan trọng nhất trong 5 slide đầu):**
> "Bộ dữ liệu có sẵn 3 cột có thể dùng làm nhãn để dự đoán, nhóm phải chọn 1.
>
> Cột thứ nhất, `Is Account Takeover`, đánh dấu tài khoản đã thực sự bị chiếm quyền —
> nghe rất đúng ý nghĩa bảo mật, nhưng trên 500.000 dòng chỉ có khoảng 4 mẫu dương.
> Bốn mẫu là quá ít để một mô hình học máy học được bất kỳ điều gì có ý nghĩa, nên
> nhóm loại bỏ.
>
> Cột thứ hai, `Login Successful`, đánh dấu đăng nhập có thành công hay không — cột
> này có đủ dữ liệu, nhưng bản chất nó phản ánh lỗi kỹ thuật, ví dụ gõ sai mật khẩu
> hay lỗi mạng, chứ không phản ánh rủi ro bảo mật. Một người dùng thật gõ sai mật
> khẩu không phải là một mối đe dọa.
>
> Cột thứ ba, `Is Attack IP`, đánh dấu lượt đăng nhập có đến từ một địa chỉ IP đã biết
> là nguồn tấn công hay không. Cột này có khoảng 3% dương — đủ dữ liệu để huấn luyện
> và đánh giá, đồng thời đúng bản chất của bài toán chấm điểm rủi ro mà đồ án hướng
> tới. Vì vậy nhóm chọn `Is Attack IP` làm nhãn mục tiêu."

**Điểm cần nhấn:** Đây là **quyết định về dữ liệu quan trọng nhất** của toàn bộ đồ án
— nói chắc, không vòng vo. Cấu trúc "loại 2, chọn 1, mỗi cái nêu đúng 1 lý do" giúp
câu trả lời gọn và dễ nhớ.

**Câu hỏi có thể gặp (rất hay bị hỏi xoáy ở đây):**
- *"Chỉ 4 mẫu dương thì sao không gộp `Is Account Takeover` với `Is Attack IP` làm
  nhãn multi-task?"* → Có thể trả lời: đây là hướng khả thi nhưng nằm ngoài phạm vi
  đồ án hiện tại; với 4 mẫu, ngay cả multi-task cũng khó đánh giá được reliably; đây
  có thể là hướng phát triển.
- *"Login Successful có tương quan gì với Is Attack IP không?"* → Nếu không chắc số
  liệu cụ thể, có thể trả lời logic: hai cột này thường không trùng nhau — một tấn
  công có thể đăng nhập sai (bị chặn) hoặc thành công (nếu đoán đúng mật khẩu), nên
  không thể dùng thay thế cho nhau.

---

## Tổng kết cách trình bày 5 slide

| Slide | Thời lượng gợi ý | Mức độ chi tiết |
|---|---|---|
| 1 — Bìa | 10–15s | Ngắn gọn |
| 2 — Mục lục | 10–15s | Rất ngắn, chỉ liệt kê |
| 3 — RBA là gì | 45–60s | Có ví dụ cụ thể |
| 4 — Bộ dữ liệu | 45–60s | Có câu bắc cầu sang phần Kết quả |
| 5 — Vì sao chọn nhãn | 45–60s | Nói chắc nhất, đây là trọng tâm |

**Tổng thời gian phần mở đầu:** ~2.5–3 phút — hợp lý cho một video 10–15 phút có 19 slide.
