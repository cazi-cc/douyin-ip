# 抖音海外 IP 属地精确分流规则

**☝️想要抖音 IP 显示海外属地装逼，又想让视频流量能直连国内不绕路？👏这个项目满足你！**

**☝️它能让抖音 IP 检测接口走你选择的代理🌐，而与 IP 检测无关的流量**（视频、图片、直播等）**全部直连⚡️**

**三大特性：**

- **📱💻主流软件全支持，小白也能轻松上手。** 
- **模块设计，不影响已有配置。** 优先使用模块、插件和覆写；需要合并的客户端有单独教程。
- **属地随节点，媒体少绕路。** 关键 API 保留代理，媒体资源全部直连。
- **实测安全，不影响账号和内容。** 不需要账号密码、Cookie、HTTPS 解密证书，也不修改抖音 App。

**三个月真实使用反馈：** 维护者使用 Shadowrocket，先后使用香港、新加坡、日本、台湾、德国、美国节点，期间账号正常，未遇异常登录、验证码困扰、属地回落或功能异常。[查看实测依据](docs/evidence.md)

最近一次 PassWall2 实测：**135 次 API 代理、270 次媒体直连**，手机反馈无明显卡顿，查看到的属地均为香港。数字是连接记录数，不是流量占比。

[下载 v0.1.0](https://github.com/cazi-cc/douyin-ip/releases/tag/v0.1.0) · [小白上手](docs/beginner.md)

## 选你的软件

| 软件 | 接入方式 | 开始使用 |
| --- | --- | --- |
| Shadowrocket | 模块，移动端首选入口 | [安装](docs/clients/shadowrocket.md) |
| Loon | 插件，选择已有代理策略 | [安装](docs/clients/loon.md) |
| Surge | 媒体模块 + API 代理规则 | [安装](docs/clients/surge.md) |
| Quantumult X | 远程规则资源 / 本地规则 | [安装](docs/clients/quantumult-x.md) |
| Stash | 覆写文件 | [安装](docs/clients/stash.md) |
| Clash Meta for Android / FlClash / Clash Verge Rev | Mihomo 规则集，按客户端合并 | [安装](docs/clients/mihomo.md) |
| v2rayNG / v2rayN | 路由规则，保留原列表后添加 | [安装](docs/clients/v2ray.md) |
| sing-box | 原生规则集 + 增量路由 | [安装](docs/clients/sing-box.md) |
| PassWall2 | 两组独立分流规则 | [安装](docs/clients/passwall2.md) |

**三步试用：** 按教程添加 → 选择一个稳定的目标地区节点 → 重开抖音，检查播放与公开属地。

不熟悉配置？从 [小白上手](docs/beginner.md) 开始。效果不对，先看 [常见问题与撤销](docs/faq.md)。

> 这是分流规则，不提供节点，也不保证属地立即刷新或账号绝对安全。三个月是维护者的个人经历；节点质量、账号状态和平台机制会影响结果。其他客户端为规则适配，实测范围请看[兼容性](docs/compatibility.md)。

## 再深入一点

[技术原理](docs/technical.md) · [规则与实测](docs/evidence.md) · [本地构建与验证](docs/development.md) · [参与维护](CONTRIBUTING.md)

开源规则与工具采用 [MIT 许可证](LICENSE)。本项目与抖音及所列客户端无隶属关系。
