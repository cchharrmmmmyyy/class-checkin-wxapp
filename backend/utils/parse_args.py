from flask import request


def parse_bool_arg(name, default=False):
    raw = request.args.get(name, None)
    if raw is None:
        return default
    return str(raw).lower() in ('1', 'true', 'yes', 'on')
