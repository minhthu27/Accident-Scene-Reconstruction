"""
Inference module for the YOLO11 Accident Detection pipeline.

Wraps ``model.predict()`` with structured logging, timestamped output
directories, and graceful error handling.
"""

from pathlib import Path
from datetime import datetime
from src.utils.logger import log

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def predict_on_source(
    source,
    weights_path,
    project_dir,
    name: str = "predict",
    conf: float = 0.25,
    iou: float = 0.45,
    imgsz: int = 640,
    save: bool = True,
    save_txt: bool = False,
    show: bool = False,
):
    """
    Run object detection inference on the given source.

    Args:
        source:       Path to image, video, directory, or camera index.
        weights_path: Path to the trained ``.pt`` weights file.
        project_dir:  Base directory for saving prediction outputs.
        name:         Prefix for the timestamped output folder.
        conf:         Confidence threshold for detections.
        iou:          IoU threshold for Non-Maximum Suppression.
        imgsz:        Input image size (pixels).
        save:         Whether to save annotated images/video.
        save_txt:     Whether to save detection results as ``.txt`` files.
        show:         Whether to display results in a GUI window.

    Returns:
        List of Ultralytics ``Results`` objects, or ``None`` on failure.
    """
    weights_path = Path(weights_path)

    if not weights_path.exists():
        log.error("[PREDICT] Weights file not found: %s", weights_path)
        log.error("[PREDICT] Train a model first before running inference.")
        return None

    from ultralytics import YOLO
    model = YOLO(str(weights_path))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"{name}_{timestamp}"

    log.info("-" * 60)
    log.info("[PREDICT] Starting inference")
    log.info("-" * 60)
    log.info("  Model   : %s", weights_path)
    log.info("  Source   : %s", source)
    log.info("  Conf     : %.2f", conf)
    log.info("  IoU      : %.2f", iou)
    log.info("  ImgSize  : %d", imgsz)
    log.info("  Output   : %s/%s/", project_dir, run_name)
    log.info("-" * 60)

    try:
        results = model.predict(
            source=source,
            conf=conf,
            iou=iou,
            imgsz=imgsz,
            project=str(project_dir),
            name=run_name,
            exist_ok=True,
            save=save,
            save_txt=save_txt,
            show=show,
            line_width=2,
            show_labels=True,
            show_conf=True,
            verbose=False,
        )
    except Exception as exc:
        log.error("[PREDICT] Inference failed: %s", exc, exc_info=True)
        return None

    total_detections = sum(len(r.boxes) for r in results)
    log.info(
        "[PREDICT] Finished -- %d detection(s) across %d frame(s)",
        total_detections, len(results),
    )
    log.info("[PREDICT] Results saved to: %s/%s/", project_dir, run_name)

    return results
