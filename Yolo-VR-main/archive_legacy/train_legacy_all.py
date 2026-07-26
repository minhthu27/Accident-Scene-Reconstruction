
import argparse
import os
import sys
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent


# ========================= DATASET CONFIGS =========================

DATASETS = {
    "cardd": {
        "name": "CarDD-DamageDetection",
        "data_yaml": BASE_DIR / "Dataset" / "CarDD-DamageDetection" / "data.yaml",
        "project": BASE_DIR / "runs" / "cardd",
        "nc": 6,
        "classes": ['dent', 'scratch', 'crack', 'glass shatter', 'lamp broken', 'tire flat'],
        "description": "Car Damage Detection - 4,000 images, 8,740 bboxes",
    },
    "fire_smoke": {
        "name": "FireSmokeAccident",
        "data_yaml": BASE_DIR / "Dataset" / "FireSmokeAccident" / "data.yaml",
        "project": BASE_DIR / "runs" / "fire_smoke",
        "nc": 5,
        "classes": ['accident', 'vehicle', 'pothole', 'fire', 'smoke'],
        "description": "Fire/Smoke/Accident Detection - 25,425 images, 108,000+ bboxes",
    },
}

# ========================= TRAINING CONFIG =========================

def get_train_config(model="yolo11n.pt", epochs=150, batch=16, imgsz=640):
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
        "momentum": 0.937,
        "weight_decay": 0.0005,
        "warmup_epochs": 5.0,
        "warmup_momentum": 0.8,
        "warmup_bias_lr": 0.1,
        "box": 7.5,
        "cls": 0.5,
        "dfl": 1.5,
        "hsv_h": 0.015,
        "hsv_s": 0.7,
        "hsv_v": 0.4,
        "degrees": 10.0,
        "translate": 0.1,
        "scale": 0.5,
        "shear": 2.0,
        "perspective": 0.0,
        "flipud": 0.0,
        "fliplr": 0.5,
        "mosaic": 1.0,
        "mixup": 0.1,
        "copy_paste": 0.1,
        "erasing": 0.4,
        "cos_lr": True,
        "close_mosaic": 15,
        "amp": True,
        "workers": 4,
        "cache": False,
        "seed": 42,
        "deterministic": True,
        "plots": True,
        "save_period": 25,
        "val": True,
        "verbose": True,
    }


