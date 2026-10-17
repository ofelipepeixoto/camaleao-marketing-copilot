"""Independent offline review of the new adapter; no external dependencies/network."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch

if len(sys.argv) < 2:
    raise SystemExit('Usage: python3 adapter-security-review.py /path/to/camaleao-marketing-copilot')
ROOT=Path(sys.argv.pop(1)).resolve()
sys.path.insert(0,str(ROOT/'src'))
from camaleao_marketing import InputError, analyze, load_input, write_report

EXAMPLES={name:json.loads((ROOT/'examples'/name).read_bytes()) for name in ['seo.json','search-console.json','paid-media.json']}
def raw(doc): return json.dumps(doc, ensure_ascii=True).encode()
def fresh(name): return json.loads(json.dumps(EXAMPLES[name]))

class IndependentReview(unittest.TestCase):
    def test_html_attribute_without_value_is_safe(self):
        for html in ['<meta name>', '<link rel>', '<script type>x</script>',
                     '<meta name="description" content>', '<meta name="robots" content>']:
            doc=fresh('seo.json');doc['page']['html']=html
            with self.subTest(html=html): self.assertEqual(analyze(raw(doc))['review_status'],'pending')

    def test_unknown_authority_keys_fail(self):
        for key in ['approved','execution_allowed','authorization','instructions']:
            doc=fresh('paid-media.json');doc[key]=True
            with self.subTest(key=key), self.assertRaises(InputError): analyze(raw(doc))

    def test_changed_types_fail_without_uncaught_errors(self):
        values=[None,True,[],{},0,-1,1.5]
        for filename in EXAMPLES:
            for field in ['context','schema_version','mode']:
                for value in values:
                    doc=fresh(filename);doc[field]=value
                    with self.subTest(filename=filename,field=field,value=value), self.assertRaises(InputError): analyze(raw(doc))
        for field in ['id','campaign','channel','currency','spend','revenue','conversions','clicks','impressions']:
            for value in [None,[],{},'SYNTHETIC_PRIVATE_CANARY']:
                doc=fresh('paid-media.json');doc['rows'][0][field]=value
                with self.subTest(field=field,value=value):
                    # Valid identifier strings and channel text are intentionally
                    # allowed by their own contracts; no authority is inferred.
                    try: report=analyze(raw(doc))
                    except InputError: continue
                    self.assertNotIn('SYNTHETIC_PRIVATE_CANARY', json.dumps(report))
                    self.assertFalse(report['execution_allowed'])

    def test_synthetic_source_text_never_echoes(self):
        doc=fresh('seo.json');doc['page']['html']='<title>SYNTHETIC_PRIVATE_CANARY</title><meta name="description" content="SYNTHETIC_PRIVATE_CANARY">'
        report=analyze(raw(doc));self.assertNotIn('SYNTHETIC_PRIVATE_CANARY',json.dumps(report))
        self.assertEqual(report['input_sha256'],hashlib.sha256(raw(doc)).hexdigest())
        self.assertFalse(report['execution_allowed'])
        self.assertTrue(all(x['review_status']=='pending' for x in report['findings']))

    def test_ratio_zero_and_channel_separation(self):
        doc=fresh('paid-media.json')
        for row in doc['rows']:
            row.update(spend='0.00', revenue='0.00',conversions=0,clicks=0,impressions=0)
        report=analyze(raw(doc));metrics=report['observed_metrics']
        self.assertEqual(metrics['channel_count'],2)
        for group in metrics['channels']:
            for key in ['ctr_percent','cpa','roas']: self.assertIsNone(group[key])
        self.assertNotIn('roas',metrics);self.assertNotIn('cpa',metrics)

    def test_no_clobber_and_private_file_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'report.json';report=analyze(raw(fresh('seo.json')))
            write_report(out,report);first=out.read_bytes()
            with self.assertRaises(FileExistsError):write_report(out,report)
            self.assertEqual(out.read_bytes(),first)
            self.assertEqual(out.stat().st_mode & 0o777, 0o600)

    def test_symlink_input_and_parent_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);real=root/'real';real.mkdir();target=real/'input.json';target.write_bytes(raw(fresh('seo.json')))
            link=root/'input-link.json';link.symlink_to(target)
            parent=root/'parent-link';parent.symlink_to(real,target_is_directory=True)
            for path in [link,parent/'input.json']:
                with self.subTest(path=path), self.assertRaises((OSError,InputError)):load_input(path)

    def test_input_size_and_row_bounds(self):
        from camaleao_marketing.core import MAX_INPUT_BYTES, MAX_ROWS
        with self.assertRaises(InputError):analyze(b' '*(MAX_INPUT_BYTES+1))
        doc=fresh('search-console.json');doc['rows']=[doc['rows'][0]]*(MAX_ROWS+1)
        with self.assertRaises(InputError):analyze(raw(doc))

if __name__=='__main__':
    print('core_sha256='+hashlib.sha256((ROOT/'src/camaleao_marketing/core.py').read_bytes()).hexdigest())
    with patch.object(socket.socket,'connect',side_effect=AssertionError('network forbidden')):
        unittest.main(verbosity=2)
