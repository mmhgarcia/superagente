import { useState } from 'react'

export default function AgentConfig() {
  const [model, setModel] = useState('tinyllama-1.1b-chat-v1.0')
  const [maxTokens, setMaxTokens] = useState(300)
  const [temperature, setTemperature] = useState(0.7)
  const [saved, setSaved] = useState(false)

  function handleSave() {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="card">
      <h2>Configuración de la Fábrica</h2>
      <p>Ajusta los parámetros por defecto para la generación de agentes.</p>

      <label>Modelo LLM</label>
      <select value={model} onChange={e => setModel(e.target.value)}>
        <option value="tinyllama-1.1b-chat-v1.0">TinyLlama 1.1B</option>
        <option value="mistralai/mistral-7b-instruct-v0.3">Mistral 7B</option>
        <option value="google/gemma-4-e2b">Gemma 4B</option>
      </select>

      <label>Máximo de tokens</label>
      <input type="number" value={maxTokens} onChange={e => setMaxTokens(Number(e.target.value))} min={50} max={4096} />

      <label>Temperatura (creatividad)</label>
      <input type="range" min="0" max="2" step="0.1" value={temperature} onChange={e => setTemperature(Number(e.target.value))} />
      <span style={{color:'#94a3b8',fontSize:'0.875rem',display:'block',marginBottom:'1rem'}}>{temperature.toFixed(1)}</span>

      <button className="primary" onClick={handleSave}>
        {saved ? '✓ Guardado' : 'Guardar configuración'}
      </button>

      <hr style={{borderColor:'#334155',margin:'1.5rem 0'}} />

      <h2 style={{fontSize:'1rem',marginBottom:'1rem'}}>Skills disponibles</h2>
      <p>Skills que la fábrica puede asignar a los agentes (próximamente).</p>
      <div style={{display:'flex',flexWrap:'wrap',gap:'0.5rem'}}>
        {['base_chat', 'busqueda_web', 'procesar_pdf', 'analisis_datos', 'traductor'].map(s => (
          <span key={s} className="tag">{s} ✏️</span>
        ))}
      </div>
    </div>
  )
}
