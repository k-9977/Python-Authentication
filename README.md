# Python Authentication

A backend authentication API built with Python and Flask.

The project provides a complete authentication flow with user registration, login, JWT authentication, refresh tokens, protected routes, logout, and token revocation.

## Features

* User registration
* Input validation
* Password hashing
* User login
* JWT access tokens
* JWT refresh tokens
* Protected routes
* User information endpoint
* Logout
* Token revocation
* MySQL database
* SQLAlchemy ORM
* Environment variables for configuration

## Tech Stack

* Python
* Flask
* MySQL
* SQLAlchemy
* PyMySQL
* PyJWT
* Werkzeug
* python-dotenv

## Project Structure

```text
Python-Authentication/
│
├── app.py
├── models.py
├── extensions.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

Clone the repository:

```bash
git clone https://github.com/k-9977/Python-Authentication.git
cd Python-Authentication
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```powershell
venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file and add the required database configuration and secret key.

Start the application:

```bash
python app.py
```

The API runs locally at:

```text
http://127.0.0.1:5000
```

## Authentication Flow

```text
Register
   ↓
Login
   ↓
Access Token
   ↓
Protected Routes
   ↓
Logout
   ↓
Token Revoked
```

## Main Endpoints

| Method | Endpoint    | Purpose                         |
| ------ | ----------- | ------------------------------- |
| POST   | `/register` | Register a new user             |
| POST   | `/login`    | Login and receive JWT tokens    |
| GET    | `/me`       | Get the authenticated user      |
| POST   | `/refresh`  | Generate a new access token     |
| POST   | `/logout`   | Revoke the current access token |

## Security

* Passwords are stored as hashes rather than plain text.
* JWTs are used for authentication.
* Access tokens have an expiration time.
* Revoked tokens are stored in the database.
* Protected routes require a valid access token.
* Secrets and database configuration are kept in environment variables.

## Status

Completed and tested locally.
