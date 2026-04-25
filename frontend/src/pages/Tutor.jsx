import { useState } from 'react'
import { askTutor, approveTutor } from '../api.js'
import ApprovalCard from '../components/ApprovalCard.jsx'

const SUGGESTED = [
  'What is MEDDIC?',
  'Can you just send me an email with the info?',
  'What is the difference between a champion and an economic buyer?',
  'How many touches before I stop reaching out?',
  'How do I cold call a CFO?',
]

export default function Tutor() {
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [approvalStatus, setApprovalStatus] = useState('idle')

  async function handleAsk() {
    if (!question.trim() || loading) return
    setLoading(true)
    setError(null)
    setResult(null)
    setApprovalStatus('idle')
    try {
      const data = await askTutor(question.trim())
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleApprove() {
    try {
      await approveTutor({ question, answer: result.answer, pair_id: result.pair_id, was_edited: false })
      setApprovalStatus('approved')
    } catch (e) {
      setError(e.message)
    }
  }

  async function handleEdit(editedText) {
    try {
      await approveTutor({ question, answer: editedText, pair_id: result.pair_id, was_edited: true })
      setApprovalStatus('edited')
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-gray-900 mb-1">AI Tutor</h1>
        <p className="text-gray-500">Ask any question about Salesforce SDR processes — answers are cited from the knowledge base.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Left — Input */}
        <div>
          <textarea
            rows={5}
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleAsk() }}
            placeholder="e.g. How do I handle the 'send me an email' objection?"
            className="w-full bg-gray-100 rounded-lg p-4 text-sm text-gray-900 placeholder-gray-400 focus:outline-none resize-none"
          />

          <div className="mt-3 mb-4">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Suggested</p>
            <div className="flex flex-wrap gap-2">
              {SUGGESTED.map(q => (
                <button
                  key={q}
                  onClick={() => { setQuestion(q); setResult(null); setApprovalStatus('idle'); setError(null) }}
                  className="text-xs font-medium bg-white border border-gray-200 text-gray-600 px-3 py-1.5 rounded-full hover:border-blue-400 hover:text-blue-600 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleAsk}
              disabled={loading || !question.trim()}
              className="bg-blue-500 text-white font-semibold px-6 py-2.5 rounded-md hover:bg-blue-600 hover:scale-105 transition-all disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100"
            >
              {loading ? 'Thinking…' : 'Ask'}
            </button>
            <span className="text-xs text-gray-400">⌘ + Enter</span>
          </div>

          {error && <p className="text-red-500 text-sm mt-3">{error}</p>}
        </div>

        {/* Right — Answer */}
        <div>
          {result ? (
            <div className="bg-white border-2 border-gray-200 rounded-lg p-6">
              {/* Flagged warning */}
              {result.flagged && (
                <div className="bg-amber-50 border-2 border-amber-500 rounded-lg p-3 mb-4 text-amber-800 text-xs font-medium">
                  Low confidence — this answer may not be fully grounded in the KB. Review carefully before approving.
                </div>
              )}

              <p className="text-gray-800 text-sm leading-relaxed mb-5 whitespace-pre-wrap">{result.answer}</p>

              {/* Sources */}
              {result.sources?.length > 0 && (
                <div className="mb-4">
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Sources</p>
                  <div className="flex flex-wrap gap-2">
                    {result.sources.map((src, i) => (
                      <span key={i} className="bg-blue-100 text-blue-700 text-xs font-medium px-3 py-1 rounded-full">
                        [{i + 1}] {typeof src === 'object' ? src.source : src}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Confidence bar */}
              {result.confidence_score != null && (
                <div>
                  <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                    <span>Confidence</span>
                    <span className="font-semibold">{Math.round(result.confidence_score * 100)}%</span>
                  </div>
                  <div className="bg-gray-100 rounded-full h-1.5">
                    <div
                      className="bg-blue-500 h-1.5 rounded-full transition-all duration-700"
                      style={{ width: `${result.confidence_score * 100}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-lg p-6 min-h-[220px] flex items-center justify-center text-gray-400 text-sm">
              {loading ? 'Retrieving from knowledge base…' : 'Your answer will appear here'}
            </div>
          )}
        </div>
      </div>

      {result && (
        <ApprovalCard
          result={result}
          status={approvalStatus}
          onApprove={handleApprove}
          onEdit={handleEdit}
          onReject={() => setApprovalStatus('rejected')}
          editableContent={result.answer}
        />
      )}
    </div>
  )
}
