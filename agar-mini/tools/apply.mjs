import { open } from './conn.mjs';
import fs from 'fs';
const target = JSON.parse(fs.readFileSync(process.argv[2]));
const { rpc, close } = await open();
const km = (await rpc({ keymap: { getKeymap: true } })).keymap.getKeymap;
let n = 0, errs = [];
for (const [lid, binds] of Object.entries(target)) {
  const layer = km.layers.find(l => l.id === +lid);
  for (let i = 0; i < binds.length; i++) {
    if (!binds[i]) continue;
    const [behaviorId, param1, param2] = binds[i];
    const c = layer.bindings[i];
    if (c.behaviorId === behaviorId && (c.param1||0) === param1 && (c.param2||0) === param2) continue;
    const r = await rpc({ keymap: { setLayerBinding: { layerId: +lid, keyPosition: i, binding: { behaviorId, param1, param2 } } } });
    const res = r.keymap?.setLayerBinding;
    if (res !== 0 && res !== undefined) errs.push([lid, i, res, JSON.stringify(r)]); else n++;
  }
}
console.log('set', n, 'errors', errs);
if (errs.length) { await rpc({ keymap: { discardChanges: true } }); console.log('discarded, nothing saved'); }
else { const s = await rpc({ keymap: { saveChanges: true } }); console.log('save', JSON.stringify(s.keymap?.saveChanges)); }
close(); setTimeout(() => process.exit(0), 300);
