// Sinh báo cáo Word tổng hợp dự án RBA (gộp TongHop + LuatMo, nhúng hình).
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
  ImageRun, PageBreak, TableOfContents, LevelFormat, PositionalTab,
  PositionalTabAlignment, PositionalTabLeader
} = require("docx");

const REPO = "D:/01.DuAn/MachineLearningAdvance/MachineLearningAdvance";
const OUT = "D:/01.DuAn/MachineLearningAdvance/MachineLearningAdvance/BaoCao_TongHop_RBA.docx";
const FONT = "Times New Roman";
const NAVY = "1F3864", BLUE = "2E75B6", GREY = "595959", RED = "C00000", GREEN = "2E7D32";
const TW = 9360; // table width (DXA)

const img = (rel) => fs.readFileSync(path.join(REPO, rel));

// ---------- helpers ----------
function h1(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 260, after: 130 },
    children: [new TextRun({ text, bold: true, font: FONT, size: 32, color: NAVY })] });
}
function h2(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 },
    children: [new TextRun({ text, bold: true, font: FONT, size: 27, color: BLUE })] });
}
function h3(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 150, after: 80 },
    children: [new TextRun({ text, bold: true, font: FONT, size: 25, color: "000000" })] });
}
function p(runs, opts = {}) {
  const arr = Array.isArray(runs) ? runs : [{ text: runs }];
  return new Paragraph({ spacing: { after: 100, line: 300 }, alignment: opts.align,
    children: arr.map(r => new TextRun({ text: r.text, bold: r.bold, italics: r.i,
      font: r.mono ? "Consolas" : FONT, size: r.size || 26, color: r.color || "000000" })) });
}
function bullet(runs) {
  const arr = Array.isArray(runs) ? runs : [{ text: runs }];
  return new Paragraph({ bullet: { level: 0 }, spacing: { after: 60, line: 290 },
    children: arr.map(r => new TextRun({ text: r.text, bold: r.bold, italics: r.i,
      font: r.mono ? "Consolas" : FONT, size: r.size || 26, color: r.color || "000000" })) });
}
function code(text) {
  return new Paragraph({ spacing: { after: 100, line: 260 }, shading: { type: ShadingType.CLEAR, fill: "F2F2F2" },
    children: text.split("\n").map((ln, i) => new TextRun({ text: ln, break: i ? 1 : 0, font: "Consolas", size: 22 })) });
}
function note(text) {
  return new Paragraph({ spacing: { after: 120, line: 290 }, shading: { type: ShadingType.CLEAR, fill: "FFF8E1" },
    border: { left: { style: BorderStyle.SINGLE, size: 18, color: "F59E0B", space: 8 } },
    children: [new TextRun({ text, italics: true, font: FONT, size: 24, color: "5D4037" })] });
}
function picture(rel, w, ratio, caption) {
  const kids = [new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 100, after: 40 },
    children: [new ImageRun({ type: "png", data: img(rel), transformation: { width: w, height: Math.round(w * ratio) } })] })];
  if (caption) kids.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 },
    children: [new TextRun({ text: caption, italics: true, font: FONT, size: 22, color: GREY })] }));
  return kids;
}
function cell(text, { bold, fill, color, w, align } = {}) {
  const lines = String(text).split("\n");
  return new TableCell({ width: { size: w, type: WidthType.DXA },
    shading: fill ? { type: ShadingType.CLEAR, fill } : undefined,
    margins: { top: 40, bottom: 40, left: 80, right: 80 },
    children: [new Paragraph({ alignment: align, spacing: { after: 0, line: 264 },
      children: lines.map((ln, i) => new TextRun({ text: ln, break: i ? 1 : 0, bold, font: FONT, size: 23, color: color || "000000" })) })] });
}
function table(widths, header, rows) {
  const headRow = new TableRow({ tableHeader: true,
    children: header.map((t, i) => cell(t, { bold: true, fill: NAVY, color: "FFFFFF", w: widths[i], align: AlignmentType.CENTER })) });
  const bodyRows = rows.map((r, ri) => new TableRow({
    children: r.map((t, i) => cell(t, { w: widths[i], fill: ri % 2 ? "F4F7FB" : "FFFFFF" })) }));
  return new Table({ width: { size: TW, type: WidthType.DXA }, columnWidths: widths,
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: "BFBFBF" }, bottom: { style: BorderStyle.SINGLE, size: 4, color: "BFBFBF" },
      left: { style: BorderStyle.SINGLE, size: 4, color: "BFBFBF" }, right: { style: BorderStyle.SINGLE, size: 4, color: "BFBFBF" },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: "D9D9D9" }, insideVertical: { style: BorderStyle.SINGLE, size: 2, color: "D9D9D9" } },
    rows: [headRow, ...bodyRows] });
}
const spacer = () => new Paragraph({ spacing: { after: 60 }, children: [] });

