"""
Inference entry point for the YOLO11 Accident Detection pipeline.

Usage examples:
    python scripts/infer.py --source image.jpg --model cardd
    python scripts/infer.py --source video.mp4 --model custom_scene --show
    python scripts/infer.py --source 0 --model all --show
    python scripts/infer.py --source dir/ --weights path/to/best.pt
"""

import sys
import argparse
from pathlib import Path

# ---------------------------------------------------------------------------
# Project path bootstrap
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from src.core.config_parser import get_model_config, get_system_config
from src.core.predictor import predict_on_source
from src.utils.logger import log

# ---------------------------------------------------------------------------
# Available dataset keys
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
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="YOLO11 Inference -- Enterprise MLOps Edition",
    )
    parser.add_argument("--source",   type=str, required=True,
                        help="Image / video / directory / webcam index (use 0)")
    parser.add_argument("--model",    type=str, default="cardd",
                        choices=DATASET_KEYS + ["both", "all"],
                        help="Which trained model to use")
    parser.add_argument("--weights",  type=str, default=None,
                        help="Custom weights path (overrides --model)")
    parser.add_argument("--conf",     type=float, default=0.25,
                        help="Confidence threshold")
    parser.add_argument("--iou",      type=float, default=0.45,
                        help="IoU threshold for NMS")
    parser.add_argument("--imgsz",    type=int,   default=640,
                        help="Input image size (px)")
    parser.add_argument("--no-save",  action="store_true",
                        help="Do not save annotated output")
    parser.add_argument("--save-txt", action="store_true",
                        help="Save detection results as .txt files")
    parser.add_argument("--show",     action="store_true",
                        help="Display results in a GUI window")
    args = parser.parse_args()

    # Resolve the output directory from system config
    sys_cfg = get_system_config()
    runs_dir = BASE_DIR / sys_cfg.get("directories", {}).get("runs", "runs")

    # Shared kwargs for every predict call
    common = dict(
        source=args.source,
        project_dir=runs_dir / "predict",
        conf=args.conf,
        iou=args.iou,
        imgsz=args.imgsz,
        save=not args.no_save,
        save_txt=args.save_txt,
        show=args.show,
    )

    # -- Custom weights path (highest priority) ----------------------------
    if args.weights:
        predict_on_source(weights_path=args.weights, name="custom", **common)
        return

    # -- Multi-model mode --------------------------------------------------
    if args.model in ("both", "all"):
        for key in DATASET_KEYS:
            try:
                cfg = get_model_config(key)
                weights = Path(cfg["project_dir"]) / "train" / "weights" / "best.pt"
                if weights.exists():
                    predict_on_source(weights_path=weights, name=key, **common)
                else:
                    log.warning("Skipping '%s' -- no trained weights found.", key)
            except FileNotFoundError:
                log.warning("Skipping '%s' -- model config missing.", key)
        return

    # -- Single-model mode -------------------------------------------------
    try:
        cfg = get_model_config(args.model)
        weights = Path(cfg["project_dir"]) / "train" / "weights" / "best.pt"
        predict_on_source(weights_path=weights, name=args.model, **common)
    except Exception as exc:
        log.error("Failed to load model '%s': %s", args.model, exc)


if __name__ == "__main__":
    main()
