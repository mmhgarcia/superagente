import { useState, useEffect } from 'react'
import { listAgents, deleteAgent, listSkills, updateAgent } from '../api'
import CreateAgent from './CreateAgent'

export default function AgentManager() {
  const [agents, setAgents] = useState([])
  const [skills, setSkills] = useState([])
  const [editing, setEditing] = useState(null)
  const [error, setError] = useState(null)
  const [showCreate, setShowCreate] = useState(false)
  const [historyAgent, setHistoryAgent] = useState(null)

  useEffect(() => {
    load()
    listSkills().then(d => setSkills(d.skills)).catch(() => {})
  }, [])

  function handleCreated() {
    setShowCreate(false)
    load()
  }

  async function load() {
    try {
      const d = await listAgents()
      setAgents(d.agents)
    } catch {}
  }

  async function handleDelete(agentId, name) {
    if (!confirm(`¿Eliminar al agente "${name}" (${agentId})?`)) return
    setError(null)
    try {
      await deleteAgent(agentId)
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  function startEdit(agent) {
    setEditing({
      id: agent.id,
      name: agent.name,
      description: agent.description,
      skills: [...(agent.skills || [])],
    })
    setError(null)
  }

  function cancelEdit() {
    setEditing(null)
    setError(null)
  }

  function toggleSkill(id) {
    setEditing(prev => ({
      ...prev,
      skills: prev.skills.includes(id) ? prev.skills.filter(s => s !== id) : [...prev.skills, id],
    }))
  }

  async function handleSave(e) {
    e.preventDefault()
    setError(null)
    try {
      await updateAgent(editing.id, {
        name: editing.name,
        description: editing.description,
        skills: editing.skills,
      })
      setEditing(null)
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="card">
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'0.5rem'}}>
        <div>
          <h2 style={{margin:0}}>Gestionar Agentes</h2>
          <p style={{margin:'0.25rem 0 0 0'}}>Lista, edita o elimina agentes existentes.</p>
        </div>
        <button
          className="primary"
          onClick={() => setShowCreate(true)}
          style={{fontSize:'1.25rem',fontWeight:'bold',width:'40px',height:'40px',padding:0,display:'flex',alignItems:'center',justifyContent:'center',borderRadius:'8px',flexShrink:0}}
          title="Crear nuevo agente"
        >+</button>
      </div>

      {showCreate && (
        <div style={{
          position:'fixed',top:0,left:0,right:0,bottom:0,
          background:'rgba(0,0,0,0.6)',zIndex:1000,
          display:'flex',alignItems:'center',justifyContent:'center',
          padding:'1rem',
        }} onClick={() => setShowCreate(false)}>
          <div style={{
            background:'#1e293b',borderRadius:'12px',padding:'1.5rem',
            maxWidth:'600px',width:'100%',maxHeight:'90vh',overflow:'auto',
            border:'1px solid #334155',
          }} onClick={e => e.stopPropagation()}>
            <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'1rem'}}>
              <h3 style={{margin:0}}>Crear nuevo agente</h3>
              <button onClick={() => setShowCreate(false)} style={{background:'transparent',border:'none',color:'#94a3b8',fontSize:'1.25rem',cursor:'pointer',padding:'0.25rem'}}>✕</button>
            </div>
            <CreateAgent onCreated={handleCreated} />
          </div>
        </div>
      )}

      {error && <p style={{color:'#fca5a5',fontSize:'0.875rem',marginBottom:'0.5rem'}}>{error}</p>}

      {agents.length === 0 ? (
        <p style={{color:'#fde047'}}>Aún no hay agentes. Presiona <strong>+</strong> para crear uno.</p>
      ) : (
        <div style={{display:'flex',flexDirection:'column',gap:'0.75rem'}}>
          {agents.map(a => (
            <div key={a.id} style={{
              padding:'0.75rem',background:'#0f172a',borderRadius:'8px',
              border:'1px solid #334155',
            }}>
              {editing && editing.id === a.id ? (
                <form onSubmit={handleSave}>
                  <label>Nombre</label>
                  <input value={editing.name} onChange={e => setEditing({...editing, name: e.target.value})} required />
                  <label>Descripción</label>
                  <textarea value={editing.description} onChange={e => setEditing({...editing, description: e.target.value})} required />
                  <label>Skills</label>
                  <div style={{display:'flex',flexWrap:'wrap',gap:'0.5rem',marginBottom:'1rem'}}>
                    {skills.map(s => (
                      <label key={s.id} style={{
                        display:'flex',alignItems:'center',gap:'0.375rem',
                        padding:'0.375rem 0.75rem',background:'#1e293b',borderRadius:'6px',
                        border: editing.skills.includes(s.id) ? '1px solid #38bdf8' : '1px solid #334155',
                        cursor:'pointer',fontSize:'0.8125rem'
                      }}>
                        <input type="checkbox" checked={editing.skills.includes(s.id)} onChange={() => toggleSkill(s.id)} style={{width:'auto',margin:0}} />
                        {s.name}
                      </label>
                    ))}
                  </div>
                  <div style={{display:'flex',gap:'0.5rem'}}>
                    <button className="primary" type="submit" style={{fontSize:'0.8125rem'}}>Guardar</button>
                    <button type="button" onClick={cancelEdit} style={{padding:'0.5rem 1rem',background:'transparent',border:'1px solid #334155',borderRadius:'6px',color:'#94a3b8',cursor:'pointer',fontSize:'0.8125rem'}}>Cancelar</button>
                  </div>
                </form>
              ) : (
                <>
                  <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start'}}>
                    <div style={{flex:1}}>
                      <div style={{fontWeight:600,fontSize:'0.875rem',marginBottom:'0.25rem'}}>
                        {a.name} <span className="tag">{a.id}</span>
                      </div>
                      <div style={{color:'#94a3b8',fontSize:'0.8125rem',marginBottom:'0.375rem'}}>{a.description}</div>
                      <div style={{display:'flex',gap:'0.25rem',flexWrap:'wrap'}}>
                        {(a.skills || []).map(s => <span key={s} className="tag">{s}</span>)}
                      </div>
                    </div>
                    <div style={{display:'flex',gap:'0.375rem',marginLeft:'1rem',flexShrink:0}}>
                      <button onClick={() => setHistoryAgent(a)} style={{background:'transparent',border:'1px solid #334155',borderRadius:'4px',color:'#a78bfa',cursor:'pointer',padding:'0.25rem 0.5rem',fontSize:'0.75rem'}} title="Ver historial">📋</button>
                      <button onClick={() => startEdit(a)} style={{background:'transparent',border:'1px solid #334155',borderRadius:'4px',color:'#38bdf8',cursor:'pointer',padding:'0.25rem 0.5rem',fontSize:'0.75rem'}}>✏️</button>
                      <button onClick={() => handleDelete(a.id, a.name)} style={{background:'transparent',border:'1px solid #334155',borderRadius:'4px',color:'#fca5a5',cursor:'pointer',padding:'0.25rem 0.5rem',fontSize:'0.75rem'}}>🗑️</button>
                    </div>
                  </div>
                  <div style={{fontSize:'0.75rem',color:'#64748b',marginTop:'0.5rem'}}>
                    {a.history?.length || 0} mensajes en historial
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      )}
      {historyAgent && (
        <div style={{
          position:'fixed',top:0,left:0,right:0,bottom:0,
          background:'rgba(0,0,0,0.6)',zIndex:1000,
          display:'flex',alignItems:'center',justifyContent:'center',
          padding:'1rem',
        }} onClick={() => setHistoryAgent(null)}>
          <div style={{
            background:'#1e293b',borderRadius:'12px',padding:'1.5rem',
            maxWidth:'700px',width:'100%',maxHeight:'90vh',overflow:'auto',
            border:'1px solid #334155',
          }} onClick={e => e.stopPropagation()}>
            <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'1rem'}}>
              <h3 style={{margin:0}}>Historial: {historyAgent.name}</h3>
              <button onClick={() => setHistoryAgent(null)} style={{background:'transparent',border:'none',color:'#94a3b8',fontSize:'1.25rem',cursor:'pointer',padding:'0.25rem'}}>✕</button>
            </div>
            {(historyAgent.history || []).length === 0 ? (
              <p style={{color:'#64748b'}}>Sin conversaciones aún.</p>
            ) : (
              <div style={{display:'flex',flexDirection:'column',gap:'0.75rem'}}>
                {historyAgent.history.map((m, i) => (
                  <div key={i} style={{
                    padding:'0.75rem',borderRadius:'8px',
                    background: m.role === 'user' ? '#0f172a' : '#1a2a4a',
                    border: '1px solid ' + (m.role === 'user' ? '#334155' : '#2a3a5a'),
                  }}>
                    <div style={{fontSize:'0.75rem',fontWeight:600,marginBottom:'0.25rem',color: m.role === 'user' ? '#38bdf8' : '#a78bfa'}}>
                      {m.role === 'user' ? '👤 Usuario' : '🤖 Asistente'}
                    </div>
                    <div style={{fontSize:'0.875rem',whiteSpace:'pre-wrap',color:'#e2e8f0'}}>{m.content}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

    </div>
  )
}