// ---------- content ----------
const body = [];

// Title page
body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 2600, after: 120 },
  children: [new TextRun({ text: "BÁO CÁO PHÂN TÍCH DỰ ÁN", bold: true, font: FONT, size: 40, color: NAVY })] }));
body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
  children: [new TextRun({ text: "Phát hiện đăng nhập rủi ro (RBA)", bold: true, font: FONT, size: 34, color: "000000" })] }));
body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
  children: [new TextRun({ text: "Kết hợp MLP (Multi-Layer Perceptron) và hệ mờ Mamdani", font: FONT, size: 28, color: BLUE })] }));
body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
  children: [new TextRun({ text: "Học Máy Nâng Cao — Tài liệu đọc hiểu & tổng hợp mã nguồn", italics: true, font: FONT, size: 26, color: GREY })] }));
body.push(new Paragraph({ children: [new PageBreak()] }));

// TOC
body.push(h1("Mục lục"));
body.push(new TableOfContents("Mục lục", { hyperlink: true, headingStyleRange: "1-3" }));
body.push(new Paragraph({ children: [new PageBreak()] }));

// 1. Tổng quan
body.push(h1("1. Tổng quan"));
body.push(h2("1.1. Dự án làm gì"));
body.push(p("Dự án xây dựng hệ thống phát hiện rủi ro cho từng lượt đăng nhập (login-risk detection) phục vụ bài toán RBA — Risk-Based Authentication (Xác thực dựa trên rủi ro). Với mỗi lượt đăng nhập, hệ thống trả về:"));
body.push(bullet([{ text: "attack_probability", mono: true }, { text: ": xác suất lượt đăng nhập đến từ IP tấn công (số thực trong [0, 1])." }]));
body.push(bullet([{ text: "predicted_label", mono: true }, { text: ": nhãn nhị phân (0 = bình thường, 1 = tấn công), quyết định theo ngưỡng mặc định 0.5." }]));
body.push(h2("1.2. Bài toán RBA"));
body.push(p("RBA là cơ chế bảo mật trong đó mỗi lượt đăng nhập được chấm điểm rủi ro dựa trên ngữ cảnh: vị trí (Country/City), nhà mạng (ASN), thiết bị/trình duyệt/OS, thời điểm đăng nhập, độ trễ mạng (RTT) và lịch sử hành vi người dùng. Rủi ro cao thì yêu cầu xác thực bổ sung (OTP/2FA), thấp thì cho đăng nhập bình thường — cân bằng giữa bảo mật và trải nghiệm."));
body.push(h2("1.3. Ý tưởng cốt lõi — vì sao kết hợp MLP + Fuzzy"));
body.push(p("Dự án dùng mô hình lai (hybrid) theo hướng feature-level fusion (kết hợp ở tầng đặc trưng), KHÔNG phải hai mô hình chạy song song để so sánh:"));
body.push(bullet([{ text: "Hệ mờ Mamdani", bold: true }, { text: " mã hóa tri thức chuyên gia thành luật IF-THEN (vd: quốc gia mới + ASN mới sau thời gian dài ⇒ rủi ro cao). Đầu ra hệ mờ (15 mức thuộc + 1 điểm rủi ro) dùng làm đặc trưng bổ sung." }]));
body.push(bullet([{ text: "MLP", bold: true }, { text: " là bộ phân loại chính, học từ: đặc trưng số đã chuẩn hóa + one-hot + toàn bộ đặc trưng mờ." }]));
body.push(p("Lợi ích: hệ mờ đưa vào tri thức miền có tính giải thích, giúp MLP học nhanh và dễ diễn giải; MLP bù lại khả năng học tương tác phi tuyến phức tạp. Tên file model mlp_mamdani_model.pt phản ánh trực tiếp kiến trúc lai này."));

