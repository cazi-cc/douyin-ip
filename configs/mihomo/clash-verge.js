// 只修改下方目标策略名。此脚本供 Clash Verge Rev 的配置扩展使用。
const TARGET = "Douyin-IP-Proxy";
const PATCH = {
  "rule-providers": {
    "douyin-ip-media": {
      "type": "inline",
      "behavior": "classical",
      "payload": [
        "DOMAIN-SUFFIX,douyincdn.com",
        "DOMAIN-SUFFIX,douyinliving.com",
        "DOMAIN-SUFFIX,douyinvod.com",
        "DOMAIN-SUFFIX,douyinpic.com",
        "DOMAIN-SUFFIX,bytegecko.com",
        "DOMAIN-SUFFIX,byteeffecttos.com",
        "DOMAIN-SUFFIX,byteimg.com",
        "DOMAIN-SUFFIX,ecombdimg.com",
        "DOMAIN-SUFFIX,bytehwm.com",
        "DOMAIN-SUFFIX,bytecdn.com",
        "DOMAIN-SUFFIX,zjcdn.com",
        "DOMAIN-KEYWORD,awememusicpgc",
        "DOMAIN,v9-awememusicpgc.amemv.com"
      ]
    },
    "douyin-ip-api": {
      "type": "inline",
      "behavior": "classical",
      "payload": [
        "DOMAIN-SUFFIX,snssdk.com",
        "DOMAIN-SUFFIX,amemv.com"
      ]
    }
  },
  "rules": [
    "RULE-SET,douyin-ip-media,DIRECT",
    "RULE-SET,douyin-ip-api,Douyin-IP-Proxy"
  ]
};

function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort().map(key => [key, canonical(value[key])]));
  }
  return value;
}

function main(config) {
  const copy = JSON.parse(JSON.stringify(config));
  const names = [...(copy.proxies || []), ...(copy["proxy-groups"] || [])].map(p => p.name);
  if (!names.includes(TARGET) || ["DIRECT", "REJECT", "PASS", "GLOBAL"].includes(TARGET.toUpperCase())) {
    throw new Error("请把 TARGET 改成现有代理节点或策略组名称，不能选直连。");
  }
  const providers = copy["rule-providers"] || {};
  for (const [name, value] of Object.entries(PATCH["rule-providers"])) {
    if (name in providers && JSON.stringify(canonical(providers[name])) !== JSON.stringify(canonical(value))) {
      throw new Error("同名规则集已存在且内容不同：" + name);
    }
    providers[name] = value;
  }
  const owned = ["RULE-SET,douyin-ip-media,", "RULE-SET,douyin-ip-api,"];
  const prefix = ["RULE-SET,douyin-ip-media,DIRECT", "RULE-SET,douyin-ip-api," + TARGET];
  const oldRules = copy.rules || [];
  for (const rule of oldRules) {
    if (owned.some(start => rule.startsWith(start)) && !prefix.includes(rule)) {
      throw new Error("已有 Douyin-IP 规则使用不同策略，请先停用旧扩展。");
    }
  }
  copy["rule-providers"] = providers;
  copy.rules = prefix.concat(oldRules.filter(rule => !prefix.includes(rule)));
  return copy;
}
