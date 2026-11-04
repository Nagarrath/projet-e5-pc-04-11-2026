from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def health():
    return jsonify({"status": "ok", "service": "stock-api"}), 200

@app.route('/stocks')
def get_stocks():
    return jsonify([
        {"id": 1, "item": "Clavier RGB", "quantity": 15},
        {"id": 2, "item": "Souris sans fil", "quantity": 42}
    ]), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
