from flask import Flask
from flask_talisman import DENY

from app.configuration import AppConfig
from app.extensions import talisman

ENDPOINT_CSP = {"default-src": "'none'", "frame-ancestors": "'none'"}
DOC_CSP = {
    "default-src": "'self'",
    "script-src": ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
    "style-src": ["'self'", "'unsafe-inline'"],
    "img-src": ["'self'", "data:"],
    "font-src": ["'self'", "data:", "https://fonts.scalar.com"],
    "connect-src": "'self'",
    "frame-ancestors": "'none'",
}


def register_security(app: Flask, configuration: AppConfig) -> None:
    talisman.init_app(
        app,
        force_https=configuration.https_forced,
        strict_transport_security=configuration.hsts_enabled,
        frame_options=DENY,
        x_content_type_options=True,
        content_security_policy=ENDPOINT_CSP,
    )


def relax_doc_csp(app: Flask, doc_path: str) -> None:
    doc_page_prefix = f"openapi_{doc_path}_"
    for endpoint, view in app.view_functions.items():
        if endpoint.startswith(doc_page_prefix):
            app.view_functions[endpoint] = talisman(content_security_policy=DOC_CSP)(view)
