# -*- coding: utf-8 -*-
"""停车场信息登记 — 本地服务端（数据持久化到 JSON 文件）"""
import http.server
import json
import os
import sys
import urllib.parse

PORT = 8765
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parking_data.json')
HTML_DIR = os.path.dirname(os.path.abspath(__file__))

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"lotIds": [], "currentLotId": None, "lots": {}}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=HTML_DIR, **kwargs)

    def do_POST(self):
        if self.path == '/api/save':
            try:
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length).decode('utf-8')
                data = json.loads(body)
                save_data(data)
                self._json({"ok": True})
            except Exception as e:
                self._json({"ok": False, "error": str(e)}, 500)
        else:
            self._json({"ok": False, "error": "unknown endpoint"}, 404)

    def do_GET(self):
        if self.path == '/api/load':
            try:
                data = load_data()
                self._json({"ok": True, "data": data})
            except Exception as e:
                self._json({"ok": False, "error": str(e)}, 500)
        else:
            super().do_GET()

    def _json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    print(f'停车场服务端已启动 → http://localhost:{PORT}')
    print(f'数据文件: {DATA_FILE}')
    try:
        http.server.HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print('\n服务已停止')
