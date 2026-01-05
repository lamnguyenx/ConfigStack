import os
import argparse
import tomllib
from pathlib import Path
import typing as tp
import pydantic as pdt
from deepmerge import always_merger


def load_config(
    model: type[pdt.BaseModel],
    config_file: tp.Optional[str] = None,
    cli_args: tp.Optional[tp.List[str]] = None,
) -> pdt.BaseModel:
    # Load constants
    const_path = Path(__file__).parent.parent / "const.toml"
    with open(const_path, "rb") as f:
        const_data = tomllib.load(f)

    # Layer 3: Config file
    config_dict = {}
    if config_file and Path(config_file).exists():
        with open(config_file, "rb") as f:
            config_dict = tomllib.load(f)

    # Layer 2: CLI arguments
    cli_dict = {}
    if cli_args:
        # Simple parser for dot notation.
        i = 0
        while i < len(cli_args):
            if cli_args[i].startswith("--"):
                key = cli_args[i][2:].replace("-", ".")
                if i + 1 < len(cli_args) and not cli_args[i + 1].startswith("--"):
                    value = cli_args[i + 1]
                    i += 2
                else:
                    value = True  # boolean flag
                    i += 1
                set_nested_value(cli_dict, key.split("."), parse_value(value))
            else:
                i += 1

    # Layer 1: Environment variables
    env_dict = {}
    for key, value in os.environ.items():
        if key in const_data["read_only_envs"]["skip_env_vars"] or any(key.startswith(prefix) for prefix in const_data["read_only_envs"]["skip_prefixes"]):
            continue
        config_key = key.lower().replace("__", ".")
        set_nested_value(env_dict, config_key.split("."), parse_value(value))

    # Merge layers: env overrides cli overrides config (defaults in model)
    merged = {}
    always_merger.merge(merged, config_dict)
    always_merger.merge(merged, cli_dict)
    always_merger.merge(merged, env_dict)

    return model(**merged)


def parse_value(value):
    # Simple type conversion
    if isinstance(value, str):
        if value.lower() in ("true", "false"):
            return value.lower() == "true"
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value
    return value


def set_nested_value(
    d: tp.Dict[str, tp.Any], keys: tp.List[str], value: tp.Any
) -> None:
    for key in keys[:-1]:
        d = d.setdefault(key, {})
    d[keys[-1]] = value
