---
title: "Build an AI Agent from Scratch: Part 1"
description: ""
publishDate: 2026-11-12
draft: false
tags: []
sources:
  - title: "Building effective agents"
    author: "Anthropic"
    url: "https://www.anthropic.com/research/building-effective-agents"
  - title: "LangChain Documentation"
    author: "LangChain"
    url: "https://docs.langchain.com/oss/python/langchain/overview"
  - title: "LangGraph Documentation"
    author: "LangChain"
    url: "https://docs.langchain.com/oss/python/langgraph/overview"
---

## Why we need AI Agents?

Before LLMs, the systems that we built were deterministic.  
For a given set of inputs and actions the user performs on the system, there is an expected set of outcomes and behaviour of the system.  

User makes a payment transfer of amount X from account A to account B
- If there is not enough balance in account A, the transfer will fail.
- If there is enough balance and there is a system issue mid-transfer, the transaction will roll back and amount X debited from account A will be credited back to account A.
- If the transfer is successful, amount in account A will be (A - X) and in account B will be (B + X)

API request runs a Database Query to send back results
- If the query fails with a temporary error, like a dropped connection, the API will retry the query a fixed number of times before it returns an error.
- If the query runs longer than the timeout, the database will cancel it and the API will return a timeout error.
- If the query returns results in time, the API will send the results back in the response.

<figure class="diagram">
<img class="theme-light-only" src="/images/posts/build-an-ai-agent-from-scratch/deterministic-system.light.png" alt="Input 1 and Input 2 go into a Deterministic System, which gives Output 1 and Output 2." />
<img class="theme-dark-only" src="/images/posts/build-an-ai-agent-from-scratch/deterministic-system.dark.png" alt="Input 1 and Input 2 go into a Deterministic System, which gives Output 1 and Output 2." />
</figure>

LLMs are probabilistic, i.e., for the same input you won't always get the same output.

The user sends a text query, which is converted to tokens. The LLM is trained on a vast set of data, and it uses this training to give each possible next token a probability.

The LLM picks one token based on these probabilities, so the same query can give a different token. It then adds the picked token to the input and predicts the next one.
- 1st pass : Input Query Q -> Output Token T1
- 2nd pass : Input Q + T1 -> Output Token T2
- Nth pass : Input Q + T1 + T2 + ... + TN-1 -> Output Token TN

<figure class="diagram">
<img class="theme-light-only" src="/images/posts/build-an-ai-agent-from-scratch/llm-inference.light.png" alt="Pass 1: the question &quot;Best 1st language for coding?&quot; goes into the LLM, which gives Java (0.4), Python (0.3), Golang (0.2), English (0.01) and Spanish (0.007). Python is selected. Pass 2: the question plus Python goes into the LLM, which gives because (0.4), or (0.3), and (0.2) and others. because is selected." />
<img class="theme-dark-only" src="/images/posts/build-an-ai-agent-from-scratch/llm-inference.dark.png" alt="Pass 1: the question &quot;Best 1st language for coding?&quot; goes into the LLM, which gives Java (0.4), Python (0.3), Golang (0.2), English (0.01) and Spanish (0.007). Python is selected. Pass 2: the question plus Python goes into the LLM, which gives because (0.4), or (0.3), and (0.2) and others. because is selected." />
</figure>

This continues until the LLM outputs an end token. The tokens are then converted to text and sent back to the user.

Some tasks are not completely deterministic in nature. They are open ended and need someone to understand the problem, plan the steps, make judgements, and perform actions using various deterministic systems. These tasks have always needed humans.

LLMs can now do the understanding, planning and judgement. But an LLM only outputs text. It cannot perform actions on the systems by itself.

An AI Agent uses an LLM enhanced with augmentations of deterministic systems, such as tools, retrieval and memory, to automate such tasks. The LLM decides the next step. The deterministic system performs the step and returns the result. The LLM reads the result and decides the next step, until the task is complete.

<figure class="diagram">
<img class="theme-light-only" src="/images/posts/build-an-ai-agent-from-scratch/ai-agent.light.png" alt="A Task goes into the AI Agent, which gives an Outcome. The AI Agent sends calls to Tools and gets responses, and sends queries to the LLM and gets answers." />
<img class="theme-dark-only" src="/images/posts/build-an-ai-agent-from-scratch/ai-agent.dark.png" alt="A Task goes into the AI Agent, which gives an Outcome. The AI Agent sends calls to Tools and gets responses, and sends queries to the LLM and gets answers." />
</figure>

