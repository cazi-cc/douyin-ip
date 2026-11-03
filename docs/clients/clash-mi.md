# Clash Mi

可以使用。Clash Mi 内置 Mihomo 核心，本项目提供 [clash-mi.js](../../configs/mihomo/clash-mi.js) 作为 **JavaScript 自定义覆写**。它在原规则前加入“媒体直连 → API 代理”，保留原配置数据。

本教程核对了 Clash Mi 稳定版 **1.0.31.1703** 的上游源码；主分支也保留同一脚本入口。不依赖测试版新增的规则前插功能，旧版找不到入口时建议先更新稳定版。已进行脚本和核心配置检查，尚未完成 Clash Mi 手机导入与属地实测。

## 安装

1. 备份原配置，并记下当前配置的“核心覆写”和原覆写文件的“追加覆写”选择。
2. 下载 [v0.1.1 固定版本脚本](https://raw.githubusercontent.com/cazi-cc/douyin-ip/v0.1.1/configs/mihomo/clash-mi.js)。用文本编辑器将开头的 `TARGET` 从 `Douyin-IP-Proxy` 改为**当前订阅 YAML 中已有的节点或策略组名称**，包括空格、大小写和表情。例：已有组名是“香港”，就写 `const TARGET = "香港";`。组名不会自动锁定地区，组内还要选好目标节点。
3. 在 Clash Mi 的“覆写”管理页点 `+`，选择“导入配置文件”，类型选 **`js`**，导入修改后的文件，名称可填“抖音 IP 分流”。这是覆写文件，不是机场订阅，不要放到“我的配置”中当完整订阅导入。
4. 到“我的配置”，编辑正在使用的订阅，将“核心覆写”明确选为刚导入的“抖音 IP 分流”，避免仅导入文件却没有绑定。不同版本入口文字可能略有变化。
5. 检查该文件的“追加覆写”：保持原先需要的内置 DNS/TUN 等设置。如果沿用“内置-覆写”，在目标订阅中关闭会**替换整个规则列表**的“规则覆写”；新版则应确认规则覆写方式没有覆盖掉本项目规则。不要为了加分流而重置 DNS/TUN 或其他网络设置。
6. 使用**规则模式**，保存并重新连接，再按下面的方法检查最终结果。

脚本只接受已存在的代理节点或策略组，不会创建节点。找不到 `TARGET`、已有同名规则集内容冲突、旧项目规则指向其他策略时会报错；先修正名称或停用旧的项目扩展，再重连。

## 已有自定义覆写时

每份配置只能选择一个自定义覆写，不要直接用本文件替换正在使用的 DNS、节点或其他业务覆写。

- 已有 JavaScript：在自己的副本中，将本脚本的 `main` 改名为 `appendDouyin`，并在原脚本 `main` 返回最终对象前调用 `return appendDouyin(原脚本生成的对象);`。同时检查顶层常量、辅助函数是否重名。这是集成方法说明，不是可原样粘贴的代码。
- 已有 YAML 或不会合并脚本：优先在电脑上按 [Mihomo 离线合并方式](mihomo.md)处理导出的完整配置，生成新的配置副本，保留原配置以便撤销。静态副本不能自动跟随机场更新；不要切换后忘记维护。

不要把 [merge-fragment.yaml](../../configs/mihomo/merge-fragment.yaml) 直接当作 Clash Mi 的普通 YAML 覆写来替换规则，也不要假定 `prepend-rules` 是 Clash Mi 通用字段。上游曾明确建议用 JavaScript 完成此类前插需求。

## 验证和撤销

重连后查看“运行时配置”或面板规则：

```text
RULE-SET,douyin-ip-media,DIRECT
RULE-SET,douyin-ip-api,你设置的 TARGET 名称
……原有规则……
```

确认 `douyin-ip-media` 与 `douyin-ip-api` 两个 provider 存在，媒体例外排在 API 前，两者先于普通国内直连和兜底；原有规则、节点与其他 provider 仍在。内置必要规则可能在前，重点检查没有抢先匹配抖音的规则。

若缺少本项目规则，先核对“核心覆写”是否选对、类型是否为 `js`、是否重新连接；再检查“追加覆写”中的规则覆写。JS 执行后 App 仍可施加内置覆写，不能只凭文件内容确认最终生效。

在连接记录中，实际出现的 API 主机应走目标代理，已列出的媒体例外应直连。随后检查视频、图文、直播和公开属地；无须安装解密证书。加密 DNS、裸 IP、TUN 排除等限制见[技术说明](../technical.md)。本项目保守代理两个 API 后缀，不能把所有命中都断言为单独的属地检测请求。

撤销时将目标订阅的“核心覆写”恢复为原选择，恢复本次调整的规则覆写选项并重连。组合脚本用户切回原脚本，离线合并用户切回原配置。无需删除原节点或其他模块。

## 核对依据

- [Clash Mi 官方说明](https://github.com/KaringX/clashmi)：内置 Mihomo。
- [官方 FAQ：覆写顺序](https://clashmi.app/guide/faq)：订阅配置 → 自定义覆写 → App 内置覆写。
- [上游 Issue #460](https://github.com/KaringX/clashmi/issues/460)：维护者建议用 JavaScript 保留原规则并前插。
- [稳定版脚本入口](https://github.com/KaringX/clashmi/blob/v1.0.31.1703/lib/app/modules/profile_patch_manager.dart#L803)：调用 `main(config)` 并读取返回的配置。
- [稳定版配置准备](https://github.com/KaringX/clashmi/blob/v1.0.31.1703/lib/app/local_services/vpn_service.dart#L155)：先生成自定义结果，再应用最终内置覆写。
