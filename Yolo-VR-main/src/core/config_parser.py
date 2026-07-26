"""
Configuration parser for the YOLO11 Accident Detection pipeline.

Reads YAML-based configuration files from the ``configs/`` directory and
resolves dataset paths relative to the project root.  All model metadata,
training hyperparameters, and system paths are managed through this module
so that no hardcoded constants exist in the training or inference scripts.
"""

import yaml
from pathlib import Path
from src.utils.logger import log

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]
CONFIGS_DIR = BASE_DIR / "configs"

# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def load_yaml(file_path: Path) -> dict:
    """
    Parse a YAML file and return its contents as a dictionary.

    Args:
        file_path: Absolute or relative path to the YAML file.

    Returns:
        Dictionary of parsed values, or empty dict on failure.
    """
    if not file_path.exists():
        log.error("Config file not found: %s", file_path)
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
            return data if data else {}
    except Exception as exc:
        log.error("Failed to parse YAML file %s: %s", file_path, exc)
        return {}

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_system_config() -> dict:
    """Load global system paths from ``configs/system.yaml``."""
    return load_yaml(CONFIGS_DIR / "system.yaml")


def get_training_config(config_name: str = "default") -> dict:
    """
    Load training hyperparameters from ``configs/training/<config_name>.yaml``.

    Falls back to ``default.yaml`` when the requested profile is missing.

    Args:
        config_name: Basename (without extension) of the training profile.

    Returns:
        Dictionary of hyperparameter key-value pairs.
    """
    train_yaml = CONFIGS_DIR / "training" / f"{config_name}.yaml"

    if not train_yaml.exists():
        log.warning(
            "Training config '%s' not found -- falling back to default.", config_name
        )
        train_yaml = CONFIGS_DIR / "training" / "default.yaml"

    config = load_yaml(train_yaml)
    log.info("Loaded training config: %s", train_yaml.name)
    return config


def get_model_config(dataset_key: str) -> dict:
    """
    Load dataset/model metadata from ``configs/model/<dataset_key>.yaml``.

    The returned dictionary is enriched with two computed keys:
        - ``data_yaml_path``:  Absolute path to the dataset's ``data.yaml``.
        - ``project_dir``:     Absolute path to the runs output directory.

    Args:
        dataset_key: Identifier matching a YAML filename in ``configs/model/``.

    Returns:
        Enriched configuration dictionary.

    Raises:
        FileNotFoundError: If the requested model config does not exist.
    """
    model_yaml = CONFIGS_DIR / "model" / f"{dataset_key}.yaml"

    if not model_yaml.exists():
        log.error("Model config '%s.yaml' is required but missing.", dataset_key)
        raise FileNotFoundError(f"Missing config: {model_yaml}")

    config = load_yaml(model_yaml)

    # Resolve filesystem paths using system-level directory settings
    sys_cfg = get_system_config()
    dirs = sys_cfg.get("directories", {})
    base_data_dir = BASE_DIR / dirs.get("data_processed", "data/processed")
    base_runs_dir = BASE_DIR / dirs.get("runs", "runs")

    config["data_yaml_path"] = base_data_dir / config.get("dir_name", "") / "data.yaml"
    config["project_dir"] = base_runs_dir / dataset_key

    log.info("Loaded model config: %s", dataset_key)
    return config
