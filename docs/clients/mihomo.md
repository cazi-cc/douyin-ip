# Mihomo：Clash Meta for Android / FlClash / Clash Verge Rev

这几款客户端使用的界面不同，不能把“核心支持规则集”当成“每个 App 都支持同一种覆写”。本项目同时提供[两个规则集](../../configs/mihomo)、[增量片段](../../configs/mihomo/merge-fragment.yaml)和 [Clash Verge Rev 扩展脚本](../../configs/mihomo/clash-verge.js)。

目标是支持 `type: inline`、`behavior: classical` 的较新 Mihomo 核心；旧版 Clash 不在此适配范围。

## Clash Verge Rev：优先扩展脚本

1. 复制 `clash-verge.js`，把顶部 `TARGET` 改成原配置中已存在的代理节点或策略组名。
2. 在目标订阅的“编辑脚本/扩展脚本”入口添加；如果你已经有脚本，不直接覆盖它，应把本脚本逻辑整合到原 `main` 的末尾，或使用独立配置扩展入口。
3. 保存并检查最终配置。脚本只添加两个命名空间独立的规则集和两条置顶规则，不改变节点、DNS、TUN、端口和其他配置数据。
4. 在规则模式下选择稳定的目标节点，再验证抖音。

脚本可重复应用，不重复叠加本项目规则；找不到策略名、已有同名资源内容不同会报错，避免悄悄误用其他策略。

## Clash Meta for Android / FlClash

先查看你的版本是否支持保留原数组的“前插规则/配置扩展”：

- 如果支持，使用 `merge-fragment.yaml`，替换 API 目标名，将它的 `rule-providers` 合入原字典、`rules` **前插**到原列表。不要选择覆盖整个 `rules` 数组。
- 如果扩展功能或数组行为不明确，导出原配置，在电脑上用下面的离线工具生成副本。它保留原有配置数据，不直接操作客户端。

```sh
python -m pip install -r requirements-dev.txt
python tools/merge.py mihomo local/original.yaml local/with-douyin.yaml --policy "已有代理组名"
```

将新文件作为**新的本地配置副本**导入。不要上传 `local/` 下包含节点的个人文件。导出的静态副本不会自动同步原托管配置更新；长期使用优先选择客户端原生扩展，或更新订阅后重新合并。

## 手动合并

片段使用内联规则集，无需先发布到 GitHub，不依赖远程下载。也可以自行把 `media.yaml`、`api.yaml` 接到现有 `rule-providers` 机制，使用 `behavior: classical`；关键词规则不能塞进仅支持后缀的纯域名规则集。

确保 Fake-IP/域名映射或适当嗅探可以把手机连接关联到域名。若原配置关闭嗅探、把抖音排除在 TUN 外，单独添加域名规则不能解决。此包不擅自覆盖你的 DNS/嗅探设置；检查方法见[技术文档](../technical.md)。

撤销：停用本项目扩展；合并副本用户切回原配置。手动合并用户删除两个 `douyin-ip-*` 规则集及它们的两条引用。

参考：[Mihomo 规则集](https://wiki.metacubex.one/config/rule-providers/)、[Clash Verge Rev 脚本](https://www.clashverge.dev/guide/script.html)。核心检查和数据合并测试不等于三个客户端都已做手机验收。
