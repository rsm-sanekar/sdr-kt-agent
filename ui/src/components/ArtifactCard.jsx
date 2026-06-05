import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

/**
 * Light-mode markdown card. Drop-in replacement for the dark `<pre>`-block
 * `ArtifactBlock` that used to render chain artifacts. Renders the markdown
 * via react-markdown inside a scrollable bounded-height card so long plans
 * don't push the page layout around.
 */
export default function ArtifactCard({ content, title = "Artifact" }) {
  if (!content) return null
  return (
    <div className="mt-3">
      <div className="text-xs uppercase tracking-wider text-gray-500 mb-2">{title}</div>
      <div className="bg-white border border-gray-200/70 rounded-xl p-7 max-h-[36rem] overflow-y-auto shadow-[inset_0_-1px_0_rgba(0,0,0,0.02)]">
        <div className="prose prose-base prose-gray max-w-none
          prose-headings:font-semibold prose-headings:text-gray-900
          prose-h1:text-xl prose-h1:mt-0 prose-h1:mb-4 prose-h1:pb-2 prose-h1:border-b prose-h1:border-gray-100
          prose-h2:text-base prose-h2:mt-6 prose-h2:mb-2
          prose-h3:text-xs prose-h3:font-bold prose-h3:mt-5 prose-h3:mb-2 prose-h3:uppercase prose-h3:tracking-wider prose-h3:text-gray-500
          prose-p:my-3 prose-p:leading-relaxed prose-p:text-gray-700
          prose-strong:text-gray-900 prose-strong:font-semibold
          prose-ul:my-3 prose-li:my-1.5 prose-li:leading-relaxed prose-li:text-gray-700
          prose-em:text-gray-600
          prose-code:text-xs prose-code:bg-gray-100 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:before:hidden prose-code:after:hidden">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
        </div>
      </div>
    </div>
  )
}
