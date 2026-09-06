# Quantumult X

采用两份独立资源：[media.list](../../configs/quantumult-x/media.list) 与 [api.list](../../configs/quantumult-x/api.list)。不要对包含两类流量的混合文件统一强制策略。

## 本地规则方式

复制当前配置副本，把 [local-rules.conf](../../configs/quantumult-x/local-rules.conf) 的有效行放到现有 `[filter_local]` 顶部。将其中 `Douyin-IP-Proxy` 改成已有代理策略名称。保留原有规则，媒体直连必须排在 API 代理前。

## 远程资源方式

在远程分流资源管理中分别添加两个文件的 Raw URL：

- `media.list` 的强制策略选 `direct`。
- `api.list` 的强制策略选你已有的目标代理策略。
- 两个资源均使用插入资源方式（`inserted-resource=true`），媒体资源在 API 前，且都在普通国内放行资源之前。检查最终规则顺序，已有本地规则也可能更靠前。

资源管理入口和本地编辑方式二选一，不需要重写资源或解析脚本。文件中的 `proxy` 为 QX 内置代理策略；远程资源的 `force-policy` 应明确覆盖为你实际选择的地区策略。

现有 `[dns]` 和系统设置保留。官方样例说明 QX 默认占位 IP 映射有远端解析效果；检查 API 不在你的 `dns_exclusion_list` 或隧道排除列表中。加密 DNS、自行解析和裸 IP 流量仍需实际连接验证，不复制 Shadowrocket 的专用参数。

撤销：停用两个远程资源，或删除手动添加的本地规则，重连后恢复原分流。

参考：[Quantumult X 官方配置样例](https://github.com/crossutility/Quantumult-X/blob/master/sample.conf)。本适配未宣称 QX 真机验收。

## 固定版本下载地址

以下链接固定到 `v0.1.0`。复制链接地址导入；升级需主动切换版本。

- [媒体直连资源](https://raw.githubusercontent.com/cazi-cc/douyin-ip/v0.1.0/configs/quantumult-x/media.list)
- [API 代理资源](https://raw.githubusercontent.com/cazi-cc/douyin-ip/v0.1.0/configs/quantumult-x/api.list)