// 2. Kiến trúc
body.push(h1("2. Kiến trúc tổng thể"));
body.push(p("Luồng dữ liệu: CSV thô → feature engineering → tách 3 nhánh tiền xử lý (chuẩn hóa số, one-hot Device Type, hệ mờ Mamdani) → ghép thành ma trận đặc trưng → MLP → xác suất tấn công → ngưỡng 0.5 → nhãn."));
body.push(...picture("BaoCao_Assets/hinh1_kien_truc_tong_the.png", 600, 0.752, "Hình 1 — Kiến trúc tổng thể hệ lai MLP + Mamdani Fuzzy."));
body.push(note("Điểm mấu chốt: hệ mờ Mamdani KHÔNG thay thế và không chạy song song để so sánh với MLP. Toàn bộ 16 đặc trưng mờ (15 mức thuộc + 1 điểm mamdani_risk_score) được bơm thẳng vào MLP làm đầu vào, hợp nhất ở tầng đặc trưng cùng đặc trưng số và one-hot."));

// 3. Dữ liệu & đặc trưng
body.push(h1("3. Dữ liệu & Đặc trưng"));
body.push(h2("3.1. Dataset"));
body.push(bullet([{ text: "File: " }, { text: "rba_sample_500k.csv", mono: true }, { text: " (~500.000 dòng), đặt trong thư mục data/ (không đưa vào git vì nặng ~140MB)." }]));
body.push(bullet("Nguồn: mẫu trích từ bộ dữ liệu công khai “Login Data Set for Risk-Based Authentication” (Wiefling, Lo Iacono, Dürmuth — IFIP SEC 2019)."));
body.push(bullet("Kích thước không hard-code trong mã, lấy động qua len(df) và X_train.shape[1]."));
body.push(h2("3.2. Nhãn & mất cân bằng lớp"));
body.push(bullet([{ text: "Nhãn: " }, { text: "Is Attack IP", mono: true }, { text: " (nhị phân), tỉ lệ dương ~3% → mất cân bằng nặng." }]));
body.push(bullet("Lý do chọn: Is Account Takeover chỉ có ~4 mẫu dương (quá ít); Login Successful chỉ phản ánh lỗi kỹ thuật; Is Attack IP phù hợp nhất với bài toán chấm điểm rủi ro."));
body.push(bullet([{ text: "Xử lý mất cân bằng KHÔNG nằm ở khâu dữ liệu (chỉ có " }, { text: "stratify", mono: true }, { text: " giữ tỉ lệ lớp, không oversampling) mà nằm ở hàm mất mát của MLP (pos_weight)." }]));
body.push(h2("3.3. Chia train/val/test"));
body.push(bullet([{ text: "Hai bước train_test_split: tách 30% (TEST_SIZE) làm tạm, rồi chia đôi (VAL_TEST_SPLIT) → tổng thể " }, { text: "70% train / 15% val / 15% test", bold: true }, { text: "." }]));
body.push(bullet("stratify ở cả hai bước, random_state = 42 (tái lập được). Mọi bộ tiền xử lý (Mamdani FIS, OneHotEncoder, StandardScaler) fit CHỈ trên train để tránh leakage."));
body.push(h2("3.4. Danh sách đặc trưng"));
body.push(h3("A. Đặc trưng số/nhị phân (19 cột, features.py)"));
body.push(table([3000, 6360], ["Đặc trưng", "Cách tính"], [
  ["hour_of_day / day_of_week", "Giờ và thứ trong tuần từ Login Timestamp"],
  ["is_weekend / is_odd_hour", "Cuối tuần; giờ lạ (trước 6h hoặc sau 22h)"],
  ["rtt_missing / rtt_filled", "Cờ thiếu RTT; điền thiếu bằng median cột"],
  ["country_rarity / asn_rarity", "1 − tần suất xuất hiện của Country/ASN (càng hiếm càng gần 1)"],
  ["time_since_last_login_h", "Giờ kể từ lần login trước của cùng user; lần đầu → 8760 (24×365)"],
  ["is_first_login", "1 nếu là lần đăng nhập đầu tiên"],
  ["is_new_country / city / asn", "So với lần trước của user (shift); lần đầu = 1"],
  ["is_new_device / browser / os", "Tương tự cho thiết bị / trình duyệt / OS"],
  ["user_success_rate_so_far", "Tỉ lệ đăng nhập thành công tích lũy (chỉ quá khứ)"],
  ["user_login_count_so_far", "Số lần đăng nhập trước đó (cumcount)"],
  ["num_changes", "Tổng 6 cờ is_new_* theo hàng (0–6)"],
]));
body.push(p([{ text: "Chống data leakage: ", bold: true }, { text: "mọi đặc trưng lịch sử chỉ dùng thông tin TRƯỚC ĐÓ của cùng user (shift/cumsum/cumcount)." }]));
body.push(h3("B. Đặc trưng phân loại & mờ"));
body.push(bullet([{ text: "Phân loại: chỉ ", bold: false }, { text: "Device Type", mono: true }, { text: " → OneHotEncoder (4 cột trong tập train)." }]));
body.push(bullet("Mờ (Mamdani): 15 mức thuộc (5 biến × 3 mức) + 1 điểm mamdani_risk_score = 16 cột."));
body.push(note("Tổng chiều đầu vào MLP ≈ 39 = 19 đặc trưng số + 4 one-hot Device Type (= 23) + 16 đặc trưng mờ. Con số 4 phụ thuộc số giá trị Device Type trong train, nên input_dim có thể đổi nếu dữ liệu khác."));

