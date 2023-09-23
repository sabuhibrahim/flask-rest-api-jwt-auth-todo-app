from typing import Callable
from functools import wraps

from jose import jwt, JWTError
from flask import request
from todo_app.config import SECRET_KEY, ALGORITHM
from todo_app.models import User, BlackListToken
from todo_app.exceptions import AuthorizationException


def auth_required(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = None

        if "Authorization" not in request.headers:
            raise AuthorizationException()

        token_type, token = request.headers["Authorization"].split(" ")

        if any(
            [
                not token_type,
                token_type.lower() != "bearer",
                not token,
            ]
        ):
            raise AuthorizationException("Valid token required")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("frs"):
                raise JWTError("Access token need")
            black_list_token = BlackListToken.query.filter_by(id=payload["jti"]).first()
            if black_list_token:
                raise JWTError("Token is blacklisted")

            user = User.query.filter_by(id=payload["sub"]).first()

            if not user:
                raise AuthorizationException(message="User not found")

            if not user.is_active:
                raise AuthorizationException(message="User is not active")
        except JWTError as e:
            raise AuthorizationException(message=str(e))

        return func(user, *args, **kwargs)

    return wrapper