## Designing the AI Agent

### Picking a use case

Let's take an Open Source SQL Linter  named [sqlfluff](https://github.com/sqlfluff/sqlfluff) and build a Support Agent that does the following:
- When a new Github Issue is created on the repository, the Agent picks up the issue.
- Triage the issue, resolve it and raise a PR having the fix.
- Write all teh details of the fix in the PR description and link it back to the issue.

<figure class="diagram">
<img class="theme-light-only" src="/images/posts/build-an-ai-agent-from-scratch/support-agent.light.png" alt="Task: a sqlfluff GH Issue goes into the Support Agent. Outcome: a Fix PR." />
<img class="theme-dark-only" src="/images/posts/build-an-ai-agent-from-scratch/support-agent.dark.png" alt="Task: a sqlfluff GH Issue goes into the Support Agent. Outcome: a Fix PR." />
</figure>

Any developer with the understanding of how SQL linters work and with a modern Coding Agent like Claude Code/Codex can handle such issues with ease as this is a simple use case for Coding Agents.

But in our article, we have used a simple use case to actually give an understanding of approaches to take for building such Support Agents to handle complex codebase and use cases.
The goal is to also automate the Issue -> PR end-to-end without any human in the loop (HITL)

### Support Agent Requirements

1. The Support Agent should pick up the issue when it is created in Github and start working on it.
2. The Agent will reproduce the issue as described in the issue description and report the steps performed and results in the issue comment.
3. The Agent will then write failing tests as per the issue reproduced.
4. The Agent will fix the issue and run the tests. In a loop work on the fix till the tests pass. 
5. A review step that will check the validity of tests and the fix against the original issue. Run the entire test suite
6. Repeat steps 3 - 5 till the outcome is achieved
7. Raise a PR of the fix and the tests, add the details of all the performed steps and results, link the PR to the issue.

We have established that you need AI Agents when tasks are open ended. Yet you can see that from the requirements it looks like there is a fixed predictable path.  

That is true, the issues are open ended, but when it comes to coding, there are some fixed steps - Software Development Lifecycle (SDLC).  

We can delegate to the Support Agent on what actions to take in the SDLC steps.

### High Level Design

We need an automated process where as soon as the Issue is created on Github, the Agent picks up the Issue and starts working on the Task as per the Issue description. So first step to create a webhook such that GitHub sends an event to our system every time a new issue is opened on the repository.

This is an ideal situation where a Task can be decomposed into fixed SubTasks.

Each SubTask will use LLM calls augmented by Tools to achieve parts of the outcome:

- Setup: Checkout the codebase in a Sandbox environment. Tools - git, files
- Reproduce: Understand the requirement and SQL dialect. Reproduce the issue on the real Database environment as per the dialect. Tools - sqlfluff, Database calls, Web Search where environment is not available.
- Plan: Find the root cause in the codebase and plan the fix. Tools - code search, files, git log
- Write Tests: Write tests that fail because of the issue. Tools - files, test runner
- Implement: Change the code until the new tests pass. Tools - files, test runner, sqlfluff

<figure class="diagram">
<img class="theme-light-only" src="/images/posts/build-an-ai-agent-from-scratch/high-level-design.light.png" alt="A GH Issue (the Task) goes through a Webhook to the Support Agent. The Support Agent runs the Sub-Tasks (Setup, Reproduce, Plan, Write Tests, Implement), which use the LLM and Tools: Git, DB Tools for MySQL, Postgres, Oracle and MSSQL, and Web Search for Snowflake, Databricks and BigQuery. The Sub-Tasks and Review loop. A Sandbox checks out the code, creates branches and worktrees, and runs Docker containers for the databases. Evals and Observability watch the Support Agent. The Support Agent outputs a Fixed PR (the Outcome), which links back to the GH Issue." />
<img class="theme-dark-only" src="/images/posts/build-an-ai-agent-from-scratch/high-level-design.dark.png" alt="A GH Issue (the Task) goes through a Webhook to the Support Agent. The Support Agent runs the Sub-Tasks (Setup, Reproduce, Plan, Write Tests, Implement), which use the LLM and Tools: Git, DB Tools for MySQL, Postgres, Oracle and MSSQL, and Web Search for Snowflake, Databricks and BigQuery. The Sub-Tasks and Review loop. A Sandbox checks out the code, creates branches and worktrees, and runs Docker containers for the databases. Evals and Observability watch the Support Agent. The Support Agent outputs a Fixed PR (the Outcome), which links back to the GH Issue." />
</figure>

