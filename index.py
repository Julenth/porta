from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
from functools import wraps

app = Flask(__name__)   
app.secret_key = "thomas"

# Configuración de MySQL
def obtener_coneccion():
    """Establece la conexión a la base de datos."""
    return mysql.connector.connect( 
        host='localhost',
        user='root',
        password='thomas2009', 
        database='porta'   
    )








def login_required(f):
    """Decorador que requiere que el usuario haya iniciado sesión."""
    @wraps(f)
    def funcion_decorativa (*args, **kwargs):
        if 'usuario' not in session:
            # Redirigir al login si no hay usuario en la sesión
            return redirect(url_for('login')) 
        return f(*args, **kwargs)
    # CORRECCIÓN: Se elimina la coma para que retorne la función decorativa, no una tupla.
    return funcion_decorativa  

def admin_required(f):
    """Decorador que verifica si el usuario tiene el rol de administrador."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session or session.get('rol') != 'admin':
            # Redirigir a la página principal si no tiene el rol de admin
            return redirect(url_for('index')) 
        return f(*args, **kwargs)
    return decorated_function

@app.route('/logout')
def logout():
    """Cierra la sesión del usuario."""
    session.pop('usuario', None)
    session.pop('rol', None)
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
        
        # Consulta para verificar las credenciales del usuario
        query = "SELECT * FROM usuarios WHERE usuario = %s AND password = %s"
        cursor.execute(query, (usuario, password))
        resultado = cursor.fetchone()
        
        conexion.close()
        
        if resultado:
            # Si el login es exitoso, se guarda en la sesión y redirige a index
            session['usuario'] = usuario
            session['rol'] = resultado['rol']
            return redirect(url_for('index'))
        else:
            mensaje = "Usuario o contraseña incorrecta"
    
    return render_template('login.html', mensaje=mensaje)

@app.route('/index')
def index():
    """Muestra la página principal con las habilidades dinámicas."""
    habilidades = []
    try:
        conexion = obtener_coneccion()
        cursor = conexion.cursor(dictionary=True)
        # Se asume que la tabla 'habilidades' tiene los campos id, nombre, descripcion, icono_svg
        cursor.execute("SELECT id, nombre, descripcion, icono_svg FROM habilidades ORDER BY id DESC")
        habilidades = cursor.fetchall()
        conexion.close()
    except Exception as e:
        print(f"Error al cargar habilidades: {e}")
        
    return render_template('index.html', page="index", habilidades=habilidades)


# --- Rutas de Administración de Habilidades (Protegidas) ---

@app.route('/editar_habilidades_lista')
@login_required
@admin_required
def editar_habilidades_lista():
    """Muestra la lista de habilidades para editar/eliminar (solo Admin)."""
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
    """Permite crear o editar una habilidad (solo Admin)."""
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
            # Actualizar
            query = "UPDATE habilidades SET nombre = %s, descripcion = %s, icono_svg = %s WHERE id = %s"
            cursor.execute(query, (nombre, descripcion, icono_svg, habilidad_id))
        else:
            # Insertar
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
    """Elimina una habilidad por su ID (solo Admin)."""
    conexion = obtener_coneccion()
    cursor = conexion.cursor()
    query = "DELETE FROM habilidades WHERE id = %s"
    cursor.execute(query, (habilidad_id,))
    conexion.commit()
    conexion.close()
    
    return redirect(url_for('editar_habilidades_lista'))

# --- Fin Rutas de Administración de Habilidades ---


@app.route('/acercademi')
def acercademi():  
    return render_template('acercademi.html')

@app.route('/proyectos')
def proyectos():
    """Muestra la página de proyectos con proyectos dinámicos."""
    proyectos_data = []
    try:
        conexion = obtener_coneccion()
        cursor = conexion.cursor(dictionary=True)
        # Se asume que la tabla 'proyectos' tiene los campos id, titulo, descripcion, enlace, imagen_url
        cursor.execute("SELECT id, titulo, descripcion, enlace, imagen_url FROM proyectos ORDER BY id DESC")
        proyectos_data = cursor.fetchall()
        conexion.close()
    except Exception as e:
        print(f"Error al cargar proyectos: {e}")
        
    return render_template('proyectos.html', proyectos_data=proyectos_data)


# --- Rutas de Administración de Proyectos (Placeholder, solo para que el link funcione) ---

@app.route('/editar_proyectos_lista')
@login_required
@admin_required
def editar_proyectos_lista():
    """Muestra la lista de proyectos para editar/eliminar (solo Admin)."""
    # En un proyecto real, aquí cargarías la lista de proyectos para la interfaz de edición
    return render_template('edit_proyecto.html') # Usando tu plantilla existente para proyectos


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