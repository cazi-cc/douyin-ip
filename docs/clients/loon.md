# Loon

文件：[douyin.plugin](../../configs/loon/douyin.plugin)。

1. 在插件管理中添加本插件。使用下方固定版本的 Raw URL；本地版本支持导入文件时可直接导入。
2. 为插件的 `PROXY` 指定你现有的代理节点或策略组，选好目标地区。不要留空：Loon 文档说明未指定时可能使用全局第一个节点，并不一定是你想要的地区。
3. 启用插件，检查生成规则的最终顺序：本项目媒体直连 → API 代理 → 其他国内/兜底规则。
4. 重连 Loon、重开抖音，验证播放和公开属地。

如果当前版本没有本地插件入口，复制插件 `[Rule]` 中的规则到当前配置副本的 `[Rule]` 顶部，并将其中 `PROXY` 改成已有的目标策略名。手动规则与插件只选一种。

不添加 DNS、重写、脚本或 MITM 设置。Loon 没有沿用 Shadowrocket 的 `force-remote-dns` 参数；不要把另一软件的附加参数粘进来。确认现有 DNS/域名映射可以识别 API，且未被跳过代理设置排除。

撤销：停用该插件，或删除手动添加的规则，然后重连。

参考：[Loon 官方插件手册](https://github.com/Loon0x00/LoonManual/blob/master/docs/cn/plugin.md)。本适配未宣称已有 Loon 真机验收。

## 固定版本下载地址

以下链接固定到 `v0.1.0`。复制链接地址导入；升级需主动切换版本。

- [插件地址](https://raw.githubusercontent.com/cazi-cc/douyin-ip/v0.1.0/configs/loon/douyin.plugin)
