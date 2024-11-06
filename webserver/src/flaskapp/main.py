from flask import Flask
from config import Config
from flask_login import LoginManager
from flaskapp.modules.global_names import Arabic


app = Flask(__name__)
app.config.from_object(Config)
login = LoginManager(app)
login.login_view = "login"

ar = Arabic()


@app.context_processor
def utility_processor():
    return {"ar" : ar}


from flaskapp import routes