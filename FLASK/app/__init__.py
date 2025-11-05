from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager 
from flask_bcrypt import Bcrypt 


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager() 
bcrypt = Bcrypt() 

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'sua_chave_secreta'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    
    db.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.init_app(app)
    bcrypt.init_app(app)

    
    from app.models.task import User 
    
    login_manager.login_view ='home.login'
    
    
    @login_manager.user_loader 
    def load_user(user_id):
        
        with app.app_context():
            return User.query.get(int(user_id))
    
   
    from app.routes.home import home_bp
    app.register_blueprint(home_bp)

    
    from app.utils.reminder_scheduler import start_scheduler
    start_scheduler(app)
    
    return app