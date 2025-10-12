from flask import Flask, render_template,request,redirect,session,url_for
from flask_mysqldb import MySQL
from flask_login import LoginManager
import mysql.connector 
app = Flask(__name__)   

app.secret_key="thomas"


# Configuración de MySQL
def obtener_coneccion():
    coneccion = mysql.connector.connect( 
           host= 'localhost',
           user= 'root',
           password= 'thomas2009', 
           database= 'porta'   
    )
    return coneccion



@app.route('/')
def inicio():
    return render_template('inicio.html',)


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
            return redirect (url_for('index'))
        else:
            mensaje = "Usuario o contraseña incorrecta"
    
    return render_template('login.html', mensaje=mensaje)
       

@app.route('/index')
def index():
    return render_template('index.html',page="index")

@app.route('/acercademi')
def acercademi():  
    return render_template('acercademi.html')

@app.route('/proyectos')
def proyectos():
    return render_template('proyectos.html')

@app.route('/contactos')
def conctatos():
    return render_template('conctatos.html')



@app.route('/imc', methods=['get','post'])
def iMC():
    imc = None
    categoria = None
    
    if request.method == 'POST':
        peso = float(request.form['peso'])
        altura = float(request.form['altura'])
        
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
    
    return render_template('imc.html', imc=imc, categoria=categoria)



@app.route('/calculadora')
def calculadora():
    return render_template('calculadora.html')

@app.route('/proyecto_agro')
def proyecto():
    return render_template('proyecto_agro.html')



if __name__ == '__main__':
  app.run(debug=True)