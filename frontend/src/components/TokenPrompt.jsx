import { useState } from 'react'
import './TokenPrompt.css'

export default function TokenPrompt({ onSubmit, defaultBase }) {
  const [token, setToken] = useState('')
  const [base, setBase] = useState(defaultBase || 'http://localhost:8080')
  const [error, setError] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!token.trim()) {
      setError('Token é obrigatório')
      return
    }
    onSubmit(token.trim(), base.trim())
  }

  return (
    <div className="token-prompt-container">
      <div className="token-prompt-card">
        <h2>🔐 Autenticação</h2>
        <p>Digite seu token de acesso para continuar</p>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="base">URL da API</label>
            <input
              id="base"
              type="text"
              placeholder="https://api.example.com"
              value={base}
              onChange={(e) => setBase(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label htmlFor="token">Token</label>
            <input
              id="token"
              type="password"
              placeholder="Seu token de acesso"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              autoFocus
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="submit-btn">
            Acessar
          </button>
        </form>

        <p className="hint">
          💡 O token será armazenado localmente no seu navegador.
        </p>
      </div>
    </div>
  )
}
