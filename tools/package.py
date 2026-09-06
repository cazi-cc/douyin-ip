"""Create an offline archive from explicitly allowed public project files."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from build import ROOT, load_rules

ROOT_FILES = {'README.md', 'LICENSE', 'CHANGELOG.md', 'CONTRIBUTING.md',
              'requirements-dev.txt', '.gitignore', '.gitattributes'}
FOLDERS = {'configs', 'source', 'docs', 'tools', 'tests', '.github'}
SUFFIXES = {'.md', '.json', '.yaml', '.yml', '.py', '.js', '.list', '.conf', '.domains', '.module', '.sgmodule', '.plugin', '.stoverride'}


def payload():
    files = []
    for path in ROOT.rglob('*'):
        relative = path.relative_to(ROOT)
        if any(part in {'__pycache__', '.git', '.venv', 'local', '.private'} for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError('发布目录不得含符号链接：' + relative.as_posix())
        if not path.is_file():
            continue
        if relative.as_posix() in ROOT_FILES or relative.parts[0] in FOLDERS and path.suffix in SUFFIXES:
            files.append(path)
        else:
            raise ValueError('未列入公开文件类型，请审查：' + relative.as_posix())
    return sorted(files)


def main():
    parser = argparse.ArgumentParser(description='只生成本地 ZIP 和校验清单，不发布。')
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.output.resolve().is_relative_to(ROOT):
        parser.error('请将交付 ZIP 放在项目目录之外。')
    manifest_path = args.output.with_suffix('.manifest.json')
    if args.output.exists() or manifest_path.exists():
        parser.error('输出已存在，请选择新的文件名。')
    files = payload()
    data = load_rules()
    year, month, day = map(int, data['verified_on'].split('-'))
    manifest = {'version': data['version'], 'files': {}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            relative = path.relative_to(ROOT).as_posix()
            content = path.read_bytes()
            info = zipfile.ZipInfo('douyin-ip/' + relative, (year, month, day, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
            manifest['files'][relative] = hashlib.sha256(content).hexdigest()
    with zipfile.ZipFile(args.output) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('ZIP 完整性检查失败')
    manifest['archive_sha256'] = hashlib.sha256(args.output.read_bytes()).hexdigest()
    with manifest_path.open('x', encoding='utf-8') as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2)
    print(json.dumps({'files': len(files), 'bytes': args.output.stat().st_size,
                      'sha256': manifest['archive_sha256']}, indent=2))


if __name__ == '__main__':
    main()
