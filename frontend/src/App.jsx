import { useState } from 'react'
import CreateAgent from './components/CreateAgent'
import AgentChat from './components/AgentChat'
import AgentConfig from './components/AgentConfig'

const TABS = [
  { key: 'create', label: 'Crear Agente' },
  { key: 'chat', label: 'Probar Agente' },
  { key: 'config', label: 'Configuración' },
]

export default function App() {
  const [tab, setTab] = useState('create')
  const [lastAgent, setLastAgent] = useState(null)
  const [agents, setAgents] = useState([])

  return (
    <div className="app">
      <header>
        <h1>⚙️ Smart Factory de Agentes</h1>
        <nav>
          {TABS.map(t => (
            <button
              key={t.key}
              className={tab === t.key ? 'active' : ''}
              onClick={() => setTab(t.key)}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </header>

      <main>
        {tab === 'create' && (
          <CreateAgent
            onCreated={(agent) => {
              setLastAgent(agent)
              setAgents(prev => [...prev, agent])
              setTab('chat')
            }}
          />
        )}
        {tab === 'chat' && <AgentChat agent={lastAgent} agents={agents} />}
        {tab === 'config' && <AgentConfig />}
      </main>
    </div>
  )
}
