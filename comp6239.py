import logging

from backend.app import App

logging.getLogger().setLevel(logging.DEBUG)

if __name__ == "__main__":
    app = App(8080)
    app.run()
