# 本地构建与维护

运行环境：Python 3.10+；开发检查使用 PyYAML；脚本测试另需 Node.js 18+。普通使用者直接取 `configs/` 文件，不需要安装开发依赖。

```sh
python -m pip install -r requirements-dev.txt
python tools/build.py
python tools/build.py --check
python -m unittest discover -s tests -v
node tests/test_mihomo.js
```

`source/rules.json` 是唯一规则源；修改后必须重新生成，不能只改某个客户端的产物。`configs/manifest.json` 保存每份生成内容的 SHA-256，用于核对交付文件。

## 给自己的策略名生成副本

```sh
python tools/build.py --policy "已有代理组名称" --output local/personal
```

这会生成 Surge、Stash、QX 和 Mihomo 使用的目标策略名。Shadowrocket/Loon 仍按软件的 PROXY 绑定方式选择节点；Xray 系使用已有出站标签，不能把界面节点名直接套进去。

不要直接修改项目默认文件来存放私人策略名。`local/` 已忽略，里面的个人配置不能加入公开发布包。

## 离线合并工具

`tools/merge.py` 只读取明确指定的导出文件，将合并结果写到一个尚不存在的新文件。不会覆盖原文件，不登录客户端，不连接路由器，不更新系统代理。

支持 `mihomo`、`v2rayng`、`v2rayn`、`sing-box`、`xray`。除本项目新增规则/规则集外保留已有配置数据；YAML 注释和排版不承诺保留，托管订阅优先使用客户端扩展。所有输入输出可能含私人节点，留在 `local/` 或自己的私有目录。

工具拒绝：不存在的目标、直连作为 API 出站、冲突的项目命名空间、v2rayNG 锁定规则自动合并，以及无法确定插入点的 sing-box 嗅探配置。遇到拒绝应检查当前配置后手动处理，不建议绕过校验。

## 本地交付包

```sh
python tools/package.py ../douyin-ip-local-0.1.0.zip
```

工具只打包明确允许的源码、配置和文档，并生成独立文件哈希清单；忽略 `local/`、私有目录、Python 缓存和 Git 元数据，拒绝符号链接及未知文件类型。不会调用 Git 或上传服务，也不会覆盖已有 ZIP。打包前仍需执行内容扫描和测试，允许的文本类型不能自动证明其中没有私人数据。

## 原生核心检查

从各项目官方发布页取得二进制后，运行：

```sh
python tools/check_cores.py --mihomo /path/to/mihomo --xray /path/to/xray --sing-box /path/to/sing-box
```

Windows 对应 `.exe` 路径。工具使用临时目录和纯回环的合成配置，仅执行配置检查与规则集编译，不运行代理服务。测试用二进制不进入本仓库，也不作为用户依赖分发。

## GitHub 发布边界

公开仓库为 [cazi-cc/douyin-ip](https://github.com/cazi-cc/douyin-ip)。客户端教程的 Raw 链接固定到 `v0.1.0`，避免主分支更新自动影响已有配置；升级时先阅读更新记录，再主动切换版本。在线资源可下载不等于客户端已完成真机验收，实测范围见[验证记录](validation.md)。

`.github/workflows/check.yml` 仅在将来推送后执行本地构建/测试，不包含发布、部署、自动创建 Release 或上传私人文件的步骤。

正式发布前检查：公开文件清单、秘密/地址扫描、全部本地链接、生成一致性、README 的实测表述，以及平台实测范围。只有维护者明确授权后才创建公开仓库、推送或发布 Release。
