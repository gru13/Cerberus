**Level:** Initiative (split into epics, then stories)

**Purpose:** Help the user learn to debug without giving the answer.

### Scope
- **Provider adapter:**
  - OpenAI-compatible (base URL): OpenAI, OpenRouter, Groq, Gemini compat endpoint, Ollama, LM Studio, vLLM.
  - Anthropic native (Claude). Gemini native (optional).
  - One interface: `chat(messages, stream, tools?)` + capability flags (tools, streaming, context size).
- **Model context:** bug report, the user's current code, the question, RAG passages. **The model never sees the patch or the fix.**
- **RAG:** project docs + pinned library docs, with citations.
- **Allowed:** Socratic questions, concepts, function/class usage from docs, generic samples.
- **Forbidden:** the fix, code similar to the reverse patch, the bug location (exam mode).
- **Guardrails:**
  - Versioned system policy.
  - Input filter: prompt injection, "show the diff" requests.
  - Output filter (server side): similarity and AST check against the reverse patch, then block or regenerate. Works for any model, including weak local ones.
- **Modes:** practice = hint ladder, unlimited. Exam = limited hints, each costs score.
- **Logs:** one entry per hint (asked / blocked / answered). Never message text.

### Open questions
- Hint levels.
- Example set of allowed / blocked / borderline conversations for guardrail tests.
