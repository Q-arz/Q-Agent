## Commands & Semantics

### Command Schema

- Trigger-first commands with optional arguments, e.g. `post <text>`
- Each module declares commands in its manifest with:
  - `trigger`: prefix for routing
  - `description`: for help/UX
  - `args`: typed parameters (name, type, required)

### Natural Language Interpretation

The assistant should map natural language to commands consistently:

- A lightweight intent matcher (prefix + synonyms) is implemented in `core/nlu/intent.py`
- Manifests can declare `synonyms` per command; the matcher indexes them
- Unmatched text still returns fallback phrases; future: model-based suggestions

### Confirmation Model (Voice)

- Voice inputs ask for confirmation before executing actions
- Corrections via `no, dije ...` pipeline are re-routed

### Consistency Across Models

- Centralize normalization (lowercase, trim, punctuation) in IO layer
- Keep a single place for intent synonyms and examples
- Log executed commands and outcomes to memory for feedback


