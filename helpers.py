import os
from flask import redirect, render_template, request, session
from functools import wraps

def apology(message, code=400):
    """Renderiza un mensaje de error al usuario."""
    def escape(s):
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~sl"), ('"', "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """Protege las rutas exigiendo iniciar sesión."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def usd(value):
    """Da formato de moneda (USD) a un número."""
    return f"${value:,.2f}"
