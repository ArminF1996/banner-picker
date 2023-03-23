from config import get_config
from etl import run
import sys

if len(sys.argv) < 2:
    raise ValueError("Please enter config.ini path as an argument.")
config = get_config(sys.argv[1])

run(config)