// 4. Hệ mờ Mamdani
body.push(new Paragraph({ children: [new PageBreak()] }));
body.push(h1("4. Hệ mờ Mamdani (trọng tâm)"));
body.push(p("File src/fuzzy_mamdani.py, lớp MamdaniFuzzyRiskSystem, cài đặt thủ công bằng NumPy (không dùng scikit-fuzzy), theo đúng 4 bước chuẩn: Fuzzification → Rule Evaluation → Aggregation → Defuzzification."));
body.push(h2("4.1. Toán tử mờ"));
body.push(table([1800, 3000, 4560], ["Toán tử", "Cài đặt", "Ý nghĩa"], [
  ["AND", "np.minimum(.reduce)", "Lấy min — cần MỌI điều kiện đều cao"],
  ["OR", "np.maximum", "Lấy max — chỉ cần MỘT điều kiện cao"],
  ["NOT", "1 − μ", "Phần bù mờ chuẩn (not_new = 1 − is_new)"],
]));
body.push(h2("4.2. Biến ngôn ngữ & hàm thuộc"));
body.push(p("5 biến liên tục (time_since_last_login_h, country_rarity, asn_rarity, user_success_rate_so_far, num_changes) được mờ hóa thành 3 mức Low/Med/High bằng hàm TAM GIÁC. Ngưỡng học từ percentile 20/50/80 trên tập train; min/max toàn cục của train. Hai biến nhị phân is_new_country, is_new_asn dùng trực tiếp (0/1)."));
body.push(p("Hàm thuộc đầu ra (risk) cố định trên lưới 51 điểm trong [0,1]: OUT_LOW = tri(0,0,0.5), OUT_MED = tri(0.2,0.5,0.8), OUT_HIGH = tri(0.5,1,1)."));
body.push(...picture("BaoCao_Assets/hinh2_membership_functions.png", 600, 0.554, "Hình 2 — Các hàm thuộc (membership functions) Low/Medium/High."));
body.push(note("xmin/xmax PHẢI là giá trị toàn cục của train. Nếu tính lại từ batch nhỏ khi inference thì xmin=xmax= chính giá trị mẫu → méo mức thuộc Low/High. Vì vậy inference gán lại thresholds_/minmax_ từ pipeline đã lưu, không gọi fit() lại (đây là lỗi đã được phát hiện và sửa)."));
body.push(h2("4.3. Chi tiết 8 luật mờ"));
body.push(p("Cột “Kích hoạt” là ví dụ cho một lượt đăng nhập rủi ro (nguồn rule_list.txt)."));
body.push(table([760, 4000, 1200, 1200, 2200], ["Luật", "Tiền đề", "Toán tử", "Hệ quả", "Kích hoạt"], [
  ["R1", "is_new_country AND is_new_asn AND gap_high", "AND (min)", "High", "0.052"],
  ["R2", "success_rate Low", "trực tiếp", "High", "0.629"],
  ["R3", "num_changes High", "trực tiếp", "High", "0.600"],
  ["R4", "asn_rarity High", "trực tiếp", "High", "0.943"],
  ["R5", "NOT new_country AND NOT new_asn AND changes_low AND success_high", "AND (min)", "Low", "0.000"],
  ["R6", "gap_low AND country_rarity_low", "AND (min)", "Low", "0.000"],
  ["R7", "changes_med OR gap_med", "OR (max)", "Medium", "0.000"],
  ["R8", "success_med AND (NOT new_country OR NOT new_asn)", "AND lồng OR", "Medium", "0.000"],
]));
body.push(h3("Diễn giải từng luật"));
body.push(p([{ text: "Nhóm đẩy về RỦI RO CAO (R1–R4): ", bold: true, color: RED }]));
body.push(bullet([{ text: "R1", bold: true }, { text: " — Quốc gia mới + ASN mới + lâu không đăng nhập: chân dung điển hình chiếm tài khoản. Dùng AND nên cần cả 3 cùng cao (ví dụ chỉ 0.052)." }]));
body.push(bullet([{ text: "R2", bold: true }, { text: " — Tỉ lệ đăng nhập thành công quá khứ thấp → nghi brute-force / dò mật khẩu." }]));
body.push(bullet([{ text: "R3", bold: true }, { text: " — Nhiều thứ thay đổi cùng lúc (thiết bị + trình duyệt + OS + thành phố) → ngữ cảnh khác lạ." }]));
body.push(bullet([{ text: "R4", bold: true }, { text: " — ASN rất hiếm (VPN/proxy/hosting lạ). Kích hoạt mạnh nhất (0.943), kéo điểm rủi ro lên cao nhất." }]));
body.push(p([{ text: "Nhóm kéo về RỦI RO THẤP (R5–R6): ", bold: true, color: GREEN }]));
body.push(bullet([{ text: "R5", bold: true }, { text: " — Không đổi quốc gia + không đổi ASN + ít thay đổi + tỉ lệ thành công cao → an toàn." }]));
body.push(bullet([{ text: "R6", bold: true }, { text: " — Vừa đăng nhập gần đây + quốc gia quen thuộc → an toàn." }]));
body.push(p([{ text: "Nhóm giữ RỦI RO TRUNG BÌNH (R7–R8): ", bold: true, color: "B8860B" }]));
body.push(bullet([{ text: "R7", bold: true }, { text: " — Số thay đổi trung bình HOẶC khoảng cách thời gian trung bình (OR, chỉ cần 1)." }]));
body.push(bullet([{ text: "R8", bold: true }, { text: " — Tỉ lệ thành công trung bình VÀ (ít nhất quốc gia HOẶC ASN không đổi)." }]));
body.push(note("Thiết kế bất đối xứng có chủ đích: 4 luật cho High, 2 cho Low, 2 cho Medium — đúng tinh thần bảo mật, nhiều “cửa” để phát hiện rủi ro."));
body.push(h2("4.4. Cơ chế 4 bước & cách ra số 0.8391"));
body.push(...picture("BaoCao_Assets/hinh3_vidu_mamdani_4buoc.png", 620, 0.772, "Hình 3 — Minh họa 4 bước Mamdani trên một mẫu rủi ro cao (centroid = 0.839)."));
body.push(bullet([{ text: "Bước 1 — Fuzzification: ", bold: true }, { text: "mờ hóa 5 biến (asn_rarity High ≈ 0.943, success_low ≈ 0.629, num_changes High ≈ 0.600…)." }]));
body.push(bullet([{ text: "Bước 2 — Rule Evaluation: ", bold: true }, { text: "R1=0.052, R2=0.629, R3=0.600, R4=0.943 (đều → High); R5–R8 = 0." }]));
body.push(bullet([{ text: "Bước 3 — Aggregation (max): ", bold: true }, { text: "mỗi luật cắt phẳng tập mờ hệ quả tại độ kích hoạt, gộp bằng max. Cả 4 cùng “High” → tập OUT_HIGH bị cắt ngang tại 0.943; Low/Med đóng góp 0." }]));
body.push(bullet([{ text: "Bước 4 — Defuzzification (Centroid): ", bold: true }, { text: "centroid = Σ(μ·y)/Σμ trên lưới 51 điểm = 0.8391. Nếu không luật nào kích hoạt → mặc định 0.5." }]));
body.push(p([{ text: "⇒ 0.8391 > 0.5 nên rủi ro cao. Điểm này (cùng 15 mức thuộc) trở thành đặc trưng cho MLP, không phải quyết định cuối.", bold: true }]));

