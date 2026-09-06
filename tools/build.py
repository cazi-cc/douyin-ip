"""Generate client adapters from one reviewed rule source; no network or deployment."""
import argparse
import hashlib
import json
from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = 'Douyin-IP-Proxy'
KINDS = {'suffix': 'DOMAIN-SUFFIX', 'full': 'DOMAIN', 'keyword': 'DOMAIN-KEYWORD'}
QX_KINDS = {'suffix': 'host-suffix', 'full': 'host', 'keyword': 'host-keyword'}
XRAY_KINDS = {'suffix': 'domain:', 'full': 'full:', 'keyword': ''}


def load_rules():
    data = json.loads((ROOT / 'source/rules.json').read_text(encoding='utf-8'))
    assert data['schema'] == 1
    for group in ('media', 'api'):
        assert data[group]
        seen = set()
        for rule in data[group]:
            assert set(rule) == {'type', 'value'} and rule['type'] in KINDS
            assert re.fullmatch(r'[a-z0-9][a-z0-9.-]*', rule['value'])
            key = (rule['type'], rule['value'])
            assert key not in seen
            seen.add(key)
    return data


def validate_policy(policy):
    if not policy.strip() or policy != policy.strip() or any(c in policy for c in ',\r\n[]#'):
        raise ValueError('策略名不能为空，不能带逗号、换行、方括号或 #。')
    if policy.upper() in {'DIRECT', 'REJECT', 'BLOCK', 'PASS', 'GLOBAL', 'COMPATIBLE'}:
        raise ValueError('API 必须选择已有代理节点或代理策略组，不能使用内置直连/兜底策略。')
    return policy


def lines(rules, policy=None, qx=False):
    kinds = QX_KINDS if qx else KINDS
    return [','.join([kinds[r['type']], r['value']] + ([policy] if policy else [])) for r in rules]


def xdomains(rules):
    return [XRAY_KINDS[r['type']] + r['value'] for r in rules]


def headless(rules):
    fields = {'suffix': 'domain_suffix', 'full': 'domain', 'keyword': 'domain_keyword'}
    result = {}
    for rule in rules:
        result.setdefault(fields[rule['type']], []).append(rule['value'])
    return result


