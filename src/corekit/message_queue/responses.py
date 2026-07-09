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
def success_response(data=None):
    payload = {
        'success': True,
        'data': data
    }

    return payload


def error_response(code, message):
    payload = {
        'success': False,
        'error': {
            'code': code,
            'message': message,
        }
    }

    return payload