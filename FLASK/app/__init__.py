import os 
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager 
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager() 
bcrypt = Bcrypt()


basedir = os.path.abspath(os.path.dirname(__file__)) 

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'sua_chave_secreta'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tasks.db') 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    
    from app.models.task import User, Task  
    
    login_manager.login_view ='home.login'
    
    from app.routes.home import home_bp
    app.register_blueprint(home_bp)

    @login_manager.user_loader 
    def load_user(user_id):
        with app.app_context():
            return User.query.get(int(user_id))
    
    from app.utils.reminder_scheduler import start_scheduler
    start_scheduler(app)
    
    return app