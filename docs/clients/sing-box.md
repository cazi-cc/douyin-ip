# sing-box

面向使用较新 sing-box 原生 JSON 的用户，建议 1.11 或更高。不同图形客户端对扩展的支持不同，不能把 JSON 片段直接当成完整订阅导入。已有 Hiddify 等包装客户端的专属格式不在这个原生适配的承诺范围。

文件：[route.fragment.json](../../configs/sing-box/route.fragment.json)，以及可复用的 [media.json](../../configs/sing-box/media.json)、[api.json](../../configs/sing-box/api.json) 规则集。

## 推荐：在导出副本上合并

```sh
python -m pip install -r requirements-dev.txt
python tools/merge.py sing-box local/original.json local/with-douyin.json --proxy-tag proxy --direct-tag direct
sing-box check -c local/with-douyin.json
```

将 `proxy` / `direct` 替换成原配置实际的出站标签。工具仅增加两组内联规则集及路由，不下载节点、不修改原文件、不直接导入手机。

如果你使用 TUN，原配置必须先获得域名：保留前置 `action: sniff`、DNS 劫持/映射等必要规则。合并工具会保留列表开头的 `sniff`、`resolve`、`hijack-dns` 处理，然后插入媒体与 API 路由；遇到嗅探在其他位置的复杂配置会拒绝自动合并。

如果原配置完全没有嗅探/域名映射，单纯格式检查通过也不意味着 App 的 IP 连接会匹配域名规则。先按你所用版本官方文档处理入站，不能靠猜域名所属 IP 来补一个大网段。

## 手动或远程规则集

`route.fragment.json` 使用内联规则集，避免本地阶段依赖下载。手动合并时把 `route.rule_set` 按标签追加，把 `route.rules` 放到前置处理之后、普通国内分流之前，媒体先于 API；不要覆盖原数组。

`media.json` / `api.json` 是 source 格式的 headless rule-set，不含出站动作。可换成 local/remote 引用后，仍在 `route.rules` 中绑定直连和代理。它们使用旧版兼容的规则集 schema 1，只有域名字段；这不表示新路由片段也支持 sing-box 1.8。

DNS 路由和代理出站的域名解析沿用原配置。当前接口的 DNS 必须可用；若目标服务器不支持 IPv6，要在对应代理 DNS/出站处理，不能全局关闭家庭 IPv6 来代替分流。

验证：先 `sing-box check`，再导入配置副本、重连、重开抖音，检查实际路由和公开属地。撤销时切回原配置；手动用户移除两组 `douyin-ip-*` 规则集及引用。

参考：[规则集](https://sing-box.sagernet.org/configuration/rule-set/)、[路由规则](https://sing-box.sagernet.org/configuration/route/rule/)。原生核心检查不等于各手机客户端真机验收。
