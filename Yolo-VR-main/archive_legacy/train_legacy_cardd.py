import argparse
import sys
from pathlib import Path
from datetime import datetime

# CẤU HÌNH

# Đường dẫn
BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "Dataset" / "CarDD-DamageDetection"
DATA_YAML = DATASET_DIR / "data.yaml"
PROJECT_DIR = BASE_DIR / "runs" / "cardd"

# Thông tin dataset
DATASET_NAME = "CarDD-DamageDetection"
NUM_CLASSES = 6
CLASS_NAMES = ['dent', 'scratch', 'crack', 'glass shatter', 'lamp broken', 'tire flat']

# CẤU HÌNH TRAINING

DEFAULT_CONFIG = {
    # Model
    "model": "yolo11n.pt",          # yolo11n/s/m/l/x.pt (nano -> extra-large)

    # Siêu tham số training
    "epochs": 150,                   # Tổng số epoch
    "batch": 16,                     # Batch size (-1 để tự động)
    "imgsz": 640,                    # Kích thước ảnh đầu vào
    "patience": 30,                  # Số epoch chờ trước khi dừng sớm

    # Optimizer
    "optimizer": "AdamW",            # SGD, Adam, AdamW, NAdam, RAdam, RMSProp
    "lr0": 0.001,                    # Learning rate ban đầu
    "lrf": 0.01,                     # Learning rate cuối (lr0 * lrf)
    "momentum": 0.937,               # Momentum SGD / beta1 của Adam
    "weight_decay": 0.0005,          # L2 regularization

    # Warmup
    "warmup_epochs": 5.0,            # Số epoch warmup
    "warmup_momentum": 0.8,          # Momentum ban đầu khi warmup
    "warmup_bias_lr": 0.1,           # Bias lr ban đầu khi warmup

    # Trọng số loss
    "box": 7.5,                      # Trọng số box loss
    "cls": 0.5,                      # Trọng số classification loss
    "dfl": 1.5,                      # Trọng số distribution focal loss

    # Augmentation (tinh chỉnh cho bài toán nhận diện hư hỏng xe)
    "hsv_h": 0.015,                  # Augmentation HSV-Hue
    "hsv_s": 0.7,                    # Augmentation HSV-Saturation
    "hsv_v": 0.4,                    # Augmentation HSV-Value
    "degrees": 5.0,                  # Xoay ảnh (+/- độ)
    "translate": 0.1,                # Dịch chuyển (+/- tỉ lệ)
    "scale": 0.5,                    # Tỉ lệ (+/- gain)
    "shear": 2.0,                    # Cắt xén (+/- độ)
    "perspective": 0.0,              # Phối cảnh (+/- tỉ lệ)
    "flipud": 0.0,                   # Xác suất lật dọc
    "fliplr": 0.5,                   # Xác suất lật ngang
    "mosaic": 1.0,                   # Xác suất augmentation mosaic
    "mixup": 0.1,                    # Xác suất augmentation mixup
    "copy_paste": 0.1,               # Xác suất augmentation copy-paste
    "erasing": 0.4,                  # Xác suất random erasing

    # Khác
    "cos_lr": True,                  # Dùng cosine learning rate scheduler
    "close_mosaic": 15,              # Tắt mosaic N epoch cuối
    "amp": True,                     # Automatic Mixed Precision
    "workers": 4,                    # Số DataLoader workers
    "cache": False,                  # Cache ảnh (True/ram/disk)
    "seed": 42,                      # Seed cho tính tái hiện
    "deterministic": True,           # Chế độ deterministic
    "plots": True,                   # Sinh biểu đồ training
    "save_period": 25,               # Lưu checkpoint mỗi N epoch
    "val": True,                     # Validate trong khi train
    "verbose": True,                 # In thông tin chi tiết
}


def validate_dataset():
    """Kiểm tra dataset tồn tại và đúng cấu trúc."""
    print(f"\n{'='*60}")
    print(f"  Validating Dataset: {DATASET_NAME}")
    print(f"{'='*60}")

    if not DATA_YAML.exists():
        print(f"  data.yaml không tìm thấy tại: {DATA_YAML}")
        sys.exit(1)
    print(f"  data.yaml tìm thấy")

    for split in ["train", "val", "test"]:
        img_dir = DATASET_DIR / split / "images"
        lbl_dir = DATASET_DIR / split / "labels"

        if not img_dir.exists():
            print(f"  {split}/images không tìm thấy")
            sys.exit(1)

        img_count = len(list(img_dir.glob("*")))
        # Chỉ đếm file .txt, tránh đếm nhầm các file khác trong thư mục labels
        lbl_count = len(list(lbl_dir.glob("*.txt"))) if lbl_dir.exists() else 0

        status = "✅" if img_count == lbl_count else "⚠️"
        print(f"  {status} {split}: {img_count} ảnh, {lbl_count} nhãn")

    print(f"\n  Classes ({NUM_CLASSES}):")
    for i, name in enumerate(CLASS_NAMES):
        print(f"    [{i}] {name}")
    print(f"{'='*60}\n")


