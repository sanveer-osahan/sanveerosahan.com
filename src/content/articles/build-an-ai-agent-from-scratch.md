---
title: "Build an AI Agent from Scratch"
description: ""
publishDate: 2026-11-08
draft: true
tags: []
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

### High Level Design

We have established that you need AI Agents when tasks are open ended. Yet you can see that from the requirements it looks like there is a fixed predictable path.  


