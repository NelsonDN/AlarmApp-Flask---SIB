from flask import Flask, render_template, request, url_for, redirect, flash
from flask import session
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import PasswordField, StringField, SubmitField, EmailField, FileField, TimeField
from wtforms.validators import InputRequired, Length, Email, EqualTo
from werkzeug.utils import secure_filename
from config import Config
from flask_mail import Mail, Message
import hashlib
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "SIB"
app.config.from_object(Config)
mail = Mail(app)
app.config['RECAPTCHA_PUBLIC_KEY']= '6Ldgm8weAAAAAL4gXsaroEmafj2Po16Ov0VN0AOS'
app.config['RECAPTCHA_PRIVATE_KEY']= '6Ldgm8weAAAAAF172R4ehN6G8lWmquU1Uh8kLcxX'
app.config['UPLOAD_FOLDER']= 'static/UserAvatar'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

@app.route('/')
def index():
    return render_template("index.html")

class loginForm(FlaskForm):
    email = EmailField('email', validators=[InputRequired(message='A email is required'), Email()])
    password = PasswordField('password', validators=[InputRequired(message='A password is required')])

class UserForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(message='A name is required')])
    email = EmailField('email', validators=[InputRequired(message='A email is required'), Email()])
    password = PasswordField('password', validators=[InputRequired(message='A password is required'), EqualTo('confirm_password',message='password must match' )])
    confirm_password = PasswordField('confirm_password')
    telephone = StringField('telephone', validators=[InputRequired(message='A contact number is required'), Length(min=6, max=20)])
    avatar = FileField('avatar')
    recaptcha = RecaptchaField()

class AlarmForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(message='A name is required')])
    heure = TimeField('heure', validators=[InputRequired(message='A Hour is required')])

@app.route('/login-form')
def login_form():
    form = loginForm()
    return render_template("login.html", form=form)

@app.route("/login", methods=['POST'])
def login():
    form = loginForm()
    conn = sqlite3.connect( 'alarm.db' )
    cur = conn.cursor()
    global ok
    ok = None
    element = request.form
    email = element['email']
    password = element['password']
    requete = "SELECT email , password  FROM users where email= ? and password= ? "
    donnees = cur.execute( requete, (email, hashlib.sha256(str.encode(password)).hexdigest(),) )
    donnees = donnees.fetchall()
    conn.commit()
    conn.close()
    if len( donnees ) == 1:
        conn = sqlite3.connect( 'alarm.db' )
        cur = conn.cursor()
        requete_session = "SELECT id , name , email, telephone, avatar FROM users WHERE email=? "
        donnees_session = cur.execute( requete_session, (email,) )
        conn.commit()
        valeur = donnees_session.fetchall()
        for row in valeur:
            session['id'] = row[0]
            session['nom'] = row[1]
            session['email'] = row[2]
            session['telephone'] = row[3]
            session['avatar'] = row[4]

        # nombre d'utilisateurs
        req_nbre_users = "SELECT * FROM users "
        nbre_users = cur.execute( req_nbre_users )
        nbre_users = nbre_users.fetchall()
        nbre_users = len( nbre_users )

        # nombre d'alarms
        req_nbre_alarms = "SELECT * FROM alarms "
        nbre_alarms = cur.execute( req_nbre_alarms )
        nbre_alarms = nbre_alarms.fetchall()
        nbre_alarms = len( nbre_alarms )
        conn.commit()
        conn.close()

        return render_template( "dashboard/dashboard-content.html", nbre_users=nbre_users, nbre_alarms=nbre_alarms )
    else:
        return render_template( "login.html", erreur="AUCUN COMPTE EXISTANT", form=form )

@app.route('/logout')
def logout():
    session['user'] = None
    session.clear()
    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect( 'alarm.db' )
    cur = conn.cursor()

    # nombre d'utilisateurs
    req_nbre_users = "SELECT * FROM users "
    nbre_users = cur.execute( req_nbre_users )
    nbre_users = nbre_users.fetchall()
    nbre_users = len( nbre_users )

    # nombre d'alarms
    req_nbre_alarms = "SELECT * FROM alarms "
    nbre_alarms = cur.execute( req_nbre_alarms )
    nbre_alarms = nbre_alarms.fetchall()
    nbre_alarms = len( nbre_alarms )
    conn.commit()
    conn.close()

    return render_template("dashboard/dashboard-content.html", title="Alarm control - SIB || Dashboard", nbre_users=nbre_users, nbre_alarms=nbre_alarms )

