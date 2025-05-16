from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Instanciar db e migrate fora da função create_app
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'sua_chave_secreta'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar db e migrate com o app
    db.init_app(app)
    migrate.init_app(app, db)

    # Registrar o blueprint
    from app.routes.home import home_bp
    app.register_blueprint(home_bp)

    return app