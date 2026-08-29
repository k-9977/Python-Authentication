from flask import Flask, request, send_from_directory
from extensions import db
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

db.init_app(app)


@app.route("/<path:filename>")
def frontend(filename):
    return send_from_directory("frontend", filename)


@app.route("/")
def home():
    return send_from_directory("frontend", "index.html")


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
    from models import User, RefreshToken

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

    # Create access token
    access_token = jwt.encode(
        {
            "user_id": user.id,
            "username": user.username,
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15)
        },
        app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    # Create refresh token
    refresh_token = jwt.encode(
        {
            "user_id": user.id,
            "username": user.username,
            "type": "refresh",
            "exp": datetime.now(timezone.utc) + timedelta(days=7)
        },
        app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    # Save refresh token in database
    refresh_token_record = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )

    db.session.add(refresh_token_record)
    db.session.commit()

    return {
        "message": "Login successful",
        "username": user.username,
        "access_token": access_token,
        "refresh_token": refresh_token
    }, 200


@app.route("/refresh", methods=["POST"])
def refresh():
    from models import RefreshToken

    data = request.get_json()

    refresh_token = data.get("refresh_token")

    if not refresh_token:
        return {"error": "Refresh token is required"}, 401

    try:
        # Check if refresh token exists in database
        stored_token = RefreshToken.query.filter_by(
            token=refresh_token
        ).first()

        if not stored_token:
            return {"error": "Invalid refresh token"}, 401

        # Decode and validate refresh token
        payload = jwt.decode(
            refresh_token,
            app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )

        # Make sure this is actually a refresh token
        if payload.get("type") != "refresh":
            return {"error": "Invalid token type"}, 401

        # Create a new access token
        new_access_token = jwt.encode(
            {
                "user_id": payload["user_id"],
                "username": payload["username"],
                "type": "access",
                "exp": datetime.now(timezone.utc) + timedelta(minutes=15)
            },
            app.config["SECRET_KEY"],
            algorithm="HS256"
        )

        return {
            "message": "Access token refreshed successfully",
            "access_token": new_access_token
        }, 200

    except jwt.ExpiredSignatureError:
        return {"error": "Refresh token has expired"}, 401

    except jwt.InvalidTokenError:
        return {"error": "Invalid refresh token"}, 401


@app.route("/protected", methods=["GET"])
def protected():
    from models import RevokedToken

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return {"error": "Authorization token is required"}, 401

    try:
        token = auth_header.split(" ")[1]

        revoked = RevokedToken.query.filter_by(token=token).first()

        if revoked:
            return {"error": "Token has been revoked"}, 401

        payload = jwt.decode(
            token,
            app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )
        if payload.get("type") != "access":
            return {"error": "Access token required"}, 401

        return {
            "message": "You have access to the protected route",
            "username": payload["username"]
        }, 200

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return {"error": "Invalid or expired token"}, 401


@app.route("/me", methods=["GET"])
def me():
    from models import User, RevokedToken

    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return {"error": "Bearer token is required"}, 401

    try:
        token = auth_header.split(" ", 1)[1]

        revoked = RevokedToken.query.filter_by(token=token).first()

        if revoked:
            return {"error": "Token has been revoked"}, 401

        payload = jwt.decode(
            token,
            app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )

        if payload.get("type") != "access":
            return {"error": "Access token required"}, 401

        user = User.query.get(payload["user_id"])

        if not user:
            return {"error": "User not found"}, 404

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }, 200

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return {"error": "Invalid or expired token"}, 401


@app.route("/logout", methods=["POST"])
def logout():
    from models import RevokedToken

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return {"error": "Authorization token is required"}, 401

    try:
        token = auth_header.split(" ")[1]

        jwt.decode(
            token,
            app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )

        revoked_token = RevokedToken(token=token)

        db.session.add(revoked_token)
        db.session.commit()

        return {"message": "Logout successful"}, 200

    except jwt.ExpiredSignatureError:
        return {"error": "Token has already expired"}, 401

    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}, 401


if __name__ == "__main__":
    app.run(debug=True)
