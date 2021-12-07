from flask import Flask, request, render_template, redirect, url_for, json, session
from pymongo import MongoClient
import json
import re
import base64
from bson import ObjectId
from flask_session import Session
from datetime import datetime

app = Flask(__name__)

app.config["SESSION_TYPE"] = "mongodb"

Session(app)

client = MongoClient()
db = client.citas

@app.route("/", methods=["GET"])
def get_index():
    if 'userid' in session:
        return redirect('citas')
    else:
        return redirect('login')

@app.route("/login", methods=["GET"])
def get_login():
    return render_template("login.html", title='Login Page')

@app.route("/register", methods=["POST"])
def get_register():

    nombre = request.form["nombre"]
    email = request.form["email"]
    password = request.form["password"]
    conf_password = request.form["conf-password"]

    #Validamos que no haya algún usuario con ese mismo correo electrónico
    filter = {"email": email}
    user_exists = db.users.find(filter).count();
    if user_exists < 1: #No existe el usuario
        
        #Validamos password si la confirmación es igual
        if password != conf_password:
            return {"message": "Las contraseñas no coinciden",
                    "error": 1,
                    "alert": "alert-danger",
                    "focus": "password"
                    }

        #Validamos si tiene algún número
        if not re.search("[0-9]",password):
            return {"message": "La contraseña debe contener al menos un número",
                    "error": 1,
                    "alert": "alert-danger",
                    "focus": "password"
                    }

        #Encriptamos el Password
        password = password.encode("utf-8")
        encoded = str(base64.b64encode(password))

        #Guardamos en DB
        user = {'nombre': nombre,'email': email, 'password': encoded}
        db.users.insert_one(user)
        return {"message": "Usuario registrado correctamente. Inicie Sesión para continuar.",
        "error": 0,
        "alert": "alert-success"
        }
    else: #Ya existe el usuario
        return {"message": "El correo electrónico ingresado ya ha sido registrado previamente.",
        "error": 1,
        "alert": "alert-danger",
        "focus": "email"
        }

@app.route("/loginuser", methods=["POST"])
def get_loginuser():

    email = request.form["email"]
    password = request.form["password"]

    #password encriptado
    password = password.encode("utf-8")
    encoded = str(base64.b64encode(password))

    #Validamos que no haya algún usuario con ese mismo correo electrónico
    filter = {"email": email, "password": encoded}
    user_exists = db.users.find(filter).count()
    if user_exists == 1: #Usuario correcto
        user =  db.users.find_one(filter)
        #Regresamos a dónde debe ir
        user_id = str(user['_id'])
        session['userid'] = user_id
        session['username'] = user['nombre']
        return {'error': 0}

    else: #Datos erróneos
        return {"message": "Usuario/password incorrecto",
        "error": 1,
        "alert": "alert-danger"
        }

@app.route("/citas", methods=["GET"])
def get_citas():
    #Revisamos la sesión
    if 'userid' in session:

        #Obtenemos las citas pasadas
        hoy = datetime.now()
        #hoy = hoy.strftime("%Y-%m-%d %H:%M")
        filter = {"$and": [{"fecha": {"$lte": hoy}}, {"userid": session['userid']}]}
        citas_pasadas = db.citas.find(filter)

        filter = {"$and": [{"fecha": {"$gte": hoy}}, {"userid": session['userid']}]}
        #filter = {"userid": session['userid']}
        proximas_citas = db.citas.find(filter)

        return render_template("citas.html", title='Mis Citas', username=session['username'], citas_pasadas=citas_pasadas, proximas_citas=proximas_citas)
    else:
        return redirect('login')

@app.route("/crear", methods=["GET"])
def get_crear():
    if 'userid' in session:
        return render_template("crear.html", title='Nueva Cita')
    else:
        return redirect('login')

