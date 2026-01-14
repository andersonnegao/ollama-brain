import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'
import DossierForm from './components/DossierForm'
import DossierResult from './components/DossierResult'
import TokenPrompt from './components/TokenPrompt'

function App() {
  const [apiToken, setApiToken] = useState('')
  const [apiBase, setApiBase] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [status, setStatus] = useState('')

  useEffect(() => {
    // Load token from localStorage
    const savedToken = localStorage.getItem('api_token')
    const savedBase = localStorage.getItem('api_base') || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'
    
    if (savedToken) setApiToken(savedToken)
    setApiBase(savedBase)
  }, [])

  const handleTokenSubmit = (token, base) => {
    localStorage.setItem('api_token', token)
    localStorage.setItem('api_base', base)
    setApiToken(token)
    setApiBase(base)
    setError('')
  }

  const handleFormSubmit = async (formData) => {
    setLoading(true)
    setError('')
    setStatus('')
    setResult(null)

    try {
      setStatus('Validando vídeo...')
      
      const data = new FormData()
      data.append('url', formData.url)
      if (formData.audio) {
        data.append('audio', formData.audio)
      }

      const response = await axios.post(
        `${apiBase}/dossier`,
        data,
        {
          headers: {
            Authorization: `Bearer ${apiToken}`,
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
              setStatus(`Enviando arquivo... ${percent}%`)
            }
          }
        }
      )

      setStatus('Analisando com Ollama...')
      
      setResult(response.data)
      setStatus('')
    } catch (err) {
      if (err.response?.status === 422) {
        setError(err.response.data.detail || 'Nenhuma transcrição encontrada. Envie um arquivo de áudio.')
      } else if (err.response?.status === 401) {
        setError('Token inválido. Verifique suas credenciais.')
        setApiToken('')
        localStorage.removeItem('api_token')
      } else {
        setError(err.response?.data?.detail || 'Erro ao processar. Tente novamente.')
      }
    } finally {
      setLoading(false)
      setStatus('')
    }
  }

  if (!apiToken) {
    return <TokenPrompt onSubmit={handleTokenSubmit} defaultBase={apiBase} />
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🎥 Dossiê de Vídeos</h1>
        <p>Análise inteligente de conteúdo com transcrição automática</p>
        <button 
          className="logout-btn"
          onClick={() => {
            localStorage.removeItem('api_token')
            setApiToken('')
          }}
        >
          Sair
        </button>
      </header>

      <main className="app-main">
        {!result ? (
          <>
            <DossierForm 
              onSubmit={handleFormSubmit}
              loading={loading}
              error={error}
              status={status}
            />
          </>
        ) : (
          <>
            <DossierResult 
              result={result}
              onReset={() => {
                setResult(null)
                setError('')
              }}
            />
          </>
        )}
      </main>
    </div>
  )
}

export default App
