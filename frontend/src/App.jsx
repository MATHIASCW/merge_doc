import { useRef, useState } from 'react'
import {
  ArrowDown, ArrowUp, FileArchive, FileImage, FileText, GripVertical,
  Layers3, LoaderCircle, Plus, Settings2, Sparkles, Trash2, Upload, X,
} from 'lucide-react'

const ACCEPTED = '.pdf,.png,.jpg,.jpeg,.docx,.doc,.odt'
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function fileIcon(file) {
  return file.type.startsWith('image/') ? <FileImage /> : file.name.toLowerCase().endsWith('.pdf') ? <FileText /> : <FileArchive />
}

function App() {
  const inputRef = useRef(null)
  const [files, setFiles] = useState([])
  const [watermark, setWatermark] = useState('')
  const [opacity, setOpacity] = useState(0.15)
  const [size, setSize] = useState(40)
  const [outputName, setOutputName] = useState('merged.pdf')
  const [dragIndex, setDragIndex] = useState(null)
  const [isMerging, setIsMerging] = useState(false)
  const [message, setMessage] = useState('')

  function addFiles(selected) {
    const incoming = Array.from(selected).filter((file) => {
      const extension = `.${file.name.split('.').pop().toLowerCase()}`
      return ACCEPTED.includes(extension)
    })
    setFiles((current) => [...current, ...incoming])
    setMessage('')
  }

  function moveFile(index, direction) {
    setFiles((current) => {
      const next = [...current]
      const target = index + direction
      if (target < 0 || target >= next.length) return current
      ;[next[index], next[target]] = [next[target], next[index]]
      return next
    })
  }

  function removeFile(index) {
    setFiles((current) => current.filter((_, fileIndex) => fileIndex !== index))
  }

  async function mergeFiles() {
    if (!files.length) {
      setMessage('Add at least one file before merging.')
      return
    }
    setIsMerging(true)
    setMessage('')
    const form = new FormData()
    files.forEach((file) => form.append('files', file, file.name))
    form.append('watermark', watermark)
    form.append('watermark_opacity', opacity)
    form.append('watermark_size', size)
    form.append('output_name', outputName)

    try {
      const response = await fetch(`${API_URL}/api/merge`, { method: 'POST', body: form })
      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(error.detail || 'Merging failed.')
      }
      const blob = await response.blob()
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = outputName.endsWith('.pdf') ? outputName : `${outputName}.pdf`
      link.click()
      URL.revokeObjectURL(link.href)
      setMessage('PDF created and downloaded to output/.')
    } catch (error) {
      setMessage(error.message || 'Unable to reach the Python API.')
    } finally {
      setIsMerging(false)
    }
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand"><span className="brand-mark"><Layers3 size={19} /></span><span>MERGE<span className="brand-accent">DOC</span></span></div>
        <span className="status"><span className="status-dot" /> local engine ready</span>
      </header>

      <section className="intro">
        <div>
          <p className="eyebrow"><Sparkles size={15} /> DOCUMENT WORKSPACE</p>
          <h1>One single file.<br /><em>Your entire dossier.</em></h1>
          <p className="lede">Combine PDFs, images, and Office documents in exactly the order you need.</p>
        </div>
        <div className="counter"><strong>{String(files.length).padStart(2, '0')}</strong><span>file{files.length !== 1 ? 's' : ''}<br />in the stack</span></div>
      </section>

      <section className="workspace">
        <div className="files-panel">
          <div className="section-heading"><div><span className="section-kicker">01 / CONTENT</span><h2>Your file stack</h2></div><button className="icon-button" title="Add files" onClick={() => inputRef.current?.click()}><Plus size={19} /></button></div>
          <input ref={inputRef} type="file" accept={ACCEPTED} multiple hidden onChange={(event) => addFiles(event.target.files)} />

          <div className="dropzone" onClick={() => inputRef.current?.click()} onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); addFiles(event.dataTransfer.files) }}>
            <div className="upload-icon"><Upload size={21} /></div><div><strong>Drop your files here</strong><span>or click to browse · PDF, PNG, JPG, DOCX</span></div><kbd>⌘ K</kbd>
          </div>

          {files.length === 0 ? <div className="empty-state"><FileText size={30} strokeWidth={1.3} /><p>The stack is empty</p><span>Add files from your document set to get started.</span></div> : <div className="file-list">{files.map((file, index) => <article className={`file-row ${dragIndex === index ? 'is-dragging' : ''}`} key={`${file.name}-${index}`} draggable onDragStart={() => setDragIndex(index)} onDragOver={(event) => event.preventDefault()} onDrop={() => { if (dragIndex !== null && dragIndex !== index) { const reordered = [...files]; const [item] = reordered.splice(dragIndex, 1); reordered.splice(index, 0, item); setFiles(reordered) }; setDragIndex(null) }} onDragEnd={() => setDragIndex(null)}>
            <GripVertical className="grip" size={17} /><span className="file-type">{fileIcon(file)}</span><div className="file-details"><strong>{file.name}</strong><span>{(file.size / 1024 / 1024).toFixed(2)} MB · {file.name.split('.').pop().toUpperCase()}</span></div><span className="order">{String(index + 1).padStart(2, '0')}</span><div className="row-actions"><button title="Move up" onClick={() => moveFile(index, -1)} disabled={index === 0}><ArrowUp size={15} /></button><button title="Move down" onClick={() => moveFile(index, 1)} disabled={index === files.length - 1}><ArrowDown size={15} /></button><button title="Remove" onClick={() => removeFile(index)}><X size={16} /></button></div>
          </article>)}</div>}
        </div>

        <aside className="settings-panel"><div className="section-heading"><div><span className="section-kicker">02 / OUTPUT</span><h2>Settings</h2></div><Settings2 size={19} className="muted-icon" /></div>
          <label>File name<input value={outputName} onChange={(event) => setOutputName(event.target.value)} /></label>
          <div className="setting-divider" /><label>Watermark <span className="optional">OPTIONAL</span><input placeholder="Ex. CONFIDENTIAL" value={watermark} onChange={(event) => setWatermark(event.target.value)} /></label>
          <div className="range-label"><label htmlFor="opacity">Opacity</label><output>{Math.round(opacity * 100)}%</output></div><input id="opacity" type="range" min="0" max="1" step="0.05" value={opacity} onChange={(event) => setOpacity(event.target.value)} />
          <div className="range-label"><label htmlFor="size">Size</label><output>{size} pt</output></div><input id="size" type="range" min="8" max="100" step="1" value={size} onChange={(event) => setSize(event.target.value)} />
          <div className="settings-note"><Sparkles size={16} /><span>Your result will be saved to <b>output/</b> and downloaded automatically.</span></div>
          <button className="merge-button" onClick={mergeFiles} disabled={isMerging}>{isMerging ? <LoaderCircle className="spin" size={19} /> : <Layers3 size={19} />} {isMerging ? 'Merging…' : 'Merge files'}</button>
          {message && <p className={`message ${message.includes('created') ? 'success' : 'error'}`}>{message}</p>}
        </aside>
      </section>
      <footer><span>MERGE DOC · local processing</span><span>Your files never leave your machine.</span></footer>
    </main>
  )
}

export default App
