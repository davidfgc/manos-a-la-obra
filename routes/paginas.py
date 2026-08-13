from flask import Blueprint, render_template, request

from services import contenido

paginas_bp = Blueprint("paginas", __name__)


@paginas_bp.route("/")
def index():
    return render_template("index.html")


@paginas_bp.route("/impresion-3d")
def impresion_3d():
    modelos = contenido.listar_modelos3d()
    return render_template("impresion_3d.html", modelos=modelos)


@paginas_bp.route("/puntos-acopio")
def puntos_acopio():
    pais = request.args.get("pais") or None
    ciudad = request.args.get("ciudad") or None
    puntos = contenido.listar_puntos(pais=pais, ciudad=ciudad)
    opciones = contenido.opciones_filtro()
    return render_template(
        "puntos_acopio.html",
        puntos=puntos,
        opciones=opciones,
        pais=pais,
        ciudad=ciudad,
    )
