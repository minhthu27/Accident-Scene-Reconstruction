import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

# ========================= CONFIGURATION =========================

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "Dataset" / "FireSmokeAccident"
DATA_YAML = DATASET_DIR / "data.yaml"
PROJECT_DIR = BASE_DIR / "runs" / "fire_smoke"

# Dataset info
DATASET_NAME = "FireSmokeAccident"
NUM_CLASSES = 5
CLASS_NAMES = ['accident', 'vehicle', 'pothole', 'fire', 'smoke']

# ========================= TRAINING CONFIG =========================

DEFAULT_CONFIG = {
    # Model
    "model": "yolo11n.pt",          # yolo11n/s/m/l/x.pt

    # Training Hyperparameters
    "epochs": 150,                   # Total training epochs
    "batch": 16,                     # Batch size (-1 for auto)
    "imgsz": 640,                    # Input image size
    "patience": 30,                  # Early stopping patience

    # Optimizer
    "optimizer": "AdamW",            # SGD, Adam, AdamW, NAdam, RAdam
    "lr0": 0.001,                    # Initial learning rate
    "lrf": 0.01,                     # Final learning rate factor
    "momentum": 0.937,              # SGD momentum / Adam beta1
    "weight_decay": 0.0005,         # L2 regularization

    # Warmup
    "warmup_epochs": 5.0,
    "warmup_momentum": 0.8,
    "warmup_bias_lr": 0.1,

    # Loss weights
    "box": 7.5,                     # Box loss weight
    "cls": 0.5,                     # Cls loss weight (tuned for class imbalance)
    "dfl": 1.5,                     # Distribution focal loss weight

    # Augmentation (tuned for accident/fire/smoke scenes)
    "hsv_h": 0.015,                 # HSV-Hue
    "hsv_s": 0.7,                   # HSV-Saturation (important for fire/smoke)
    "hsv_v": 0.4,                   # HSV-Value
    "degrees": 10.0,                # Rotation (more for varied accident angles)
    "translate": 0.15,              # Translation
    "scale": 0.5,                   # Scale
    "shear": 3.0,                   # Shear
    "perspective": 0.0001,          # Perspective
    "flipud": 0.0,                  # Vertical flip
    "fliplr": 0.5,                  # Horizontal flip
    "mosaic": 1.0,                  # Mosaic augmentation
    "mixup": 0.15,                  # Mixup (helps with smoke/fire overlap)
    "copy_paste": 0.15,             # Copy-paste augmentation
    "erasing": 0.4,                 # Random erasing

    # Other
    "cos_lr": True,                 # Cosine learning rate scheduler
    "close_mosaic": 15,             # Disable mosaic for last N epochs
    "amp": True,                    # Automatic Mixed Precision
    "workers": 4,                   # DataLoader workers
    "cache": False,                 # Cache images
    "seed": 42,                     # Random seed
    "deterministic": True,          # Deterministic mode
    "plots": True,                  # Generate training plots
    "save_period": 25,              # Save checkpoint every N epochs
    "val": True,                    # Validate during training
    "verbose": True,                # Verbose output
}


def validate_dataset():
    """Validate dataset exists and is properly structured."""
    print(f"\n{'='*60}")
    print(f"  Validating Dataset: {DATASET_NAME}")
    print(f"{'='*60}")

    if not DATA_YAML.exists():
        print(f"  [ERROR] data.yaml not found at: {DATA_YAML}")
        sys.exit(1)
    print(f"  [OK] data.yaml found")

    splits = {"train": "train", "valid": "valid", "test": "test"}
    for split_name, split_dir in splits.items():
        img_dir = DATASET_DIR / split_dir / "images"
        lbl_dir = DATASET_DIR / split_dir / "labels"

        if not img_dir.exists():
            print(f"  [ERROR] {split_dir}/images not found")
            sys.exit(1)

        img_count = len(list(img_dir.glob("*")))
        lbl_count = len(list(lbl_dir.glob("*.txt"))) if lbl_dir.exists() else 0

        status = "[OK]" if abs(img_count - lbl_count) <= 5 else "[WARN]"
        print(f"  {status} {split_name}: {img_count} images, {lbl_count} labels")

    print(f"\n  Classes ({NUM_CLASSES}):")
    for i, name in enumerate(CLASS_NAMES):
        print(f"    [{i}] {name}")
    print(f"{'='*60}\n")


