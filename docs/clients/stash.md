# Stash

文件：[douyin.stoverride](../../configs/stash/douyin.stoverride)。只包含名称、说明和规则列表，不定义节点、代理组、DNS 或其他网络设置。

1. 编辑此文件，把两处 `Douyin-IP-Proxy` 改成当前配置中已存在的代理节点或策略组名。
2. 在 Stash 的覆写管理中添加这份文件，启用到当前配置。也可使用下方 Raw URL 获取文件，但仍需要正确设置目标策略名。
3. 检查最终规则顺序：媒体例外 → API 代理 → 原有规则。多个覆写文件同时启用时，后续覆写也可能插入规则，应以最终结果为准。
4. 重连，重新打开抖音，验证播放和公开属地。

Stash 官方的数组合并语义是**将覆写数组插到原数组前面**。本文件不使用 `#!replace`，不覆盖你原来的整个规则列表。

无法编辑远程覆写时，使用本地副本；维护者也可按[构建说明](../development.md)用 `--policy` 生成适合自己的文件，个人策略文件不要提交回本项目。

撤销：停用这份覆写并重连。原配置无需手工恢复。

参考：[Stash 官方覆写说明](https://stash.wiki/configuration/override)。已核对格式及合并语义，未进行 Stash 真机验收。

## 固定版本下载地址

以下链接固定到 `v0.1.0`。复制链接地址导入；升级需主动切换版本。

- [覆写文件地址（须设置已有代理策略名）](https://raw.githubusercontent.com/cazi-cc/douyin-ip/v0.1.0/configs/stash/douyin.stoverride)
