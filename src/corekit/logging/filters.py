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
from opentelemetry import trace
from corekit.context import user_id_var


class ContextFilter(logging.Filter):

    def __init__(self, service_name):
        super().__init__()
        self.service_name = service_name

    def filter(self, record):
        span_context = trace.get_current_span().get_span_context()

        if span_context.is_valid:
            record.trace_id = format(span_context.trace_id, '032x')
            record.span_id = format(span_context.span_id, '016x')
        else:
            record.trace_id = ''
            record.span_id = ''

        record.user_id = user_id_var.get()
        record.service = self.service_name

        return True