Review is the guardrail. Once all the SubTasks complete, it checks whether the Agent actually achieved the outcome: it runs the full test suite, and it validates that both the new tests and the fix match the original ask in the Issue description. Passing tests are not enough if the tests check the wrong thing. Review is an Agent of its own, with its own design, which we will cover later.

When Review passes the fix, the Agent finalises the PR, pushes it to the remote, and links it to the Issue.

Before we deploy the Support Agent, we also need Evals to measure how well it solves issues, and Observability to see what it does on every run. Together they make the Agent production ready. We will cover both later.

## Building the Components

### Calling the LLM API

It's an HTTP request where we send the message in a POST request and get back the response in JSON format.

Request:

```bash
curl "$LLM_BASE_URL/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LLM_API_KEY" \
  -d '{
    "model": "$LLM_MODEL",
    "messages": [
      {"role": "user", "content": "In one sentence, what does a SQL linter do?"}
    ]
  }'
```

Response

```json
{
  "id": "chatcmpl-8f2c1a7e-3b4d-4e9a-9c61-2d5f0b7a1e33",
  "object": "chat.completion",
  "created": 1794312000,
  "model": "$LLM_MODEL",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "A SQL linter checks SQL code for syntax errors, style problems and bad practices, so that the code is correct and consistent."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 18,
    "completion_tokens": 27,
    "total_tokens": 45
  }
}
```

- `$LLM_BASE_URL/chat/completions`: An OpenAI-compatible API endpoint
- `LLM_MODEL`: swap a model supported by the endpoint
- `LLM_API_KEY`: Authorization Key from the model provider
- `"role": "user"` means the message is by the user and the `"role": "assistant"` denotes the response message back by the model.

There are various ways in which an LLM API can be called using Python:
- Using `requests` library to make HTTP requests
- Using the official SDKs from Model Providers (OpenAI, Anthropic)
- LangChain: an open-source Python framework that puts one interface for every LLM model and providers

