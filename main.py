from flask import Flask, send_from_directory, render_template, request, g, url_for, redirect, make_response
from werkzeug.utils import secure_filename
import sqlite3 as sql
import requests
import os
import time
UPLOAD_FOLDER = '/home/user/proyecto/imagenes'
ALL_EXTEN = 'png,jpg,jpeg,gif'
app = Flask(__name__)
app.config.update(
    DEBUG=True,
)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALL_EXTEN


@app.route('/')
def inicio():
	conex = sql.connect("productos.sqlite")
	conex.row_factory = sql.Row
	cur = conex.cursor()
	cur.execute('select * from productos where existencia = "true"')
	registros = cur.fetchall()
	conex.close()
	return render_template('index.html', registros=registros)
@app.route('/ofertas')
def ofertas():
    conex = sql.connect("productos.sqlite")
    conex.row_factory = sql.Row
    cur = conex.cursor()
    cur.execute('select * from productos where existencia = "true" and oferta > "0"')
    registros = cur.fetchall()
    conex.close()
    return render_template('ofertas.html', registros=registros)
@app.route('/informacion')
def informacion():
    return render_template('informacion.html')
@app.route('/acercade')
def acerca():
    return render_template('acercade.html')
@app.route('/verproducto/<id_articulo>')
def ver_articulo(id_articulo):
	conex = sql.connect("productos.sqlite")
	conex.row_factory = sql.Row
	cur = conex.cursor()
	cur.execute("select * from productos where id = '" + str(id_articulo) + "' limit 1;")
	registros = cur.fetchall()
	conex.close()
	return render_template('ver_producto.html', detalle=registros)
@app.route('/gestion')
def gestion():
	logeado = request.cookies.get("logeado")
	if logeado == "si":
		conex = sql.connect("productos.sqlite")
		conex.row_factory = sql.Row
		cur = conex.cursor()
		cur.execute('select * from productos')
		registros = cur.fetchall()
		conex.close()
		return render_template('gestion.html', formulario="listado", listado=registros)
	else:
		return redirect(url_for('login', err="0"))
@app.route('/gestion/<f>', methods=['GET', 'POST'])
def gestion_r(f):
	logeado = request.cookies.get("logeado")
	if logeado == "si":
		if f == "n_datos":
			return render_template('gestion.html', formulario="nuevo")
		if f == "imagen":
			#actualizar imagen producto
			if 'imagen_p' in request.files:
				archivo = request.files['imagen_p']
				if archivo.filename != "":
					if archivo and allowed_file(archivo.filename):
						nombre = time.strftime("%d_%m_%y_-_%H_%M_%S_-_") + secure_filename(archivo.filename)
						archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre))
						id_producto = request.form['id_producto']
						conex = sql.connect("productos.sqlite")
						cur = conex.cursor()
						cur.execute("update productos set imagen='" + nombre + "' where id='" + id_producto + "';")
						conex.commit()
						conex.close()
			return redirect(url_for("gestion"))
		if f == "up":
			conex = sql.connect("productos.sqlite")
			cur = conex.cursor()
			id_ar = request.form['id_a']
			nombre = request.form['nombre']
			descripcion = request.form['descripcion']
			precio = request.form['precio']
			oferta = request.form['oferta']
			existencia = request.form['existencia']
			cur.execute("update productos set nombre='" + str(nombre) + "', descripcion = '" + str(descripcion) + "', precio='" + str(precio) + "', oferta='" + str(oferta) + "', existencia='" + str(existencia) + "' where id='" + id_ar + "';")
			conex.commit()
			conex.close()
			return redirect(url_for("gestion"))
		if f == "nuevo_p":
			conex = sql.connect("productos.sqlite")
			cur = conex.cursor()
			nombre = request.form['nombre']
			descripcion = request.form['descripcion']
			precio = request.form['precio']
			oferta = request.form['oferta']
			existencia = request.form['existencia']
			cur.execute("insert into productos (id, nombre, descripcion, precio, oferta, existencia, imagen) values (null, '" + str(nombre) + "', '" + str(descripcion) + "', '" + str(precio) + "', '" + str(oferta) + "', '" + str(existencia) + "', 'default.png');")
			conex.commit()
			conex.close()
			return redirect(url_for("gestion"))
		if f=="eliminar":
			id_b = request.args.get('id_p')
			conex = sql.connect("productos.sqlite")
			cur = conex.cursor()
			cur.execute("delete from productos where id = '" + str(id_b) + "' limit 1;")
			conex.commit()
			conex.close()
			return redirect(url_for("gestion"))
	else:
		return redirect(url_for('login', err="0"))
@app.route('/gestion-<f>-<id_a>')
def gestion_s(f, id_a):
	logeado = request.cookies.get("logeado")
	if logeado == "si":
		if f=="datos":
			conex = sql.connect("productos.sqlite")
			conex.row_factory = sql.Row
			cur = conex.cursor()
			query_sql = "select * from productos where id='" + str(id_a) + "'"
			cur.execute(query_sql)
			registros = cur.fetchall()
			conex.close()
			return render_template('gestion.html', formulario="datos", datos=registros)
		if f=="imagen":
			return render_template('gestion.html', formulario="imagen", id_a=id_a)
	else:
		return redirect(url_for('login', err="0"))
@app.route('/login/<err>')
def login(err):
	return render_template('login.html', err=err)
@app.route('/log', methods=['POST'])
def log():
	passw = request.form['passw']
	if(passw == "12345678"):
		redireccion = redirect(url_for('gestion'))
		resp = make_response(redireccion)
		resp.set_cookie("logeado", value="si")
		return resp
	else:
		return redirect(url_for('login', err="1"))
@app.route('/logout')
def logout():
	redireccion = redirect(url_for('inicio'))
	resp = make_response(redireccion)
	resp.set_cookie("logeado", value="no")
	return resp
@app.route('/img/<imagen>')
def imagen_de_directorio(imagen):
	return send_from_directory(app.config['UPLOAD_FOLDER'], imagen)

if __name__ == '__main__':
	app.run()
