import http.server
import cgi
import os
import subprocess
from pathlib import Path

PASSWORD_ENV = 'UPLOAD_PASSWORD'
TOKEN_ENV = 'GITHUB_TOKEN'

class UploadHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        html = b"""<html><body><form method='POST' enctype='multipart/form-data'>\n"""
        html += b"Password: <input type='password' name='password'><br/>\n"
        html += b"File: <input type='file' name='file'><br/>\n"
        html += b"<input type='submit' value='Upload'>\n"
        html += b"</form></body></html>"
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html)

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.get('Content-Type'))
        if ctype != 'multipart/form-data':
            self.send_error(400, 'Invalid request')
            return
        pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
        pdict['CONTENT-LENGTH'] = int(self.headers.get('Content-Length'))
        fs = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST'}, keep_blank_values=True)
        password = fs.getvalue('password')
        if password != os.environ.get(PASSWORD_ENV):
            self.send_error(403, 'Forbidden')
            return
        if 'file' not in fs:
            self.send_error(400, 'No file provided')
            return
        fileitem = fs['file']
        if not fileitem.filename:
            self.send_error(400, 'No file provided')
            return
        filename = Path(fileitem.filename).name
        with open(filename, 'wb') as f:
            f.write(fileitem.file.read())
        subprocess.run(['git', 'add', filename])
        subprocess.run(['git', 'commit', '-m', f'Add {filename}'], check=False)
        token = os.environ.get(TOKEN_ENV)
        if token:
            remote = subprocess.run(['git', 'remote', 'get-url', 'origin'], capture_output=True, text=True).stdout.strip()
            if remote.startswith('https://') and '@' not in remote:
                authed = remote.replace('https://', f'https://{token}@')
            else:
                authed = remote
            subprocess.run(['git', 'push', authed, 'HEAD'], check=False)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'File uploaded and committed.')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8000'))
    http.server.ThreadingHTTPServer(('', port), UploadHandler).serve_forever()
