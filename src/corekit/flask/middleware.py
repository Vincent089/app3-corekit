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
import logging
import time
import uuid
from flask import g, request
from corekit.context import trail_id_var, user_id_var
from corekit.utils import calc_duration, get_client_ip
from corekit.execptions import DomainError
from corekit.flask import error_response

logger = logging.getLogger(__name__)


def register_middleware(app):
    @app.errorhandler(DomainError)
    def handle_domain_error(e):
        return error_response(code=e.__class__.__name__, message=str(e), status=e.status_code)

    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.client_ip = get_client_ip(request)

        log_id = request.headers.get('X-Trail-ID', str(uuid.uuid4()))
        user_id = request.headers.get('X-User-ID', None)

        trail_id_var.set(log_id)
        user_id_var.set(user_id)

        logger.info(
                f'Request',
                extra={
                    'method': request.method,
                    'path': request.path,
                    'bytes': request.content_length,
                    'client_ip': g.client_ip,
                    'user_agent': request.user_agent.string,
                }
        )

    @app.after_request
    def after_request(response):
        duration = calc_duration(g.start_time)

        response.headers["X-Trail-ID"] = trail_id_var.get()

        logger.info(
                f'Response',
                extra={
                    'status_code': response.status_code,
                    'method': request.method,
                    'path': request.path,
                    'bytes': response.content_length,
                    'duration_ms': duration,
                    'client_ip': g.client_ip,
                    'user_agent': request.user_agent.string,
                }
        )

        return response
