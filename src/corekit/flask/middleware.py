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
from flask import g, request
from prometheus_flask_exporter import PrometheusMetrics
from corekit.context import user_id_var
from corekit.utils import calc_duration, get_client_ip
from corekit.execptions import DomainError
from corekit.flask.responses import error_response

logger = logging.getLogger(__name__)


def register_middleware(app):
    PrometheusMetrics(app)

    @app.errorhandler(DomainError)
    def handle_domain_error(e):
        return error_response(code=e.__class__.__name__, message=str(e), status=e.status_code)

    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.client_ip = get_client_ip(request)

        # traceparent extraction and span creation are handled automatically by
        # FlaskInstrumentor (wired in corekit.telemetry.otel.init_otel) — no manual
        # header parsing here. trace_id/span_id land on log records via the OTel
        # logging bridge in corekit.logging, not via this middleware.
        user_id = request.headers.get('X-User-ID', None)

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
