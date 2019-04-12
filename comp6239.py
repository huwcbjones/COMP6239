import logging

from backend import log
from backend.app import App

log.main_logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    app = App(8080)
    app.run()
