from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from pydantic import ValidationError
from todo_app.config import PG_URL
from todo_app.exceptions import (
    AuthorizationException,
    NotFoundException,
    BadRequestException,
)


__name__ = "todo_app"

app = Flask(__name__)

db = SQLAlchemy()

app.config["SQLALCHEMY_DATABASE_URI"] = PG_URL

db.init_app(app)


@app.errorhandler(ValidationError)
def validate_validation_error(e: ValidationError):
    return (
        jsonify(
            {
                "message": "Unprocessable Content",
                "data": e.errors,
            }
        ),
        422,
    )


@app.errorhandler(AuthorizationException)
def validate_auth_error(e: AuthorizationException):
    return jsonify(e.dict()), e.status_code


@app.errorhandler(BadRequestException)
def validate_bad_request_error(e: BadRequestException):
    return jsonify(e.dict()), e.status_code


@app.errorhandler(NotFoundException)
def validate_not_found_error(e: NotFoundException):
    return jsonify(e.dict()), e.status_code


import todo_app.routers
