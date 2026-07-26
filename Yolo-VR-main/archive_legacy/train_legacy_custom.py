import argparse
import time
from pathlib import Path
from datetime import datetime
from ultralytics import YOLO

BASE_DIR = Path(__file__).resolve().parent

# ========================= CUSTOM CONFIG =========================

DATASET_NAME = "Custom-Accident-Scene"
DATA_YAML = BASE_DIR / "Dataset" / DATASET_NAME / "data.yaml"
PROJECT_DIR = BASE_DIR / "runs" / "custom_scene"

def get_train_config(model="yolo11s.pt", epochs=150, batch=16, imgsz=640):
    """Return training configuration dict."""
    return {
        "model": model,
        "epochs": epochs,
        "batch": batch,
        "imgsz": imgsz,
        "patience": 30,
        "optimizer": "AdamW",
        "lr0": 0.001,
        "lrf": 0.01,
        "workers": 4,
        "plots": True,
        "save_period": 25,
        "val": True,
        "verbose": True,
        # Một số augmentations nhẹ (tránh đổi màu quá mức đối với máu/vết phanh)
        "hsv_h": 0.015,
        "hsv_s": 0.5,
        "hsv_v": 0.4,
        "degrees": 10.0,
        "translate": 0.1,
        "scale": 0.5,
        "fliplr": 0.5,
        "mosaic": 1.0,
    }

def main():
    parser = argparse.ArgumentParser(description="Train YOLO11 on Custom Accident Scene Dataset")
    parser.add_argument("--model", type=str, default="yolo11s.pt",
                        help="Pre-trained model to start from (default: yolo11s.pt)")
    parser.add_argument("--epochs", type=int, default=150, help="Training epochs (default: 150)")
    parser.add_argument("--batch", type=int, default=16, help="Batch size (default: 16)")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size (default: 640)")
    args = parser.parse_args()

    print(f"\n{'='*70}")
    print(f"  🚀 Training: {DATASET_NAME}")
    print(f"  📝 Custom Objects: Blood, Belongings, Skid Mark, Scale Bar")
    print(f"  📁 Data: {DATA_YAML}")
    print(f"  ⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    if not DATA_YAML.exists():
        print(f"  ❌ File không tồn tại: {DATA_YAML}")
        print("  Hãy đảm bảo bạn đã copy đủ ảnh và file labels vào thư mục Dataset/Custom-Accident-Scene/")
        return

    # Load pre-trained model
    model = YOLO(args.model)

    # Prepare arguments
    config = get_train_config(model=args.model, epochs=args.epochs, batch=args.batch, imgsz=args.imgsz)
    train_args = {k: v for k, v in config.items() if k != "model"}
    train_args["data"] = str(DATA_YAML)
    train_args["project"] = str(PROJECT_DIR)
    train_args["name"] = "train"
    train_args["exist_ok"] = True

    try:
        start_time = time.time()
        results = model.train(**train_args)
        elapsed = time.time() - start_time
        hours, remainder = divmod(int(elapsed), 3600)
        minutes, seconds = divmod(remainder, 60)

        print(f"\n{'='*70}")
        print(f"  ✅ {DATASET_NAME} - Training Complete!")
        print(f"  ⏱️  Duration: {hours}h {minutes}m {seconds}s")
        print(f"  📦 Best weights: {PROJECT_DIR}/train/weights/best.pt")
        print(f"{'='*70}\n")
    except Exception as e:
        print(f"  ❌ Lỗi khi huấn luyện: {e}")

if __name__ == "__main__":
    main()