Create the project with [uv](https://docs.astral.sh/uv/) and add the dependencies:

```bash
uv init support-agent
cd support-agent
uv add langchain langchain-openai python-dotenv
```

Add the values to a `.env` file:

```bash
LLM_BASE_URL=...
LLM_API_KEY=...
LLM_MODEL=...
```


```python
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    base_url=os.environ["LLM_BASE_URL"],
    api_key=os.environ["LLM_API_KEY"],
    model=os.environ["LLM_MODEL"],
)

response = llm.invoke("In one sentence, what does a SQL linter do?")
print(response.content)
```

Run it:

```bash
uv run main.py
```

Output:

```
A SQL linter checks SQL code for syntax errors, style problems and bad practices, so that the code is correct and consistent.
```

### Tool Calls in LLM

There are some cases where we can't fully rely on the LLM's response.  
We need some additional inputs so that LLM can verify some facts before providing a response that minimal hallucinations.

For eg, the user asks - ""In Postgres, does ORDER BY put NULL values first or last?"

In this case, if the LLM has access to a real Postgres Database to run a query and verify the result, it can respond with an answer based on actual behaviour.

Start a Postgres instance with Docker:

```bash
docker run -d --name postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:18
```

Add SQLAlchemy and the Postgres driver to the project:

```bash
uv add sqlalchemy "psycopg[binary]"
```

Add the connection URL to the `.env` file:

```bash
POSTGRES_DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/postgres
```

Define the Tool, give it to the LLM, and run the Tool when the LLM asks for it:

```python
import os
import json

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

pg_engine = create_engine(os.environ["POSTGRES_DATABASE_URL"])


@tool
def run_postgres_query(sql: str):
    """Run a SQL query on a real Postgres Database and return the results"""
    with pg_engine.connect() as conn:
        try:
            rows = conn.execute(text(sql)).fetchall()
        except SQLAlchemyError as e:
            return f"Error: {e}"
        finally:
            conn.rollback()
    return str(rows)


llm = ChatOpenAI(
    base_url=os.environ["LLM_BASE_URL"],
    api_key=os.environ["LLM_API_KEY"],
    model="gemma4:26b",
)

llm_with_tools = llm.bind_tools([run_postgres_query])

messages = [
    SystemMessage("You have the ability to call run_postgres_query tool which takes the sql text as input and returns the results. When answering questions related to Postgres, do use this tool to verify the results"),
    HumanMessage("In Postgres, does ORDER BY ASC put null values first or last? What happens when we run ORDER BY DESC on the same data having null values?")
]

response = llm_with_tools.invoke(messages)
print("\nLLM Response : ")
response.pretty_print()

while response.tool_calls:
    messages.append(response)
    for tool_call in response.tool_calls:
        print("\nTool Call : \n", json.dumps(tool_call, indent=2))
        tool_response = run_postgres_query.invoke(tool_call)
        print("\nTool Response : \n", tool_response)
        messages.append(tool_response)
    response = llm_with_tools.invoke(messages)
    print("\nLLM Response : ")
    response.pretty_print()
```

Output:

```
{'name': 'run_postgres_query', 'args': {'sql': 'SELECT x FROM (VALUES (2), (NULL), (1)) AS t(x) ORDER BY x;'}, 'id': 'call_9b1e4f', 'type': 'tool_call'}
Last. In ascending order, Postgres puts NULL values last: the query returned [(1,), (2,), (None,)]. In descending order they come first. Use NULLS FIRST or NULLS LAST to change this.
```

- `@tool`: turns the function into a Tool. LangChain sends its name, the docstring and the `sql: str` argument to the LLM, so the LLM knows what the Tool does and what input it needs.
- `bind_tools`: adds the Tool definitions to every request to the LLM.
- `response.tool_calls`: the LLM does not run the query. It only sends back the Tool name and the SQL it wrote.
- `run_postgres_query.invoke(tool_call)`: our code runs the query and returns a `ToolMessage` with the rows.
- `create_engine`: SQLAlchemy picks the database and the driver from the URL. For MySQL or SQL Server, change the URL and add the driver. The Tool code stays the same.
- `conn.rollback()`: the query never changes the database.
- The 2nd call sends the full conversation back: the question, the Tool call and the Tool result. The LLM answers from the actual result.

### Tool Calls using MCP

Add the MCP adapter for LangChain to the project:

```bash
uv add langchain-mcp-adapters
```

We use the [DuckDuckGo MCP server](https://github.com/nickclyde/duckduckgo-mcp-server). It gives the LLM 3 Tools:
- `search`: searches the web and returns the titles, URLs and snippets.
- `fetch_content`: fetches a web page and returns its text.
- `expand_link`: returns the full URL for a link from the search results.

Start the MCP server in a separate terminal:

```bash
uvx duckduckgo-mcp-server --transport streamable-http --port 8000
```

```python
import asyncio
import os
import json

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import tool
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

pg_engine = create_engine(os.environ["POSTGRES_DATABASE_URL"])

SYSTEM_PROMPT = """
You have the ability to call run_postgres_query tool which takes the sql text as input and returns the results. 
When answering questions related to Postgres, do use this tool to verify the results.
For any other database, if you don't have the tool to run a query against it, use web search tools - search, fetch_content, expand_link, to gather context.
"""


@tool
def run_postgres_query(sql: str):
    """Run a SQL query on a real Postgres Database and return the results"""
    with pg_engine.connect() as conn:
        try:
            rows = conn.execute(text(sql)).fetchall()
        except SQLAlchemyError as e:
            return f"Error: {e}"
        finally:
            conn.rollback()
    return str(rows)


tools_by_name = {"run_postgres_query": run_postgres_query}
tools = [run_postgres_query]


async def main():
    mcp_client = MultiServerMCPClient(
        {
            "duckduckgo": {
                "url": "http://127.0.0.1:8000/mcp",
                "transport": "streamable_http",
            }
        }
    )

    mcp_tools = await mcp_client.get_tools()
    for tool in mcp_tools:
        tools_by_name[tool.name] = tool
        tools.append(tool)

    llm = ChatOpenAI(
        base_url=os.environ["LLM_BASE_URL"],
        api_key=os.environ["LLM_API_KEY"],
        model="gemma4:26b",
    )
    
    llm_with_tools = llm.bind_tools(tools)
    
    messages = [
        SystemMessage(SYSTEM_PROMPT),
        HumanMessage("In Snowflake, what are the various Data Types supported? Which data type was added recently and when it was added? Provide verified references for the claim with the source links.")
    ]
    
    response = await llm_with_tools.ainvoke(messages)
    
    while response.tool_calls:
        messages.append(response)
        for tool_call in response.tool_calls:
            tool_call_name = tool_call["name"]
            print("\nTool Call:\n")
            print(json.dumps(tool_call, indent=2))
            tool = tools_by_name[tool_call_name]
            tool_response = await tool.ainvoke(tool_call)
            print("\nTool Response:\n")
            tool_response.pretty_print()
            messages.append(tool_response)
        response = llm_with_tools.invoke(messages)
        print("\nLLM Response:\n")
        response.pretty_print()
        
asyncio.run(main())
```

- `MultiServerMCPClient`: connects to the MCP server that runs at `http://127.0.0.1:8000/mcp`, over the `streamable_http` transport.
- `get_tools()`: asks the MCP server for its Tools and turns them into LangChain Tools. We do not write any Tool code.
- `tools_by_name`: the LLM can pick any of the 3 Tools, so we find the Tool by the name in the Tool call.
- `await` and `ainvoke`: the MCP Tools are async, so the code runs inside `asyncio.run(main())`.

### Create Agent

Instead of creating the loop yourself, you can create an agent in langchain which creates and manages the loop for you.

```python
import asyncio
import os
import json

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import tool
from langgraph.errors import GraphRecursionError
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

pg_engine = create_engine(os.environ["POSTGRES_DATABASE_URL"])

SYSTEM_PROMPT = """
You have the ability to call run_postgres_query tool which takes the sql text as input and returns the results. 
When answering questions related to Postgres, do use this tool to verify the results.
For any other database, if you don't have the tool to run a query against it, use web search tools - search, fetch_content, expand_link, to gather context.
"""


@tool
def run_postgres_query(sql: str):
    """Run a SQL query on a real Postgres Database and return the results"""
    with pg_engine.connect() as conn:
        try:
            rows = conn.execute(text(sql)).fetchall()
        except SQLAlchemyError as e:
            return f"Error: {e}"
        finally:
            conn.rollback()
    return str(rows)


tools_by_name = {"run_postgres_query": run_postgres_query}
tools = [run_postgres_query]


async def main():
    mcp_client = MultiServerMCPClient(
        {
            "duckduckgo": {
                "url": "http://127.0.0.1:8000/mcp",
                "transport": "streamable_http",
            }
        }
    )

    mcp_tools = await mcp_client.get_tools()
    for tool in mcp_tools:
        tools_by_name[tool.name] = tool
        tools.append(tool)

    llm = ChatOpenAI(
        base_url=os.environ["LLM_BASE_URL"],
        api_key=os.environ["LLM_API_KEY"],
        model="gemma4:26b",
    )

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT
    )

    messages = [
        HumanMessage("In Snowflake, what are the various Data Types supported? Which data type was added recently and when it was added? Provide verified references for the claim with the source links.")
    ]
    
    response = await agent.ainvoke(input={"messages": messages}, config={"recursion_limit": 10})
    for message in response["messages"]:
        message.pretty_print()
        
asyncio.run(main())
```

- `recursion_limit`: each Tool call uses 2 steps, one LLM step and one Tool step. The final answer uses 1 more step. With a limit of 10, the agent can make about 4 Tool calls before it raises `GraphRecursionError`.

### Structured Output

`create_agent` uses LangGraph to build the loop. One agent can solve one subtask, and we can connect these subtasks together to solve a complex task.

For that, each subtask can return a Structured Output: an object with fixed fields instead of text. The other downstream subtasks can read its values and can define their own behaviour.

Example: compare how regex matching works in Postgres, MySQL and Snowflake, and return the result as a Pydantic object.

Start a MySQL instance with Docker:

```bash
docker run -d --name mysql \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=demo \
  -p 3306:3306 \
  mysql:8.4
```

Add the MySQL driver to the project:

```bash
uv add pymysql cryptography
```

Add the connection URL to the `.env` file:

```bash
MYSQL_DATABASE_URL=mysql+pymysql://root:password@localhost:3306/demo
```

```python
import asyncio
import os
from typing import Literal

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

pg_engine = create_engine(os.environ["POSTGRES_DATABASE_URL"])
mysql_engine = create_engine(os.environ["MYSQL_DATABASE_URL"])

SYSTEM_PROMPT = """
You compare SQL behaviour across databases.
Use run_postgres_query to run SQL on Postgres and run_mysql_query to run SQL on MySQL.
For Snowflake, there is no database to run a query against. Use the web search tools - search, fetch_content, expand_link - to find the answer in the Snowflake docs.
Do not answer from memory. Every result must come from a query or a source link.
When you have all the results, call the RegexComparison tool to return the final answer. Do not answer in plain text.
"""


def run_query(engine, sql):
    with engine.connect() as conn:
        try:
            rows = conn.execute(text(sql)).fetchall()
        except SQLAlchemyError as e:
            return f"Error: {e}"
        finally:
            conn.rollback()
    return str(rows)


@tool
def run_postgres_query(sql: str):
    """Run a SQL query on a real Postgres Database and return the results"""
    return run_query(pg_engine, sql)


@tool
def run_mysql_query(sql: str):
    """Run a SQL query on a real MySQL Database and return the results"""
    return run_query(mysql_engine, sql)


class PatternMatch(BaseModel):
    pattern: str
    matched: bool


class DatabaseResult(BaseModel):
    database: Literal["postgres", "mysql", "snowflake"]
    sql: str = Field(description="The SQL that tests the patterns")
    checked_by: Literal["query", "web_search"]
    query_result: str | None = Field(description="The rows exactly as the query tool returned them. None if checked_by is web_search")
    source_url: str | None = Field(description="The URL of the docs page. None if checked_by is query")
    matches: list[PatternMatch] = Field(description="One item for each pattern")


class RegexComparison(BaseModel):
    results: list[DatabaseResult] = Field(description="One item for each database")
    differences: list[str] = Field(description="Each difference between the databases, one per item")


async def main():
    mcp_client = MultiServerMCPClient(
        {
            "duckduckgo": {
                "url": "http://127.0.0.1:8000/mcp",
                "transport": "streamable_http",
            }
        }
    )
    mcp_tools = await mcp_client.get_tools()

    llm = ChatOpenAI(
        base_url=os.environ["LLM_BASE_URL"],
        api_key=os.environ["LLM_API_KEY"],
        model="gemma4:26b",
    )

    agent = create_agent(
        model=llm,
        tools=[run_postgres_query, run_mysql_query, *mcp_tools],
        system_prompt=SYSTEM_PROMPT,
        response_format=ToolStrategy(RegexComparison),
    )

    messages = [
        HumanMessage("How does regex matching work in Postgres, MySQL and Snowflake? For each database, check if 'Hello World' matches the patterns 'World' and 'world'. Show the SQL and the result.")
    ]

    response = await agent.ainvoke(input={"messages": messages}, config={"recursion_limit": 25})
    for message in response["messages"]:
        message.pretty_print()

    comparison = response["structured_response"]
    if comparison is None:
        comparison = await llm.with_structured_output(RegexComparison).ainvoke(response["messages"])
    print(comparison.model_dump_json(indent=2))


asyncio.run(main())
```

Example structured response:

```json
{
  "results": [
    {
      "database": "postgres",
      "sql": "SELECT 'Hello World' ~ 'World' AS matches_World, 'Hello World' ~ 'world' AS matches_world;",
      "checked_by": "query",
      "query_result": "[(True, False)]",
      "source_url": "N/A",
      "matches": [
        {
          "pattern": "'Hello World' ~ 'World' -> True",
          "matched": true
        },
        {
          "pattern": "'Hello World' ~ 'world' -> False",
          "matched": false
        }
      ]
    },
    {
      "database": "mysql",
      "sql": "SELECT 'Hello World' REGEXP 'World' AS matches_World, 'Hello World' REGEXP 'world' AS matches_world;",
      "checked_by": "query",
      "query_result": "[(1, 1)]",
      "source_url": "N/A",
      "matches": [
        {
          "pattern": "'Hello World' REGEXP 'World' -> 1",
          "matched": true
        },
        {
          "pattern": "'Hello World' REGEXP 'world' -> 1",
          "matched": true
        }
      ]
    },
    {
      "database": "snowflake",
      "sql": "SELECT REGEXP_LIKE('Hello World', 'World') AS matches_World, REGEXP_LIKE('Hello World', 'world') AS matches_world;",
      "checked_by": "web_search",
      "query_result": "N/A",
      "source_url": "https://docs.snowflake.com/en/sql-reference/functions-regexp",
      "matches": [
        {
          "pattern": "REGEXP_LIKE('Hello World', 'World') -> True",
          "matched": true
        },
        {
          "pattern": "REGEXP_LIKE('Hello World', 'world') -> False",
          "matched": false
        }
      ]
    }
  ],
  "differences": [
    "Postgres uses the `~` operator and is case-sensitive by default.",
    "MySQL uses the `REGEXP` operator and is case-insensitive by default (dependent on the collation, e.g., `utf8mb4_general_ci`).",
    "Snowflake uses `REGEXP_LIKE` and is case-sensitive by default (unless the 'i' parameter is explicitly used)."
  ]
}
```

- `RegexComparison`: the Pydantic model the agent must return. The `Field` descriptions go to the LLM with the schema.
- `response_format=ToolStrategy(RegexComparison)`: LangChain gives the LLM the schema as one more Tool. The agent stops when the LLM calls that Tool, and LangChain checks the arguments against the model.
- `recursion_limit` is 25: the agent runs queries on 2 databases, searches the web, and calls the schema Tool.

### Creating a Workflow

In the previous section, one agent solved one subtask and returned a Structured Output. With LangGraph, we can orchestrate multiple agents in one workflow, where the output of one agent decides which agent runs next.

Let's take an example where a user asks a question about the data in the database. The first step classifies the question:

- `non_sql`: the question is not related to SQL, so we reject it.
- `data`: the user asks for specific data. An agent translates it into a SQL query, runs it and returns the results.
- `generic`: the user asks how to do something in SQL. One agent searches the web and another agent runs an example query, both at the same time. A final step combines both the results.

<figure class="diagram">
<img class="theme-light-only" src="/images/posts/build-an-ai-agent-from-scratch/workflow.light.png" alt="Workflow graph: START goes to classify. classify routes non_sql to reject, data to data_agent, and generic to query_agent and web_agent in parallel. query_agent and web_agent go to combine. reject, data_agent and combine go to END." />
<img class="theme-dark-only" src="/images/posts/build-an-ai-agent-from-scratch/workflow.dark.png" alt="Workflow graph: START goes to classify. classify routes non_sql to reject, data to data_agent, and generic to query_agent and web_agent in parallel. query_agent and web_agent go to combine. reject, data_agent and combine go to END." />
</figure>

Create the `orders` table in Postgres and add some rows:

```bash
docker exec -i postgres psql -U postgres <<'SQL'
CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  customer TEXT,
  amount NUMERIC,
  created_at DATE
);

INSERT INTO orders (customer, amount, created_at) VALUES
  ('Asha', 120, '2026-10-01'),
  ('Ravi', 80, '2026-10-02'),
  ('Asha', 200, '2026-10-05'),
  ('Meera', 50, '2026-10-07'),
  ('Ravi', 150, '2026-10-09');
SQL
```

Start the MCP server in a separate terminal:

```bash
uvx duckduckgo-mcp-server --transport streamable-http --port 8000
```

```python
import asyncio
import os
from typing import Literal, TypedDict

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

pg_engine = create_engine(os.environ["POSTGRES_DATABASE_URL"])

mcp_client = MultiServerMCPClient(
    {
        "duckduckgo": {
            "url": "http://127.0.0.1:8000/mcp",
            "transport": "streamable_http",
        }
    }
)

llm = ChatOpenAI(
    base_url=os.environ["LLM_BASE_URL"],
    api_key=os.environ["LLM_API_KEY"],
    model="gemma4:26b",
)

CLASSIFY_PROMPT = """
Find the type of the question:
- non_sql: the question is not about SQL or about data in the database.
- data: the question asks for data that is in the database.
- generic: the question asks how to do something in SQL.
To find if the database has the data, use run_postgres_query to query information_schema or the pg system tables.
"""

SQL_PROMPT = """
You answer questions with SQL on a Postgres database.
Use run_postgres_query to run the SQL. Do not answer from memory.
Return the SQL and the result.
"""

WEB_PROMPT = """
You find how to do something in Postgres SQL.
Use the web search tools to find the answer in the Postgres docs. Do not answer from memory.
Return the answer and the source URL.
"""


@tool
def run_postgres_query(sql: str):
    """Run a SQL query on a real Postgres Database and return the results"""
    with pg_engine.connect() as conn:
        try:
            rows = conn.execute(text(sql)).fetchall()
        except SQLAlchemyError as e:
            return f"Error: {e}"
        finally:
            conn.rollback()
    return str(rows)


class Question(BaseModel):
    kind: Literal["non_sql", "data", "generic"]


classify_agent = create_agent(
    model=llm,
    tools=[run_postgres_query],
    system_prompt=CLASSIFY_PROMPT,
    response_format=ToolStrategy(Question),
)

sql_agent = create_agent(model=llm, tools=[run_postgres_query], system_prompt=SQL_PROMPT)


class State(TypedDict):
    question: str
    kind: str
    query_result: str
    web_result: str
    answer: str


async def classify(state: State):
    response = await classify_agent.ainvoke({"messages": [("human", state["question"])]})
    question = response["structured_response"]
    if question is None:
        question = await llm.with_structured_output(Question).ainvoke(response["messages"])
    return {"kind": question.kind}


def route(state: State):
    if state["kind"] == "non_sql":
        return "reject"
    if state["kind"] == "data":
        return "data_agent"
    return ["query_agent", "web_agent"]


def reject(state: State):
    return {"answer": "I can only answer SQL questions and questions about the data in the database."}


async def data_agent(state: State):
    response = await sql_agent.ainvoke({"messages": [("human", state["question"])]})
    return {"answer": response["messages"][-1].content}


async def query_agent(state: State):
    response = await sql_agent.ainvoke(
        {"messages": [("human", f"Write and run an example query on a table in the database for: {state['question']}")]}
    )
    return {"query_result": response["messages"][-1].content}


async def web_agent(state: State):
    mcp_tools = await mcp_client.get_tools()
    agent = create_agent(model=llm, tools=mcp_tools, system_prompt=WEB_PROMPT)
    response = await agent.ainvoke({"messages": [("human", state["question"])]})
    return {"web_result": response["messages"][-1].content}


async def combine(state: State):
    response = await llm.ainvoke(
        f"Question: {state['question']}\n"
        f"From the docs: {state['web_result']}\n"
        f"Example query on the database: {state['query_result']}\n"
        "Answer the question. Explain the SQL from the docs, and show the example query and its result."
    )
    return {"answer": response.content}


def build_graph():
    graph = StateGraph(State)
    graph.add_node("classify", classify)
    graph.add_node("reject", reject)
    graph.add_node("data_agent", data_agent)
    graph.add_node("query_agent", query_agent)
    graph.add_node("web_agent", web_agent)
    graph.add_node("combine", combine)

    graph.add_edge(START, "classify")
    graph.add_conditional_edges("classify", route, ["reject", "data_agent", "query_agent", "web_agent"])
    graph.add_edge("reject", END)
    graph.add_edge("data_agent", END)
    graph.add_edge(["query_agent", "web_agent"], "combine")
    graph.add_edge("combine", END)

    return graph.compile()


async def main():
    workflow = build_graph()
    for question in [
        "What is the weather in Delhi?",
        "How much did each customer spend?",
        "How do I get a running total in Postgres?",
    ]:
        result = await workflow.ainvoke({"question": question})
        print(question)
        print(result["answer"])
        print()


asyncio.run(main())
```

- `classify_agent`: queries `information_schema` to find if the database has the data, and returns a `Question`. `kind` picks the next node.
- `graph.add_conditional_edges("classify", route, ...)`: the router. `route` reads `kind` and returns the name of the next node.
- `return ["query_agent", "web_agent"]`: the parallelizer. For a `generic` question, LangGraph runs both agents at the same time.
- `graph.add_edge(["query_agent", "web_agent"], "combine")`: `combine` waits for both agents.
- `sql_agent`: one agent that `data_agent` and `query_agent` both use, with a different message.
- `reject` does not call the LLM.


## What's Next

In Part 1, we designed the Support Agent and understood the building blocks of an AI Agent:

- Calling the LLM API
- Tool Calls, with local Tools and with MCP
- Creating an Agent
- Structured Output
- Creating a Workflow that orchestrates multiple agents

In the upcoming parts, we will use these building blocks to create a production level Support Agent with:

- A Webhook that starts the Agent when a new issue is created on Github
- Evals to measure how well the Agent resolves the issues
- Observability to see what the Agent does on every run
- Deploying the Agent in production
