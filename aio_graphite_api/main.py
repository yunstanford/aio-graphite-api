import asyncio
import os
import logging
import sys
from .app import create_app
from aiohttp import web
import yaml
from .models.config import Config

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
DEFAULT_CONFIG_PATH = os.path.join(ROOT_DIR, "config", "config.yaml")


def from_yaml(path):
    with open(path) as fh:
        return Config(yaml.load(fh.read()))


LOG = logging.getLogger(__name__)

config_path = DEFAULT_CONFIG_PATH
config = from_yaml(config_path)

# Get the event loop for the current context (or current thread).
# https://docs.python.org/3/library/asyncio-eventloops.html
loop = asyncio.get_event_loop()

# creates an application object.
# run_until_complete runs the event loop until the task is complete.
app = loop.run_until_complete(create_app(loop, config))
