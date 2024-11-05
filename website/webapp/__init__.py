from flask import Flask
from config import Config
from flask_login import LoginManager
from webapp.querier import Querier


from webapp.modules.global_names import Arabic







app = Flask(__name__)
app.config.from_object(Config)
login = LoginManager(app)
login.login_view = "login"
db = Querier(**app.config['DATABASE'])


ar = Arabic()



#from webapp import routes