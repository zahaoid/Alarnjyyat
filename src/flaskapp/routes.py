from flaskapp.main import app, ar, login as lg
from database.main import qr
from flask import render_template, flash, redirect, url_for, request, abort
from flaskapp.modules.forms import LoginForm, RegisterForm, AddEntry
from flaskapp.modules.models import User
from flask_login import current_user, login_user, login_required
from flask_login import logout_user
from urllib.parse import urlsplit
from datetime import timezone, datetime
from werkzeug.security import generate_password_hash, check_password_hash




@app.route('/')
@app.route('/index')
def index():
    return render_template("home.html", entries= qr.getAllEntries())

@app.route('/discord')
def discord():
    return redirect("https://t.co/urn3hWKEJf")


@lg.user_loader
def load_user(username):
    user_info = qr.getUser(username)

    #this check is important for when the user was logged in but got deleted from the database before
    #the session expired, if user doesnt exist then this must return None according to flask-login doc
    if user_info:
        return User(username= user_info['username'], isadmin=user_info['isadmin'])
    else:
        return None


@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    loginform = LoginForm()
    #if it is a POST request
    if loginform.validate_on_submit():
        user_info = qr.getUser(loginform.username.data)
        if not user_info or not check_password_hash(user_info['passwordhash'] ,loginform.password.data):
            flash(ar.username +" و"+ ar.password +" أو إحداهما خاطئ")
            return redirect(url_for('login'))
        user = User(username=user_info['username'], isadmin=user_info['isadmin'])
        login_user(user, remember=loginform.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    
    #if it is a GET request
    return render_template("loginform.html", form=loginform)





@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("index"))
    
    registerform = RegisterForm()

    #if POST
    if registerform.validate_on_submit():
        qr.addUser(username=registerform.username.data, passwordhash=registerform.email.data, email=registerform.password.data)
        flash('حياك الله بيننا يا ' + registerform.username.data)
        return redirect(url_for('login'))


    #if it is a GET request
    return render_template('registerform.html', form=registerform)


@app.route("/addentry", methods=["GET", "POST"])
def add_entry():

    ############## HELPER FUNCTION ################
    primarySeperator = ','
    altSeperators = ['،', '.']
    def parseCorrectionsIntoList(correctionsString):
        
        #subtitutes alt seperators
        for altSeperator in altSeperators:
            correctionsString = correctionsString.replace(altSeperator, primarySeperator) 
        corrections = correctionsString.split(primarySeperator) #self-explaintory
        corrections = map(lambda c: " ".join(c.split()) ,corrections) #strips extra spaces
        corrections = filter(lambda c: c != "", corrections) #removes empty elements
        corrections = set(corrections) #removes duplicates            
        corrections = list(corrections) # "because why not" -pyhton
        return corrections


    entryform = AddEntry()

    #POST
    if entryform.validate_on_submit():

        corrections = parseCorrectionsIntoList(entryform.corrections.data)
        arcontext = entryform.context.data['arcontext']
        trcontext = entryform.context.data['trcontext']
        contexts = list[tuple[str, str]]()

        # TRCONTEXT FIRST THEN ARCONTEXT!!
        contexts.append((trcontext, arcontext))

        qr.addEntry(origin = entryform.origin.data,
                    original = entryform.original.data,
                    translationese = entryform.translationese.data,
                    submitter = current_user.username if current_user.is_authenticated else None, 
                    corrections = corrections, 
                    contexts=contexts)
        
        flash('رصدت اللفظة, وسيراجعها أحد المشرفين لقبولها ونشرها')
        return redirect(url_for('index'))

    #GET
    return render_template('addentry.html', form=entryform)


@app.route('/entries/<entryid>')
def entry_page(entryid):
    entry = qr.getEntry(entryid=entryid)
    if not entry: abort(404)

    return render_template('entry.html', entry=entry)


@app.route('/pending')
@login_required
def pending():
    if not current_user.isadmin:
        return "لا يجوز لك دخول هذه الصفحة", 404
    
    entries = qr.getAllEntries(desc=False, limit=None, isapproved=False)
    return render_template("home.html", entries= entries)

@app.route('/pending/<int:entryid>')
@login_required
def accept(entryid: int):
    if not current_user.isadmin:
        return "لا يجوز لك دخول هذه الصفحة", 404
    
    qr.acceptEntry(entryid=entryid, approvedby=current_user.username)
    flash('قبلت اللفظة ونشرت')
    return redirect(url_for('pending'))