def train(args):
    """Run YOLO11 training."""
    from ultralytics import YOLO

    # Validate dataset
    validate_dataset()

    # Load model
    model_name = args.model or DEFAULT_CONFIG["model"]
    print(f"  Loading model: {model_name}")

    if args.resume:
        last_ckpt = PROJECT_DIR / "train" / "weights" / "last.pt"
        if last_ckpt.exists():
            model = YOLO(str(last_ckpt))
            print(f"  [RESUME] Resuming from: {last_ckpt}")
        else:
            print(f"  [ERROR] No checkpoint found at {last_ckpt}")
            sys.exit(1)
    else:
        model = YOLO(model_name)

    # Build training arguments
    train_args = {
        "data": str(DATA_YAML),
        "project": str(PROJECT_DIR),
        "name": "train",
        "exist_ok": True,
    }

    # Merge defaults
    for key, value in DEFAULT_CONFIG.items():
        if key == "model":
            continue
        if hasattr(args, key) and getattr(args, key) is not None:
            train_args[key] = getattr(args, key)
        else:
            train_args[key] = value

    # CLI overrides
    if args.epochs:
        train_args["epochs"] = args.epochs
    if args.batch:
        train_args["batch"] = args.batch
    if args.imgsz:
        train_args["imgsz"] = args.imgsz

    # Print config
    print(f"\n{'='*60}")
    print(f"  Training Configuration")
    print(f"{'='*60}")
    print(f"  Model:    {model_name}")
    print(f"  Dataset:  {DATASET_NAME}")
    print(f"  Epochs:   {train_args['epochs']}")
    print(f"  Batch:    {train_args['batch']}")
    print(f"  ImgSize:  {train_args['imgsz']}")
    print(f"  Device:   auto")
    print(f"  Output:   {PROJECT_DIR}/train/")
    print(f"  Time:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # Train
    results = model.train(**train_args)

    print(f"\n{'='*60}")
    print(f"  [OK] Training Complete!")
    print(f"  Best weights: {PROJECT_DIR}/train/weights/best.pt")
    print(f"  Last weights: {PROJECT_DIR}/train/weights/last.pt")
    print(f"{'='*60}\n")

    return results


def evaluate(args):
    """Run validation on the best model."""
    from ultralytics import YOLO

    best_pt = PROJECT_DIR / "train" / "weights" / "best.pt"
    if not best_pt.exists():
        print(f"  [ERROR] No trained model found. Train first!")
        sys.exit(1)

    model = YOLO(str(best_pt))

    print(f"\n  [EVAL] Evaluating on test set...")
    results = model.val(
        data=str(DATA_YAML),
        split="test",
        project=str(PROJECT_DIR),
        name="eval",
        exist_ok=True,
        plots=True,
        verbose=True,
    )

    print(f"\n{'='*60}")
    print(f"  [RESULTS] Evaluation Results - {DATASET_NAME}")
    print(f"{'='*60}")
    print(f"  mAP50:      {results.box.map50:.4f}")
    print(f"  mAP50-95:   {results.box.map:.4f}")
    print(f"  Precision:  {results.box.mp:.4f}")
    print(f"  Recall:     {results.box.mr:.4f}")
    print(f"{'='*60}\n")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YOLO11 Training - FireSmokeAccident")
    parser.add_argument("--model", type=str, default=None, help="Model: yolo11n/s/m/l/x.pt")
    parser.add_argument("--epochs", type=int, default=None, help="Training epochs")
    parser.add_argument("--batch", type=int, default=None, help="Batch size")
    parser.add_argument("--imgsz", type=int, default=None, help="Image size")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint")
    parser.add_argument("--eval", action="store_true", help="Run evaluation only")

    args = parser.parse_args()

    if args.eval:
        evaluate(args)
    else:
        train(args)
