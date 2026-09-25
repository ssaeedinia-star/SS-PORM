import os
from flask import Flask, send_from_directory

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

# Explicitly serve the post-save reset patch. The app uses static_folder='.'
# so Liara/Flask may not expose this root file under /static automatically.
@app.route('/static/save-fix.js')
def serve_save_fix():
    response = send_from_directory('/app', 'save-fix.js', mimetype='application/javascript')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response
