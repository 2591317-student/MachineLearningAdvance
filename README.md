# Báo cáo cuối kỳ — Học Máy Nâng Cao

Kết hợp **MLP (Multi-Layer Perceptron)** với **Mamdani Fuzzy Logic** cho bài
toán phát hiện đăng nhập rủi ro (Risk-Based Authentication — RBA).

## Cấu trúc repo

```
CuoiKy/
├── Nhom_10-Nhan_Kien_Tuan.ipynb          # Notebook (Colab): code chia theo cell + kết quả chạy
├── Nhom_10-Nhan_Kien_Tuan.docx           # Báo cáo chính thức (giải thích thuật toán, công thức, kết quả)
├── Nhom_10-Nhan_Kien_Tuan.pptx           # Slide thuyết trình (19 trang)
├── GiaiThich_ThuatToan_ViDu.md           # Giải thích 2 thuật toán kèm ví dụ tính tay từng bước
├── STATUS.md                             # Nhật ký tiến độ / trạng thái dự án
├── TongHop_DuAn_RBA.md, LuatMo_SoDo_RBA.md  # Ghi chú phân tích chi tiết
├── BaoCao_Assets/                        # Hình minh hoạ thuật toán dùng trong báo cáo/slide
│   ├── hinh1_kien_truc_tong_the.png
│   ├── hinh2_membership_functions.png
│   ├── hinh3_vidu_mamdani_4buoc.png
│   ├── hinh4_kien_truc_mlp.png
│   └── rule_list.txt
└── rba_local_project/                    # Toàn bộ source code (xem README riêng bên trong)
    ├── src/                               # feature engineering, Mamdani FIS, MLP, train/inference
    ├── outputs/                           # model đã train, metrics, biểu đồ kết quả
    ├── data/                              # ĐẶT DATASET VÀO ĐÂY (không nằm trong git, xem bên dưới)
    └── README.md                          # hướng dẫn cài đặt & chạy chi tiết
```

## Notebook (Colab) — code chia theo từng cell + kết quả

File [`Nhom_10-Nhan_Kien_Tuan.ipynb`](Nhom_10-Nhan_Kien_Tuan.ipynb) trình bày toàn
bộ pipeline theo **từng code cell kèm kết quả chạy tương ứng** (23 bước): nạp dữ
liệu thật → feature engineering theo lịch sử đăng nhập → hệ mờ Mamdani → chia
train/val/test → kiến trúc MLP → huấn luyện → đánh giá + biểu đồ → lưu model →
suy luận demo → **ablation (MLP có/không đặc trưng mờ)**. Notebook chạy trên
Google Colab trên **toàn bộ 500.000 lượt đăng nhập** (train 350.000 / val 75.000 /
test 75.000); kết quả và biểu đồ tương ứng được lưu ở `rba_local_project/outputs/`.

## Bắt đầu nhanh

Xem hướng dẫn cài đặt/chạy đầy đủ tại [`rba_local_project/README.md`](rba_local_project/README.md).

```bash
git clone https://github.com/2591317-student/MachineLearningAdvance.git
cd MachineLearningAdvance/rba_local_project
python -m venv venv && venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

**Lưu ý:** file dataset (`rba_sample_500k.csv`, ~140MB) **không được đưa vào
git** (xem `.gitignore`) vì quá lớn. Sau khi clone, phải tự chép file dataset
vào `rba_local_project/data/rba_sample_500k.csv` trước khi chạy `train.py`.

## Model đã train sẵn

`rba_local_project/outputs/` đã có sẵn model, pipeline tiền xử lý và toàn bộ
biểu đồ kết quả từ lần train gần nhất — không bắt buộc phải train lại nếu chỉ
muốn xem/dùng kết quả. Chạy `python inference.py` để thử dự đoán ngay mà
không cần dataset đầy đủ hay train lại.

## Kết quả (tập Test, 75.000 dòng)

| Metric | Giá trị |
|---|---|
| AUROC | 0.877 |
| AUPRC | 0.216 |
| Recall | 84.3% |
| Precision | 11.4% |

Chi tiết đầy đủ (kiến trúc, công thức, phân tích, hạn chế) xem trong
[`Nhom_10-Nhan_Kien_Tuan.docx`](Nhom_10-Nhan_Kien_Tuan.docx).
