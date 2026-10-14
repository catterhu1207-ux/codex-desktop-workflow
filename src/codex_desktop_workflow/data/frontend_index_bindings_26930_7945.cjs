const fs=require('fs'),Module=require('module');
const a=new Module('acorn');a._compile(process.binding('natives')['internal/deps/acorn/acorn/dist/acorn'],'acorn.js');
const payload=JSON.parse(fs.readFileSync(0,'utf8')),out={};
for(const [role,raw] of Object.entries(payload)){
 const ast=a.exports.parse(raw,{ecmaVersion:'latest',sourceType:'module'}),bindings={};
 function add(name,node,kind,depth){(bindings[name]??=[]).push({kind,depth,start:node.start,end:node.end,source:raw.slice(node.start,node.end)})}
 function walk(n,depth=0){if(!n||typeof n!=='object')return;
  if(n.type==='FunctionDeclaration')add(n.id.name,n,'function',depth);
  if(n.type==='VariableDeclarator'&&n.id.type==='Identifier'&&n.init)add(n.id.name,n.init,'initializer',depth);
  if(n.type==='AssignmentExpression'&&n.left.type==='Identifier')add(n.left.name,n.right,'assignment',depth);
  if(n.type==='ImportDeclaration')for(const s of n.specifiers){add(s.local.name,s,'import',depth);bindings[s.local.name].at(-1).module=n.source.value;bindings[s.local.name].at(-1).imported=s.imported?.name}
  if(n.type==='ExportNamedDeclaration')for(const s of n.specifiers)add(s.exported.name,s,'export',depth);
  if(['FunctionDeclaration','FunctionExpression','ArrowFunctionExpression','ClassExpression','ClassDeclaration'].includes(n.type))depth++;
  for(const v of Object.values(n)){if(Array.isArray(v))v.forEach(x=>walk(x,depth));else if(v&&typeof v==='object')walk(v,depth)}
 }
 walk(ast);out[role]=bindings;
}
process.stdout.write(JSON.stringify(out));
