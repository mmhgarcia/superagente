import { useState } from 'react'
import { generateAgent } from '../api'

export default function CreateAgent({ onCreated }) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await generateAgent(name, description)
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
      <p>Describe el agente que quieres generar.</p>
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
        <button className="primary" type="submit" disabled={loading}>
          {loading ? 'Generando...' : 'Generar agente'}
        </button>
      </form>
      {error && <div className="response-box" style={{color:'#fca5a5'}}>Error: {error}</div>}
      {result && (
        <div className="response-box">
          <div style={{marginBottom:'0.5rem'}}>
            <strong>{result.name}</strong>
            <span className={`status-badge status-${result.status}`} style={{marginLeft:'0.5rem'}}>
              {result.status}
            </span>
          </div>
          {result.response}
        </div>
      )}
    </div>
  )
}
