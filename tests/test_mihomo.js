const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const script = fs.readFileSync(path.join(root, 'configs/mihomo/clash-verge.js'), 'utf8');
const context = vm.createContext({});
vm.runInContext(script, context);
const plain = value => JSON.parse(JSON.stringify(value));
const original = {
  proxies: [{name: 'Douyin-IP-Proxy', type: 'socks5', server: '127.0.0.1', port: 65534}],
  dns: {enable: true, nameserver: ['system']},
  tun: {enable: false},
  rules: ['DOMAIN,example.org,DIRECT', 'MATCH,Douyin-IP-Proxy'],
};
const before = plain(original);
const merged = plain(context.main(original));
assert.deepEqual(original, before);
assert.deepEqual(merged.dns, original.dns);
assert.deepEqual(merged.tun, original.tun);
assert.deepEqual(merged.proxies, original.proxies);
assert.deepEqual(merged.rules.slice(2), original.rules);
assert.deepEqual(plain(context.main(merged)), merged);
const reordered = plain(merged);
for (const key of Object.keys(reordered['rule-providers'])) {
  reordered['rule-providers'][key] = Object.fromEntries(Object.entries(reordered['rule-providers'][key]).reverse());
}
assert.deepEqual(plain(context.main(reordered)), merged);
assert.throws(() => context.main({...original, proxies: []}), /TARGET/);
const conflict = plain(original);
conflict['rule-providers'] = {'douyin-ip-media': {type: 'inline', payload: ['DOMAIN,unexpected.example']}};
assert.throws(() => context.main(conflict), /同名/);
console.log('Mihomo script: preservation, ordering, idempotence and conflict checks passed.');
