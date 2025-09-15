from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import shutil
import platform
import subprocess

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers=["Content-Type", "X-API-KEY"])

API_KEY = "SECRET123"
BASE_PATH = "C:\\Users\\Danil\\Desktop"  # корневая папка ПК

def check_api_key(req):
    token = req.headers.get("X-API-KEY")
    if token != API_KEY:
        return False
    return True

@app.route("/list", methods=["GET"])
def list_folder():
    if not check_api_key(request):
        return jsonify({"error": "Unauthorized"}), 403

    rel_path = request.args.get("path", "")
    abs_path = os.path.abspath(os.path.join(BASE_PATH, rel_path))
    if not abs_path.startswith(BASE_PATH):
        return jsonify({"error": "Запрещён доступ вне базовой папки"}), 403
    if not os.path.exists(abs_path):
        return jsonify({"error": "Путь не найден"}), 404

    items = []
    for name in os.listdir(abs_path):
        path = os.path.join(abs_path, name)
        items.append({
            "name": name,
            "is_dir": os.path.isdir(path)
        })
    return jsonify({"path": rel_path, "items": items})

@app.route("/open", methods=["POST"])
def open_item():
    if not check_api_key(request):
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    rel_path = data.get("name")
    abs_path = os.path.abspath(os.path.join(BASE_PATH, rel_path))
    if not os.path.exists(abs_path):
        return jsonify({"error": "Файл или папка не найдены"}), 404
    try:
        system = platform.system().lower()
        if system == "windows":
            subprocess.Popen(f'start "" "{abs_path}"', shell=True)
        else:
            subprocess.Popen(["xdg-open", abs_path])
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/delete", methods=["POST"])
def delete_item():
    if not check_api_key(request):
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    rel_path = data.get("name")
    abs_path = os.path.abspath(os.path.join(BASE_PATH, rel_path))
    if not os.path.exists(abs_path):
        return jsonify({"error": "Файл или папка не найдены"}), 404
    try:
        if os.path.isdir(abs_path):
            shutil.rmtree(abs_path)
        else:
            os.remove(abs_path)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/copy", methods=["POST"])
def copy_item():
    if not check_api_key(request):
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    src = os.path.abspath(os.path.join(BASE_PATH, data.get("src")))
    dst = os.path.abspath(os.path.join(BASE_PATH, data.get("dst")))
    try:
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/move", methods=["POST"])
def move_item():
    if not check_api_key(request):
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    src = os.path.abspath(os.path.join(BASE_PATH, data.get("src")))
    dst = os.path.abspath(os.path.join(BASE_PATH, data.get("dst")))
    try:
        shutil.move(src, dst)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/create_file", methods=["POST"])
def create_file():
    if request.headers.get("X-API-KEY") != API_KEY:
        return jsonify({"error":"Unauthorized"}),403
    data = request.json
    path = os.path.abspath(os.path.join(BASE_PATH, data.get("name")))
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/create_folder", methods=["POST"])
def create_folder():
    if request.headers.get("X-API-KEY") != API_KEY:
        return jsonify({"error":"Unauthorized"}),403
    data = request.json
    path = os.path.abspath(os.path.join(BASE_PATH, data.get("name")))
    try:
        os.makedirs(path, exist_ok=True)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)
