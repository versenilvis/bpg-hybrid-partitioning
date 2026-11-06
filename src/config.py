from __future__ import annotations
import os


def load_env(env_path: str | None = None) -> None:
    # doc file .env neu ton tai va nap vao os.environ
    if env_path is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_path = os.path.join(root_dir, '.env')

    if not os.path.exists(env_path):
        return

    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k not in os.environ:
                    os.environ[k] = v


def get_int(key: str, default: int) -> int:
    try:
        return int(os.environ.get(key, default))
    except (TypeError, ValueError):
        return default


def get_float(key: str, default: float) -> float:
    try:
        return float(os.environ.get(key, default))
    except (TypeError, ValueError):
        return default


def get_bool(key: str, default: bool) -> bool:
    val = os.environ.get(key)
    if val is None:
        return default
    return val.strip().lower() in ('1', 'true', 'yes', 'on')


def get_str(key: str, default: str) -> str:
    return os.environ.get(key, default)


# nap cau hinh tu file .env
load_env()

# workload configs
DEFAULT_NUM_RECORDS = get_int('DEFAULT_NUM_RECORDS', 5)
DEFAULT_SEED = get_int('DEFAULT_SEED', 42)
DEFAULT_CROSS_TX_RATIO = get_float('DEFAULT_CROSS_TX_RATIO', 0.08)
DEFAULT_SITE_NUM = get_int('DEFAULT_SITE_NUM', 2)

# algorithm 2 dynamic partitioning configs
ALGO2_WORKLOAD_FACTOR = get_float('ALGO2_WORKLOAD_FACTOR', 0.2)
ALGO2_DISTRIBUTED_PERCENTAGE = get_float('ALGO2_DISTRIBUTED_PERCENTAGE', 0.02)
ALGO2_RECURSION_DEPTH = get_int('ALGO2_RECURSION_DEPTH', 10)
ALGO2_USE_BPG = get_bool('ALGO2_USE_BPG', True)

# bpg solver hyperparameters
BPG_MAX_ITER = get_int('BPG_MAX_ITER', 100)
BPG_TOL = get_float('BPG_TOL', 1e-4)
BPG_NUM_RESTARTS = get_int('BPG_NUM_RESTARTS', 3)
BPG_STEP_SCALE = get_float('BPG_STEP_SCALE', 0.06)

