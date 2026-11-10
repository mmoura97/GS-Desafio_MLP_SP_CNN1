"""Executar da raiz do projeto: python SERVIR_APP.py"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
if __name__=='__main__':
    root=Path(__file__).resolve().parent/'dist'
    print('Aplicação em http://localhost:8000 — Ctrl+C para encerrar.',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8000),partial(SimpleHTTPRequestHandler,directory=str(root))).serve_forever()
