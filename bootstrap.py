import os
from flask import Flask, send_from_directory, request

# Liara storage variable aliases used in the dashboard.
if not os.environ.get("LIARA_ENDPOINT_URL") and os.environ.get("LIARA_ENDPOINT"):
    os.environ["LIARA_ENDPOINT_URL"] = os.environ["LIARA_ENDPOINT"]
if not os.environ.get("LIARA_BUCKET_NAME") and os.environ.get("LIARA_BUCKET"):
    os.environ["LIARA_BUCKET_NAME"] = os.environ["LIARA_BUCKET"]

# Liara's application filesystem is read-only at runtime. Force Flask's
# automatically discovered instance directory to a writable /tmp location.
def _liara_instance_path(self):
    path = "/tmp/ss_porm_instance"
    os.makedirs(path, exist_ok=True)
    return path

Flask.auto_find_instance_path = _liara_instance_path

from app import app

@app.route('/static/save-fix.js')
def serve_save_fix():
    response = send_from_directory('/app', 'save-fix.js', mimetype='application/javascript')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/static/ui-patch.js')
def serve_ui_patch():
    response = send_from_directory('/app', 'ui-patch.js', mimetype='application/javascript')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/cervical')
def serve_cervical_module():
    response = send_from_directory('/app', 'cervical.html', mimetype='text/html')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.after_request
def inject_ui_patch(response):
    if request.path == '/' and response.content_type and 'text/html' in response.content_type:
        try:
            html = response.get_data(as_text=True)
            tag = '<script src="/static/ui-patch.js?v=1"></script>'
            if tag not in html:
                html = html.replace('</body>', tag + '</body>')
                response.set_data(html)
                response.headers['Content-Length'] = str(len(response.get_data()))
        except Exception:
            pass
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response
