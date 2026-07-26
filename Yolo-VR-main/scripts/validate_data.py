"""
Dataset validation script for the YOLO11 Accident Detection pipeline.

Performs a health check on a YOLO-format dataset before training to catch
common issues early:
    - Missing label files for images.
    - Incorrect number of fields per annotation line.
    - Class IDs outside the valid range.
    - Bounding-box coordinates outside the normalised [0, 1] interval.

Usage:
    python scripts/validate_data.py --dataset custom_scene
    python scripts/validate_data.py --dataset cardd
"""

import sys
import argparse
from pathlib import Path

# ---------------------------------------------------------------------------
# Project path bootstrap
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from src.core.config_parser import get_model_config
from src.utils.logger import log

# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------

def validate_yolo_dataset(data_dir: Path, nc: int) -> bool:
    """
    Walk through train/valid/test splits and verify label integrity.

    Args:
        data_dir: Root directory of the dataset (parent of train/valid/test).
        nc:       Expected number of classes.

    Returns:
        True if no issues were found, False otherwise.
    """
    if not data_dir.exists():
        log.error("[VALIDATE] Directory does not exist: %s", data_dir)
        return False

    splits = ["train", "valid", "test"]
    is_clean = True
    total_images = 0
    total_issues = 0

    log.info("[VALIDATE] Scanning dataset at: %s", data_dir)
    log.info("[VALIDATE] Expected class count (nc): %d", nc)

    for split in splits:
        img_dir = data_dir / split / "images"
        lbl_dir = data_dir / split / "labels"

        if not img_dir.exists() or not lbl_dir.exists():
            continue

        images = list(img_dir.rglob("*.jpg")) + list(img_dir.rglob("*.png"))
        log.info("  [%s] Found %d image(s).", split.upper(), len(images))
        total_images += len(images)

        for img_path in images:
            lbl_path = lbl_dir / f"{img_path.stem}.txt"

            # Check 1: corresponding label file exists
            if not lbl_path.exists():
                log.warning("  Missing label for: %s", img_path.name)
                total_issues += 1
                is_clean = False
                continue

            # Check 2: parse each annotation line
            try:
                with open(lbl_path, "r", encoding="utf-8") as fh:
                    for line_no, line in enumerate(fh, start=1):
                        parts = line.strip().split()
                        if not parts:
                            continue

                        if len(parts) != 5:
                            log.warning(
                                "  Bad format (line %d) in %s -- expected 5 fields, got %d",
                                line_no, lbl_path.name, len(parts),
                            )
                            total_issues += 1
                            is_clean = False
                            continue

                        class_id = int(parts[0])
                        if class_id < 0 or class_id >= nc:
                            log.warning(
                                "  Class ID %d out of range [0, %d) in %s (line %d)",
                                class_id, nc, lbl_path.name, line_no,
                            )
                            total_issues += 1
                            is_clean = False

                        coords = [float(v) for v in parts[1:]]
                        if any(c < 0.0 or c > 1.0 for c in coords):
                            log.warning(
                                "  Coordinate out of [0, 1] in %s (line %d)",
                                lbl_path.name, line_no,
                            )
                            total_issues += 1
                            is_clean = False

            except Exception as exc:
                log.error("  Error reading %s: %s", lbl_path.name, exc)
                total_issues += 1
                is_clean = False

    # Final verdict
    if is_clean and total_images > 0:
        log.info("[VALIDATE] PASSED -- all data is valid and ready for training.")
    elif total_images == 0:
        log.warning("[VALIDATE] No images found in any split.")
        is_clean = False
    else:
        log.error(
            "[VALIDATE] FAILED -- %d issue(s) detected. Fix before training.",
            total_issues,
        )

    return is_clean


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dataset health-check for the YOLO MLOps pipeline",
    )
    parser.add_argument(
        "--dataset", type=str, required=True,
        help="Model/dataset key (e.g. custom_scene, cardd, fire_smoke)",
    )
    args = parser.parse_args()

    try:
        config = get_model_config(args.dataset)
        dataset_dir = Path(config["data_yaml_path"]).parent

        log.info("=" * 60)
        log.info("[VALIDATE] Health check: %s", config["name"])
        log.info("=" * 60)

        validate_yolo_dataset(dataset_dir, config["nc"])

    except Exception as exc:
        log.error("Validator initialisation failed: %s", exc)


if __name__ == "__main__":
    main()
