#!/usr/bin/env node

"use strict";

/**
 * Command-line interface to packet decoding
 *
 * Usage:
 *   devlora-packet-decode --hex <packet>
 *   devlora-packet-decode --base64 <packet>
 */

var lora_packet = require('../lib/devindex.js');

var cmdlineArgs = process.argv;

var hexOption = cmdlineArgs.indexOf("--hex");
var b64Option = cmdlineArgs.indexOf("--base64");
var inputData;
if (hexOption != -1 && hexOption+1 <  cmdlineArgs.length) {
    var arg = cmdlineArgs[hexOption+1];
    console.log("decoding from Hex: ", arg);
    inputData = new Buffer(arg, 'hex');
} else if (b64Option != -1 && b64Option+1 <  cmdlineArgs.length) {
        var arg = cmdlineArgs[b64Option+1];
        console.log("decoding from Base64: ", arg);
        inputData = new Buffer(arg, 'base64');
} else {
    console.log ("Usage:");
    console.log ("\tdevlora-packet-decode --hex <data>");
    console.log ("\tdevlora-packet-decode --base64 <data>");
    process.exit(1);
}

var packet = lora_packet.fromWire(inputData);
console.log ("Decoded packet")
console.log ("--------------")
console.log (packet.toString());
