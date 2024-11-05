from webapp import app, ar, login, db
from webapp.modules.models import User
from webapp import routes




@app.context_processor
def utility_processor():
    return {"ar" : ar}

