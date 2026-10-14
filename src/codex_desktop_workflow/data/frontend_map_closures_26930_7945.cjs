// Map only free module references, keeping nested minified names in their scopes.
const fs=require('fs'),Module=require('module'),mod=new Module('acorn');
mod._compile(process.binding('natives')['internal/deps/acorn/acorn/dist/acorn'],'acorn.js');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const parse=s=>mod.exports.parse('('+s+')',{ecmaVersion:'latest',sourceType:'module'}).body[0].expression;
function free(root){
 const declared=new Set(),ranges=[];
 function bind(pattern,scope){if(!pattern)return;if(pattern.type==='Identifier'){declared.add(pattern.start);ranges.push({name:pattern.name,start:scope.start,end:scope.end});return;}
  if(pattern.type==='RestElement')bind(pattern.argument,scope);
  else if(pattern.type==='AssignmentPattern')bind(pattern.left,scope);
  else if(pattern.type==='ArrayPattern')pattern.elements.forEach(e=>bind(e,scope));
  else if(pattern.type==='ObjectPattern')pattern.properties.forEach(e=>bind(e.type==='RestElement'?e.argument:e.value,scope));
 }
 function collect(n,functions=[],blocks=[]){if(!n||typeof n!=='object')return;
  if(/^(FunctionDeclaration|FunctionExpression|ArrowFunctionExpression)$/.test(n.type)){
   if(n.id)bind(n.id,n.type==='FunctionDeclaration'&&blocks.length?blocks.at(-1):n);
   n.params.forEach(p=>bind(p,n));functions=[...functions,n];
  }
  if(['BlockStatement','ForStatement','ForInStatement','ForOfStatement','CatchClause'].includes(n.type))blocks=[...blocks,n];
  if(n.type==='CatchClause')bind(n.param,n);
  if(n.type==='VariableDeclaration')n.declarations.forEach(d=>bind(d.id,n.kind==='var'?functions.at(-1):blocks.at(-1)||functions.at(-1)));
  for(const value of Object.values(n)){if(Array.isArray(value))value.forEach(v=>collect(v,functions,blocks));else if(value&&typeof value==='object')collect(value,functions,blocks);}
 }
 collect(root);const references=new Map();
 function visit(n,parent=null,key=''){if(!n||typeof n!=='object')return;
  if(n.type==='Identifier'&&!declared.has(n.start)){
   const property=parent&&((parent.type==='MemberExpression'&&key==='property'&&!parent.computed)||((parent.type==='Property'||parent.type==='MethodDefinition')&&key==='key'&&!parent.computed));
   if(!property&&!ranges.some(r=>r.name===n.name&&r.start<=n.start&&n.end<=r.end))references.set(n.start,n.name);
  }
  for(const [k,value]of Object.entries(n)){if(Array.isArray(value))value.forEach(v=>visit(v,n,k));else if(value&&typeof value==='object')visit(value,n,k);}
 }
 visit(root);return references;
}
const results=[];
for(const item of input){
 const a=parse(item.old),b=parse(item.current),af=free(a),bf=free(b),changes={},failures=[];
 function pair(x,y,path=''){
  if(!x||!y||typeof x!=='object'||typeof y!=='object')return;
  if(x.type==='Identifier'&&af.has(x.start)){
   if(y.type!=='Identifier'||!bf.has(y.start)){failures.push({path,reason:'free reference changed ownership',old:x.name,new:y.name});return;}
   if(changes[x.name]&&changes[x.name]!==y.name)failures.push({path,reason:'inconsistent module reference',old:x.name,new:y.name});
   changes[x.name]=y.name;return;
  }
  for(const k of Object.keys(x)){if(['start','end','loc','raw'].includes(k))continue;
   if(Array.isArray(x[k])&&Array.isArray(y[k]))x[k].forEach((v,i)=>pair(v,y[k][i],path+'.'+k+'.'+i));
   else if(x[k]&&y[k]&&typeof x[k]==='object'&&typeof y[k]==='object')pair(x[k],y[k],path+'.'+k);
  }
 }
 pair(a,b);
 results.push({role:item.role,old:item.name,current:item.target,closure_bindings:changes,old_free:[...new Set(af.values())],current_free:[...new Set(bf.values())],failures});
}
process.stdout.write(JSON.stringify(results));
