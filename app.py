from flask import Flask, jsonify

from config import X_HANDLE


def create_app():
    app = Flask(__name__)

    @app.context_processor
    def inject_globals():
        return {"x_handle": X_HANDLE}

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
