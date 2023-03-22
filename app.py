from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base_de_datos.db'
app.config['SECRET_KEY'] = 'pollo_frito'
db = SQLAlchemy(app)


#modelos
class Movil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    n_movil = db.Column(db.String(80), unique=True, nullable=False)
    cuartel = db.Column(db.String(80), unique=False, nullable=False)
    tipo = db.Column(db.String(80), unique=False, nullable=False)
    estado = db.Column(db.String(80), unique=False, default='disponible', nullable=True)

class Incidente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operador = db.Column(db.String(80), unique=False, nullable=False)
    movil_id = db.Column(db.Integer, db.ForeignKey('movil.id'), nullable=False)
    servicio = db.Column(db.String(80), unique=False, nullable=False)
    tipo_servicio = db.Column(db.String(80), unique=False, nullable=False)
    salida = db.Column(db.DateTime, nullable=True)
    llegada = db.Column(db.DateTime, nullable=True)
    lugar = db.Column(db.String(80), unique=False, nullable=False)
    observaciones = db.Column(db.String(80), unique=False, nullable=False)
    estado = db.Column(db.String(80), unique=False, default="en progreso", nullable=False)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/movil', methods = ['GET', 'POST'])
def crear_movil():
    if request.method == 'POST':
        n_movil = request.form['n_movil']
        cuartel = request.form['cuartel']
        tipo = request.form['tipo']
        movil = Movil(n_movil=n_movil, cuartel=cuartel, tipo=tipo)
        db.session.add(movil)
        db.session.commit()
        return redirect(url_for('moviles'))
    return render_template('crear_movil.html')

@app.route('/moviles')
def moviles():
    moviles = Movil.query.all()
    return render_template('listar_moviles.html', moviles=moviles)

@app.route('/moviles/<int:movil_id>/cambiar_estado', methods=['POST'])
def cambiar_estado(movil_id):
    movil = Movil.query.get_or_404(movil_id)
    nuevo_estado = request.form['estado']
    movil.estado = nuevo_estado
    db.session.commit()
    return redirect(url_for('moviles'))

@app.route('/incidentes/cambiar_estado', methods=['GET', 'POST'])
def cambiar_estado_incidente():
    if request.method == 'POST':
        incidente_id = request.form['incidente_id']
        incidente = Incidente.query.get_or_404(incidente_id)
        nuevo_estado = request.form['estado']
        incidente.estado = nuevo_estado
        db.session.commit()
        if nuevo_estado == 'finalizado':
            movil = Movil.query.get_or_404(incidente.movil_id)
            movil.estado = 'disponible'
            db.session.commit()
        
        redirect(url_for('incidentes'))
    return redirect(url_for('incidentes'))

@app.route('/disponibles')
def disponibles():
    cuartel = request.args.get('cuartel', 'Todos', type=str)
    
    if cuartel == 'Todos':
        moviles = Movil.query.filter_by(estado='disponible').all()
    else:
        moviles = Movil.query.filter_by(estado='disponible').filter(Movil.cuartel == cuartel).all()
    
    moviles_filter = Movil.query.filter_by(estado='disponible').all()
    cuarteles = ['Todos']
    for movil in moviles_filter:
        if movil.cuartel not in cuarteles:
            cuarteles.append(movil.cuartel)

    return render_template('listar_moviles_disponibles.html', moviles=moviles, cuarteles=cuarteles)

@app.route('/incidente', methods = ['GET', 'POST'])
def crear_incidente():
    n_movil = request.args.get('n_movil', None, type=str)

    if n_movil is None:
        return redirect(url_for('disponibles'))
    movil_id = Movil.query.filter_by(n_movil=n_movil).first().id
    
    if request.method == 'POST':
        operador = request.form['operador']
        servicio = request.form['servicio']
        tipo_servicio = request.form['tipo_servicio']
        salida = datetime.strptime(request.form['salida'], '%Y-%m-%dT%H:%M')
        llegada = datetime.strptime(request.form['llegada'], '%Y-%m-%dT%H:%M')
        lugar = request.form['lugar']
        observaciones = request.form['observaciones']
        try :
            movil = Movil.query.get_or_404(movil_id)
            movil.estado = 'en uso'
            db.session.commit()

        except:
            
            redirect(url_for('disponibles'))

        incidente = Incidente(operador=operador, movil_id=movil_id, servicio=servicio, tipo_servicio=tipo_servicio, salida=salida, llegada=llegada, lugar=lugar, observaciones=observaciones)
        db.session.add(incidente)
        db.session.commit()
        return redirect(url_for('incidentes'))
    return render_template('crear_incidente.html', n_movil=n_movil)


@app.route('/incidentes')

def incidentes():

    incidentes = Incidente.query.all()

    return render_template('listar_incidentes.html', incidentes=incidentes)

with app.app_context():
    db.create_all()
# run the app
if __name__ == '__main__':
    app.run( debug=True, port='8888')
