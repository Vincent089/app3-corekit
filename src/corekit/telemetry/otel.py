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
import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

DEFAULT_OTLP_ENDPOINT = 'http://alloy.infra-obs.svc.cluster.local:4318/v1/traces'


def init_otel(service_name: str, environment: str):
    """
    Call once at service startup, before the Flask app is created.
    No-op if OTEL_ENABLED is unset/false — lets local dev run without Alloy.
    """
    if os.getenv('OTEL_ENABLED', 'false').lower() != 'true':
        return

    endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', DEFAULT_OTLP_ENDPOINT)

    provider = TracerProvider(
            resource=Resource.create({
                'service.name': service_name,
                'deployment.environment': environment,
            })
    )
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
    trace.set_tracer_provider(provider)

    set_global_textmap(TraceContextTextMapPropagator())

    FlaskInstrumentor().instrument()

    try:
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        RequestsInstrumentor().instrument()
    except ImportError:
        pass
