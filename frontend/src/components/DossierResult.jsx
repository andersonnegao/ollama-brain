import { useState } from 'react'
import './DossierResult.css'

export default function DossierResult({ result, onReset }) {
  const [activeTab, setActiveTab] = useState('dossier')

  const handleCopyMarkdown = () => {
    navigator.clipboard.writeText(result.markdown)
    alert('✓ Markdown copiado para a área de transferência!')
  }

  const handleDownloadMarkdown = () => {
    const element = document.createElement('a')
    const file = new Blob([result.markdown], { type: 'text/markdown' })
    element.href = URL.createObjectURL(file)
    element.download = `dossier_${result.meta.video_id}.md`
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  const handleDownloadTranscript = () => {
    const element = document.createElement('a')
    const file = new Blob([result.transcript], { type: 'text/plain' })
    element.href = URL.createObjectURL(file)
    element.download = `transcript_${result.meta.video_id}.txt`
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  // Extract dossier content (remove frontmatter and header)
  const dossierLines = result.markdown.split('\n')
  const startIdx = dossierLines.findIndex(line => line === '# 🎥 Dossiê do vídeo')
  const transcriptIdx = dossierLines.findIndex(line => line === '# 📝 Transcrição (bruta)')
  
  const dossierContent = dossierLines.slice(startIdx + 1, transcriptIdx).join('\n').trim()
  const transcriptContent = dossierLines.slice(transcriptIdx + 1).join('\n').trim()

  return (
    <div className="result-container">
      <div className="result-header">
        <div className="result-meta">
          <h2>✓ Dossiê Gerado</h2>
          <div className="meta-info">
            <span>🎥 {result.meta.video_id}</span>
            <span>📊 {result.meta.used === 'youtube' ? 'Transcrição Oficial' : 'Whisper'}</span>
            <span>🤖 {result.meta.model}</span>
          </div>
        </div>
        <button onClick={onReset} className="back-btn">
          ← Novo Dossiê
        </button>
      </div>

      <div className="tabs">
        <button
          className={`tab-btn ${activeTab === 'dossier' ? 'active' : ''}`}
          onClick={() => setActiveTab('dossier')}
        >
          📋 Dossiê
        </button>
        <button
          className={`tab-btn ${activeTab === 'transcript' ? 'active' : ''}`}
          onClick={() => setActiveTab('transcript')}
        >
          📝 Transcrição
        </button>
      </div>

      <div className="content-area">
        {activeTab === 'dossier' && (
          <>
            <div className="markdown-content">
              <div dangerouslySetInnerHTML={{ __html: markdownToHtml(dossierContent) }} />
            </div>
            <div className="action-buttons">
              <button onClick={handleCopyMarkdown} className="action-btn primary">
                📋 Copiar Markdown
              </button>
              <button onClick={handleDownloadMarkdown} className="action-btn">
                ⬇️ Baixar .md
              </button>
            </div>
          </>
        )}

        {activeTab === 'transcript' && (
          <>
            <div className="transcript-content">
              <p>{transcriptContent}</p>
            </div>
            <div className="action-buttons">
              <button onClick={handleDownloadTranscript} className="action-btn">
                ⬇️ Baixar .txt
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

// Simple markdown to HTML converter
function markdownToHtml(markdown) {
  let html = markdown
    // Headers
    .replace(/^### (.*?)$/gm, '<h3>$1</h3>')
    .replace(/^## (.*?)$/gm, '<h2>$1</h2>')
    .replace(/^# (.*?)$/gm, '<h1>$1</h1>')
    // Bold
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Blockquotes
    .replace(/^> (.*?)$/gm, '<blockquote>$1</blockquote>')
    // Code blocks
    .replace(/```(.*?)```/gs, '<pre><code>$1</code></pre>')
    // Inline code
    .replace(/`(.*?)`/g, '<code>$1</code>')
    // Links
    .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')
    // Lists
    .replace(/^\- (.*?)$/gm, '<li>$1</li>')
    // Line breaks and paragraphs
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')

  html = '<p>' + html + '</p>'
  html = html.replace(/<li>/g, '<li>')
  html = html.replace(/<\/li>/g, '</li>')

  // Fix list wrapper
  html = html.replace(/<p><li>/g, '<ul><li>')
  html = html.replace(/<\/li><p>/g, '</li></ul><p>')

  return html
}
