# Ontology

Fixed vocabulary for logs and the knowledge graph. Add a term here before you use it in code.

## Entity types

| Type | Meaning |
|------|---------|
| Project | A base code repository |
| ProjectVersion | One version of a project (git SHA) |
| Issue | A bug definition |
| IssueVersion | One version of an issue (a diff on one ProjectVersion) |
| Run | One user attempt to fix one IssueVersion |
| User | A person with an account |
| Test | One test case |
| Hint | One tutor answer |
| File | One file in a workspace |

## Verbs (predicates)

| Verb | Example triple |
|------|----------------|
| proposes | User/LLM proposes Issue |
| applies | Sandbox applies IssueVersion to ProjectVersion |
| validates | Validator validates IssueVersion |
| verifies | Reviewer verifies IssueVersion |
| starts | User starts Run |
| edits | User edits File |
| tests | Run tests Test |
| asks | User asks Hint |
| submits | User submits Run |
| scores | Grader scores Run |
| retires | Admin retires IssueVersion |
