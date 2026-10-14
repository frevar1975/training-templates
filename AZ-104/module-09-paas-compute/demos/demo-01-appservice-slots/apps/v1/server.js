const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const release = require('./release.json');
const products = [{id:'audifonos',name:'Audífonos inalámbricos',price:300,icon:'🎧'}, {id:'teclado',name:'Teclado mecánico',price:400,icon:'⌨️'}, {id:'mouse',name:'Mouse inalámbrico',price:100,icon:'🖱️'}];
const send=(res,status,data)=>{res.writeHead(status,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'});res.end(JSON.stringify(data));};
const server=http.createServer((req,res)=>{
 const url=new URL(req.url,'http://localhost');
 if(url.pathname==='/health') return send(res,200,{status:'ok',version:release.version});
 if(url.pathname==='/api/info') return send(res,200,{...release,products});
 if(url.pathname==='/api/quote') {
  const id=url.searchParams.get('product'); const qty=Number(url.searchParams.get('qty'));
  const product=products.find(p=>p.id===id);
  if(!product || !Number.isInteger(qty) || qty<1 || qty>20) return send(res,400,{error:'Elegí un producto y una cantidad entre 1 y 20.'});
  const subtotal=product.price*qty;
  // Defecto didáctico intencional: V2 aplica 10%, aunque la promoción anuncia 20%.
  const rate=subtotal>=500?(release.version==='2.0'?0.10:0.20):0;
  return send(res,200,{version:release.version,subtotal,discount:subtotal*rate,total:subtotal*(1-rate),advertisedRate:subtotal>=500?0.20:0});
 }
 if(url.pathname==='/' || url.pathname==='/index.html') {
  res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store'});
  return res.end(fs.readFileSync(path.join(__dirname,'index.html')));
 }
 return send(res,404,{error:'No encontrado'});
});
server.listen(Number(process.env.PORT || 8080),'0.0.0.0',()=>console.log('Tienda '+release.version+' preparada'));
