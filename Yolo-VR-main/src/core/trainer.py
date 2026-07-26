"""
Training module for the YOLO11 Accident Detection pipeline.

Provides ``train_dataset()`` and ``evaluate_dataset()`` functions that
wrap the Ultralytics training and validation APIs with structured
logging, timing, and error handling.
"""

import time
from pathlib import Path
from src.utils.logger import log

# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train_dataset(dataset_info: dict, training_cfg: dict):
    """
    Fine-tune a YOLO11 model on a specific dataset.

    The function loads a pre-trained base model, merges the provided
    hyperparameters, and delegates to ``model.train()``.  All progress
    and error messages are routed through the project logger.

    Args:
        dataset_info: Dictionary returned by ``get_model_config()``.  Must
                      contain keys: name, description, data_yaml_path,
                      project_dir, nc, classes.
        training_cfg: Dictionary of training hyperparameters (typically
                      loaded from a YAML profile via ``get_training_config()``).

    Returns:
        Ultralytics ``Results`` object on success, or ``None`` on failure.
    """
    from ultralytics import YOLO

    name = dataset_info.get("name", "Unknown")
    data_yaml = Path(dataset_info["data_yaml_path"])

    log.info("-" * 70)
    log.info("[TRAIN] Starting task: %s", name)
    log.info("[TRAIN] Description : %s", dataset_info.get("description", ""))
    log.info("[TRAIN] Data path   : %s", data_yaml)
    log.info("[TRAIN] Classes (%d): %s", dataset_info.get("nc", 0), dataset_info.get("classes", []))
    log.info("-" * 70)

    if not data_yaml.exists():
        log.error("[TRAIN] data.yaml not found at: %s", data_yaml)
        return None

    model_path = training_cfg.get("model", "yolo11n.pt")
    log.info("[TRAIN] Loading base weights: %s", model_path)

    try:
        model = YOLO(model_path)
    except Exception as exc:
        log.error("[TRAIN] Failed to load base model (%s): %s", model_path, exc)
        return None

    # Build kwargs for model.train(), excluding the 'model' key itself
    train_args = {k: v for k, v in training_cfg.items() if k != "model"}
    train_args["data"] = str(data_yaml)
    train_args["project"] = str(dataset_info["project_dir"])
    train_args["name"] = "train"
    train_args["exist_ok"] = True

    log.info(
        "[TRAIN] Hyperparameters: epochs=%s, batch=%s, imgsz=%s",
        train_args.get("epochs"), train_args.get("batch"), train_args.get("imgsz"),
    )

    try:
        start = time.time()
        results = model.train(**train_args)
        elapsed = time.time() - start

        h, remainder = divmod(int(elapsed), 3600)
        m, s = divmod(remainder, 60)
        best_pt = Path(dataset_info["project_dir"]) / "train" / "weights" / "best.pt"

        log.info("-" * 70)
        log.info("[TRAIN] Completed: %s", name)
        log.info("[TRAIN] Duration : %dh %dm %ds", h, m, s)
        log.info("[TRAIN] Best weights saved to: %s", best_pt)
        log.info("-" * 70)
        return results

    except Exception as exc:
        log.error("[TRAIN] Critical failure for %s: %s", name, exc, exc_info=True)
        return None


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_dataset(dataset_info: dict):
    """
    Run validation on the test split using the best trained weights.

    Args:
        dataset_info: Dictionary returned by ``get_model_config()``.

    Returns:
        Ultralytics ``Results`` object on success, or ``None`` on failure.
    """
    from ultralytics import YOLO

    name = dataset_info.get("name", "Unknown")
    best_pt = Path(dataset_info["project_dir"]) / "train" / "weights" / "best.pt"

    if not best_pt.exists():
        log.error("[EVAL] No trained weights found for %s at %s", name, best_pt)
        return None

    log.info("[EVAL] Starting evaluation for: %s", name)
    model = YOLO(str(best_pt))

    try:
        results = model.val(
            data=str(dataset_info["data_yaml_path"]),
            split="test",
            project=str(dataset_info["project_dir"]),
            name="eval",
            exist_ok=True,
            plots=True,
            verbose=False,
        )

        log.info("-" * 60)
        log.info("[EVAL] Test-set results -- %s", name)
        log.info("-" * 60)
        log.info("  mAP@50    : %.4f", results.box.map50)
        log.info("  mAP@50-95 : %.4f", results.box.map)
        log.info("  Precision : %.4f", results.box.mp)
        log.info("  Recall    : %.4f", results.box.mr)

        if hasattr(results.box, "ap50") and results.box.ap50 is not None:
            log.info("  Per-class AP@50:")
            for idx, (cls_name, ap) in enumerate(
                zip(dataset_info["classes"], results.box.ap50)
            ):
                log.info("    [%d] %-15s %.4f", idx, cls_name, ap)

        log.info("-" * 60)
        return results

    except Exception as exc:
        log.error("[EVAL] Evaluation failed for %s: %s", name, exc, exc_info=True)
        return None
