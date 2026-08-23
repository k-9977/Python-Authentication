from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os
import jwt
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

load_dotenv()

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# MySQL database connection
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://root:7777@localhost:3306/python_auth"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy()
db.init_app(app)


@app.route("/")
def home():
    return {"message": "Authentication API is running"}


@app.route("/db-test")
def db_test():
    try:
        db.session.execute(db.text("SELECT 1"))
        return {"database": "connected"}
    except Exception as e:
        return {"database": "error", "message": str(e)}, 500


@app.route("/register", methods=["POST"])
def register():
    from models import User

    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return {
            "error": "Username, email, and password are required"
        }, 400

    if User.query.filter_by(username=username).first():
        return {"error": "Username already exists"}, 409

    if User.query.filter_by(email=email).first():
        return {"error": "Email already exists"}, 409

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )

    db.session.add(user)
    db.session.commit()

    return {
        "message": "User registered successfully",
        "username": user.username,
        "email": user.email
    }, 201


@app.route("/login", methods=["POST"])
def login():
    from models import User

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {
            "error": "Username and password are required"
        }, 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return {"error": "Invalid username or password"}, 401

    if not user.check_password(password):
        return {"error": "Invalid username or password"}, 401

    token = jwt.encode(
        {
            "user_id": user.id,
            "username": user.username,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        },
        app.config["SECRET_KEY"],
        algorithm="HS256"
    )
    return {
        "message": "Login successful",
        "username": user.username,
        "token": token
    }, 200


@app.route("/protected", methods=["GET"])
def protected():
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return {"error": "Authorization token is required"}, 401

    try:
        token = auth_header.split(" ")[1]

        payload = jwt.decode(
            token,
            app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )

        return {
            "message": "You have access to the protected route",
            "username": payload["username"]
        }, 200

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return {"error": "Invalid or expired token"}, 401


if __name__ == "__main__":
    app.run(debug=True)
