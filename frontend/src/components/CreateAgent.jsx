import { useState, useEffect } from 'react'
import { createAgent, listSkills } from '../api'

export default function CreateAgent({ onCreated }) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [allSkills, setAllSkills] = useState([])
  const [selectedSkills, setSelectedSkills] = useState(['base_chat'])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    listSkills().then(d => setAllSkills(d.skills)).catch(() => {})
  }, [])

  function toggleSkill(id) {
    setSelectedSkills(prev =>
      prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]
    )
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await createAgent(name, description, selectedSkills)
      setResult(data.agent)
      onCreated(data.agent)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Crear nuevo agente</h2>
      <p>Configura un agente con nombre, propósito y habilidades.</p>
      <form onSubmit={handleSubmit}>
        <label>Nombre del agente</label>
        <input
          value={name}
          onChange={e => setName(e.target.value)}
          placeholder="ej. asistente-soporte"
          required
        />
        <label>Descripción / propósito</label>
        <textarea
          value={description}
          onChange={e => setDescription(e.target.value)}
          placeholder="ej. responde preguntas técnicas sobre programación"
          required
        />
        <label>Skills (habilidades)</label>
        <div style={{display:'flex',flexWrap:'wrap',gap:'0.5rem',marginBottom:'1rem'}}>
          {allSkills.map(s => (
            <label key={s.id} style={{
              display:'flex',alignItems:'center',gap:'0.375rem',
              padding:'0.375rem 0.75rem',background:'#0f172a',borderRadius:'6px',
              border: selectedSkills.includes(s.id) ? '1px solid #38bdf8' : '1px solid #334155',
              cursor:'pointer',fontSize:'0.8125rem'
            }}>
              <input
                type="checkbox"
                checked={selectedSkills.includes(s.id)}
                onChange={() => toggleSkill(s.id)}
                style={{width:'auto',margin:0}}
              />
              {s.name}
            </label>
          ))}
        </div>
        <button className="primary" type="submit" disabled={loading}>
          {loading ? 'Generando...' : 'Generar agente'}
        </button>
      </form>
      {error && <div className="response-box" style={{color:'#fca5a5'}}>Error: {error}</div>}
      {result && (
        <div className="response-box">
          <div style={{marginBottom:'0.5rem'}}>
            <strong>{result.name}</strong> <span className="tag">{result.id}</span>
            <div style={{marginTop:'0.25rem',display:'flex',gap:'0.25rem',flexWrap:'wrap'}}>
              {result.skills.map(s => <span key={s} className="tag">{s}</span>)}
            </div>
          </div>
          <div style={{color:'#94a3b8',fontSize:'0.8125rem'}}>Agente creado correctamente</div>
        </div>
      )}
    </div>
  )
}
