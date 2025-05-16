import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

# Cria a aplicação Flask
app = create_app()

# Inicia o servidor
if __name__ == "__main__":
    app.run(debug=True)
