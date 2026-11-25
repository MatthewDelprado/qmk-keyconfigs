#!/bin/sh
# Installs the ZMK Studio client and patches its imports so plain Node can load it.
set -e
cd "$(dirname "$0")"
[ -f package.json ] || npm init -y >/dev/null
npm i --ignore-scripts @zmkfirmware/zmk-studio-ts-client@0.0.18 serialport
cd node_modules/@zmkfirmware/zmk-studio-ts-client/lib
perl -pi -e 's#(from\s+["\x27])(\./[^"\x27]+?)(?<!\.js)(["\x27])#$1$2.js$3#g' *.js transport/*.js
perl -pi -e 's#from "\./transport\.js"#from "./transport/index.js"#; s#import \* as _m0 from "protobufjs/minimal(\.js)?";#import _m0 from "protobufjs/minimal.js";#' *.js
echo ready
