import os
from dotenv import load_dotenv

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, usd

#configure application 
app = Flask(__name__)

load_dotenv()

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

#plantillas en html para mostrar los numeros en $
app.jinja_env.filters["usd"] = usd 

#cuando el navegador se cierra, se cierra la session
app.config["SESSION_PERMANENT"] = False

#se guarda la session en archivos fisicos en el servidor y no el cookies
app.config["SESSION_TYPE"] = "filesystem"

#activa esas configuraciones en las sessiones de la aplicacion Flask
Session(app) 

#conectamos la base de datos cy usamos Qlite database 
db = SQL("sqlite:///instance/proyectofinanza.db")

#para crear un proyecto debes crear el archivo SQL de base de datos
# lo creas asi New-Item proyectofinanza.db

#DROP TABLE IF EXISTS transactions; esto es para borrar las tablas por completo 
#DROP TABLE IF EXISTS username;

#CREATE TABLE usuarios(id INTEGER PRIMARY KEY AUTOINCREMENT,
#username TEXT NOT NULL,
#hash TEXT NOT NULL
#);

#CREATE  UNIQUE  INDEX  username  ON  usuarios (username);   aqui se crea para que los usuarios sean unicos

#CREATE TABLE transactions (
#id_transactions INTEGER PRIMARY KEY AUTOINCREMENT,
#user_id INTEGER,
#Categoria TEXT,
#tipo TEXT,
#gasto NUMERIC NOT NULL,
#time DEFAULT CURRENT_TIMESTAMP,
#FOREIGN KEY(user_id) REFERENCES usuarios(id) 
#);


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            return apology("Introduzca un nombre")
        try: #aqui hago una consulta pero si algo sale mal no te rompas 
            rows = db.execute("SELECT * FROM usuarios WHERE username = ?", username)
        except Exception:
            return redirect("/")   
        #except exc Si la base de datos falla (por ejemplo, si la tabla no existe o el archivo de la base de datos está bloqueado), el programa no se detendrá bruscamente con una pantalla de error.
        # En su lugar, atrapará el fallo y ejecutará la alternativa: redirigir al usuario a la página de inicio con redirect("/").
        if len(rows) > 0:
            return apology("ya ese nombre existe")

        password = request.form.get("password")
        if not password:
            return apology("introduzca una contraseña")
        confirmation = request.form.get("confirmation")
        if not confirmation:
            return "Error: introduzca una contraseña"
        if confirmation != password:
            return apology("las contraseñas no coinciden")

        #utilizamos generate_password_hash para que la contraseña
        # no se guarde en texto plano sino con un algoritmo criptograficos como scrypt o bcrytp  para triturar y mezclar texto
        # tambien los combina con caracteres haciendo que sea muy dificil descifrarlos

        password_hash = generate_password_hash(password)
        #introducimos el hash generado en la base de datos 
        db.execute("INSERT INTO usuarios (username, hash) values (?,?)", username, password_hash)

        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":

        username = request.form.get("username")
        if not username:
            return apology("introduzca un nombre")

        password = request.form.get("password")
        if not password:
            return apology("intorduce una contraseña")
        #haces una consulta con la variable usarname para ver si exite
        rows = db.execute("SELECT * FROM usuarios WHERE username = ?", username)

        #verificamos si existe
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("el usuario o las contraseñas no son validas")

        #guardamos la variable del id del usuario en session["user_id"] porque la estaremos usando varias veces
        session["user_id"] = rows[0]["id"] #objeto especial de flask que funciona como variable gLOBAL

        #una vez iniciado con exito te manda al inicio
        return redirect("/")
        #sabemos que el metodo post envia los datos y oculto via http
    else:

        return render_template ("login.html") #muestra plantilla y estes en el sitio, el usario mira

@app.route("/")
@login_required
def index():
    rows = db.execute("SELECT id_transactions, tipo, gasto, Categoria, time FROM transactions WHERE user_id = ?", session["user_id"])

    dinero = 0
    total_ingresos = 0
    total_gastos = 0

    for row in rows:
        if row["tipo"] == "ingreso":
            dinero += row["gasto"]
            total_ingresos += row["gasto"]
        elif row["tipo"] == "gasto":
            dinero -= row["gasto"]
            total_gastos += row["gasto"]

    return render_template("index.html", dinero=dinero, transacciones=rows, ingresos=total_ingresos, gastos=total_gastos)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():

    if request.method == "POST":
        categoria = request.form.get("categoria")
        if not categoria:
            return "Error: introduzca una categoria"
        tipo = request.form.get("tipo")
        if not tipo:
            return "Error: introduzca una categoria"
        monto = request.form.get ("monto")
        if not monto:
            return "Error: introduzca una monto"
        try:
            monto_numerico = float(monto)
        except ValueError:
            return "Error: el monto debe ser un numero valido"
        if monto_numerico <= 0:
            return "Error: introduzca montos positvos"

        #vamos insertando los datos de donde iniciaste session
        db.execute("INSERT INTO transactions (user_id, Categoria, tipo, gasto) VALUES (?, ?, ?, ?)", session["user_id"], categoria, tipo, monto_numerico)
        return redirect("/")
    else:

        return render_template ("add.html")

@app.route("/logout")
def logout():
    # Borra todas las variables guardadas en la sesión actual 
    session.clear()
    # Redirige inmediatamente a la página de inicio obliga que si no has inciado session te redirija al inicio
    return redirect("/")

@app.route("/delete_historial", methods=["POST"])
@login_required
def delete_historial():

    db.execute(
        "DELETE FROM transactions WHERE user_id = ?",
        session["user_id"]
    )

    return redirect("/")


@app.route("/delete_transaction", methods = ["POST"])
@login_required
def delete_transaction():

    
    
    id_transaction = request.form.get("id_transaction")

    if not id_transaction:
        return redirect("/")

    try:
        int_numero = int(id_transaction)
    except (TypeError, ValueError):
        return redirect("/")

    db.execute(
            "DELETE FROM transactions WHERE id_transactions = ? AND user_id = ?",
            int_numero, session["user_id"] 
        )
   

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)

