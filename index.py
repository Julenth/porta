from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
from functools import wraps

app = Flask(__name__)   
app.secret_key = "thomas"

def obtener_coneccion():
    return mysql.connector.connect( 
        host='localhost',
        user='root',
        password='thomas2009', 
        database='porta'   
    )

def login_required(f):
    @wraps(f)
    def funcion_decorativa (*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login')) 
        return f(*args, **kwargs)
    return funcion_decorativa  

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session or session.get('rol') != 'admin':
            return redirect(url_for('index')) 
        return f(*args, **kwargs)
    return decorated_function

@app.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('inicio'))

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje = ''
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        conexion = obtener_coneccion()
        cursor = conexion.cursor(dictionary=True)
        query = "SELECT * FROM usuarios WHERE usuario = %s AND password = %s"
        cursor.execute(query, (usuario, password))
        resultado = cursor.fetchone()
        conexion.close()
        if resultado:
            session['usuario'] = usuario
            session['rol'] = resultado['rol']
            return redirect(url_for('index'))
        else:
            mensaje = "Usuario o contraseña incorrecta"
    return render_template('login.html', mensaje=mensaje)

@app.route('/index')
def index():
    habilidades = []
    try:
        conexion = obtener_coneccion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, descripcion, icono_svg FROM habilidades ORDER BY id DESC")
        habilidades = cursor.fetchall()
        conexion.close()
    except Exception as e:
        print(f"Error al cargar habilidades: {e}")
        
    proyectos = []
    try:
        conexion = obtener_coneccion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, descripcion, url_repositorio, url_imagen FROM proyectos ORDER BY id DESC")
        proyectos = cursor.fetchall()
        conexion.close()
    except Exception as e:
        print(f"Error al cargar proyectos: {e}")
        
    return render_template('index.html', page="index", habilidades=habilidades, proyectos=proyectos)

@app.route('/proyectos')
def proyectos():
    proyectos=[]
    try:
        conexion = obtener_coneccion()
        cursor = conexion.cursor(dictionary=True)
        # Se recupera la lista de proyectos de la base de datos
        cursor.execute("SELECT id, nombre, descripcion, url_repositorio, url_imagen FROM proyectos ORDER BY id DESC")
        proyectos = cursor.fetchall()
        conexion.close()
    except Exception as e:
        print(f"Error al cargar proyectos en /proyectos: {e}")
        
    return render_template('proyectos.html', proyectos=proyectos)




@app.route('/editar_habilidades_lista')
@login_required
@admin_required
def editar_habilidades_lista():
    conexion = obtener_coneccion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, descripcion, icono_svg FROM habilidades ORDER BY id DESC")
    habilidades = cursor.fetchall()
    conexion.close()
    return render_template('edit_habilidades.html', habilidades=habilidades)

@app.route('/editar_habilidad', methods=['GET', 'POST'], defaults={'habilidad_id': None})
@app.route('/editar_habilidad/<int:habilidad_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_habilidad(habilidad_id):
    habilidad = None
    if habilidad_id:
        conexion = obtener_coneccion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM habilidades WHERE id = %s", (habilidad_id,))
        habilidad = cursor.fetchone()
        conexion.close()

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        icono_svg = request.form['icono_svg']
        conexion = obtener_coneccion()
        cursor = conexion.cursor()
        if habilidad_id:
            query = "UPDATE habilidades SET nombre = %s, descripcion = %s, icono_svg = %s WHERE id = %s"
            cursor.execute(query, (nombre, descripcion, icono_svg, habilidad_id))
        else:
            query = "INSERT INTO habilidades (nombre, descripcion, icono_svg) VALUES (%s, %s, %s)"
            cursor.execute(query, (nombre, descripcion, icono_svg))
        conexion.commit()
        conexion.close()
        return redirect(url_for('editar_habilidades_lista'))
    return render_template('edit_habilidades_form.html', habilidad=habilidad)

@app.route('/eliminar_habilidad/<int:habilidad_id>', methods=['POST'])
@login_required
@admin_required
def eliminar_habilidad(habilidad_id):
    conexion = obtener_coneccion()
    cursor = conexion.cursor()
    query = "DELETE FROM habilidades WHERE id = %s"
    cursor.execute(query, (habilidad_id,))
    conexion.commit()
    conexion.close()
    return redirect(url_for('editar_habilidades_lista'))

@app.route('/acercademi')
def acercademi():  
    return render_template('acercademi.html')

@app.route('/editar_proyectos_lista')
@login_required
@admin_required
def editar_proyectos_lista():
    conexion = obtener_coneccion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, descripcion, url_repositorio, url_imagen FROM proyectos ORDER BY id DESC")
    proyecto = cursor.fetchall()
    conexion.close()
    return render_template('edit_proyecto.html', proyecto=proyecto)

@app.route('/editar_proyecto', methods=['GET', 'POST'], defaults={'proyecto_id': None})
@app.route('/editar_proyecto/<int:proyecto_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_proyecto(proyecto_id): 
    proyecto = None
    if proyecto_id:
        conexion = obtener_coneccion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, descripcion, url_repositorio, url_imagen FROM proyectos WHERE id = %s", (proyecto_id,))
        proyecto = cursor.fetchone()
        conexion.close()

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        url_repositorio = request.form['url_repositorio'] 
        url_imagen = request.form['url_imagen']
        conexion = obtener_coneccion()
        cursor = conexion.cursor()
        if proyecto_id:
            query = "UPDATE proyectos SET nombre = %s, descripcion = %s, url_repositorio = %s, url_imagen = %s WHERE id = %s"
            cursor.execute(query, (nombre, descripcion, url_repositorio, url_imagen, proyecto_id))
        else:
            query = "INSERT INTO proyectos (nombre, descripcion, url_repositorio, url_imagen) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (nombre, descripcion, url_repositorio, url_imagen))
        conexion.commit()
        conexion.close()
        return redirect(url_for('editar_proyectos_lista'))
    return render_template('edit_proyecto_form.html', proyecto=proyecto) 

@app.route('/eliminar_proyecto/<int:proyecto_id>', methods=['POST'])
@login_required
@admin_required
def eliminar_proyecto(proyecto_id):
    conexion = obtener_coneccion()
    cursor = conexion.cursor()
    query = "DELETE FROM proyectos WHERE id = %s"
    cursor.execute(query, (proyecto_id,))
    conexion.commit()
    conexion.close()
    return redirect(url_for('editar_proyectos_lista'))

@app.route('/contactos')
def conctatos():
    return render_template('conctatos.html')

@app.route('/calculadora')
def calculadora():
    return render_template('calculadora.html')

@app.route('/imc', methods=['GET', 'POST'])
def iMC():
    imc = None
    categoria = None
    if request.method == 'POST':
        try:
            peso = float(request.form['peso'])
            altura = float(request.form['altura'])
            if altura > 0:
                imc = peso / (altura ** 2)
                if imc < 18.5:
                    categoria = 'Bajo peso'
                elif imc < 25:
                    categoria = 'Peso normal'
                elif imc < 30:
                    categoria = 'Sobrepeso'
                else:
                    categoria = 'Obesidad'
                imc = round(imc, 2)
            else:
                imc = None
                categoria = "Error: La altura debe ser positiva"
        except ValueError:
            imc = None
            categoria = "Error: Ingrese valores numéricos válidos"
    return render_template('imc.html', imc=imc, categoria=categoria)

if __name__ == '__main__':
    app.run(debug=True)
