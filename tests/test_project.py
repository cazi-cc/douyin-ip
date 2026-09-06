import copy
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build import load_rules, render
from merge import merge_config


def text_rules(content):
    kinds = {'DOMAIN-SUFFIX': 'suffix', 'DOMAIN': 'full', 'DOMAIN-KEYWORD': 'keyword',
             'host-suffix': 'suffix', 'host': 'full', 'host-keyword': 'keyword'}
    result = []
    for line in content.splitlines():
        if not line or line.startswith(('#', '[')):
            continue
        fields = line.split(',')
        result.append((kinds[fields[0]], fields[1], 'direct' if len(fields) > 2 and fields[2].lower() == 'direct' else 'proxy'))
    return result


def domain_values(values, action):
    result = []
    for value in values:
        if value.startswith('domain:'):
            result.append(('suffix', value[7:], action))
        elif value.startswith('full:'):
            result.append(('full', value[5:], action))
        else:
            result.append(('keyword', value, action))
    return result


def headless_values(group, action):
    return [(kind, value, action) for key, kind in [('domain_suffix', 'suffix'), ('domain', 'full'), ('domain_keyword', 'keyword')]
            for value in group.get(key, [])]


def decide(rules, host):
    for kind, value, action in rules:
        if (kind == 'full' and host == value or kind == 'suffix' and (host == value or host.endswith('.' + value))
                or kind == 'keyword' and value in host):
            return action
    return 'unchanged'


def mihomo_base():
    return {'mode': 'rule', 'dns': {'enable': True, 'enhanced-mode': 'fake-ip'},
            'proxies': [{'name': 'MyProxy', 'type': 'socks5', 'server': '127.0.0.1', 'port': 65534}],
            'proxy-groups': [], 'rules': ['DOMAIN,unrelated.example,DIRECT', 'MATCH,MyProxy'],
            'rule-providers': {'existing': {'type': 'inline', 'behavior': 'classical', 'payload': ['DOMAIN,other.example']}}}


class RuleTests(unittest.TestCase):
    def test_all_adapters_preserve_cases(self):
        files = render(load_rules())
        adapters = {}
        for client, path in [('shadowrocket', 'shadowrocket/douyin.module'), ('loon', 'loon/douyin.plugin'), ('qx', 'quantumult-x/local-rules.conf')]:
            adapters[client] = text_rules(files['configs/' + path])
        adapters['surge'] = text_rules(files['configs/surge/media.sgmodule']) + text_rules(files['configs/surge/api-rules.conf'])
        adapters['stash'] = text_rules('\n'.join(yaml.safe_load(files['configs/stash/douyin.stoverride'])['rules']))
        providers = yaml.safe_load(files['configs/mihomo/merge-fragment.yaml'])['rule-providers']
        adapters['mihomo'] = text_rules('\n'.join(r + ',DIRECT' for r in providers['douyin-ip-media']['payload'])) + text_rules('\n'.join(r + ',PROXY' for r in providers['douyin-ip-api']['payload']))
        for client in ('v2rayng', 'v2rayn'):
            groups = json.loads(files[f'configs/{client}/rules.json'])
            adapters[client] = [item for group in groups for item in domain_values(group['domain'], group['outboundTag'])]
        groups = json.loads(files['configs/xray/routing.fragment.json'])['routing']['rules']
        adapters['xray'] = [item for group in groups for item in domain_values(group['domain'], group['outboundTag'])]
        groups = json.loads(files['configs/sing-box/route.fragment.json'])['route']['rule_set']
        adapters['sing-box'] = headless_values(groups[0]['rules'][0], 'direct') + headless_values(groups[1]['rules'][0], 'proxy')
        adapters['passwall2'] = domain_values(files['configs/passwall2/media.domains'].splitlines(), 'direct') + domain_values(files['configs/passwall2/api.domains'].splitlines(), 'proxy')
        cases = {
            'api.amemv.com': 'proxy', 'amemv.com': 'proxy', 'ecomuser.snssdk.com': 'proxy',
            'webcast-core-m.amemv.com': 'proxy', 'api-play-zjg.amemv.com': 'proxy',
            'tos-d-x-hl.snssdk.com': 'proxy', 'v3-awememusicpgc.amemv.com': 'direct',
            'v9-awememusicpgc.amemv.com': 'direct', 'p3.douyinpic.com': 'direct',
            'v5-hl-mly-ov.zjcdn.com': 'direct', 'pull-flv-t13.douyincdn.com': 'direct',
            'unrelated.example': 'unchanged', 'example.com': 'unchanged', 'notamemv.com': 'unchanged',
            'amemv.com.example.org': 'unchanged', 'douyinpic.com.example.org': 'unchanged',
            'tos-mya2lf.vodupload.com': 'unchanged', 'location.bytedance.com': 'unchanged',
        }
        for client, rules in adapters.items():
            self.assertEqual(len(rules), 15, client)
            for host, expected in cases.items():
                with self.subTest(client=client, host=host):
                    self.assertEqual(decide(rules, host), expected)

    def test_modules_do_not_modify_other_sections(self):
        files = render(load_rules())
        for path in ('shadowrocket/douyin.module', 'surge/media.sgmodule', 'loon/douyin.plugin'):
            self.assertEqual(re.findall(r'^\[(.+)\]$', files['configs/' + path], re.M), ['Rule'])
        self.assertTrue(all(action == 'direct' for _, _, action in text_rules(files['configs/surge/media.sgmodule'])))
        override = yaml.safe_load(files['configs/stash/douyin.stoverride'])
        self.assertEqual(set(override), {'name', 'desc', 'rules'})
        self.assertNotIn('#!replace', files['configs/stash/douyin.stoverride'])

    def test_source_and_generated_are_in_sync(self):
        subprocess.run([sys.executable, str(ROOT / 'tools/build.py'), '--check'], check=True, capture_output=True)


