"""Load YAML configuration, resolving explicit ${ENV_VAR} values after parsing."""
import os
import re
from pathlib import Path

import yaml

_ENV = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def load_agent_config(path):
    def resolve(value):
        if isinstance(value, dict):
            return {key: resolve(item) for key, item in value.items()}
        if isinstance(value, list):
            return [resolve(item) for item in value]
        if isinstance(value, str):
            def substitute(match):
                name = match.group(1)
                if not os.environ.get(name):
                    raise ValueError(f"Set the non-empty environment variable {name}")
                return os.environ[name]
            return _ENV.sub(substitute, value)
        return value

    data = resolve(yaml.safe_load(Path(path).read_text()))
    if not isinstance(data, dict) or not isinstance(data.get("agent"), dict):
        raise ValueError("Configuration must contain an agent mapping")
    return data
