"""
Unified training entry point for the YOLO11 Accident Detection pipeline.

Usage examples:
    python scripts/train.py                        # train all datasets
    python scripts/train.py --only custom_scene     # train single dataset
    python scripts/train.py --eval                  # evaluate only
    python scripts/train.py --model yolo11s.pt --epochs 200
"""

import sys
import argparse
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Project path bootstrap
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from src.core.config_parser import get_model_config, get_training_config
from src.core.trainer import train_dataset, evaluate_dataset
from src.utils.logger import log

# ---------------------------------------------------------------------------
# Available dataset keys (must match filenames in configs/model/)
# ---------------------------------------------------------------------------
DATASET_KEYS = [
    "cardd",
    "fire_smoke",
    "custom_scene",
    "motorcycle_detection",
    "motorcycle_helmet",
    "broken_motorcycles",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def print_summary(results: dict, targets: list) -> None:
    """Log a summary table of training outcomes."""
    log.info("")
    log.info("=" * 70)
    log.info("  TRAINING SUMMARY")
    log.info("=" * 70)
    log.info("  %-30s %s", "Dataset", "Weights status")
    log.info("  %s", "-" * 58)

    for key in targets:
        cfg = get_model_config(key)
        best_pt = Path(cfg["project_dir"]) / "train" / "weights" / "best.pt"
        status = "OK" if best_pt.exists() else "MISSING"
        log.info("  %-30s %s", cfg["name"], status)

    log.info("")
    log.info("  Output directories:")
    for key in targets:
        cfg = get_model_config(key)
        log.info("    %s: %s/train/", cfg["name"], cfg["project_dir"])
    log.info("=" * 70)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="YOLO11 Training Pipeline -- Enterprise MLOps Edition",
    )
    parser.add_argument("--model",  type=str, default="yolo11n.pt", help="Pre-trained base model")
    parser.add_argument("--epochs", type=int, default=150,          help="Number of training epochs")
    parser.add_argument("--batch",  type=int, default=16,           help="Batch size")
    parser.add_argument("--imgsz",  type=int, default=640,          help="Input image size (px)")
    parser.add_argument("--only",   type=str, choices=DATASET_KEYS, help="Train a single dataset")
    parser.add_argument("--eval",   action="store_true",            help="Run evaluation only (skip training)")
    args = parser.parse_args()

    targets = [args.only] if args.only else DATASET_KEYS

    # -- Evaluate-only mode ------------------------------------------------
    if args.eval:
        for key in targets:
            evaluate_dataset(get_model_config(key))
        return

    # -- Training loop -----------------------------------------------------
    all_results = {}
    total_start = time.time()

    for key in targets:
        ds_config = get_model_config(key)

        # Select the appropriate hyperparameter profile
        # Small or sensitive datasets use milder augmentations
        small_datasets = {"custom_scene", "motorcycle_helmet", "broken_motorcycles"}
        profile = "custom_finetune" if key in small_datasets else "default"
        train_cfg = get_training_config(profile)
        log.info("Using training profile: %s.yaml", profile)

        # CLI overrides take precedence over YAML values
        if args.model:  train_cfg["model"]  = args.model
        if args.epochs: train_cfg["epochs"] = args.epochs
        if args.batch:  train_cfg["batch"]  = args.batch
        if args.imgsz:  train_cfg["imgsz"]  = args.imgsz

        all_results[key] = train_dataset(ds_config, train_cfg)

    # -- Post-training summary ---------------------------------------------
    elapsed = time.time() - total_start
    h, remainder = divmod(int(elapsed), 3600)
    m, s = divmod(remainder, 60)
    log.info("Total training time: %dh %dm %ds", h, m, s)

    print_summary(all_results, targets)

    # -- Automatic evaluation on test split --------------------------------
    log.info("Running post-training evaluation on test splits ...")
    for key in targets:
        evaluate_dataset(get_model_config(key))


if __name__ == "__main__":
    main()
