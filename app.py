from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import dotenv_values
import yaml
import os


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


defaults = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

with open("config.development.yaml", "r") as f:
    yaml_config = yaml.safe_load(f) or {}

env_config = dotenv_values(".env")

def get_config():
    config = defaults.copy()

    # Layer 2: YAML
    config.update(yaml_config)

    # Layer 3: .env
    if "APP_PORT" in env_config:
        config["port"] = env_config["APP_PORT"]

    if "NUM_WORKERS" in env_config:
        config["workers"] = env_config["NUM_WORKERS"]

    if "APP_DEBUG" in env_config:
        config["debug"] = env_config["APP_DEBUG"]

    if "APP_LOG_LEVEL" in env_config:
        config["log_level"] = env_config["APP_LOG_LEVEL"]

    # Layer 4: OS environment variables
    for key in ["PORT", "WORKERS", "DEBUG", "LOG_LEVEL", "API_KEY"]:
        env_key = "APP_" + key

        if env_key in os.environ:
            config[key.lower()] = os.environ[env_key]

    return config

def coerce_config(config):
    config["port"] = int(config["port"])
    config["workers"] = int(config["workers"])

    if isinstance(config["debug"], str):
        config["debug"] = config["debug"].lower() in ("true", "1", "yes", "on")

    return config

@app.get("/effective-config")
def effective_config(set: list[str] | None = Query(default=None)):
    config = get_config()
    config = coerce_config(config)

    if set:
        for item in set:
            key, value = item.split("=", 1)

            if key in ["port", "workers"]:
                config[key] = int(value)
            elif key == "debug":
                config[key] = value.lower() in ("true", "1", "yes", "on")
            else:
                config[key] = value

    config["api_key"] = "****"

    return config