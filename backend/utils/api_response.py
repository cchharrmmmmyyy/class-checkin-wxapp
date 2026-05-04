"""
统一 API 响应工具。
"""
from datetime import date
from flask import jsonify


LEGACY_ROUTES_SUNSET_DATE = date(2026, 7, 31)
LEGACY_ROUTES_DOC = '/docs/deprecations#legacy-plural-routes'


def success(data=None, message='success', code=200, http_status=200):
    payload = {
        'code': code,
        'message': message,
        'data': data,
    }
    return jsonify(payload), http_status


def error(data=None, message='', code=0, http_status=400):
    payload = {
        'code': code,
        'message': message,
        'data': data,
    }
    return jsonify(payload), http_status


def mark_legacy_route(response):
    response.headers['Deprecation'] = 'true'
    response.headers['Sunset'] = LEGACY_ROUTES_SUNSET_DATE.isoformat()
    response.headers['Link'] = f'<{LEGACY_ROUTES_DOC}>; rel="deprecation"'
    return response