@app.route('/indexUser')
def indexUser():
    conn = sqlite3.connect( 'alarm.db', check_same_thread=True )
    cur = conn.cursor()
    request = "SELECT id, avatar, name, email , telephone FROM users WHERE deleted_at is null "
    donnees = cur.execute( request )
    title = ['id', 'avatar', 'name', 'email', 'telephone']

    dict = {}
    users = []
    for row in donnees:
        for i in range( len( row ) ):
            dict[title[i]] = row[i]
        users.append( dict.copy() )

    return render_template("dashboard/indexUser.html", title="Alarm control - SIB || Users List", users=users)

@app.route('/addUser', methods=['GET','POST'])
def addUser():
    form = UserForm()
    return render_template("dashboard/addUser.html", title="Alarm control - SIB || Add User", form=form)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/ajouter_utilisateur", methods=['GET','POST'])
def ajouter_utilisateur():
    form = UserForm()
    conn = sqlite3.connect( 'alarm.db', check_same_thread=False )
    cur = conn.cursor()

    element = request.form
    name = element['name']
    email = element['email']
    password = element['password']
    confirm_password = element['confirm_password']
    telephone = element['telephone']
    file = form.avatar.data

    req_lastId = "SELECT COUNT(id) FROM users ORDER BY id DESC LIMIT 1"
    valeur = cur.execute(req_lastId)
    valeur = valeur.fetchall()
    lastId = 0
    for row in valeur:
        lastId = row[0]
    lastId = lastId+1
    filename = str(lastId) +".png"

    if password == confirm_password:
        if file and allowed_file( file.filename ):
            file.save( os.path.join( os.path.abspath( os.path.dirname( __file__ ) ), app.config['UPLOAD_FOLDER'], secure_filename( filename ) ) )
            req = "insert into users (name, email, password, telephone, avatar, created_at) values (?,?,?,?,?,?)"
            cur.execute( req, (name, email, hashlib.sha256(str.encode(password)).hexdigest(), telephone, filename, datetime.now()) )
            conn.commit()
            conn.close()
        else:
            req = "insert into users (name, email, password, telephone, created_at) values (?,?,?,?,?)"
            cur.execute( req, (name, email, hashlib.sha256(str.encode(password)).hexdigest(), telephone, datetime.now()) )
            conn.commit()
            conn.close()
    msg = Message("Bienvenue dans l'application de contrôle d'alarme d'etablissements scolaire AlarmControl-SIB ",
                  recipients=[email])
    msg.body = "Vous êtes à present Administrateur de notre plateforme"
    msg.html = "<h2>Vous êtes à present <strong>Administrateur</strong> de notre plateforme</h2><h3>Vos droits d'acces sont les suivants<br> <strong>Email : "+email+" <br>Mot de passe : "+password+" </strong></h3>"
    mail.send(msg)

    flash( "L'utilisateur " +name +" a bien éte ajoutée", 'success' )
    return redirect(url_for('indexUser'))

@app.route('/editUser/<id>')
def editUser(id):
    form = UserForm()
    conn = sqlite3.connect( 'alarm.db', check_same_thread=False )
    cur = conn.cursor()
    req_getUser = "SELECT * FROM users WHERE id = ? ORDER BY id DESC LIMIT 1"
    users = cur.execute(req_getUser, id)
    users = users.fetchall()

    title = ['id', 'name', 'email', 'password', 'telephone', 'avatar', 'created_at', 'deleted_at']

    dict = {}
    user = []
    for row in users:
        for i in range( len( row ) ):
            dict[title[i]] = row[i]
        user.append( dict.copy() )

    conn.commit()
    conn.close()

    return render_template("dashboard/editUser.html", form=form, user=user[0])

@app.route('/updateUser/<id>', methods=['GET','POST'])
def updateUser(id):
    form = UserForm()
    conn = sqlite3.connect( 'alarm.db', check_same_thread=False )
    cur = conn.cursor()

    element = request.form
    name = element['name']
    email = element['email']
    telephone = element['telephone']
    file = form.avatar.data
    filename = str(id) +".png"

    if file and allowed_file( file.filename ):
        os.unlink( os.path.join( app.config['UPLOAD_FOLDER'], filename) )
        file.save( os.path.join( os.path.abspath( os.path.dirname( __file__ ) ), app.config['UPLOAD_FOLDER'], secure_filename( filename ) ) )

        req_update = "UPDATE users SET name=?, email=?, telephone=?, avatar=? WHERE id = ?"
        cur.execute( req_update, (name, email, telephone, filename, id) )
        conn.commit()
        conn.close()
    else:
        req_update = "UPDATE users SET name=?, email=?, telephone=? WHERE id = ?"
        cur.execute( req_update, (name, email, telephone, id) )
        conn.commit()
        conn.close()

    flash( "Modification de l'utilisateur "+ name +" a ete un succes", 'info' )
    return redirect(url_for('indexUser'))

