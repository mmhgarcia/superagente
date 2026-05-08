import { useState, useEffect, useRef } from 'react'
import { listAgents, askAgent } from '../api'

export default function AgentChat() {
  const [agents, setAgents] = useState([])
  const [selected, setSelected] = useState('')
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    listAgents().then(d => setAgents(d.agents)).catch(() => {})
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
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Error: no se pudo obtener respuesta' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Probar agente</h2>
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
                <span style={{marginLeft:'0.5rem',whiteSpace:'pre-wrap'}}>{m.content}</span>
              </div>
            ))}
            {loading && <p style={{color:'#64748b'}}>Pensando...</p>}
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