class MergeTests(unittest.TestCase):
    def test_mihomo_preserves_original_and_is_idempotent(self):
        original = mihomo_base()
        before = copy.deepcopy(original)
        merged = merge_config(original, 'mihomo', 'MyProxy')
        self.assertEqual(original, before)
        for key in ('dns', 'proxies', 'proxy-groups', 'mode'):
            self.assertEqual(merged[key], original[key])
        self.assertEqual(merged['rules'][2:], original['rules'])
        self.assertEqual(merge_config(merged, 'mihomo', 'MyProxy'), merged)
        with self.assertRaises(ValueError):
            merge_config(original, 'mihomo', 'missing')
        original['rule-providers']['douyin-ip-media'] = {'payload': ['unexpected']}
        with self.assertRaises(ValueError):
            merge_config(original, 'mihomo', 'MyProxy')

    def test_native_client_preserves_user_rules_and_rejects_locked_ng(self):
        original = [{'id': 'local-test', 'remarks': 'My existing rule', 'domain': ['full:example.org'], 'outboundTag': 'direct', 'enabled': True}]
        for client in ('v2rayn', 'v2rayng'):
            merged = merge_config(original, client)
            self.assertEqual(merged[2:], original)
            self.assertEqual(merge_config(merged, client), merged)
        with self.assertRaises(ValueError):
            merge_config([dict(original[0], locked=True)], 'v2rayng')
        changed = merge_config(original, 'v2rayng')
        changed[0]['network'] = 'tcp'
        with self.assertRaises(ValueError):
            merge_config(changed, 'v2rayng')

    def test_singbox_preserves_preprocessing_and_rejects_unsafe_proxy(self):
        original = {'outbounds': [{'tag': 'direct', 'type': 'direct'}, {'tag': 'proxy', 'type': 'socks', 'server': '127.0.0.1', 'server_port': 65534}],
                    'dns': {'servers': []}, 'route': {'rules': [{'action': 'sniff'}, {'protocol': 'dns', 'action': 'hijack-dns'}, {'domain': ['example.org'], 'outbound': 'direct'}]}}
        merged = merge_config(original, 'sing-box')
        self.assertEqual(merged['route']['rules'][:2], original['route']['rules'][:2])
        self.assertEqual(merged['route']['rules'][4:], original['route']['rules'][2:])
        self.assertEqual(merged['dns'], original['dns'])
        self.assertEqual(merged['outbounds'], original['outbounds'])
        self.assertEqual(merge_config(merged, 'sing-box'), merged)
        with self.assertRaises(ValueError):
            merge_config(original, 'sing-box', proxy='direct')
        original['route']['rules'].reverse()
        with self.assertRaises(ValueError):
            merge_config(original, 'sing-box')

    def test_xray_preserves_settings_and_rejects_modified_owned_rule(self):
        original = {'outbounds': [{'tag': 'direct', 'protocol': 'freedom'}, {'tag': 'proxy', 'protocol': 'socks'}],
                    'inbounds': [{'tag': 'existing', 'sniffing': {'enabled': True}}],
                    'routing': {'domainStrategy': 'IPIfNonMatch', 'rules': [{'type': 'field', 'domain': ['full:example.org'], 'outboundTag': 'direct'}]}}
        merged = merge_config(original, 'xray')
        self.assertEqual(merged['routing']['domainStrategy'], 'IPIfNonMatch')
        self.assertEqual(merged['inbounds'], original['inbounds'])
        self.assertEqual(merged['routing']['rules'][2:], original['routing']['rules'])
        self.assertEqual(merge_config(merged, 'xray'), merged)
        merged['routing']['rules'][0]['outboundTag'] = 'proxy'
        with self.assertRaises(ValueError):
            merge_config(merged, 'xray')

    def test_cli_never_overwrites_input_or_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / 'original.json'
            original.write_text('[]', encoding='utf-8')
            result = subprocess.run([sys.executable, str(ROOT / 'tools/merge.py'), 'v2rayng', str(original), str(original)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(original.read_text(), '[]')


class DocumentationTests(unittest.TestCase):
    def test_local_links_resolve(self):
        for path in ROOT.rglob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
                if re.match(r'\w+://', target) or target.startswith('#'):
                    continue
                target = unquote(target.split('#')[0].split('?')[0])
                self.assertTrue((path.parent / target).exists(), f'{path.relative_to(ROOT)} -> {target}')

    def test_public_payload_has_no_private_network_artifacts(self):
        deny = [r'192\.168\.\d+\.\d+', r'100\.64\.0\.\d+',
                r'[A-Za-z]:[\\/]+Users[\\/]', r'BEGIN [A-Z ]*PRIVATE KEY',
                r'gh[pousr]_[A-Za-z0-9]{25,}', r'(?i)(?:vless|vmess|trojan|ss)://[^\s]+']
        files = [p for p in ROOT.iterdir() if p.is_file()]
        for folder in ('configs', 'source', 'docs', 'tools', 'tests', '.github'):
            files.extend(p for p in (ROOT / folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
        for path in files:
            content = path.read_text(encoding='utf-8')
            for pattern in deny:
                self.assertIsNone(re.search(pattern, content), str(path.relative_to(ROOT)))


if __name__ == '__main__':
    unittest.main()