def train(args):
    """Chạy training YOLO11."""
    # Import trong hàm để tránh lỗi khi chỉ chạy --eval mà chưa cài ultralytics
    from ultralytics import YOLO

    # Kiểm tra dataset
    validate_dataset()

    # Load model
    model_name = args.model or DEFAULT_CONFIG["model"]
    print(f"  Đang tải model: {model_name}")

    if args.resume:
        # Tiếp tục từ checkpoint cuối
        last_ckpt = PROJECT_DIR / "train" / "weights" / "last.pt"
        if last_ckpt.exists():
            model = YOLO(str(last_ckpt))
            print(f"  Tiếp tục từ: {last_ckpt}")
        else:
            print(f"  Không tìm thấy checkpoint tại {last_ckpt}")
            sys.exit(1)
    else:
        model = YOLO(model_name)

    # Xây dựng tham số training
    train_args = {
        "data": str(DATA_YAML),
        "project": str(PROJECT_DIR),
        "name": "train",
        "exist_ok": True,
    }

    # Gộp DEFAULT_CONFIG với các giá trị ghi đè từ CLI
    # BUG FIX: Logic cũ bị trùng lặp — áp dụng DEFAULT_CONFIG trước,
    # sau đó CLI args ghi đè một lần duy nhất.
    for key, value in DEFAULT_CONFIG.items():
        if key == "model":
            continue  # Bỏ qua key "model", đã xử lý riêng ở trên
        train_args[key] = value

    # Ghi đè bằng CLI args nếu người dùng có truyền vào
    if args.epochs is not None:
        train_args["epochs"] = args.epochs
    if args.batch is not None:
        train_args["batch"] = args.batch
    if args.imgsz is not None:
        train_args["imgsz"] = args.imgsz

    # In cấu hình training
    print(f"\n{'='*60}")
    print(f"  Cấu hình Training")
    print(f"{'='*60}")
    print(f"  Model:    {model_name}")
    print(f"  Dataset:  {DATASET_NAME}")
    print(f"  Epochs:   {train_args['epochs']}")
    print(f"  Batch:    {train_args['batch']}")
    print(f"  ImgSize:  {train_args['imgsz']}")
    print(f"  Device:   auto")
    print(f"  Output:   {PROJECT_DIR}/train/")
    print(f"  Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # Bắt đầu training
    results = model.train(**train_args)

    print(f"\n{'='*60}")
    print(f"  Training hoàn tất!")
    print(f"  Best weights: {PROJECT_DIR}/train/weights/best.pt")
    print(f"  Last weights: {PROJECT_DIR}/train/weights/last.pt")
    print(f"{'='*60}\n")

    return results


def evaluate(args):
    """Chạy validation trên model tốt nhất."""
    from ultralytics import YOLO

    best_pt = PROJECT_DIR / "train" / "weights" / "best.pt"
    if not best_pt.exists():
        print(f"  Không tìm thấy model đã train. Hãy train trước!")
        sys.exit(1)

    model = YOLO(str(best_pt))

    print(f"\n Đang đánh giá trên tập test...")
    results = model.val(
        data=str(DATA_YAML),
        split="test",
        project=str(PROJECT_DIR),
        name="eval",
        exist_ok=True,
        plots=True,
        verbose=True,
    )

    # In kết quả đánh giá
    print(f"\n{'='*60}")
    print(f"  Kết quả đánh giá - {DATASET_NAME}")
    print(f"{'='*60}")
    print(f"  mAP50:      {results.box.map50:.4f}")
    print(f"  mAP50-95:   {results.box.map:.4f}")
    print(f"  Precision:  {results.box.mp:.4f}")
    print(f"  Recall:     {results.box.mr:.4f}")
    print(f"{'='*60}\n")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YOLO11 Training - CarDD Dataset")
    parser.add_argument("--model",   type=str, default=None, help="Model: yolo11n/s/m/l/x.pt")
    parser.add_argument("--epochs",  type=int, default=None, help="Số epoch training")
    parser.add_argument("--batch",   type=int, default=None, help="Batch size")
    parser.add_argument("--imgsz",   type=int, default=None, help="Kích thước ảnh")
    parser.add_argument("--resume",  action="store_true",    help="Tiếp tục từ checkpoint cuối")
    parser.add_argument("--eval",    action="store_true",    help="Chỉ chạy đánh giá")

    args = parser.parse_args()

    if args.eval:
        evaluate(args)
    else:
        train(args)
