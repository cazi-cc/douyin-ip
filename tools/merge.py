"""Merge into an exported COPY, preserving unrelated settings. Never deploys."""
import argparse
import copy
import json
from pathlib import Path

import yaml

from build import DEFAULT_POLICY, load_rules, native_rules, render, validate_policy


def owned_prefix(existing, additions, key):
    expected = {item[key]: item for item in additions}
    rest = []
    for item in existing:
        name = item.get(key)
        if name in expected:
            extra = {k: v for k, v in item.items() if k not in expected[name] and k != 'id'
                     and v not in (None, '', [], {}, False)}
            if extra or any(item.get(k) != v for k, v in expected[name].items()):
                raise ValueError(f'已有同名项目规则被修改，请先处理冲突：{name}')
        else:
            rest.append(item)
    return additions + rest


def require_outbounds(config, proxy, direct, client):
    outbounds = {o['tag']: o for o in config.get('outbounds', []) if 'tag' in o}
    for tag in (proxy, direct):
        if tag not in outbounds:
            raise ValueError(f'原配置不存在出站 {tag}；请用参数指定实际标签。')
    field = 'protocol' if client == 'xray' else 'type'
    if proxy == direct or outbounds[proxy].get(field) in {'direct', 'freedom', 'blackhole', 'block', 'dns'}:
        raise ValueError('API 出站必须为已有代理，不能使用直连/拒绝/DNS 出站。')
    if outbounds[direct].get(field) != ('freedom' if client == 'xray' else 'direct'):
        raise ValueError('媒体出站必须为实际直连出站。')


def merge_config(base, client, policy=DEFAULT_POLICY, proxy='proxy', direct='direct'):
    data = load_rules()
    result = copy.deepcopy(base)
    if client in ('v2rayng', 'v2rayn'):
        if not isinstance(result, list) or not all(isinstance(item, dict) for item in result):
            raise ValueError('需要从客户端导出的路由规则 JSON 数组，不是完整节点配置。')
        if client == 'v2rayng' and any(item.get('locked') for item in result):
            raise ValueError('v2rayNG 会额外保留锁定规则；请先备份并解锁，再重新导出，避免重复和优先级冲突。')
        return owned_prefix(result, native_rules(data), 'remarks')
    if not isinstance(result, dict):
        raise ValueError('需要完整配置对象。')
    generated = render(data, policy)
    if client == 'mihomo':
        validate_policy(policy)
        names = {p['name'] for p in result.get('proxies', []) + result.get('proxy-groups', [])}
        if policy not in names:
            raise ValueError('原配置中找不到目标代理节点/组：' + policy)
        patch = yaml.safe_load(generated['configs/mihomo/merge-fragment.yaml'])
        providers = result.setdefault('rule-providers', {})
        for name, provider in patch['rule-providers'].items():
            if name in providers and providers[name] != provider:
                raise ValueError('同名规则集内容不同：' + name)
            providers[name] = provider
        prefix = patch['rules']
        old = result.get('rules', [])
        for rule in old:
            if rule.startswith(('RULE-SET,douyin-ip-media,', 'RULE-SET,douyin-ip-api,')) and rule not in prefix:
                raise ValueError('已有项目规则使用不同策略，请先停用或移除旧项目规则。')
        result['rules'] = prefix + [r for r in old if r not in prefix]
    elif client == 'xray':
        require_outbounds(result, proxy, direct, client)
        patch = json.loads(generated['configs/xray/routing.fragment.json'])['routing']['rules']
        patch[0]['outboundTag'], patch[1]['outboundTag'] = direct, proxy
        routing = result.setdefault('routing', {})
        routing['rules'] = owned_prefix(routing.get('rules', []), patch, 'ruleTag')
    elif client == 'sing-box':
        require_outbounds(result, proxy, direct, client)
        patch = json.loads(generated['configs/sing-box/route.fragment.json'])['route']
        patch['rules'][0]['outbound'], patch['rules'][1]['outbound'] = direct, proxy
        route = result.setdefault('route', {})
        route['rule_set'] = owned_prefix(route.get('rule_set', []), patch['rule_set'], 'tag')
        old = route.get('rules', [])
        cleaned = []
        for rule in old:
            names = rule.get('rule_set', [])
            names = [names] if isinstance(names, str) else names
            if any(name in ('douyin-ip-media', 'douyin-ip-api') for name in names):
                if rule not in patch['rules']:
                    raise ValueError('已有项目路由内容不同，请先处理冲突。')
            else:
                cleaned.append(rule)
        # Sniffing/DNS preprocessing must run before domain routing in a TUN.
        position = 0
        while position < len(cleaned) and cleaned[position].get('action') in {'sniff', 'resolve', 'hijack-dns'}:
            position += 1
        if any(r.get('action') == 'sniff' for r in cleaned[position:]):
            raise ValueError('嗅探规则不在前处理区，不能自动确定安全插入点；请按教程手动合并。')
        route['rules'] = cleaned[:position] + patch['rules'] + cleaned[position:]
    else:
        raise ValueError('不支持的客户端')
    return result


def main():
    parser = argparse.ArgumentParser(description='离线合并到新文件；不覆盖原文件、不连接客户端。')
    parser.add_argument('client', choices=['mihomo', 'v2rayng', 'v2rayn', 'sing-box', 'xray'])
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--policy', default=DEFAULT_POLICY)
    parser.add_argument('--proxy-tag', default='proxy')
    parser.add_argument('--direct-tag', default='direct')
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve() or args.output.exists():
        parser.error('输出必须是一个尚不存在的新文件，不能覆盖原配置。')
    raw = args.input.read_text(encoding='utf-8-sig')
    base = yaml.safe_load(raw) if args.client == 'mihomo' else json.loads(raw)
    result = merge_config(base, args.client, args.policy, args.proxy_tag, args.direct_tag)
    output = yaml.safe_dump(result, allow_unicode=True, sort_keys=False) if args.client == 'mihomo' else json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(output)
    print('已生成新文件。原配置未改动；请检查差异后手动导入。')
    if args.client == 'mihomo':
        print('YAML 注释/排版可能变化，原有配置数据保留；订阅用户优先使用客户端扩展。')


if __name__ == '__main__':
    main()