// 5. MLP
body.push(new Paragraph({ children: [new PageBreak()] }));
body.push(h1("5. Mô hình MLP & Huấn luyện"));
body.push(h2("5.1. Kiến trúc (model.py, PyTorch)"));
body.push(p("Mỗi tầng ẩn h gồm khối 4 lớp theo thứ tự: Linear → ReLU → BatchNorm1d → Dropout(0.3). Với HIDDEN_DIMS = (128, 64, 32):"));
body.push(code("Input(≈39)\n  → Linear(→128) → ReLU → BatchNorm1d(128) → Dropout(0.3)\n  → Linear(→64)  → ReLU → BatchNorm1d(64)  → Dropout(0.3)\n  → Linear(→32)  → ReLU → BatchNorm1d(32)  → Dropout(0.3)\n  → Linear(→1)   # logit (không activation) → sigmoid ở bước dự đoán"));
body.push(...picture("BaoCao_Assets/hinh4_kien_truc_mlp.png", 600, 0.566, "Hình 4 — Kiến trúc mạng MLP."));
body.push(h2("5.2. Loss & xử lý mất cân bằng"));
body.push(bullet([{ text: "BCEWithLogitsLoss(pos_weight = n_neg/n_pos)", mono: true }, { text: " — trọng số lớp dương theo tỉ lệ âm/dương. Không dùng Focal Loss." }]));
body.push(h2("5.3. Optimizer & siêu tham số"));
body.push(table([3400, 5960], ["Thành phần", "Giá trị"], [
  ["Optimizer", "Adam(lr=1e-3, weight_decay=1e-5)"],
  ["LR scheduler", "ReduceLROnPlateau(mode=max, factor=0.5, patience=2) theo val AUPRC"],
  ["Epochs / Batch", "tối đa 30 / 4096 (shuffle)"],
  ["Early stopping", "patience 5 theo val AUPRC"],
  ["Chọn model tốt nhất", "theo AUPRC trên validation (không theo loss/accuracy)"],
  ["Seed / Device", "42 / cuda nếu có, ngược lại cpu"],
]));
body.push(h2("5.4. Ngưỡng phân loại"));
body.push(p("Ngưỡng cứng 0.5 khi sinh metrics.json (evaluate mặc định threshold=0.5). Hàm visualize.plot_threshold_curve có tính & in ngưỡng F1 tốt nhất nhưng chỉ để tham khảo, không dùng cho kết quả chính."));