def train_dataset(dataset_key, config):
    """Train YOLO11 on a specific dataset."""
    from ultralytics import YOLO

    ds = DATASETS[dataset_key]

    print(f"\n{'='*70}")
    print(f"  🚀 Training: {ds['name']}")
    print(f"  📝 {ds['description']}")
    print(f"  📁 Data: {ds['data_yaml']}")
    print(f"  🏷️  Classes: {ds['classes']}")
    print(f"  ⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    # Validate
    if not ds["data_yaml"].exists():
        print(f"  ❌ data.yaml not found: {ds['data_yaml']}")
        return None

    # Load model
    model = YOLO(config["model"])

    # Train
    train_args = {k: v for k, v in config.items() if k != "model"}
    train_args["data"] = str(ds["data_yaml"])
    train_args["project"] = str(ds["project"])
    train_args["name"] = "train"
    train_args["exist_ok"] = True

    start_time = time.time()
    results = model.train(**train_args)
    elapsed = time.time() - start_time

    hours, remainder = divmod(int(elapsed), 3600)
    minutes, seconds = divmod(remainder, 60)

    print(f"\n{'='*70}")
    print(f"  ✅ {ds['name']} - Training Complete!")
    print(f"  ⏱️  Duration: {hours}h {minutes}m {seconds}s")
    print(f"  📦 Best weights: {ds['project']}/train/weights/best.pt")
    print(f"{'='*70}\n")

    return results


def evaluate_dataset(dataset_key):
    """Evaluate the best model for a dataset."""
    from ultralytics import YOLO

    ds = DATASETS[dataset_key]
    best_pt = ds["project"] / "train" / "weights" / "best.pt"

    if not best_pt.exists():
        print(f"  ❌ {ds['name']}: No trained model found at {best_pt}")
        return None

    model = YOLO(str(best_pt))

    print(f"\n  🔍 Evaluating: {ds['name']}...")
    results = model.val(
        data=str(ds["data_yaml"]),
        split="test",
        project=str(ds["project"]),
        name="eval",
        exist_ok=True,
        plots=True,
        verbose=True,
    )

    print(f"\n{'='*60}")
    print(f"  📊 {ds['name']} - Test Results")
    print(f"{'='*60}")
    print(f"  mAP50:      {results.box.map50:.4f}")
    print(f"  mAP50-95:   {results.box.map:.4f}")
    print(f"  Precision:  {results.box.mp:.4f}")
    print(f"  Recall:     {results.box.mr:.4f}")

    # Per-class AP
    if hasattr(results.box, 'ap50') and results.box.ap50 is not None:
        print(f"\n  Per-class AP50:")
        for i, (cls_name, ap) in enumerate(zip(ds['classes'], results.box.ap50)):
            bar = "█" * int(ap * 30)
            print(f"    [{i}] {cls_name:15s} {ap:.4f} {bar}")

    print(f"{'='*60}\n")
    return results


def print_summary(all_results):
    """Print training summary for all datasets."""
    print(f"\n{'='*70}")
    print(f"  📋 TRAINING SUMMARY")
    print(f"{'='*70}")
    print(f"  {'Dataset':<30s} {'mAP50':>8s} {'mAP50-95':>10s} {'Weights':>10s}")
    print(f"  {'-'*58}")

    for key, results in all_results.items():
        ds = DATASETS[key]
        best_pt = ds["project"] / "train" / "weights" / "best.pt"
        exists = "✅" if best_pt.exists() else "❌"

        if results is not None:
            print(f"  {ds['name']:<30s} {'N/A':>8s} {'N/A':>10s} {exists:>10s}")
        else:
            print(f"  {ds['name']:<30s} {'SKIP':>8s} {'SKIP':>10s} {exists:>10s}")

    print(f"\n  Output directories:")
    for key, ds in DATASETS.items():
        print(f"    {ds['name']}: {ds['project']}/train/")
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(description="YOLO11 Training Pipeline - All Datasets")
    parser.add_argument("--model", type=str, default="yolo11n.pt",
                        help="Model: yolo11n/s/m/l/x.pt (default: yolo11n.pt)")
    parser.add_argument("--epochs", type=int, default=150, help="Training epochs (default: 150)")
    parser.add_argument("--batch", type=int, default=16, help="Batch size (default: 16)")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size (default: 640)")
    parser.add_argument("--only", type=str, choices=["cardd", "fire_smoke"],
                        help="Train only one dataset")
    parser.add_argument("--eval", action="store_true", help="Evaluate only (skip training)")

    args = parser.parse_args()

    print(f"\n{'='*70}")
    print(f"  🔥 YOLO11 Training Pipeline")
    print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  🏗️  Model: {args.model}")
    print(f"  📐 ImgSize: {args.imgsz}")
    print(f"  📦 Batch: {args.batch}")
    print(f"  🔄 Epochs: {args.epochs}")
    print(f"{'='*70}\n")

    # Determine which datasets to process
    if args.only:
        targets = [args.only]
    else:
        targets = list(DATASETS.keys())

    if args.eval:
        # Evaluation only
        for key in targets:
            evaluate_dataset(key)
    else:
        # Training
        config = get_train_config(
            model=args.model,
            epochs=args.epochs,
            batch=args.batch,
            imgsz=args.imgsz,
        )

        all_results = {}
        total_start = time.time()

        for key in targets:
            all_results[key] = train_dataset(key, config)

        total_elapsed = time.time() - total_start
        hours, remainder = divmod(int(total_elapsed), 3600)
        minutes, seconds = divmod(remainder, 60)

        print(f"\n  ⏱️  Total training time: {hours}h {minutes}m {seconds}s")
        print_summary(all_results)

        # Auto-evaluate after training
        print(f"\n  🔍 Running evaluation on test sets...\n")
        for key in targets:
            evaluate_dataset(key)


if __name__ == "__main__":
    main()
