import io

from flask import send_file


def send_bytes(bytes, mimetype):
    return send_file(
        io.BytesIO(bytes),
        mimetype=mimetype
    )
