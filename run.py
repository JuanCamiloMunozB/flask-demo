import os
from dotenv import load_dotenv
from app import create_app
from config import get_config

# Load environment variables
load_dotenv()

# Create app with appropriate configuration
config_class = get_config()
app = create_app(config_class)

if __name__ == '__main__':
    # Development server
    debug = os.getenv("FLASK_ENV") == "development"
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "127.0.0.1")
    
    app.run(debug=debug, host=host, port=port)