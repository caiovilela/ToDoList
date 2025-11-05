import os 
from flask import Flask
# REMOVA AS DEFINIÇÕES ANTIGAS (db = SQLAlchemy(), etc.)

# IMPORTE AS INSTÂNCIAS DO SEU ARQUIVO DE EXTENSÕES
from app.extensions import db, migrate, login_manager, bcrypt 

# Define o caminho absoluto para o diretório deste arquivo
basedir = os.path.abspath(os.path.dirname(__file__)) 

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'sua_chave_secreta'
    # Esta linha agora usa o 'basedir' definido globalmente
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tasks.db') 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # INICIALIZE AS INSTÂNCIAS IMPORTADAS
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # IMPORTAÇÃO TARDIA (Os modelos agora usam o 'db' correto)
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