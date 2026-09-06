# Surge

**需要“媒体直连模块 + API 代理规则”两部分。** Surge 官方限制模块规则只能使用内置直连/拒绝策略，不能在模块里指定代理组，因此不提供名不副实的全自动代理模块。

1. 添加并启用 [media.sgmodule](../../configs/surge/media.sgmodule)。本地文件可放到配置目录；也可通过下方固定版本的 Raw URL 安装模块。
2. 打开 [api-rules.conf](../../configs/surge/api-rules.conf)，把两处 `Douyin-IP-Proxy` 替换成你现有的固定地区节点或策略组名称。
3. 将这两行加到现有 `[Rule]` 顶部。模块注入的媒体例外必须在它们之前；最终顺序是媒体 → API → 普通国内/兜底规则。
4. 在配置检查通过后重连、重开抖音，验证公开属地与播放。

托管配置不可编辑时，先复制成自己的配置副本再操作；该副本的手动改动不会自动跟随原订阅更新。不要为了省事把整站设成直连。

## 已有规则集工作流

另提供不含策略的 [media.list](../../configs/surge/media.list) 和 [api.list](../../configs/surge/api.list)，可按 Surge 的规则集机制绑定 `DIRECT` 和你的代理策略，仍然媒体在前。这与上述模块方案二选一。

本地初次安装推荐上面的两条 API 规则，不需要等待仓库上线。未来改成远程规则集后，删除重复的手动行。

撤销：同时停用媒体模块并删除两条 API 规则；若使用规则集，则移除本项目两个规则集引用。不要只停用媒体模块而忘记 API 规则，否则媒体例外可能被 API 大域代理覆盖。

参考：[Surge 官方模块说明](https://manual.nssurge.com/profile/module.html)。仅完成文档与规则适配，未进行 Surge 真机验收。

## 固定版本下载地址

以下链接固定到 `v0.1.0`。复制链接地址导入；升级需主动切换版本。

- [媒体模块地址（仍须添加 API 代理规则）](https://raw.githubusercontent.com/cazi-cc/douyin-ip/v0.1.0/configs/surge/media.sgmodule)
