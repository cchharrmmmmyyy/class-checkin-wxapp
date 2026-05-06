import os
from dotenv import load_dotenv

load_dotenv()


def _required(key):
    value = os.environ.get(key, '')
    if not value:
        raise ValueError(f"Missing or empty environment variable: {key}")
    return value


def _required_bool(key):
    value = _required(key)
    if value.lower() not in ('true', 'false'):
        raise ValueError(f"Environment variable {key} must be 'true' or 'false', got: {value}")
    return value.lower() == 'true'


def _required_int(key):
    value = _required(key)
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Environment variable {key} must be an integer, got: {value}")


def _optional(key, default=None):
    value = os.environ.get(key, '')
    if not value:
        return default
    return value


def _optional_bool(key, default=False):
    value = os.environ.get(key, '')
    if not value:
        return default
    if value.lower() not in ('true', 'false'):
        raise ValueError(f"Environment variable {key} must be 'true' or 'false', got: {value}")
    return value.lower() == 'true'


def _optional_int(key, default=0):
    value = os.environ.get(key, '')
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Environment variable {key} must be an integer, got: {value}")


class Config:
    SECRET_KEY = _required('JWT_SECRET_KEY')
    TOKEN_EXPIRE_HOURS = _required_int('TOKEN_EXPIRE_HOURS')
    DATABASE_FILE = os.path.join(os.path.dirname(__file__), _required('DATABASE_FILE'))
    INSERT_TEST_DATA = _required_bool('INSERT_TEST_DATA')
    FLASK_HOST = _required('FLASK_HOST')
    FLASK_PORT = _required_int('FLASK_PORT')
    FLASK_DEBUG = _required_bool('FLASK_DEBUG')
    RANDOM_PASSWORD_LENGTH = _required_int('RANDOM_PASSWORD_LENGTH')
    PUNCH_RECORDS_LIMIT = _required_int('PUNCH_RECORDS_LIMIT')