// 6. Kết quả
body.push(new Paragraph({ children: [new PageBreak()] }));
body.push(h1("6. Kết quả (tập Test, 75.000 dòng)"));
body.push(table([1800, 1800, 5760], ["Chỉ số", "Giá trị", "Ý nghĩa"], [
  ["AUROC", "0.8774", "Khả năng phân biệt tổng quát 2 lớp — khá tốt"],
  ["AUPRC", "0.2188", "Đáng tin hơn AUROC khi dữ liệu mất cân bằng (~3% dương)"],
  ["Accuracy", "0.7896", "Dễ gây hiểu nhầm với dữ liệu lệch lớp"],
  ["Precision", "0.1117", "Trong các cảnh báo tấn công, ~11% đúng thật"],
  ["Recall", "0.8449", "Trong các tấn công thật, bắt được ~84%"],
  ["F1", "0.1974", "Điều hòa Precision và Recall"],
]));
body.push(...picture("rba_local_project/outputs/metrics_bar_chart.png", 560, 0.556, "Hình 5 — Các chỉ số đánh giá trên tập Test."));
body.push(...picture("rba_local_project/outputs/roc_pr_curves.png", 620, 0.385, "Hình 6 — Đường ROC và Precision-Recall."));
body.push(...picture("rba_local_project/outputs/confusion_matrix.png", 420, 0.909, "Hình 7 — Ma trận nhầm lẫn."));
body.push(h2("6.1. Diễn giải trong bối cảnh RBA"));
body.push(bullet([{ text: "Recall cao (84.5%) + Precision thấp (11.2%) là đánh đổi có chủ đích: ", bold: true }, { text: "bắt được phần lớn tấn công (tối quan trọng — bỏ sót là rủi ro nghiêm trọng), đổi lại nhiều báo động giả." }]));
body.push(bullet("Trong RBA, hệ quả của báo động giả chỉ là yêu cầu người dùng xác thực thêm (OTP/2FA) — phiền nhưng không nguy hiểm."));
body.push(bullet("AUPRC (0.219, so với baseline ngẫu nhiên ~0.03) mới phản ánh chất lượng thật, vì Accuracy/AUROC bị “thổi phồng” bởi lớp âm áp đảo."));
body.push(note("Số liệu bổ sung (chỉ có trong báo cáo gốc): ở ngưỡng tối ưu F1 = 0.829, Precision tăng lên 27.8%, F1 = 0.327, đổi lại Recall giảm còn 39.8%."));

