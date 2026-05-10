import { useState } from 'react'
import AgentChat from './components/AgentChat'
import AgentConfig from './components/AgentConfig'
import AgentManager from './components/AgentManager'

const TABS = [
  { key: 'manage', label: 'Gestionar Agentes' },
  { key: 'chat', label: 'Probar Agente' },
  { key: 'config', label: 'Configuración' },
]

export default function App() {
  const [tab, setTab] = useState('manage')

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
        {tab === 'manage' && <AgentManager />}
        {tab === 'chat' && <AgentChat />}
        {tab === 'config' && <AgentConfig />}
      </main>
    </div>
  )
}
