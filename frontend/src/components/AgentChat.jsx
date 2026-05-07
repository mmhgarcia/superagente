import { useState } from 'react'

export default function AgentChat({ agent, agents }) {
  const [selected, setSelected] = useState(agent?.name || '')
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')

  const currentAgent = agents.find(a => a.name === selected)

  function handleSend(e) {
    e.preventDefault()
    if (!input.trim()) return
    setMessages(prev => [...prev, { role: 'user', text: input }, { role: 'agent', text: `[${selected}] aún no procesa consultas. La Fase 2 implementará el chat real.` }])
    setInput('')
  }

  return (
    <div className="card">
      <h2>Probar agente</h2>
      {agents.length === 0 ? (
        <p style={{color:'#fde047'}}>Primero crea un agente en la pestaña "Crear Agente".</p>
      ) : (
        <>
          <label>Seleccionar agente</label>
          <select value={selected} onChange={e => setSelected(e.target.value)}>
            {agents.map(a => (
              <option key={a.name} value={a.name}>{a.name} ({a.status})</option>
            ))}
          </select>
          <div className="response-box" style={{minHeight:'200px',marginBottom:'1rem'}}>
            {messages.length === 0 && <p style={{color:'#64748b'}}>Envíale una pregunta al agente...</p>}
            {messages.map((m, i) => (
              <div key={i} style={{marginBottom:'0.75rem'}}>
                <strong style={{color: m.role === 'user' ? '#38bdf8' : '#a78bfa'}}>
                  {m.role === 'user' ? 'Tú' : selected}:
                </strong>
                <span style={{marginLeft:'0.5rem'}}>{m.text}</span>
              </div>
            ))}
          </div>
          <form onSubmit={handleSend} style={{display:'flex',gap:'0.5rem'}}>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Escribe tu pregunta..."
              style={{marginBottom:0}}
            />
            <button className="primary" type="submit" style={{whiteSpace:'nowrap',width:'auto'}}>
              Enviar
            </button>
          </form>
          <p style={{fontSize:'0.75rem',color:'#64748b',marginTop:'0.5rem'}}>
            ⚡ Chat real disponible en Fase 2
          </p>
        </>
      )}
    </div>
  )
}
