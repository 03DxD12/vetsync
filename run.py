import os
from dotenv import load_dotenv
from app import create_app

load_dotenv()

app = create_app(os.getenv('FLASK_ENV', 'default'))

if __name__ == '__main__':
    # host='0.0.0.0' allows external access (essential for ngrok/mobile testing)
    app.run(host='0.0.0.0', port=5000, debug=True)
