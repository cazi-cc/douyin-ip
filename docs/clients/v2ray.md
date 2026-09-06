# v2rayNG / v2rayN

提供客户端原生的路由规则数组，包含“媒体直连”和“属地 API”两项。目标标签为客户端通常使用的 `direct` / `proxy`，并不是完整的 Xray 节点配置。

## v2rayNG（Android）

文件：[rules.json](../../configs/v2rayng/rules.json)。

**不要把这两项直接当作完整列表从剪贴板导入。** 当前上游该入口会重置原路由列表，并额外保留锁定规则。

推荐手机内手动新增：

1. 导出原路由列表作为备份。
2. 在路由设置中新增一项，备注 `Douyin-IP / 媒体直连`，出站 `direct`，域名填 JSON 第一项的 `domain` 内容，每个值一行。
3. 再新增 API 项，出站 `proxy`，域名填第二项的两个值。
4. 将媒体项放在 API 项前，二者放在通用国内/GeoIP 直连前。其他字段留空，保持启用。
5. 选择目标地区节点，启用必要的域名嗅探和规则路由，重连后验证。已有裸 IP 流量仍需嗅探/映射支持。

需要批量处理时，先导出当前路由数组，再合并到新文件：

```sh
python tools/merge.py v2rayng local/original-rules.json local/merged-rules.json
```

然后导入**合并后的完整列表**。有锁定规则时工具会拒绝：先备份、解锁并重新导出，否则客户端可能重复插入锁定项或将它们放在项目规则之前。导入后再核对最终顺序，需要时恢复原锁定状态。

## v2rayN（桌面）

文件：[rules.json](../../configs/v2rayn/rules.json)。

在高级路由中复制当前方案作为新方案，进入该方案的规则编辑，选择从文件或剪贴板**追加**规则；若弹窗询问追加/替换，必须选择追加，具体按钮以文字含义为准。当前上游追加在末尾，随后把媒体和 API 两项移到通用规则之前，媒体在前。

也可导出原规则数组，离线执行：

```sh
python tools/merge.py v2rayn local/original-rules.json local/merged-rules.json
```

导入合并后的完整列表到你的方案副本；原方案保留。不要把路由数组作为节点订阅导入。这里针对 Xray 核心规则路径，选择其他核心时需重新验证转换行为。

## DNS、验证与撤销

本项目不更改客户端全局 DNS 或 `domainStrategy`。若应用自行解析地址，须保证相关入站能嗅探 HTTP/TLS/QUIC 域名，并让代理域名使用可用的远端 DNS；可参考技术文档，不能照搬家庭路由器的私有设置。

连接日志出现 `proxy` 只是出站标签，应同时确认当前节点的地区与抖音公开属地。

撤销时删除这两项或切回原路由方案；批量合并用户重新导入备份。节点订阅保持原样。

## 已有 Xray 自定义 JSON

另提供 [routing.fragment.json](../../configs/xray/routing.fragment.json)。它只包含 `routing.rules`，不能直接作为可运行的完整配置。合并副本时：

```sh
python tools/merge.py xray local/original.json local/with-douyin.json --proxy-tag proxy --direct-tag direct
```

把参数改成你已有出站标签。工具不新建出站，拒绝把 API 指向直连/黑洞出站；保留 DNS、入站、路由策略和其他规则。

参考：[v2rayNG 路由导入](https://github.com/2dust/v2rayNG/blob/master/V2rayNG/app/src/main/java/com/v2ray/ang/handler/SettingsManager.kt)、[v2rayN 规则导入](https://github.com/2dust/v2rayN/blob/master/v2rayN/ServiceLib/ViewModels/RoutingRuleSettingViewModel.cs)。客户端 UI 未在本项目逐项真机验收。