// 7. Cấu trúc & cách chạy
body.push(new Paragraph({ children: [new PageBreak()] }));
body.push(h1("7. Cấu trúc thư mục & cách chạy"));
body.push(code("rba_local_project/\n├── data/rba_sample_500k.csv     # tự đặt vào\n├── src/\n│   ├── config.py                # hằng số, đường dẫn, hyperparameter\n│   ├── features.py              # load_raw(), engineer_features()\n│   ├── fuzzy_mamdani.py         # MamdaniFuzzyRiskSystem\n│   ├── dataset_prep.py          # prepare_splits() — chia + fit pipeline\n│   ├── model.py                 # MLPClassifier, train_mlp(), evaluate()\n│   ├── train.py                 # script huấn luyện chính\n│   ├── inference.py             # dự đoán không train lại + demo\n│   └── visualize.py             # vẽ biểu đồ\n└── outputs/                     # model, pipeline, metrics, 5 biểu đồ"));
body.push(h2("7.1. Cài đặt & chạy"));
body.push(code("cd rba_local_project\npython -m venv venv && venv\\Scripts\\activate   # Windows\npip install -r requirements.txt\n\ncd src\npython train.py       # huấn luyện + xuất model/metrics/biểu đồ\npython inference.py   # dự đoán demo (không cần train lại)"));
body.push(p("requirements: numpy≥1.24, pandas≥2.0, scikit-learn≥1.3, torch≥2.0, matplotlib≥3.7. Mamdani FIS tự cài bằng numpy (không dùng scikit-fuzzy)."));
body.push(h2("7.2. Dự đoán (inference.py)"));
body.push(p("Load model + pipeline đã lưu, tái lập y hệt lúc train: dựng lại FIS từ thresholds_/minmax_ → transform; one-hot; scale; ghép đúng thứ tự cột input_columns; sigmoid → attack_probability và predicted_label. Đầu vào phải đã qua engineer_features (các đặc trưng phụ thuộc lịch sử user, không tính được từ 1 dòng đơn lẻ tách rời)."));

