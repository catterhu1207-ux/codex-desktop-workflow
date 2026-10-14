const fs=require('node:fs'),Module=require('node:module');
const bundled=new Module('acorn');bundled._compile(process.binding('natives')['internal/deps/acorn/acorn/dist/acorn'],'acorn.js');
const acorn=bundled.exports;
const request=JSON.parse(fs.readFileSync(0,'utf8')),ast=acorn.parse(request.source,{ecmaVersion:'latest',sourceType:'module'}),rows=[];
function visit(node,ancestors=[]){
 if(!node||typeof node!=='object')return;
 if(Array.isArray(node)){for(const child of node)visit(child,ancestors);return}
 const chain=node.type?[...ancestors,node]:ancestors;
 const name=node.type==='FunctionDeclaration'?node.id?.name:node.type==='VariableDeclarator'&&node.init?node.id?.name:node.type==='AssignmentExpression'&&node.operator==='='?node.left?.type==='Identifier'?node.left.name:null:null;
 if(request.names.includes(name)){
  const depth=chain.filter(n=>/Function/.test(n.type)).length;
  rows.push({name,depth,type:node.type,source:request.source.slice(node.start,node.end)});
 }
 for(const [key,child]of Object.entries(node))if(!['start','end','loc','range'].includes(key)&&child&&typeof child==='object')visit(child,chain);
}
visit(ast);
const result={};for(const name of request.names){const found=rows.filter(r=>r.name===name);if(!found.length)throw Error('Native binding absent '+name);const depth=Math.min(...found.map(r=>r.depth)),exact=found.filter(r=>r.depth===depth);if(exact.length!==1)throw Error('Native binding ambiguous '+name);result[name]=exact[0].type==='VariableDeclarator'?'const '+exact[0].source+';':exact[0].source}
process.stdout.write(JSON.stringify(result));
