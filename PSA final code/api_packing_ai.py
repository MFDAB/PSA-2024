from flask import Flask, request, jsonify
from multiprocessing import cpu_count
from ai_packing_logic import parallel_pack
import requests
app = Flask(__name__)


@app.route('/pack', methods=['POST'])
def pack():
    data = request.get_json()

    # Extract containers and cargo
    containers = data.get('containers', [])
    cargo_list = data.get('cargo', [])
    callback_url = data.get('callback_url')

    if not containers or not cargo_list or not callback_url:
        return jsonify({"error": "containers, cargo, and callback_url are required"}), 400

    # Perform the packing
    num_processes = cpu_count()
    result = parallel_pack(cargo_list, containers, num_processes)

    # Send the result to the callback URL
    try:
        response = requests.post(callback_url, json=result)
        if response.status_code != 200:
            return jsonify({"error": "Failed to send results to callback URL"}), 500
    except Exception as e:
        return jsonify({"error": f"Callback request failed: {str(e)}"}), 500

    # Return the result as a response to the client
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
