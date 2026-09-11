"use client";
import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Page() {
  const [candles, setCandles] = useState<any[]>([]);
  const [ind, setInd] = useState<any>(null);
  const [fg, setFg] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);
  const [msgs, setMsgs] = useState<{role:string, content:string}[]>([{role:"assistant", content:"Hola — soy BTC-AI (Ollama local). Pregunta: ¿BTC sobrevendido? ¿Propón scalping 15m?"}]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);

  async function load() {
    try {
      const [c, i, f, h] = await Promise.all([
        fetch(`${API}/api/market/candles?symbol=BTCUSDT&interval=1m&limit=60`).then(r=>r.json()),
        fetch(`${API}/api/market/indicators?symbol=BTCUSDT&interval=1m`).then(r=>r.json()),
        fetch(`${API}/api/market/fear-greed`).then(r=>r.json()),
        fetch(`${API}/health`).then(r=>r.json()),
      ]);
      setCandles(c);
      setInd(i);
      setFg(f);
      setHealth(h);
    } catch(e){ console.error(e); }
  }
  useEffect(()=>{ load(); const id=setInterval(load, 15000); return ()=>clearInterval(id); },[]);

  async function send() {
    if(!input.trim() || streaming) return;
    const newMsgs = [...msgs, {role:"user", content: input}];
    setMsgs(newMsgs);
    setInput("");
    setStreaming(true);
    // streaming via SSE
    try {
      const res = await fetch(`${API}/api/chat/stream`, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({messages: newMsgs})
      });
      if(!res.body) throw new Error("no body");
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let assistant = "";
      setMsgs(m=>[...m, {role:"assistant", content:""}]);
      while(true){
        const {done, value} = await reader.read();
        if(done) break;
        const text = decoder.decode(value);
        const lines = text.split("\n");
        for(const line of lines){
          if(line.startsWith("data: ")){
            const data = line.slice(6);
            if(data===" [DONE]" || data==="[DONE]") break;
            assistant += data;
            setMsgs(m=>{
              const c=[...m];
              c[c.length-1] = {role:"assistant", content: assistant};
              return c;
            });
          }
        }
      }
    } catch(e:any){
      setMsgs(m=>[...m.slice(0,-1), {role:"assistant", content: `(Error: ${e.message})`}]);
    } finally { setStreaming(false); }
  }

  const lastPrice = ind?.indicators?.close || candles[candles.length-1]?.close || "—";
  const rsi = ind?.indicators?.rsi;

  return (
    <main style={{ maxWidth: 1200, margin: "0 auto", padding: 24, display:"grid", gap: 24 }}>
      <header style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
        <h1 style={{ fontSize: 24, fontWeight: 700 }}>BTC-AI <span style={{ fontWeight:400, opacity:0.7 }}>— Local-First</span></h1>
        <span style={{ fontSize:12, opacity:0.7 }}>{health?.mode || "ANALYST"} · LIVE:{String(health?.live_trading)} · {API}</span>
      </header>

      <section style={{ display:"grid", gridTemplateColumns:"2fr 1fr", gap:24 }}>
        <div style={{ background:"#111", border:"1px solid #222", borderRadius:12, padding:16 }}>
          <h3 style={{ margin:"0 0 8px"}}>BTCUSDT 1m — Últimas {candles.length} velas</h3>
          <div style={{ fontSize:12, opacity:0.7, marginBottom:8 }}>Precio: ${lastPrice} · RSI: {rsi ?? "—"} · EMA50: {ind?.indicators?.ema50 ?? "—"} · BB: {ind?.indicators?.bb_lower ?? "—"} - {ind?.indicators?.bb_upper ?? "—"}</div>
          <div style={{ height:220, overflow:"auto", background:"#0a0a0a", borderRadius:8, padding:8, fontFamily:"monospace", fontSize:12 }}>
            {candles.slice(-20).map((c,i)=><div key={i}>{new Date(c.open_time).toLocaleTimeString()} O:{c.open} H:{c.high} L:{c.low} C:{c.close} V:{c.volume}</div>)}
            {candles.length===0 && <div style={{opacity:0.6}}>Sin velas aún — espera ingest (seed REST al iniciar) o revisa backend logs</div>}
          </div>
          <div style={{ marginTop:12, display:"flex", gap:8, fontSize:12 }}>
            <button onClick={load} style={{ padding:"6px 10px", background:"#222", color:"#fff", border:"1px solid #333", borderRadius:6, cursor:"pointer"}}>Refrescar</button>
            <span style={{ opacity:0.6 }}>Fear&Greed: {fg?.data?.[0]?.value} {fg?.data?.[0]?.value_classification} {fg?.error && `(fallback)`}</span>
          </div>
        </div>

        <div style={{ background:"#111", border:"1px solid #222", borderRadius:12, padding:16 }}>
          <h3 style={{ margin:"0 0 8px"}}>Indicadores</h3>
          <pre style={{ fontSize:12, whiteSpace:"pre-wrap", background:"#0a0a0a", padding:8, borderRadius:8 }}>{JSON.stringify(ind?.indicators || {}, null, 2)}</pre>
          <div style={{ fontSize:11, opacity:0.6, marginTop:8 }}>count: {ind?.count ?? 0} velas · interval {ind?.interval}</div>
        </div>
      </section>

      <section style={{ background:"#111", border:"1px solid #222", borderRadius:12, padding:16, display:"grid", gap:12 }}>
        <h3 style={{ margin:0}}>Chat con Ollama local</h3>
        <div style={{ height:320, overflow:"auto", background:"#0a0a0a", borderRadius:8, padding:12, display:"grid", gap:8 }}>
          {msgs.map((m,i)=><div key={i} style={{ alignSelf: m.role==="user"?"end":"start", background: m.role==="user"?"#1e293b":"#1a1a1a", border:"1px solid #222", borderRadius:8, padding:8, maxWidth:"85%", whiteSpace:"pre-wrap", fontSize:13 }}>{m.content}</div>)}
          {streaming && <div style={{ fontSize:12, opacity:0.6}}>streaming…</div>}
        </div>
        <div style={{ display:"flex", gap:8}}>
          <input value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>e.key==="Enter"&&send()} placeholder="Ej: ¿BTC sobrevendido? Propón scalping 15m con SL/TP" style={{ flex:1, padding:10, background:"#0a0a0a", border:"1px solid #333", borderRadius:8, color:"#fff"}}/>
          <button onClick={send} disabled={streaming} style={{ padding:"10px 16px", background: streaming?"#333":"#3b82f6", color:"#fff", border:"none", borderRadius:8, cursor: streaming?"not-allowed":"pointer"}}>{streaming?"...":"Enviar"}</button>
        </div>
        <div style={{ fontSize:11, opacity:0.6}}>Contexto inyectado: precio, RSI, MACD, BB, Fear&Greed. Si Ollama no está corriendo, verás fallback mock.</div>
      </section>

      <footer style={{ fontSize:11, opacity:0.5, textAlign:"center"}}>BTC-IA · Paper by default · `LIVE_TRADING=false` · Binance Testnet · No es asesoramiento financiero</footer>
    </main>
  );
}
