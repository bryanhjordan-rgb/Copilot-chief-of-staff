// Runs a compiled Office Script's pure functions under Node for parity tests.
// Usage: node run_office_script.js compiled.js < input.json
// input.json: {"call": "mine", "args": [...]}; prints JSON of the return value.
const fs = require("fs");
const vm = require("vm");

const code = fs.readFileSync(process.argv[2], "utf8");
const input = JSON.parse(fs.readFileSync(0, "utf8"));
const context = vm.createContext({ input });
// Compiled output is strict mode, so assign through globalThis.
vm.runInContext(`${code}\nglobalThis.result = JSON.stringify(${input.call}(...input.args));`, context);
process.stdout.write(context.result);
