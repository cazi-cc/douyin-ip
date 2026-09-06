"""Use downloaded official cores in check-only mode with synthetic loopback fixtures."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

import yaml

from build import ROOT
from merge import merge_config


def run(command, cwd):
    result = subprocess.run([str(x) for x in command], cwd=cwd, capture_output=True, encoding='utf-8', errors='replace', timeout=45)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description='仅原生配置检查，不启动代理服务、不接管网络。')
    parser.add_argument('--mihomo', type=Path, required=True)
    parser.add_argument('--xray', type=Path, required=True)
    parser.add_argument('--sing-box', type=Path, required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='douyin-ip-core-check-') as directory:
        work = Path(directory)
        base = {'mode': 'rule', 'proxies': [{'name': 'TestProxy', 'type': 'socks5', 'server': '127.0.0.1', 'port': 65534}], 'rules': ['MATCH,TestProxy']}
        mihomo = work / 'mihomo.yaml'
        mihomo.write_text(yaml.safe_dump(merge_config(base, 'mihomo', 'TestProxy'), allow_unicode=True), encoding='utf-8')
        run([args.mihomo, '-t', '-d', work, '-f', mihomo], work)
        xray = work / 'xray.json'
        base = {'log': {'loglevel': 'warning'}, 'inbounds': [], 'outbounds': [
            {'tag': 'proxy', 'protocol': 'socks', 'settings': {'servers': [{'address': '127.0.0.1', 'port': 65534}]}},
            {'tag': 'direct', 'protocol': 'freedom', 'settings': {}}]}
        xray.write_text(json.dumps(merge_config(base, 'xray')), encoding='utf-8')
        run([args.xray, 'run', '-test', '-c', xray], work)
        singbox = work / 'sing-box.json'
        base = {'log': {'level': 'warn'}, 'outbounds': [
            {'tag': 'proxy', 'type': 'socks', 'server': '127.0.0.1', 'server_port': 65534},
            {'tag': 'direct', 'type': 'direct'}], 'route': {'rules': [{'action': 'sniff'}], 'final': 'proxy'}}
        singbox.write_text(json.dumps(merge_config(base, 'sing-box')), encoding='utf-8')
        run([args.sing_box, 'check', '-c', singbox], work)
        for name in ('media', 'api'):
            run([args.sing_box, 'rule-set', 'compile', '--output', work / (name + '.srs'), ROOT / f'configs/sing-box/{name}.json'], work)
        versions = {
            'mihomo': run([args.mihomo, '-v'], work).splitlines()[0],
            'xray': run([args.xray, 'version'], work).splitlines()[0],
            'sing-box': run([args.sing_box, 'version'], work).splitlines()[0],
        }
        print(json.dumps({'result': 'passed', 'versions': versions, 'checks': ['mihomo config', 'xray config', 'sing-box config', 'sing-box source rule-sets']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
