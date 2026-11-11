# Build an AI Agent from Scratch: outline of the next building blocks

Article: `src/content/articles/build-an-ai-agent-from-scratch.md`
Agent code: `~/Work/customer-support-agent`

## Done

- Calling the LLM API (curl, LangChain, streaming)
- Tool Calls in LLM (`run_postgres_query` on Postgres in Docker)
- Tool Calls using MCP (DuckDuckGo MCP server for dialects with no local database)

## Next building blocks

| # | Building block | Why at that point | Where it is in the agent |
|---|---|---|---|
| 1 | Agent loop (`create_agent`) | Turns the hand-written `while response.tool_calls` loop into a reusable unit. Adds a step limit. | Each SubTask (Reproduce, Plan, Write Tests, Implement) |
| 2 | Structured output | A SubTask must return a decision, for example "reproduced: yes or no", not only text | Reproduce → Plan or END |
| 3 | Workflow with LangGraph | Connects the SubTasks in a fixed order, with state and loops | `setup → reproduce → plan → write_test → implement → finish → review` |
| 4 | Webhook trigger | Starts the workflow when someone opens an issue | `src/support_agent/webhook.py` |
| 5 | Sandbox | Each run gets its own checkout and its own database containers | Setup |
| 6 | Review | The guardrail: runs the full test suite, checks the tests and the fix against the issue | Review node |

Blocks 1 to 3 are the core of "from scratch". Blocks 4 to 6 make the agent production ready.

## Agent loop: points to cover

- The `while response.tool_calls` loop is already a small AI Agent: the LLM decides, the code runs the tool, the LLM reads the result.
- Link back to the definition at the start of the article: an LLM plus tools in a loop.
- `create_agent` replaces the hand-written loop.
- Step limit (`recursion_limit`), so a loop cannot run forever.
- The agent uses this in `src/support_agent/agent/nodes.py` with `agent.stream(...)`.

## Later: separate detailed section

- Evals: measure how well the agent solves issues.
- Observability: see what the agent does on every run (Langfuse in the agent code).

## Open items in the article

- The curl request: `"model": "$LLM_MODEL"` is inside single quotes, so bash does not expand it.
- Tool Calls in LLM: the LLM call is inside the `for` loop. The Output block and the "2nd call" bullet are from the old code.
- Tool Calls using MCP: the text before the code and the bullets are from the old code. There is no Output block. The last LLM call uses `invoke`, not `await ... ainvoke`.
- Async: the agent code is sync today. Change the nodes to async when the first MCP tool goes in.
