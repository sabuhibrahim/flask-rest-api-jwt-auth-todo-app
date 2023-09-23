import uuid
from datetime import timedelta, datetime
from jose import jwt, JWTError

from todo_app import config
from todo_app.exceptions import AuthorizationException
from todo_app.schemas import User, TokenPair, JwtTokenSchema
from todo_app.models import BlackListToken


def _create_access_token(payload: dict, minutes: int | None = None) -> JwtTokenSchema:
    expire = datetime.utcnow() + timedelta(
        minutes=minutes or config.ACCESS_TOKEN_EXPIRES_MINUTES
    )

    payload["exp"] = expire
    payload["frs"] = False

    token = JwtTokenSchema(
        token=jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM),
        payload=payload,
        expire=expire,
    )

    return token


def _create_refresh_token(payload: dict) -> JwtTokenSchema:
    expire = datetime.utcnow() + timedelta(minutes=config.REFRESH_TOKEN_EXPIRES_MINUTES)

    payload["exp"] = expire
    payload["frs"] = True

    token = JwtTokenSchema(
        token=jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM),
        expire=expire,
        payload=payload,
    )

    return token


def create_token_pair(user: User) -> TokenPair:
    payload = {"sub": str(user.id), "name": user.full_name, "jti": str(uuid.uuid4())}

    return TokenPair(
        access=_create_access_token(payload={**payload}),
        refresh=_create_refresh_token(payload={**payload}),
    )


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        if payload.get("frs"):
            raise JWTError("Access token need")
        black_list_token = BlackListToken.query.filter_by(id=payload["jti"]).first()
        if black_list_token:
            raise JWTError("Token is blacklisted")
    except JWTError:
        raise AuthorizationException()

    return payload


def refresh_token_state(token: str):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        if not payload.get("frs"):
            raise JWTError("Refresh token need")
    except JWTError as ex:
        print(str(ex))
        raise AuthorizationException()

    return {"access": _create_access_token(payload=payload).token}
