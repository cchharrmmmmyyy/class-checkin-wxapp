"""共享序列化/反序列化工具函数。"""

import json
import random
import string

from config import Config
from utils.exceptions import ServiceException


def to_time_str(value):
    if value is None:
        return None
    if hasattr(value, 'strftime'):
        return value.strftime('%H:%M:%S')
    return str(value)


def to_datetime_str(value):
    if value is None:
        return None
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    return str(value)


def as_bool_int(value, default=1):
    if value is None:
        return default
    return 1 if str(value).lower() in ('1', 'true', 'yes', 'on') else 0


def load_polygon_coords(value):
    if value is None:
        return None
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            raise ServiceException('polygon_coords 不是合法的 JSON', code=9003)
    return value


def dump_polygon_coords(value):
    if value is None:
        return None
    if isinstance(value, str):
        load_polygon_coords(value)
        return value
    return json.dumps(value, ensure_ascii=False)


def validate_polygon_coords(value):
    coords = load_polygon_coords(value)
    if not isinstance(coords, list) or len(coords) < 3:
        raise ServiceException('polygon_coords 至少需要 3 个顶点', code=9004)
    for item in coords:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ServiceException('polygon_coords 顶点格式必须为 [latitude, longitude]', code=9005)
    return coords


def generate_random_password(length=None):
    if length is None:
        length = Config.RANDOM_PASSWORD_LENGTH
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))
