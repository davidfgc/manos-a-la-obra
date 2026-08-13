from flask import Flask, jsonify

from config import SITE_URL, X_HANDLE


def create_app():
    app = Flask(__name__)

    @app.context_processor
    def inject_globals():
        def url_absoluta(ruta):
            """URL absoluta desde SITE_URL sin barras duplicadas."""
            return SITE_URL + "/" + (ruta or "").lstrip("/")

        return {"x_handle": X_HANDLE, "site_url": SITE_URL, "url_absoluta": url_absoluta}

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    from routes.paginas import paginas_bp

    app.register_blueprint(paginas_bp)

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