// 8. Nhận xét
body.push(new Paragraph({ children: [new PageBreak()] }));
body.push(h1("8. Nhận xét, hạn chế & hướng phát triển"));
body.push(h2("8.1. Điểm mạnh"));
body.push(bullet("Kiến trúc lai có tính giải thích: 8 luật Mamdani mã hóa tri thức chuyên gia minh bạch, hỗ trợ MLP."));
body.push(bullet("Chống data leakage bài bản ở phần lớn pipeline (đặc trưng lịch sử dùng shift/cumsum; FIS/Scaler/OHE fit chỉ trên train; chia stratified có seed)."));
body.push(bullet("Chọn nhãn/metric phù hợp mất cân bằng (Is Attack IP ~3%; chọn model theo AUPRC; xử lý mất cân bằng bằng pos_weight)."));
body.push(bullet("Đã phát hiện & sửa lỗi thực: xmin/xmax batch-local trong hàm thuộc → đã lưu min/max toàn cục vào pipeline để inference đúng."));
body.push(h2("8.2. Điểm yếu / rủi ro"));
body.push(bullet("Precision thấp (11.2%) ở ngưỡng 0.5 — nhiều báo động giả; chưa tối ưu ngưỡng ở quyết định cuối."));
body.push(bullet([{ text: "Rò rỉ thống kê toàn cục tinh vi (CHƯA sửa): ", bold: true }, { text: "median RTT và value_counts cho country/asn rarity tính trên TOÀN BỘ df (gồm cả val/test) vì engineer_features chạy trước prepare_splits. Nên tính chỉ trên train." }]));
body.push(bullet("8 luật fuzzy thiết kế thủ công theo trực giác, chưa tối ưu tự động."));
body.push(bullet("requirements dùng “>=” (không ghim phiên bản chính xác) → có thể lệch hành vi giữa các phiên bản."));
body.push(h2("8.3. Hướng phát triển"));
body.push(bullet("Thử Focal Loss / tinh chỉnh pos_weight để tăng Precision mà không giảm Recall quá nhiều."));
body.push(bullet("Chọn ngưỡng theo ma trận chi phí thực tế (cân bằng bỏ sót tấn công vs làm phiền người dùng)."));
body.push(bullet("Tối ưu/học tự động hệ mờ (ANFIS hoặc thuật toán tiến hóa) thay vì thiết kế luật thủ công."));
body.push(bullet("Khắc phục leakage thống kê toàn cục; ghim phiên bản thư viện để tái lập."));
body.push(h2("8.4. Kết luận"));
body.push(p("Dự án xây dựng thành công hệ lai MLP + Mamdani Fuzzy trên ~500.000 lượt đăng nhập cho bài toán RBA. Hệ mờ mã hóa tri thức chuyên gia (8 luật) thành đặc trưng giải thích được, ghép cùng đặc trưng số/one-hot làm đầu vào MLP 3 tầng ẩn (128→64→32). Kết quả test (AUROC 0.877, AUPRC 0.219, Recall 84.5%, Precision 11.2% ở ngưỡng 0.5) cho thấy mô hình bắt được phần lớn tấn công — phù hợp mục tiêu bảo mật — dù tỉ lệ báo động giả còn cao, một đánh đổi chấp nhận được và có thể tinh chỉnh qua ngưỡng."));

// ---------- document ----------
const doc = new Document({
  numbering: { config: [{ reference: "b", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 460, hanging: 260 } } } }] }] },
  styles: { default: { document: { run: { font: FONT, size: 26 } } } },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    children: body,
  }],
});

Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log("Saved:", OUT, buf.length, "bytes"); });