@app.route("/nuevacita", methods=["POST"])
def get_nuevacita():
    titulo = request.form["titulo"]
    descripcion = request.form["descripcion"]
    fecha = request.form["fecha"]

    #Revisamos que los 3 campos estén llenos
    if ((not titulo) | (not descripcion) | (not fecha)) :
        return {"message": "Todos los campos son obligatorios.",
                "error": 1,
                "alert": "alert-danger"
                }
    else :
        #Ponemos el formato correcto de fecha
        fecha_obj = datetime.strptime(fecha, '%Y/%m/%d %H:%M')
        
        #Comparamos con la fecha de hoy
        hoy = datetime.now()
        if hoy > fecha_obj:
            return {"message": "Su cita debe ser en un momento en el futuro.",
                    "error": 1,
                    "alert": "alert-danger"
                    }
        else :
            #Guardamos
            cita = {'titulo': titulo,'descripcion': descripcion, 'fecha': fecha_obj, 'userid':session['userid']}
            db.citas.insert_one(cita)

            return {"message": "Guardado con éxito.",
                    "error": 0,
                    "alert": "alert-success"
                    }
@app.route("/cita/<citaid>", methods=["GET"])
def get_cita(citaid):
    #Revisamos la sesión
    if 'userid' in session:

        #Revisamos que sea una cita existente, con fecha menor a hoy y de esa persona
        hoy = datetime.now()
        filter = {"$and": [{"fecha": {"$gte": hoy}}, {"userid": session['userid']}, {"_id": ObjectId(citaid)}]}
        cita_exists = db.citas.find(filter).count()
        if(cita_exists):
            #Regresamos toda la info de la cita
            cita =  db.citas.find_one(filter)
            return render_template("cita.html", title='Mi Cita', cita=cita)
        else:
            #Redireccionamos a la página de citas
            return redirect(url_for('get_citas'))
    else:
        return redirect(url_for('get_login'))

@app.route("/editar", methods=["POST"])
def get_editar():
    titulo = request.form["titulo"]
    descripcion = request.form["descripcion"]
    fecha = request.form["fecha"]
    idcita = request.form["idcita"]

    #Revisamos que los 3 campos estén llenos
    if ((not titulo) | (not descripcion) | (not fecha)) :
        return {"message": "Todos los campos son obligatorios.",
                "error": 1,
                "alert": "alert-danger"
                }
    else :
        #Ponemos el formato correcto de fecha
        fecha_obj = datetime.strptime(fecha, '%Y/%m/%d %H:%M')
        
        #Comparamos con la fecha de hoy
        hoy = datetime.now()
        if hoy > fecha_obj:
            return {"message": "Su cita debe ser en un momento en el futuro.",
                    "error": 1,
                    "alert": "alert-danger"
                    }
        else :
            #Guardamos
            query_cita = { "_id": ObjectId(idcita) }
            nuevos_valores = { "$set": {'titulo': titulo,'descripcion': descripcion, 'fecha': fecha_obj, 'userid':session['userid']} }
            db.citas.update_one(query_cita, nuevos_valores)

            return {"message": "Guardado con éxito.",
                    "error": 0,
                    "alert": "alert-success"
                    }
@app.route("/eliminar", methods=["POST"])
def get_eliminar():
    idcita = request.form["idcita"]
     #Revisamos que sea una cita existente, con fecha menor a hoy y de esa persona
    hoy = datetime.now()
    filter = {"$and": [{"fecha": {"$gte": hoy}}, {"userid": session['userid']}, {"_id": ObjectId(idcita)}]}
    cita_exists = db.citas.find(filter).count()
    if(cita_exists):
        #Eliminamos la cita
        db.citas.delete_one( { "_id": ObjectId(idcita) } )
        return {"error": 0}
    else: 
        return {"message": "No se pudo eliminar la cita.",
                "error": 1}

@app.route("/logout", methods=["GET"])
def get_logout():
    session.pop('userid', None)
    session.pop('username', None)
    return redirect("/") 

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
