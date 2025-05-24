from app import create_app
from dotenv import load_dotenv
load_dotenv()


app = create_app()

print("Using DB:", app.config["SQLALCHEMY_DATABASE_URI"])

if __name__ == '__main__':
    app.run(debug=True)

