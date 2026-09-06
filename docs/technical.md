# 技术说明：先保护关键 API，再让媒体直连

## 规则边界

规则源为 [source/rules.json](../source/rules.json)。所有客户端由同一份规则生成：13 条媒体例外先匹配，随后 `snssdk.com`、`amemv.com` 两个 API 后缀代理，再进入使用者自己的规则。

这两个后缀并非两个专用“查 IP 网址”，而是包含多种业务的 API 家族。我们没有解密 HTTPS，也没有证明哪个单独路径决定公开属地，因此保留较宽的 API 兜底，并只直连已有实测支持的媒体例外。

`awememusicpgc` 是原规则的关键词匹配，不限于某个后缀，范围比精确主机更宽；当前为保持已验证语义而保留。`v9-awememusicpgc.amemv.com` 虽已被该关键词包含，也保留为原有精确例外。

不将所有字节跳动流量代理，不按整个 CDN IP 段放行，也没有放行实验中的 `api-play-*`、`tos-*` 等候选。名称、一次成功、地区暂未刷新都不是端点无关属地的充分证据。

## 为什么顺序最重要

同一主域可能同时有 API 和媒体，多个域名也可能共享同一 IP：

1. 先判断媒体例外，例如音乐资源 `v3-awememusicpgc.amemv.com`。
2. 再判断 `amemv.com` / `snssdk.com` API 代理。
3. 最后才交给一般国内直连、GeoIP 或默认策略。

PassWall2 某些加速设置会把 IP 放进内核提前直连集合。这样流量根本没有进入 Xray，即使 UI 中规则顺序正确也无效。维护者的实际故障由此产生；关闭相应分流节点的 GeoIP 提前解析、直连 DNS 写 IPSet 后，手机 API 才命中代理规则。

## DNS、嗅探与 IP 缓存

App 不一定始终向系统 DNS 查询，它可能使用缓存、HTTPDNS、DoH 或已有连接。域名规则需要 Fake-IP 映射、HTTP Host、TLS SNI 或 QUIC 嗅探等元数据。把 DNS 指向代理并不自动代表每条业务连接已走代理。

- Shadowrocket 的原规则使用 `force-remote-dns`，该参数没有机械复制到其他客户端。
- 各软件的 Fake-IP、真实 IP、远端解析与 DNS 规则含义不同，先保留用户已工作的配置，再检查 API 和媒体的实际路径。
- Xray `routeOnly` 只用嗅探域名做路由，保留原目的 IP。它不是可以无条件开启的通用加速开关；远端可能无法连接原 IPv6 目标或国内调度地址。
- 加密 ClientHello、无法识别的协议、裸 IP 等可能无法提供可用域名。未知连接不能只因落在中国 IP 就认定不影响属地。
- 连接复用和 App 缓存会让新规则无法影响旧连接。重连客户端并重开 App，避免用旧连接验收。

本项目不启用 HTTPS 中间人解密、不修改请求内容、不阻断全网 UDP，也不批量清空连接跟踪。

## IPv6 与最终出口

IPv4 成功不能替代 IPv6 验收；允许 IPv6 的网络需保证相应 TCP/UDP 都进入路由判断。反过来，手机来源是 IPv6 也不说明海外服务器最终以 IPv6 出网。

地区由实际公网出口及平台自己的识别结果决定。多跳、落地分流或不同目标的专用出站可能导致“节点名字是香港、部分网站显示新加坡”。选一个稳定目标地区出口，先验证真实路径，别只看节点名称。

API 规则本身不配置故障直连，但用户选择的策略组可能含直连或跨地区回退。想维持稳定属地，应避免这样的候选和回退关系。节点失效应先修复节点，不扩大 API 直连范围。

## 模块化的实际边界

| 软件 | 能做到什么 | 需要用户配合 |
| --- | --- | --- |
| Shadowrocket | 单模块携带有序分流 | 选择当前代理、避免其他规则抢先 |
| Loon | 插件内 DIRECT / PROXY | 为插件 PROXY 选定策略 |
| Surge | 模块只能用内置直连/拒绝 | 在主配置副本或规则集中接入 API 代理 |
| QX | 独立远程过滤资源 | 分别绑定策略并检查资源/本地优先级 |
| Stash | 覆写数组前插 | 目标策略名与其他覆写次序 |
| Mihomo 客户端 | 核心规则集 | GUI 扩展行为各异，不能混用覆盖语义 |
| v2rayNG / v2rayN | 原生路由数组 | 导入的重置/追加行为不同 |
| sing-box / Xray | 原生规则片段 | 保留原 DNS、出站及入站前处理 |
| PassWall2 | 独立分流规则 | 找对 ACL/分流节点、避免内核提前放行 |

## 怎样判断一次优化成立

至少同时观察：手机功能和公开属地、域名实际命中与出站、是否产生新的失败。如果比较性能，还应控制内容、网络、预加载缓存和节点，记录起播/切换延迟及真实字节量。

当前连接次数不能推导“节省 90% 流量”“提高几倍速度”。维护者三个月经历不能推导平台对所有账号的长期风控结论。就算不输入密码、不做 HTTPS 解密，节点信任、异地登录与平台规则仍不由这份分流配置控制。

## 参考

- [PassWall2 分流选项实现](https://github.com/Openwrt-Passwall/openwrt-passwall2/blob/main/luci-app-passwall2/luasrc/model/cbi/passwall2/client/include/shunt_options.lua)
- [Xray 嗅探说明](https://xtls.github.io/config/inbound.html#sniffingobject)
- [Surge 模块限制](https://manual.nssurge.com/profile/module.html)
- [Loon 插件策略](https://github.com/Loon0x00/LoonManual/blob/master/docs/cn/plugin.md)
- [Stash 覆写合并](https://stash.wiki/configuration/override)
- [QX 官方样例](https://github.com/crossutility/Quantumult-X/blob/master/sample.conf)
- [Mihomo 规则集](https://wiki.metacubex.one/config/rule-providers/)
- [sing-box 规则集](https://sing-box.sagernet.org/configuration/rule-set/)

这些资料用于确认客户端机制，不是“抖音官方认可本分流”的证据。
