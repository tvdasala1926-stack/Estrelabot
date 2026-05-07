import threading
from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "Bot online!", 200


@app.route("/health")
def health():
    return {"status": "ok"}, 200


def keep_alive():
    thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=8000),
        daemon=True,
    )
    thread.start()
