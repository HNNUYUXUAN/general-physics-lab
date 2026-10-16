import {readFileSync} from 'node:fs';
import {pathToFileURL} from 'node:url';
const file=process.argv[2];
const {response,characteristics}=await import(pathToFileURL(file));
const cases=JSON.parse(readFileSync(0,'utf8'));
process.stdout.write(JSON.stringify(cases.map(c=>({parameters:c.parameters,frequency:c.frequency,...response(c.parameters,c.frequency),characteristics:characteristics(c.parameters)}))));
