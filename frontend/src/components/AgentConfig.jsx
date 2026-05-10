import { useState, useEffect } from 'react'
import { listSkills, addSkill, updateSkill, deleteSkill, getConfig, saveConfig } from '../api'

export default function AgentConfig() {
  const [model, setModel] = useState('qwen2.5-coder:7b')
  const [maxTokens, setMaxTokens] = useState(1024)
  const [temperature, setTemperature] = useState(0.7)
  const [saved, setSaved] = useState(false)
  const [skills, setSkills] = useState([])

  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({ id: '', name: '', description: '', prompt_hint: '' })
  const [error, setError] = useState(null)

  useEffect(() => {
    loadSkills()
    loadConfig()
  }, [])

  function loadSkills() {
    listSkills().then(d => setSkills(d.skills)).catch(() => {})
  }

  async function loadConfig() {
    try {
      const cfg = await getConfig()
      setModel(cfg.model || 'qwen2.5-coder:7b')
      setMaxTokens(cfg.max_tokens || 1024)
      setTemperature(cfg.temperature ?? 0.7)
    } catch {}
  }

  async function handleSave() {
    setSaved(false)
    setError(null)
    try {
      await saveConfig({ model, max_tokens: maxTokens, temperature })
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch (err) {
      setError(err.message)
    }
  }

  function resetForm() {
    setForm({ id: '', name: '', description: '', prompt_hint: '' })
    setEditing(null)
    setShowForm(false)
    setError(null)
  }

  function openNew() {
    resetForm()
    setShowForm(true)
  }

  function openEdit(skill) {
    setForm({ id: skill.id, name: skill.name, description: skill.description, prompt_hint: skill.prompt_hint || '' })
    setEditing(skill.id)
    setShowForm(true)
    setError(null)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    try {
      if (editing) {
        await updateSkill(editing, { name: form.name, description: form.description, prompt_hint: form.prompt_hint })
      } else {
        await addSkill(form.id, form.name, form.description, form.prompt_hint)
      }
      resetForm()
      loadSkills()
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleDelete(skillId) {
    if (!confirm(`¿Eliminar skill "${skillId}"?`)) return
    try {
      await deleteSkill(skillId)
      loadSkills()
    } catch (err) {
      setError(err.message)
    }
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

      {error && <p style={{color:'#fca5a5',fontSize:'0.875rem',marginTop:'0.5rem'}}>{error}</p>}

      <hr style={{borderColor:'#334155',margin:'1.5rem 0'}} />

      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'1rem'}}>
        <h2 style={{fontSize:'1rem',margin:0}}>Almacén de Skills</h2>
        <button className="primary" onClick={openNew} style={{fontSize:'0.75rem',padding:'0.375rem 0.75rem'}}>+ Nueva skill</button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} style={{background:'#0f172a',padding:'1rem',borderRadius:'8px',marginBottom:'1rem',border:'1px solid #334155'}}>
          {!editing && (
            <>
              <label>ID (identificador único)</label>
              <input value={form.id} onChange={e => setForm({...form, id: e.target.value})} placeholder="ej. busqueda_web" required />
            </>
          )}
          <label>Nombre</label>
          <input value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="ej. Búsqueda web" required />
          <label>Descripción</label>
          <textarea value={form.description} onChange={e => setForm({...form, description: e.target.value})} placeholder="Describe la skill..." required />
          <label>Prompt hint (instrucción para el LLM)</label>
          <textarea value={form.prompt_hint} onChange={e => setForm({...form, prompt_hint: e.target.value})} placeholder="Cuando el usuario pida X, haz Y..." />
          <div style={{display:'flex',gap:'0.5rem'}}>
            <button className="primary" type="submit" style={{fontSize:'0.8125rem'}}>
              {editing ? 'Guardar cambios' : 'Crear skill'}
            </button>
            <button type="button" onClick={resetForm} style={{padding:'0.5rem 1rem',background:'transparent',border:'1px solid #334155',borderRadius:'6px',color:'#94a3b8',cursor:'pointer'}}>
              Cancelar
            </button>
          </div>
        </form>
      )}

      {skills.length === 0 ? (
        <p style={{color:'#64748b'}}>No hay skills cargadas.</p>
      ) : (
        <div style={{display:'flex',flexDirection:'column',gap:'0.5rem'}}>
          {skills.map(s => (
            <div key={s.id} style={{
              padding:'0.75rem',background:'#0f172a',borderRadius:'8px',
              border:'1px solid #334155',display:'flex',justifyContent:'space-between',alignItems:'flex-start'
            }}>
              <div style={{flex:1}}>
                <div style={{fontWeight:600,fontSize:'0.875rem',marginBottom:'0.25rem'}}>
                  {s.name} <span className="tag">{s.id}</span>
                </div>
                <div style={{color:'#94a3b8',fontSize:'0.8125rem'}}>{s.description}</div>
                {s.prompt_hint && <div style={{color:'#64748b',fontSize:'0.75rem',marginTop:'0.25rem'}}>→ {s.prompt_hint}</div>}
              </div>
              <div style={{display:'flex',gap:'0.375rem',marginLeft:'1rem'}}>
                <button onClick={() => openEdit(s)} style={{background:'transparent',border:'1px solid #334155',borderRadius:'4px',color:'#38bdf8',cursor:'pointer',padding:'0.25rem 0.5rem',fontSize:'0.75rem'}}>✏️</button>
                <button onClick={() => handleDelete(s.id)} style={{background:'transparent',border:'1px solid #334155',borderRadius:'4px',color:'#fca5a5',cursor:'pointer',padding:'0.25rem 0.5rem',fontSize:'0.75rem'}}>🗑️</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
