import os
import sys
import pytest
import yaml
import difflib
import typing as tp
import pydantic as pdt
from pathlib import Path
import py_config_stack

def colorize_diff(diff_lines):
    """Colorize diff output for terminal display."""
    result = []
    for line in diff_lines:
        if line.startswith('+++') or line.startswith('---'):
            result.append(line)  # headers in default color
        elif line.startswith('+'):
            result.append('\033[92m' + line + '\033[0m')  # green for additions
        elif line.startswith('-'):
            result.append('\033[91m' + line + '\033[0m')  # red for deletions
        elif line.startswith('@@'):
            result.append('\033[94m' + line + '\033[0m')  # blue for hunk headers
        else:
            result.append(line)
    return result

# Default constants (Layer 4)
PORT_DEFAULT = 8080
HOST_DEFAULT = "localhost"
DATABASE_URL_DEFAULT = "postgresql://localhost/mydb"
DATABASE_PORT_DEFAULT = 5432
DATABASE_MAX_CONNECTIONS_DEFAULT = 100
CACHE_ENABLED_DEFAULT = True
CACHE_TTL_DEFAULT = 3600
CACHE_REDIS_HOST_DEFAULT = "localhost"
API_TIMEOUT_DEFAULT = 30
API_RATE_LIMIT_DEFAULT = 100


class Config(pdt.BaseModel):
    port: int = PORT_DEFAULT
    host: str = HOST_DEFAULT

    class Database(pdt.BaseModel):
        url: str = DATABASE_URL_DEFAULT
        port: int = DATABASE_PORT_DEFAULT

        class Max(pdt.BaseModel):
            connections: int = DATABASE_MAX_CONNECTIONS_DEFAULT

        max: Max = pdt.Field(default_factory=Max)

    database: Database = pdt.Field(default_factory=Database)

    class Cache(pdt.BaseModel):
        enabled: bool = CACHE_ENABLED_DEFAULT
        ttl: int = CACHE_TTL_DEFAULT

        class Redis(pdt.BaseModel):
            host: str = CACHE_REDIS_HOST_DEFAULT

        redis: Redis = pdt.Field(default_factory=Redis)

    cache: Cache = pdt.Field(default_factory=Cache)

    class Api(pdt.BaseModel):
        timeout: int = API_TIMEOUT_DEFAULT

        class Rate(pdt.BaseModel):
            limit: int = API_RATE_LIMIT_DEFAULT

        rate: Rate = pdt.Field(default_factory=Rate)

    api: Api = pdt.Field(default_factory=Api)


class ConfigTestCase(pdt.BaseModel):
    test_case: str
    layers: tp.List[str]
    cli_args: str
    env_vars: tp.Dict[str, str]
    expected: str


# Load test data from YAML file
with open(Path(__file__).parent.parent / "test_data.yml", "r") as f:
    raw_test_data = yaml.safe_load(f)["test_cases"]
    test_data = [ConfigTestCase(**case) for case in raw_test_data]


def run_config_command(cli_args, env_vars):
    """Run the config loading and return its output."""
    # Save original env
    original_env = dict(os.environ)
    try:
        # Clear env except essential
        essential_keys = [
            "PATH",
            "PYTHONPATH",
            "HOME",
            "SHELL",
            "USER",
            "LANG",
            "TZ",
            "TERM",
            "PWD",
        ]
        os.environ.clear()
        for k in essential_keys:
            if k in original_env:
                os.environ[k] = original_env[k]
        for k in original_env:
            if k.startswith(("LC_", "PYTHON")):
                os.environ[k] = original_env[k]
        # Add test env_vars
        os.environ.update(env_vars)
        # Load config
        config = py_config_stack.load_config(Config, config_file="config.toml", cli_args=cli_args)
        output = yaml.dump(config.model_dump(), default_flow_style=False)
    finally:
        # Restore env
        os.environ.clear()
        os.environ.update(original_env)
    return output


@pytest.mark.parametrize(
    "test_case,layers,cli_args,env_vars,expected",
    [
        (
            case.test_case,
            case.layers,
            case.cli_args.split() if case.cli_args else [],
            case.env_vars,
            case.expected,
        )
        for case in test_data
    ],
)
def test_configuration_showcase(test_case, layers, cli_args, env_vars, expected):
    """Test the multi-layer configuration stack with different layer combinations."""
    # Change to the repository root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))
    os.chdir(repo_root)

    print(f"\nTesting {test_case} - Layers: {', '.join(layers)}")
    print("=" * 50)

    # Run the command with the specified layers
    output = run_config_command(cli_args, env_vars)

    # Print how the config changed from defaults
    default_config = Config()
    default_output = yaml.dump(default_config.model_dump(), default_flow_style=False)
    print("Config changes from defaults:")
    diff_lines = list(difflib.unified_diff(
        default_output.splitlines(keepends=True),
        output.splitlines(keepends=True),
        fromfile='defaults',
        tofile='loaded'
    ))
    for line in colorize_diff(diff_lines):
        print(line, end='')

    # Assert that output matches expected
    if output.strip() != expected.strip():
        print("Config differences from expected:")
        diff_lines = list(difflib.unified_diff(
            expected.splitlines(keepends=True),
            output.splitlines(keepends=True),
            fromfile='expected',
            tofile='actual'
        ))
        for line in colorize_diff(diff_lines):
            print(line, end='')
        assert False, f"Output does not match expected for {test_case}"
