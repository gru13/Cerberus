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
| Agent | An AI coding session |
| Decision | One agreed design decision |
| Document | One file in this repository |
| Repository | A git repository |
| Board | The GitHub project workboard |
| Initiative | Work item larger than an epic |
| Epic | Work item split into stories |
| Story | Buildable work item |
| AuthoringSession | A session where an author creates an issue |
| Review | A decision on an issue draft |
| Session | One running dev box container |
| Snapshot | A saved copy of changed workspace files |
| Port | A listening port in a dev box |
| Volume | A Docker volume that holds one run workspace |
| Job | A background task in the job queue |

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
| decides | User decides Decision |
| creates | Agent creates Document |
| pushes | Agent pushes Repository |
| moves | User moves Initiative to a status |
| recovers | User recovers Run after a crash |
| queues | API queues Job |
