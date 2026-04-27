#!/usr/bin/env python3
"""
HTTPS local server for camera access on iPad.
Safari requires HTTPS to use getUserMedia.
Run: python3 server.py
Then open https://<your-ip>:8443 on iPad (accept the certificate warning).
"""
import http.server
import ssl
import socket
import subprocess
import os
import sys

PORT = 8443
CERT_FILE = "cert.pem"
KEY_FILE = "key.pem"

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

def generate_cert():
    if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
        return
    print("Generating self-signed certificate...")
    ip = get_local_ip()
    subprocess.run([
        "openssl", "req", "-x509", "-newkey", "rsa:2048",
        "-keyout", KEY_FILE, "-out", CERT_FILE,
        "-days", "365", "-nodes",
        "-subj", f"/CN={ip}",
        "-addext", f"subjectAltName=IP:{ip},IP:127.0.0.1",
    ], check=True, capture_output=True)
    print(f"Certificate created for IP: {ip}")

def main():
    generate_cert()
    ip = get_local_ip()

    handler = http.server.SimpleHTTPRequestHandler
    handler.log_message = lambda self, fmt, *args: None  # quiet

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(CERT_FILE, KEY_FILE)

    with http.server.HTTPServer(("0.0.0.0", PORT), handler) as httpd:
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        print(f"\n{'='*50}")
        print(f"  Particle Vision - Serveur local HTTPS")
        print(f"{'='*50}")
        print(f"\n  Sur ton iPad, ouvre Safari et va sur:")
        print(f"\n  *** https://{ip}:{PORT} ***")
        print(f"\n  -> Accepte l'avertissement de certificat")
        print(f"     (Avancé > Continuer quand même)")
        print(f"\n{'='*50}")
        print(f"  Ctrl+C pour arrêter\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServeur arrêté.")

if __name__ == "__main__":
    main()
