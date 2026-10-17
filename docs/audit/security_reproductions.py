"""Offline synthetic observations of upstream c839f30; passing means issue reproduced."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch

if len(sys.argv) < 2:
    raise SystemExit('Usage: python3 security_reproductions.py /path/to/pinned/notfair-upstream')
ROOT = Path(sys.argv.pop(1)).resolve()
SCRIPTS = ROOT / 'seo/seo-analysis/scripts'
sys.path.insert(0, str(SCRIPTS))
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

ghost = load('obs_ghost', SCRIPTS / 'fetch_ghost_content.py')
strapi = load('obs_strapi', SCRIPTS / 'push_strapi_seo.py')
checker = load('obs_checker', ROOT / 'seo/broken-link-checker/scripts/checker.py')

class Observations(unittest.TestCase):
    def test_ghost_preflight_does_not_guard_redirects(self):
        public = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 443))]
        with patch.object(ghost.socket, 'getaddrinfo', return_value=public):
            ghost.validate_url('https://cms.example')
        req = urllib.request.Request('https://cms.example/ghost/api/content/posts/?key=synthetic')
        redirected = urllib.request.HTTPRedirectHandler().redirect_request(
            req, None, 302, '', {}, 'http://127.0.0.1:8765/internal')
        self.assertEqual(redirected.full_url, 'http://127.0.0.1:8765/internal')
        # The actual helpers both use stdlib urllib.request.urlopen without a
        # restrictive redirect handler; no request is sent by this observation.
        self.assertIn('urllib.request.urlopen(req, timeout=timeout)', Path(ghost.__file__).read_text())

    def test_strapi_writes_after_failed_current_value_read(self):
        updates = [{'document_id':'synthetic123', 'meta_title':'Synthetic title',
                    'updated_at':'2026-01-01T00:00:00Z'}]
        with patch.object(strapi, 'strapi_get', side_effect=urllib.error.URLError('synthetic read failure')), \
             patch.object(strapi, 'strapi_put', return_value={}) as put, \
             contextlib.redirect_stderr(io.StringIO()):
            strapi.process_updates('https://cms.example', 'synthetic-token', 'articles', updates, '5', auto_yes=True)
        self.assertEqual(put.call_count, 1)
        self.assertEqual(put.call_args.args[2], '/api/articles/synthetic123')

    def test_max_pages_is_not_total_link_request_bound(self):
        class Response(io.BytesIO):
            headers = {'Content-Type':'text/html'}
            def __init__(self, data):
                super().__init__(data)
                self.read_sizes = []
            def getcode(self): return 200
            def read(self, n=-1):
                self.read_sizes.append(n)
                return super().read(n)
        response = Response(''.join(f'<a href="https://target.example/{i}">x</a>' for i in range(120)).encode())
        def opener(request, **kwargs):
            return Response(b'') if request.full_url.endswith('/robots.txt') else response
        with patch.object(checker, 'public_urlopen', side_effect=opener), \
             patch.object(checker, 'check_url', return_value=(200, None)) as check, \
             contextlib.redirect_stderr(io.StringIO()):
            checker.crawl('https://cms.example/', max_pages=1)
        self.assertEqual(check.call_count, 120)
        self.assertEqual(response.read_sizes, [-1])

    def test_parent_env_overrides_project_config(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            project = parent / 'client-a'; project.mkdir()
            (project / '.env.local').write_text('STRAPI_URL=https://client-a.example\nSTRAPI_API_KEY=synthetic-a\n')
            (parent / '.env').write_text('STRAPI_URL=https://client-b.example\nSTRAPI_API_KEY=synthetic-b\n')
            with patch.object(strapi.os, 'getcwd', return_value=str(project)):
                result = strapi.find_and_load_env()
            self.assertEqual(result['STRAPI_URL'], 'https://client-b.example')
            self.assertEqual(result['STRAPI_API_KEY'], 'synthetic-b')

    def test_batch_document_id_becomes_query_and_path(self):
        updates = [{'document_id':'../users/7?other=1', 'meta_title':'Synthetic title'}]
        attrs = {'data': {'updatedAt':'2026-01-01T00:00:00Z'}}
        with patch.object(strapi, 'strapi_get', return_value=attrs), \
             patch.object(strapi, 'strapi_put', return_value={}) as put, \
             contextlib.redirect_stderr(io.StringIO()):
            strapi.process_updates('https://cms.example', 'synthetic-token', 'articles', updates, '5', auto_yes=True)
        self.assertEqual(put.call_args.args[2], '/api/articles/../users/7?other=1')

if __name__ == '__main__':
    # All outbound and loopback connections forbidden; tests use in-memory mocks.
    with patch.object(socket.socket, 'connect', side_effect=AssertionError('network disabled')):
        unittest.main(verbosity=2)