@app.route('/deleteUser/<id>')
def deleteUser(id):
    conn = sqlite3.connect( 'alarm.db', check_same_thread=False )
    cur = conn.cursor()

    """"req_delete = "DELETE FROM users WHERE id = ?"
    cur.execute(req_delete, id)"""
    req_softDelete = "UPDATE users SET deleted_at=? WHERE id = ?"
    cur.execute(req_softDelete, (datetime.now(), id))

    conn.commit()
    conn.close()
    flash( "L'utilisateur a bien éte supprimé", 'danger' )
    return redirect(url_for('indexUser'))

@app.route('/indexAlarm')
def indexAlarm():
    conn = sqlite3.connect( 'alarm.db', check_same_thread=True )
    cur = conn.cursor()
    request_all = "SELECT id, name, heure FROM alarms"
    donnees = cur.execute( request_all )
    title = ['id', 'name', 'heure']

    dict = {}
    alarms = []
    for row in donnees:
        for i in range( len( row ) ):
            dict[title[i]] = row[i]
        alarms.append( dict.copy() )
    print(alarms)
    return render_template("dashboard/indexAlarm.html", title="Alarm control - SIB || Alarms List", alarms = alarms)

@app.route('/addAlarm')
def addAlarm():
    formA = AlarmForm()

    return render_template("dashboard/addAlarm.html",  title="Alarm control - SIB || Add Alarm", formA=formA)

@app.route("/ajouter_alarme", methods=['POST'])
def ajouter_alarme():
    formA = AlarmForm()

    conn = sqlite3.connect( 'alarm.db', check_same_thread=False )
    cur = conn.cursor()
    element = request.form
    name = element['name']
    heure = element['heure']

    req = "insert into alarms (name, heure, is_active, created_at) values (?,?,1,?)"
    cur.execute(req, (name, heure, datetime.now()))
    conn.commit()
    conn.close()

    flash("L'alarme a bien ete ajoutée", 'success')
    return redirect(url_for('indexAlarm'))

@app.route('/editAlarm/<id>')
def editAlarm(id):
    form = AlarmForm()
    conn = sqlite3.connect( 'alarm.db', check_same_thread=False )
    cur = conn.cursor()
    req_getAlarm = "SELECT id, name, heure, is_active FROM alarms WHERE id = ? ORDER BY id DESC LIMIT 1"
    alarms = cur.execute(req_getAlarm, id)
    alarms = alarms.fetchall()

    title = ['id', 'name', 'heure', 'is_active']

    dict = {}
    alarm = []
    for row in alarms:
        for i in range( len( row ) ):
            dict[title[i]] = row[i]
        alarm.append( dict.copy() )

    conn.commit()
    conn.close()

    return render_template("dashboard/editAlarm.html", title="Alarm control - SIB || Edit Alarm", form=form, alarm=alarm[0])

@app.route('/updateAlarm/<id>', methods=['GET','POST'])
def updateAlarm(id):
    form = AlarmForm()
    conn = sqlite3.connect( 'alarm.db', check_same_thread=False )
    cur = conn.cursor()
    element = request.form
    name = element['name']
    heure = element['heure']

    req_update = "UPDATE alarms SET name=?, heure=? WHERE id = ?"
    cur.execute( req_update, (name, heure, id) )
    conn.commit()
    conn.close()
    flash( "Modification de l'alarme "+ heure +" a ete un succes", 'info' )
    return redirect(url_for('indexAlarm'))

@app.route('/deleteAlarm/<id>')
def deleteAlarm(id):
    conn = sqlite3.connect( 'alarm.db', check_same_thread=False )
    cur = conn.cursor()

    req_delete = "DELETE FROM alarms WHERE id = ?"
    cur.execute(req_delete, id)
    conn.commit()
    conn.close()
    flash( "L'alarme a bien ete supprimée", 'danger' )
    return redirect(url_for('indexAlarm'))
