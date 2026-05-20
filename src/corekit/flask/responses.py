#   -----------------------------------------------------------------------------
#  Copyright (c) 2026. Vincent Corriveau (vincent.corriveau89@gmail.com)
#
#  Licensed under the MIT License. You may obtain a copy of the License at
#  https://opensource.org/licenses/MIT
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  -----------------------------------------------------------------------------
from flask import jsonify


def success_response(data=None, status=200, meta=None):
    payload = {
        'success': True,
        'data': data
    }

    if meta:
        payload['meta'] = meta

    return jsonify(payload), status


def error_response(code, message, status=500, details=None, meta=None):
    payload = {
        'success': False,
        'error': {
            'code': code,
            'message': message,
        }
    }

    if details:
        payload['error']['details'] = details

    if meta:
        payload['meta'] = meta

    return jsonify(payload), status

def bad_response(validation_errors: dict):
    return error_response('ValidationError', 'Missing or invalid parameters', 400, validation_errors)
