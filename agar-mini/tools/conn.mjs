import { SerialPort } from 'serialport';
import { create_rpc_connection, call_rpc } from '@zmkfirmware/zmk-studio-ts-client';
export async function open() {
  const ports = await SerialPort.list();
  const p = ports.find(x => (x.vendorId||'').toLowerCase() === '9d5b');
  if (!p) throw new Error('Agar Mini serial port not found: ' + JSON.stringify(ports.map(x=>[x.path,x.vendorId,x.productId])));
  const port = new SerialPort({ path: p.path, baudRate: 12500 });
  await new Promise((res, rej) => port.on('open', res).on('error', rej));
  const readable = new ReadableStream({ start(c) { port.on('data', d => c.enqueue(new Uint8Array(d))); port.on('close', () => { try { c.close(); } catch {} }); } });
  const writable = new WritableStream({ write(chunk) { return new Promise((res, rej) => port.write(Buffer.from(chunk), e => e ? rej(e) : port.drain(res))); } });
  const abortController = new AbortController();
  const conn = create_rpc_connection({ label: p.path, abortController, readable, writable }, { signal: abortController.signal });
  const rpc = req => Promise.race([call_rpc(conn, req), new Promise((_, rej) => setTimeout(() => rej(new Error('timeout ' + JSON.stringify(req))), 30000))]);
  return { rpc, path: p.path, close: () => { abortController.abort(); port.close(); } };
}
