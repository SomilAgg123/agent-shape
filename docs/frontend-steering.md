# Frontend steering

These principles own interaction guidance. Keep project styling and component
contracts in their own document, linked from [local validation](local-validation.md).

## Approved guidance

- **Let the layout explain itself.** Omit text already evident from selection,
  navigation, or layout. Avoid redundant titles, breadcrumbs, file labels, and
  explanatory descriptions. Do not add subtitles or permanent explanatory text.
  Use titles, controls and result feedback. Use spacing and visual dividers for structure.
- **Keep tab and page headings plain.** Do not add info icons to tab labels or page headings.
  Keep necessary help beside the specific control or result it explains.
  Reveal help on hover, focus, or click instead of permanent explanatory text.
- **Render Markdown as content.** Display formatted headings, paragraphs, and
  lists rather than raw Markdown syntax when reading context.

- **Load data without refresh controls.** Load page data on entry and update it
  after relevant saves or runs. Do not expose reload buttons or manual-refresh UI.
  Keep error recovery focused on retrying the failed action.

- **Use straightforward action labels.** Prefer short, familiar labels such as
  Save and Run tests. Explain whether saving activates edits or affects the next
  run in nearby help or feedback, rather than lengthening the button label.

- **Keep processing inspectable.** Preserve access to saved configurations,
  changes, sources, short recorded rationales and failures.

- **Keep inputs available during testing.** Support testing changes without
  losing questions or edits during iteration.

## Maintaining this file

Review chat at each UI PR for explicit, reusable steering. Keep only current
approved principles; replace or delete superseded wording instead of appending
review history. Zero changes is normal. Skip one-off changes, inferred
preferences, and duplicates. Propose wording in the PR for review, label pending
proposals separately, and incorporate them only after approval. Remove resolved
or rejected proposals; see [the retention policy](README.md).
