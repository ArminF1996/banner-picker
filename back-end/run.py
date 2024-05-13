from waitress import serve
from paste.translogger import TransLogger
from backend import create_app
from config import get_config
import sys

if len(sys.argv) < 2:
    raise ValueError("Please Enter config.ini path as an argument.")
config = get_config(sys.argv[1])

serve(TransLogger(create_app(config)), host=config.HOST, port=config.PORT, threads=config.APP_THREADS)
