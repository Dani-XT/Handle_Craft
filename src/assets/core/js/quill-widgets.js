document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.quill-widget').forEach(widget => {
    const editor = widget.querySelector('.quill-editor')
    const toolbar = widget.querySelector('.quill-toolbar')
    const textarea = widget.querySelector('textarea')

    if (!editor || !toolbar || !textarea || typeof Quill === 'undefined') return

    const quill = new Quill(editor, { theme: 'snow', modules: { toolbar } })
    quill.root.setAttribute('aria-labelledby', `${textarea.id}_label`)

    if (textarea.value) quill.clipboard.dangerouslyPasteHTML(textarea.value)

    const sync = () => {
      textarea.value = quill.getText().trim().length ? quill.root.innerHTML : ''
    }

    quill.on('text-change', sync)
    if (textarea.form) textarea.form.addEventListener('submit', sync)
  })
})
