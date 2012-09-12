import logging
from logging import Formatter, FileHandler, StreamHandler
import os
from os import path

from flask import Flask

app_path = os.environ['APP_PATH']
app = Flask(__name__,
            static_folder=path.join(app_path, 'static'),
            template_folder=path.join(app_path, 'templates')
           )

app.config.from_pyfile(path.join(app_path, 'config.defaults'))
app.config.from_pyfile(path.join(app_path, 'config.local'), silent=True)

app.secret_key = app.config['SESSION_KEY']

formatter = Formatter('[%(asctime)s] %(levelname)s: %(message)s')
app.logger.setLevel(logging.DEBUG)
if app.config['LOG_FILE']:
    filelog = FileHandler(app.config['LOG_FILE'])
    filelog.setLevel(logging.WARNING)
    filelog.setFormatter(formatter)
    app.logger.addHandler(filelog)
if app.config['LOG_CONSOLE']:
    console = StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    app.logger.addHandler(console)
