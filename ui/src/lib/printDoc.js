// Print / Save-as-PDF helper. Zero dependencies — prints a specific region of
// the current page so the rendered (Tailwind-styled) artifact carries over.
// Relies on the @media print rules in index.css (.printing / .print-region /
// .no-print). Sets document.title so it becomes the default PDF filename.
export function printRegion(node, title) {
  if (!node) return
  const prevTitle = document.title
  if (title) document.title = title
  node.classList.add("print-region")
  document.body.classList.add("printing")

  const cleanup = () => {
    document.body.classList.remove("printing")
    node.classList.remove("print-region")
    document.title = prevTitle
    window.removeEventListener("afterprint", cleanup)
  }
  window.addEventListener("afterprint", cleanup)
  window.print()
  // Safari/Firefox sometimes don't fire afterprint reliably — belt-and-braces.
  setTimeout(cleanup, 1500)
}
