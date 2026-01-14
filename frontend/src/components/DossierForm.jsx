import { useState } from 'react'
import './DossierForm.css'

export default function DossierForm({ onSubmit, loading, error, status }) {
  const [url, setUrl] = useState('')
  const [audio, setAudio] = useState(null)
  const [audioName, setAudioName] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!url.trim()) {
      alert('Digite uma URL do YouTube')
      return
    }
    onSubmit({ url: url.trim(), audio })
  }

  const handleAudioChange = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      setAudio(file)
      setAudioName(file.name)
    }
  }

  const handleRemoveAudio = () => {
    setAudio(null)
    setAudioName('')
  }

  return (
    <div className="form-container">
      <form onSubmit={handleSubmit} className="dossier-form">
        <div className="form-section">
          <h2>📌 URL do Vídeo</h2>
          
          <div className="form-group">
            <label htmlFor="url">Link do YouTube</label>
            <input
              id="url"
              type="text"
              placeholder="https://www.youtube.com/watch?v=..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={loading}
              autoFocus
            />
            <small>
              Cole a URL completa ou o ID do vídeo
            </small>
          </div>
        </div>

        <div className="form-section">
          <h2>🎵 Arquivo de Áudio (opcional)</h2>
          <p className="section-hint">
            Se o vídeo não tiver transcrição oficial, você pode enviar um arquivo de áudio
          </p>

          {!audioName ? (
            <div className="file-upload">
              <input
                id="audio"
                type="file"
                accept="audio/mp3,audio/mp4,audio/wav,.mp3,.m4a,.wav"
                onChange={handleAudioChange}
                disabled={loading}
                className="file-input"
              />
              <label htmlFor="audio" className="file-label">
                <div className="upload-icon">📁</div>
                <div className="upload-text">
                  <strong>Clique para selecionar</strong>
                  <br />
                  <small>ou arraste um arquivo aqui</small>
                  <br />
                  <small style={{ fontSize: '0.75rem', marginTop: '0.25rem' }}>
                    MP3, M4A ou WAV (máx. 200MB)
                  </small>
                </div>
              </label>
            </div>
          ) : (
            <div className="file-selected">
              <div className="file-info">
                <span className="file-icon">✓</span>
                <div>
                  <strong>{audioName}</strong>
                  <br />
                  <small>{(audio.size / (1024 * 1024)).toFixed(2)} MB</small>
                </div>
              </div>
              <button
                type="button"
                onClick={handleRemoveAudio}
                disabled={loading}
                className="remove-btn"
              >
                ✕
              </button>
            </div>
          )}
        </div>

        {error && (
          <div className="error-box">
            <strong>⚠️ Erro:</strong> {error}
          </div>
        )}

        {status && (
          <div className="status-box">
            <div className="spinner"></div>
            <span>{status}</span>
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !url.trim()}
          className="submit-btn"
        >
          {loading ? 'Processando...' : '🚀 Gerar Dossiê'}
        </button>
      </form>
    </div>
  )
}
