import argparse
import sys
from datetime import datetime
from pathlib import Path

from ultralytics import YOLO

BASE_DIR = Path(__file__).resolve().parent

MODEL_REGISTRY = {
    "cardd":      BASE_DIR / "runs" / "cardd"      / "train" / "weights" / "best.pt",
    "fire_smoke": BASE_DIR / "runs" / "fire_smoke" / "train" / "weights" / "best.pt",
}


def predict(
    source: str,
    weights_path: Path,
    project_dir: Path,
    name: str = "predict",
    conf: float = 0.25,
    iou: float = 0.45,
    imgsz: int = 640,
    save: bool = True,
    save_txt: bool = False,
    show: bool = False,
):
    weights_path = Path(weights_path)
    if not weights_path.exists():
        print(f"[ERROR] Weights not found: {weights_path}", file=sys.stderr)
        print("[ERROR] Run train_all.py first.", file=sys.stderr)
        return None

    model = YOLO(str(weights_path))
    run_name = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print(f"\n{'─'*50}")
    print(f"  model   : {weights_path.name}")
    print(f"  source  : {source}")
    print(f"  output  : {project_dir / run_name}")
    print(f"  conf={conf}  iou={iou}  imgsz={imgsz}")
    print(f"{'─'*50}\n")

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
        )
    except Exception as exc:
        print(f"[ERROR] Prediction failed: {exc}", file=sys.stderr)
        return None

    n_det = sum(len(r.boxes) for r in results if r.boxes)
    print(f"\n  Done — {n_det} detection(s) across {len(results)} frame(s)")
    print(f"  Saved to: {project_dir / run_name}\n")
    return results


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Run YOLO11 inference",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--source",    required=True,
                   help="Image / video / directory / webcam index")
    p.add_argument("--model",     default="cardd",
                   choices=[*MODEL_REGISTRY, "both"],
                   help="Pretrained model alias")
    p.add_argument("--weights",   default=None,
                   help="Custom weights path (overrides --model)")
    p.add_argument("--conf",      type=float, default=0.25)
    p.add_argument("--iou",       type=float, default=0.45)
    p.add_argument("--imgsz",     type=int,   default=640)
    p.add_argument("--no-save",   action="store_true",
                   help="Skip saving output images/video")
    p.add_argument("--save-txt",  action="store_true",
                   help="Save detections as YOLO-format .txt")
    p.add_argument("--show",      action="store_true",
                   help="Display results in a window")
    return p


def main():
    args = build_parser().parse_args()

    kwargs = dict(
        source=args.source,
        project_dir=BASE_DIR / "runs" / "predict",
        conf=args.conf,
        iou=args.iou,
        imgsz=args.imgsz,
        save=not args.no_save,
        save_txt=args.save_txt,
        show=args.show,
    )

    if args.weights:
        predict(weights_path=args.weights, name="custom", **kwargs)
    elif args.model == "both":
        for alias, weights in MODEL_REGISTRY.items():
            predict(weights_path=weights, name=alias, **kwargs)
    else:
        predict(weights_path=MODEL_REGISTRY[args.model], name=args.model, **kwargs)


if __name__ == "__main__":
    main()
