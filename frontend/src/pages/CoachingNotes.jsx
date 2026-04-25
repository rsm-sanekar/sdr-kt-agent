import { useState, useRef } from 'react'
import { generateCoaching, approveCoaching } from '../api.js'
import ApprovalCard from '../components/ApprovalCard.jsx'

function ScoreBadge({ score }) {
  const color = score >= 70
    ? 'text-emerald-500'
    : score >= 45
      ? 'text-amber-500'
      : 'text-red-500'
  return (
    <div className="bg-white border-2 border-gray-200 rounded-lg p-4 flex items-center justify-between">
      <span className="font-semibold text-gray-700 text-sm">Call Score</span>
      <span className={`text-3xl font-extrabold ${color}`}>
        {score}<span className="text-sm font-normal text-gray-400">/100</span>
      </span>
    </div>
  )
}

function ScoreBreakdown({ breakdown }) {
  if (!breakdown) return null
  const rows = [
    { label: 'Opening',            key: 'opening',            max: 20 },
    { label: 'Discovery',          key: 'discovery',          max: 25 },
    { label: 'Objection Handling', key: 'objection_handling', max: 30 },
    { label: 'Close',              key: 'close',              max: 25 },
  ]
  return (
    <div className="bg-white border-2 border-gray-200 rounded-lg p-4 space-y-3">
      <h3 className="font-semibold text-gray-700 text-sm mb-1">Score Breakdown</h3>
      {rows.map(({ label, key, max }) => {
        const raw = breakdown[key] ?? 0
        const pct = Math.min(Math.round((raw / max) * 100), 100)
        const fill = pct >= 70
          ? 'bg-emerald-500'
          : pct >= 45
            ? 'bg-amber-400'
            : 'bg-red-400'
        return (
          <div key={key}>
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-gray-600 font-medium">{label}</span>
              <span className="text-gray-400">{raw}<span className="text-gray-300">/{max}</span></span>
            </div>
            <div className="bg-gray-100 rounded-full h-1.5">
              <div
                className={`${fill} h-1.5 rounded-full transition-all duration-700`}
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default function CoachingNotes() {
  const [sdrName, setSdrName] = useState('')
  const [callContext, setCallContext] = useState('')
  const [transcript, setTranscript] = useState('')
  const [fileName, setFileName] = useState('')
  const [isDragOver, setIsDragOver] = useState(false)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [approvalStatus, setApprovalStatus] = useState('idle')
  const fileRef = useRef(null)

  function readFile(file) {
    if (!file) return
    setFileName(file.name)
    const reader = new FileReader()
    reader.onload = e => setTranscript(e.target.result)
    reader.readAsText(file)
  }

  const canGenerate = sdrName.trim() && transcript.trim() && !loading

  async function handleGenerate() {
    if (!canGenerate) return
    setLoading(true)
    setError(null)
    setResult(null)
    setApprovalStatus('idle')
    try {
      const data = await generateCoaching({ sdr_name: sdrName.trim(), transcript, call_context: callContext })
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  // Mock returns flat structure: result.overall_score, result.what_worked, etc.
  const note = result || {}

  async function handleApprove() {
    try {
      await approveCoaching({
        note_id: result.note_id,
        sdr_name: sdrName,
        approved_note: JSON.stringify(result),
        was_edited: false,
        is_zero_edit: result?.is_zero_edit_candidate ?? false,
      })
      setApprovalStatus('approved')
    } catch (e) {
      setError(e.message)
    }
  }

  async function handleEdit(editedText) {
    try {
      await approveCoaching({
        note_id: result.note_id,
        sdr_name: sdrName,
        approved_note: editedText,
        was_edited: true,
        is_zero_edit: false,
      })
      setApprovalStatus('edited')
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-gray-900 mb-1">Coaching Notes</h1>
        <p className="text-gray-500">
          Upload a call transcript and get an AI-generated structured coaching note.
          Zero-edit approvals are stored as gold standard examples in the KB.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Left — Upload + inputs */}
        <div className="space-y-4">
          {/* Dashed upload zone */}
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragOver ? 'border-blue-400 bg-blue-50' : 'border-gray-300 bg-gray-50 hover:border-gray-400'
            }`}
            onClick={() => fileRef.current?.click()}
            onDragOver={e => { e.preventDefault(); setIsDragOver(true) }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={e => { e.preventDefault(); setIsDragOver(false); readFile(e.dataTransfer.files[0]) }}
          >
            <input
              ref={fileRef}
              type="file"
              accept=".txt,.vtt,.srt"
              className="hidden"
              onChange={e => readFile(e.target.files[0])}
            />
            {fileName ? (
              <div className="text-sm font-semibold text-gray-700">📄 {fileName}</div>
            ) : (
              <div className="text-gray-400 text-sm">
                <div className="text-2xl mb-2">📄</div>
                <div className="font-medium">Drop transcript or click to upload</div>
                <div className="text-xs mt-1 text-gray-300">.txt, .vtt, .srt</div>
              </div>
            )}
          </div>

          {/* Paste fallback */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Or paste transcript
            </label>
            <textarea
              rows={4}
              value={transcript}
              onChange={e => setTranscript(e.target.value)}
              placeholder="Paste the call transcript here…"
              className="w-full bg-gray-100 rounded-lg px-4 py-3 text-sm text-gray-900 placeholder-gray-400 focus:outline-none resize-none"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">SDR Name</label>
            <input
              type="text"
              value={sdrName}
              onChange={e => setSdrName(e.target.value)}
              placeholder="e.g. Casey Kim"
              className="w-full bg-gray-100 rounded-lg px-4 py-2.5 text-sm focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Call Context <span className="text-gray-400 font-normal">(optional)</span>
            </label>
            <input
              type="text"
              value={callContext}
              onChange={e => setCallContext(e.target.value)}
              placeholder="e.g. Cold call to VP Engineering at Acme Corp"
              className="w-full bg-gray-100 rounded-lg px-4 py-2.5 text-sm focus:outline-none"
            />
          </div>

          <button
            onClick={handleGenerate}
            disabled={!canGenerate}
            className="w-full bg-blue-500 text-white font-semibold py-2.5 rounded-md hover:bg-blue-600 hover:scale-105 transition-all disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100"
          >
            {loading ? 'Analyzing…' : 'Generate Coaching Note'}
          </button>

          {error && <p className="text-red-500 text-sm">{error}</p>}
        </div>

        {/* Right — Coaching note */}
        {result ? (
          <div className="space-y-4">
            {note.overall_score != null && <ScoreBadge score={note.overall_score} />}

            {note.score_breakdown && <ScoreBreakdown breakdown={note.score_breakdown} />}

            {note.what_worked?.length > 0 && (
              <div className="bg-emerald-50 border-2 border-emerald-200 rounded-lg p-4">
                <h3 className="font-bold text-emerald-700 text-sm mb-3">What Worked</h3>
                <ul className="space-y-2">
                  {note.what_worked.map((item, i) => (
                    <li key={i} className="text-sm text-emerald-800 flex gap-2">
                      <span className="shrink-0">✓</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {note.what_to_improve?.length > 0 && (
              <div className="bg-amber-50 border-2 border-amber-200 rounded-lg p-4">
                <h3 className="font-bold text-amber-700 text-sm mb-3">What to Improve</h3>
                <ul className="space-y-2">
                  {note.what_to_improve.map((item, i) => (
                    <li key={i} className="text-sm text-amber-800 flex gap-2">
                      <span className="shrink-0">→</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {note.language_alternatives?.length > 0 && (
              <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4">
                <h3 className="font-bold text-blue-700 text-sm mb-3">Language Alternatives</h3>
                <ul className="space-y-2">
                  {note.language_alternatives.map((item, i) => (
                    <li key={i} className="text-sm text-blue-800 flex gap-2">
                      <span className="shrink-0">💬</span>
                      <span>"{item}"</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-lg p-6 flex items-center justify-center text-gray-400 text-sm min-h-[300px]">
            {loading ? 'Analyzing transcript…' : 'Upload a transcript to generate a coaching note'}
          </div>
        )}
      </div>

      {result && (
        <ApprovalCard
          result={result}
          status={approvalStatus}
          onApprove={handleApprove}
          onEdit={handleEdit}
          onReject={() => setApprovalStatus('rejected')}
          editableContent={JSON.stringify(result, null, 2)}
        />
      )}
    </div>
  )
}
