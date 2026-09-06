# Shadowrocket

适合已经有可用节点的 iPhone / iPad 用户。规则策略有维护者约三个月使用反馈；当前导出模块仍应按下面步骤核验。

## 推荐：模块

文件：[douyin.module](../../configs/shadowrocket/douyin.module)。在配置的“模块”管理中添加该模块，启用后确认它的规则位于普通国内直连和全站分流之前。可通过下方固定版本的原始文件 URL 添加；本地导入入口因版本而异，不能导入文件时使用下方方法。

模块中 `PROXY` 使用 Shadowrocket 当前代理选择。先选好一个目标地区节点，再使用规则模式。模块包含媒体直连与 API 代理，代理规则保留 `force-remote-dns`。

## 本地直接试用

复制当前配置作为备份，编辑正在使用的副本，把 [rules.conf](../../configs/shadowrocket/rules.conf) 的有效规则行添加到现有 `[Rule]` **最前面**。不要新增第二个 `[Rule]` 段，也不要删除原有规则。此文件不是完整订阅，不要作为订阅 URL 导入。

模块方式与手动规则方式选一种，避免重复。托管配置可能在更新时覆盖手动编辑，此时优先模块方式。

## 验证与撤销

重连客户端并重开抖音。连接记录中 `api.amemv.com` 等 API 应走代理；`v*-awememusicpgc.amemv.com` 应被更靠前的媒体例外直连。以你实际使用中出现的主机为准，不要求每次都出现这些示例。

确认视频/直播流畅，再检查公开属地。无须启用 HTTPS 解密或任何重写脚本。

撤销时停用该模块，或删除本文件添加的规则后重连；不动你的节点和其他模块。域名、DNS 与不明 IP 的限制见[技术说明](../technical.md)。

## 固定版本下载地址

以下链接固定到 `v0.1.0`。复制链接地址导入；升级需主动切换版本。

- [模块地址](https://raw.githubusercontent.com/cazi-cc/douyin-ip/v0.1.0/configs/shadowrocket/douyin.module)
