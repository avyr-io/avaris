from flask import Flask, request, jsonify
import ssl

app = Flask(__name__)


@app.route('/command', methods=['POST'])
def handle_command():
    # Example command handling
    data = request.json
    return jsonify({"status": "success", "data": data})


if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('path/to/cert.pem', 'path/to/key.pem')
    app.run(ssl_context=context, port=5001)
