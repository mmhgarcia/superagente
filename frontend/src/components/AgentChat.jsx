import { useState, useEffect, useRef } from 'react'
import { listAgents, askAgent, checkLlmHealth } from '../api'

export default function AgentChat() {
  const [agents, setAgents] = useState([])
  const [selected, setSelected] = useState('')
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [llmDown, setLlmDown] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    listAgents().then(d => {
      const all = d.agents
      setAgents(all)
      const coord = all.find(a => a.name === 'coordinador')
      if (coord) setSelected(coord.id)
    }).catch(() => {})
  }, [])

  useEffect(() => {
    checkLlmHealth().then(d => setLlmDown(d.status !== 'ok')).catch(() => setLlmDown(true))
  }, [])

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  useEffect(() => {
    if (!selected) return
    setMessages([])
  }, [selected])

  async function handleSend(e) {
    e.preventDefault()
    if (!input.trim() || !selected) return
    const msg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: msg }])
    setLoading(true)
    try {
      const data = await askAgent(selected, msg)
      setMessages(prev => [...prev, { role: 'assistant', content: data.response, confidence: data.confidence }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Error: no se pudo obtener respuesta' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Probar agente</h2>
      {llmDown && (
        <div style={{background:'#7f1d1d',color:'#fca5a5',padding:'0.75rem',borderRadius:'6px',marginBottom:'1rem',fontSize:'0.9rem'}}>
          ⚠️ LLM no disponible. Ejecuta en el host: <code style={{background:'#450a0a',padding:'2px 6px',borderRadius:'4px'}}>setsid python3 /home/msi/proyectos/superagente/scripts/ollama_forward.py &</code>
        </div>
      )}
      {agents.length === 0 ? (
        <p style={{color:'#fde047'}}>Primero crea un agente en "Crear Agente".</p>
      ) : (
        <>
          <label>Seleccionar agente</label>
          <select value={selected} onChange={e => setSelected(e.target.value)}>
            <option value="">-- selecciona --</option>
            {agents.map(a => (
              <option key={a.id} value={a.id}>{a.name} ({a.id})</option>
            ))}
          </select>
          <div className="response-box" style={{minHeight:'250px',marginBottom:'1rem'}}>
            {!selected && <p style={{color:'#64748b'}}>Selecciona un agente para empezar.</p>}
            {messages.map((m, i) => (
              <div key={i} style={{marginBottom:'0.75rem'}}>
                <strong style={{color: m.role === 'user' ? '#38bdf8' : '#a78bfa'}}>
                  {m.role === 'user' ? 'Tú' : selected}:
                </strong>
                {m.role === 'assistant' && m.confidence !== undefined && (
                  <span style={{
                    display:'inline-block',marginLeft:'0.5rem',padding:'0.1rem 0.4rem',
                    borderRadius:'4px',fontSize:'0.7rem',fontWeight:600,
                    background: m.confidence >= 80 ? '#166534' : m.confidence >= 50 ? '#713f12' : '#7f1d1d',
                    color: m.confidence >= 80 ? '#86efac' : m.confidence >= 50 ? '#fde047' : '#fca5a5',
                  }}>
                    {m.confidence}%
                  </span>
                )}
                <span style={{marginLeft:'0.5rem',whiteSpace:'pre-wrap'}}>{m.content}</span>
              </div>
            ))}
            {loading && (
              <div style={{padding:'0.75rem',background:'#1e293b',borderRadius:'6px',marginTop:'0.5rem'}}>
                <div style={{display:'flex',alignItems:'center',gap:'0.75rem'}}>
                  <span style={{width:'12px',height:'12px',border:'2px solid #60a5fa',borderTopColor:'transparent',borderRadius:'50%',animation:'spin 1s linear infinite',display:'inline-block'}} />
                  <span style={{color:'#60a5fa',fontWeight:'bold'}}>Procesando...</span>
                </div>
                <p style={{color:'#94a3b8',fontSize:'0.8rem',marginTop:'0.5rem',marginBottom:0}}>
                  El modelo tarda 1-2 minutos en responder en CPU. No es un cuelgue.
                </p>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
          <form onSubmit={handleSend} style={{display:'flex',gap:'0.5rem'}}>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Escribe tu pregunta..."
              disabled={!selected || loading}
              style={{marginBottom:0}}
            />
            <button className="primary" type="submit" disabled={!selected || loading || !input.trim()} style={{whiteSpace:'nowrap',width:'auto'}}>
              Enviar
            </button>
          </form>
        </>
      )}
    </div>
  )
}