def dumps(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def native_rules(data):
    return [
        {'remarks': 'Douyin-IP / 媒体直连', 'outboundTag': 'direct', 'domain': xdomains(data['media']), 'enabled': True},
        {'remarks': 'Douyin-IP / 属地 API', 'outboundTag': 'proxy', 'domain': xdomains(data['api']), 'enabled': True},
    ]


def render(data, policy=DEFAULT_POLICY):
    validate_policy(policy)
    media, api = data['media'], data['api']
    files = {}

    def text(path, content):
        files['configs/' + path] = content.rstrip() + '\n'

    def j(path, value):
        text(path, dumps(value))

    def y(path, value):
        text(path, yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=120))

    sr = lines(media, 'DIRECT') + [line + ',force-remote-dns' for line in lines(api, 'PROXY')]
    text('shadowrocket/douyin.module', '#!name=抖音海外 IP 属地精确分流\n#!desc=关键接口代理，媒体优先直连；使用当前代理策略。\n\n[Rule]\n' + '\n'.join(sr))
    text('shadowrocket/rules.conf', '# 添加到现有 [Rule] 顶部，不是完整配置。\n' + '\n'.join(sr))
    text('surge/media.sgmodule', '#!name=抖音媒体直连\n#!desc=必须配合 API 代理规则使用；此模块单独使用不改变属地。\n\n[Rule]\n' + '\n'.join(lines(media, 'DIRECT')))
    text('surge/api-rules.conf', '# 放在现有 [Rule] 顶部；先启用 media.sgmodule，再选择已有代理策略。\n' + '\n'.join(lines(api, policy)))
    text('surge/api.list', '\n'.join(lines(api)))
    text('surge/media.list', '\n'.join(lines(media)))
    text('loon/douyin.plugin', '#!name=抖音海外 IP 属地精确分流\n#!desc=安装后必须为插件 PROXY 指定已有代理策略。\n\n[Rule]\n' + '\n'.join(lines(media, 'DIRECT') + lines(api, 'PROXY')))
    text('quantumult-x/media.list', '\n'.join(lines(media, 'direct', qx=True)))
    text('quantumult-x/api.list', '\n'.join(lines(api, 'proxy', qx=True)))
    text('quantumult-x/local-rules.conf', '# 添加到 [filter_local] 顶部，不是完整配置。\n' + '\n'.join(lines(media, 'direct', qx=True) + lines(api, policy, qx=True)))
    y('stash/douyin.stoverride', {'name': '抖音海外 IP 属地精确分流', 'desc': '只前插规则；API 目标需替换成已有代理策略名。', 'rules': lines(media, 'DIRECT') + lines(api, policy)})
    for name in ('media', 'api'):
        y(f'mihomo/{name}.yaml', {'payload': lines(data[name])})
    mihomo = {
        'rule-providers': {f'douyin-ip-{name}': {'type': 'inline', 'behavior': 'classical', 'payload': lines(data[name])} for name in ('media', 'api')},
        'rules': ['RULE-SET,douyin-ip-media,DIRECT', f'RULE-SET,douyin-ip-api,{policy}'],
    }
    y('mihomo/merge-fragment.yaml', mihomo)
    js = (ROOT / 'tools/templates/mihomo.js').read_text(encoding='utf-8')
    text('mihomo/clash-verge.js', js.replace('__POLICY__', json.dumps(policy, ensure_ascii=False)).replace('__PATCH__', json.dumps(mihomo, ensure_ascii=False, indent=2)))
    for name in ('v2rayng', 'v2rayn'):
        j(f'{name}/rules.json', native_rules(data))
    j('xray/routing.fragment.json', {'routing': {'rules': [
        {'type': 'field', 'ruleTag': 'douyin-ip-media', 'domain': xdomains(media), 'outboundTag': 'direct'},
        {'type': 'field', 'ruleTag': 'douyin-ip-api', 'domain': xdomains(api), 'outboundTag': 'proxy'},
    ]}})
    for name in ('media', 'api'):
        j(f'sing-box/{name}.json', {'version': 1, 'rules': [headless(data[name])]})
    j('sing-box/route.fragment.json', {'route': {
        'rule_set': [{'type': 'inline', 'tag': f'douyin-ip-{name}', 'rules': [headless(data[name])]} for name in ('media', 'api')],
        'rules': [
            {'rule_set': 'douyin-ip-media', 'action': 'route', 'outbound': 'direct'},
            {'rule_set': 'douyin-ip-api', 'action': 'route', 'outbound': 'proxy'},
        ],
    }})
    for name in ('media', 'api'):
        text(f'passwall2/{name}.domains', '\n'.join(xdomains(data[name])))
    return files


def main():
    parser = argparse.ArgumentParser(description='本地生成各客户端规则，不读取节点、不联网。')
    parser.add_argument('--output', type=Path, default=ROOT)
    parser.add_argument('--policy', default=DEFAULT_POLICY, help='Surge / Stash / QX / Mihomo 的已有代理策略名')
    parser.add_argument('--check', action='store_true', help='只检查生成文件是否与规则源一致')
    args = parser.parse_args()
    data = load_rules()
    files = render(data, args.policy)
    manifest = {'version': data['version'], 'policy': args.policy,
                'files': {path: hashlib.sha256(content.encode()).hexdigest() for path, content in sorted(files.items())}}
    files['configs/manifest.json'] = dumps(manifest)
    stale = []
    for path, content in files.items():
        target = args.output / path
        if args.check:
            if not target.is_file() or target.read_bytes() != content.encode():
                stale.append(path)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content.encode())
    if stale:
        raise SystemExit('生成文件需要更新：' + ', '.join(stale))
    print(('已核对' if args.check else '已生成') + f' {len(files)} 个文件；未连接路由器或 GitHub。')


if __name__ == '__main__':
    main()
