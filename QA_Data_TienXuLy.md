# Bộ câu hỏi & trả lời — Data & Tiền xử lý (ôn trước khi trình bày)

> Dùng để **ôn hiểu**, không học thuộc lòng — khi trả lời (nói hoặc viết tay) hãy diễn đạt
> bằng lời của mình. Mỗi câu trả lời cố tình viết ngắn, gạch đầu dòng, đúng kiểu cần khi
> viết tay trong 15 phút. Bám sát đúng mã nguồn `features.py` / `dataset_prep.py` /
> `fuzzy_mamdani.py` — không có ý nào bịa thêm ngoài code.

---

## Nhóm 1 — Câu hỏi cơ bản về dữ liệu

**Q1. Bộ dữ liệu lấy từ đâu, có gì đặc biệt?**
- Nguồn: *Login Data Set for Risk-Based Authentication* (Wiefling và cộng sự) — log đăng nhập thật đã ẩn danh hóa.
- ~500.000 dòng, mỗi dòng = 1 lượt đăng nhập.
- Đặc biệt: chỉ **~3% là tấn công** → mất cân bằng lớp nặng.

**Q2. Vì sao chọn nhãn `Is Attack IP` mà không phải nhãn khác?**
- `Is Account Takeover`: chỉ ~4 mẫu dương / 500.000 dòng → quá ít để học.
- `Login Successful`: phản ánh lỗi kỹ thuật (sai mật khẩu, mạng lỗi...), không phải rủi ro bảo mật.
- `Is Attack IP`: ~3% dương — đủ dữ liệu để học, và đúng bản chất bài toán "chấm điểm rủi ro".

**Q3. Vì sao không dùng Accuracy để đánh giá mô hình?**
- Chỉ cần đoán "không phải tấn công" cho **mọi** dòng đã đạt Accuracy ~97% — vô nghĩa, không phát hiện được tấn công nào.
- Dùng AUPRC/Recall/Precision — các chỉ số nhạy với lớp thiểu số.
- Lúc train cũng phải bù lệch lớp bằng `pos_weight` trong hàm loss.

---

## Nhóm 2 — Feature engineering (sinh đặc trưng)

**Q4. Từ dữ liệu thô sinh ra bao nhiêu đặc trưng, chia nhóm gì?**
- Tổng **19 đặc trưng số** + 1 cột phân loại (`Device Type`, sau đó one-hot).
- 3 nhóm: (1) thời gian — tính trực tiếp từ timestamp; (2) mạng (RTT) — có xử lý giá trị thiếu; (3) hành vi lịch sử user — dùng `shift`/`cumsum` theo từng user.

**Q5. RTT bị thiếu thì xử lý thế nào, sao không bỏ luôn dòng đó?**
- Không bỏ dòng, vì mất dữ liệu và việc "thiếu RTT" tự nó **có thể là 1 tín hiệu** (liên quan loại mạng/thiết bị).
- Cách xử lý: tạo cờ `rtt_missing` (an toàn, chỉ nhìn đúng dòng đó); giá trị thực tế điền bằng **median của tập train** (`rtt_filled`) — không phải median của cả tập.

**Q6. `is_new_country` (và các is_new_* khác) tính như thế nào?**
- So sánh giá trị hiện tại với giá trị của **lần đăng nhập ngay trước đó** (`shift(1)`) của cùng user.
- Khác → 1, giống → 0. Lần đăng nhập đầu tiên của user → quy ước tất cả = 1 (vì mọi thứ đều "mới" với họ).

---

## Nhóm 3 — Chống rò rỉ dữ liệu (trọng tâm, cô hay hỏi chỗ này)

**Q7. Rò rỉ dữ liệu (data leakage) là gì, sao phải tránh?**
- Là khi mô hình "nhìn thấy" thông tin mà lẽ ra lúc dự đoán thật nó không có (ví dụ: thông tin từ tương lai, hoặc thông tin học được từ chính tập dùng để đánh giá).
- Hậu quả: điểm số lúc test cao giả tạo, nhưng triển khai thực tế thì tệ hơn hẳn — vì lúc đó không còn "nhìn trộm" được nữa.

**Q8. Làm sao đảm bảo đặc trưng lịch sử không bị leakage?**
- Nguyên tắc: đặc trưng của lượt đăng nhập tại thời điểm *t* chỉ được dùng thông tin xảy ra **trước** *t* của chính user đó.
- Kỹ thuật: `shift(1)` để lấy "lần trước", `cumsum() − giá_trị_hiện_tại` để cộng dồn nhưng loại trừ chính dòng đang xét.
- Bắt buộc `sort_values(["User ID", "Login Timestamp"])` trước, nếu không `shift(1)` sẽ lấy sai dòng.

**Q9. Nhóm từng phát hiện lỗi leakage nào, sửa ra sao?** *(câu này rất nên chủ động nhắc tới — cho thấy tự làm thật)*
- **Lỗi 1:** median RTT và tần suất Country/ASN ban đầu tính trên **toàn bộ** dữ liệu (gồm cả val/test) → sửa thành chỉ tính trên **train** (`fit_global_stats` chỉ nhận `df_train`).
- **Lỗi 2:** ngưỡng min/max của hệ mờ Mamdani từng bị tính lại theo từng lô dữ liệu đưa vào, thay vì cố định từ train → khiến suy luận 1 dòng đơn lẻ bị méo (vì min=max=chính giá trị đó). Sửa: lưu min/max cố định từ lúc `fit()` trên train, dùng lại y hệt cho mọi lần suy luận sau.

