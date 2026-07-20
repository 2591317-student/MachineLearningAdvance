"""
Cấu hình chung cho project: đường dẫn file, tên cột, hyperparameters.
Chỉnh sửa file này nếu bạn muốn đổi đường dẫn dữ liệu hoặc siêu tham số.
"""
import os

# ---- Đường dẫn ----
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs")

# ĐẶT FILE rba_sample_500k.csv (hoặc file dữ liệu RBA của bạn) VÀO THƯ MỤC data/
# Nếu tên file khác, đổi lại DATA_FILENAME bên dưới.
DATA_FILENAME = "rba_sample_500k.csv"
DATA_PATH = os.path.join(DATA_DIR, DATA_FILENAME)

MODEL_PATH = os.path.join(OUTPUT_DIR, "mlp_mamdani_model.pt")
PIPELINE_PATH = os.path.join(OUTPUT_DIR, "preprocessing_pipeline.pkl")
METRICS_PATH = os.path.join(OUTPUT_DIR, "metrics.json")

# ---- Cột dữ liệu ----
TARGET_COLUMN = "Is Attack IP"

# ---- Hyperparameters huấn luyện ----
RANDOM_STATE = 42
TEST_SIZE = 0.30       # tách 30% làm (val+test)
VAL_TEST_SPLIT = 0.50  # trong 30% đó, chia đôi val/test -> tổng thể 70/15/15

EPOCHS = 30
BATCH_SIZE = 4096
LEARNING_RATE = 1e-3
HIDDEN_DIMS = (128, 64, 32)
DROPOUT = 0.3
EARLY_STOPPING_PATIENCE = 5

# ---- Mamdani Fuzzy Inference System ----
FUZZY_OUTPUT_GRID_POINTS = 51

os.makedirs(OUTPUT_DIR, exist_ok=True)
