from flask import Blueprint, render_template

from services import contenido

paginas_bp = Blueprint("paginas", __name__)


@paginas_bp.route("/")
def index():
    return render_template("index.html")


@paginas_bp.route("/impresion-3d")
def impresion_3d():
    modelos = contenido.listar_modelos3d()
    return render_template("impresion_3d.html", modelos=modelos)
