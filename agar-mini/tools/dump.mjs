import { open } from './conn.mjs';
import fs from 'fs';
const { rpc, path, close } = await open();
const out = { path };
out.device = (await rpc({ core: { getDeviceInfo: true } })).core?.getDeviceInfo;
out.lock = (await rpc({ core: { getLockState: true } })).core?.getLockState;
console.log('device', out.device?.name, 'lock', out.lock);
try {
  const ids = (await rpc({ behaviors: { listAllBehaviors: true } })).behaviors?.listAllBehaviors?.behaviors || [];
  out.behaviors = {};
  for (const id of ids) out.behaviors[id] = (await rpc({ behaviors: { getBehaviorDetails: { behaviorId: id } } })).behaviors?.getBehaviorDetails;
  out.layouts = (await rpc({ keymap: { getPhysicalLayouts: true } })).keymap?.getPhysicalLayouts;
  out.keymap = (await rpc({ keymap: { getKeymap: true } })).keymap?.getKeymap;
  out.unsaved = (await rpc({ keymap: { checkUnsavedChanges: true } })).keymap?.checkUnsavedChanges;
} catch (e) { out.error = String(e); console.log('ERR', e); }
fs.writeFileSync(process.argv[2] || 'dump.json', JSON.stringify(out, (k, v) => v instanceof Uint8Array ? Buffer.from(v).toString('hex') : v, 1));
console.log('layers', out.keymap?.layers?.map(l => `${l.id}:${l.name}(${l.bindings.length})`), 'available', out.keymap?.availableLayers, 'behaviors', Object.keys(out.behaviors||{}).length, 'unsaved', out.unsaved);
close(); setTimeout(() => process.exit(0), 300);