**Q10. Vì sao `user_success_rate_so_far` phải trừ đi chính dòng hiện tại (`cumsum − current`)?**
- Nếu không trừ, tỉ lệ thành công "trước đó" sẽ vô tình gồm cả kết quả của **chính lượt đang xét** — tức là dùng thông tin của hiện tại để mô tả quá khứ, một dạng leakage tinh vi dễ bị bỏ sót.
- Trừ đi để đảm bảo con số này chỉ phản ánh đúng những gì đã biết **trước khi** lượt này xảy ra.

---

## Nhóm 4 — Chia tập & fit tiền xử lý

**Q11. Vì sao chia tập theo kiểu stratified (phân tầng)?**
- Ép tỉ lệ ~3% dương phải giữ nguyên ở cả train/val/test.
- Nếu chia ngẫu nhiên thường, tập test có thể ngẫu nhiên rơi vào ít mẫu tấn công hơn hẳn → chỉ số đánh giá (đặc biệt AUPRC) dao động mạnh, không đáng tin.

**Q12. Vì sao mọi thứ "học từ dữ liệu" (scaler, one-hot, ngưỡng mờ, thống kê toàn cục) chỉ được fit trên train?**
- Nếu fit trên cả val/test, nghĩa là mô hình (một cách gián tiếp) đã biết trước phân bố của tập dùng để đánh giá nó → điểm số bị thổi phồng, không phản ánh đúng khả năng tổng quát hóa thật.
- Quy tắc chung: train → `fit_transform`; val/test → chỉ `transform`.

**Q13. Lúc suy luận, gặp Country/ASN chưa từng thấy trong train thì xử lý sao?**
- `country_freq`/`asn_freq` tra không thấy → NaN → điền 0 (`fillna(0)`).
- `rarity = 1 − freq = 1 − 0 = 1` → tự động thành "rất hiếm" — hợp lý vì địa điểm hoàn toàn lạ thường đáng ngờ hơn.
- Tương tự, thiết bị lạ qua `OneHotEncoder(handle_unknown="ignore")` → toàn bộ cột one-hot = 0, không báo lỗi.

---

## Nhóm 5 — Câu hỏi "bẫy" / đào sâu (kiểm tra hiểu bản chất, không phải học thuộc)

**Q14. Nếu 1 user chỉ đăng nhập đúng 1 lần duy nhất trong toàn bộ dữ liệu thì các đặc trưng lịch sử của họ ra sao?**
- `is_first_login = 1`.
- `time_since_last_login_h` không có "lần trước" → điền `24×365 = 8760` giờ (quy ước "rất lâu rồi").
- Tất cả `is_new_country/city/asn/device/browser/os = 1` (mọi thứ đều mới với họ).
- `user_success_rate_so_far` không có lịch sử → điền mặc định `1.0`.
- `user_login_count_so_far = 0`.

**Q15. Vì sao chọn ngưỡng phân vị 20/50/80 cho hệ mờ Mamdani mà không phải con số khác?**
- Đây là lựa chọn heuristic hợp lý (chia phân phối thành vùng thấp/giữa/cao tương đối cân bằng), **không phải** kết quả tinh chỉnh (tuning) qua thử nghiệm.
- Nếu cô hỏi sâu hơn: có thể trả lời thẳng đây là hướng có thể cải tiến (vd. để ANFIS tự học ngưỡng thay vì đặt cố định — đã nêu trong phần hướng phát triển).

**Q16. Input đưa vào MLP có bao nhiêu chiều, tính từ đâu ra?**
- **39 chiều** = 19 đặc trưng số đã chuẩn hóa + 4 cột one-hot (Device Type) + 16 đặc trưng mờ Mamdani (5 biến × 3 mức Low/Med/High = 15, cộng thêm 1 điểm rủi ro centroid).

**Q17. Nếu KHÔNG chia stratified mà chia ngẫu nhiên thường thì hậu quả cụ thể là gì?**
- Tỉ lệ ~3% dương có thể lệch đáng kể giữa 3 tập (ví dụ test chỉ còn 1-2% hoặc lên tới 5%).
- Với AUPRC — vốn rất nhạy với tỉ lệ lớp dương — số đo được sẽ dao động mạnh giữa các lần chia khác nhau, khó so sánh công bằng và khó tái lập.

**Q18. Vì sao phải `sort_values` theo cả `User ID` lẫn `Login Timestamp`, thiếu 1 trong 2 thì sao?**
- Thiếu sort theo `User ID`: `groupby("User ID")` vẫn đúng nhóm, nhưng nếu dữ liệu trong nhóm không theo thứ tự thời gian thì `shift(1)` sẽ lấy nhầm dòng không phải "lần đăng nhập ngay trước".
- Thiếu sort theo thời gian: toàn bộ đặc trưng lịch sử (`time_since_last_login_h`, `is_new_*`, `user_success_rate_so_far`...) tính sai hết, vì "quá khứ" và "hiện tại" bị đảo lộn.

---

## Mẹo khi trả lời (nói hoặc viết tay)

1. Ưu tiên trả lời **Q7-Q10 (chống leakage)** kỹ nhất — đây là phần thể hiện tư duy phương pháp luận rõ nhất, và note thuyết trình đã tự nhắc "giám khảo hay hỏi về leakage".
2. Nếu bị hỏi câu không chắc 100%, **trả lời đúng phạm vi mình biết** rồi nói thẳng giới hạn (ví dụ Q15) — tốt hơn nhiều so với cố nói cho có mà sai.
3. Khi viết tay, ưu tiên gạch đầu dòng ngắn hơn là viết đoạn văn dài — giám khảo chấm nhanh trong thời gian có hạn.
