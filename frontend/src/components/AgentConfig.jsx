import { useState, useEffect } from 'react'
import { listSkills } from '../api'

export default function AgentConfig() {
  const [skills, setSkills] = useState([])
  const [model, setModel] = useState('tinyllama-1.1b-chat-v1.0')
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    listSkills().then(d => setSkills(d.skills)).catch(() => {})
  }, [])

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

      <button className="primary" onClick={handleSave} style={{marginBottom:'1.5rem'}}>
        {saved ? '✓ Guardado' : 'Guardar configuración'}
      </button>

      <hr style={{borderColor:'#334155',marginBottom:'1.5rem'}} />

      <h2 style={{fontSize:'1rem',marginBottom:'1rem'}}>Almacén de Skills</h2>
      <p>Habilidades disponibles en la fábrica.</p>
      {skills.length === 0 ? (
        <p style={{color:'#64748b'}}>No hay skills cargadas.</p>
      ) : (
        <div style={{display:'flex',flexDirection:'column',gap:'0.5rem'}}>
          {skills.map(s => (
            <div key={s.id} style={{
              padding:'0.75rem',background:'#0f172a',borderRadius:'8px',
              border:'1px solid #334155'
            }}>
              <div style={{fontWeight:600,fontSize:'0.875rem',marginBottom:'0.25rem'}}>
                {s.name} <span className="tag">{s.id}</span>
              </div>
              <div style={{color:'#94a3b8',fontSize:'0.8125rem'}}>{s.description}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
