"""
统一 API 响应工具。
"""
from datetime import date
from flask import jsonify, g


LEGACY_ROUTES_SUNSET_DATE = date(2026, 7, 31)
LEGACY_ROUTES_DOC = '/docs/deprecations#legacy-plural-routes'


def get_trace_id():
    return getattr(g, 'trace_id', None)


def success(data=None, message='success', code=200, http_status=200):
    payload = {
        'code': code,
        'message': message,
        'data': data,
    }
    trace_id = get_trace_id()
    if trace_id:
        payload['trace_id'] = trace_id
    return jsonify(payload), http_status


def error(message, code, http_status=400, data=None):
    payload = {
        'code': code,
        'message': message,
        'data': data,
    }
    trace_id = get_trace_id()
    if trace_id:
        payload['trace_id'] = trace_id
    return jsonify(payload), http_status


def mark_legacy_route(response):
    response.headers['Deprecation'] = 'true'
    response.headers['Sunset'] = LEGACY_ROUTES_SUNSET_DATE.isoformat()
    response.headers['Link'] = f'<{LEGACY_ROUTES_DOC}>; rel="deprecation"'
    return response
