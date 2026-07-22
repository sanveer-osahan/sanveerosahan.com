---
title: "Set Up your AI Coding Agent: From Premium to Free"
description: "A setup guide to the major AI coding agents across price tiers, premium down to free, with a tokens-per-second and output-quality comparison run on the same coding task."
publishDate: 2026-07-18
draft: true
tags: ["ai", "coding-agents", "guide"]
---

You open [ChatGPT](https://chatgpt.com) or [Claude](https://claude.ai) and ask it to do something for you.

Let's say it's part of your job, to do a comparison of two spreadsheets which has the same data from two different sources, every week. You have to find out and report the mismatches in the data. To save your time, you paste the spreadsheets into ChatGPT and ask it to do it for you, trusting that each time ChatGPT will do it with 100% accuracy. Another way is to ask ChatGPT for a formula that finds the mismatches and helps you generate a report. This is more accurate but you will have to do the process again if it's a different set of data in another domain.

Or maybe you have some coding experience and ask it to write a function and it responds with some code. You copy the code, paste it into your editor, and hit run. Something breaks, so you paste the error back into the chat. It apologizes and hands you a fix, and you copy that one too and repeat.

<figure class="diagram">
<img class="theme-light-only" src="/images/posts/set-up-your-ai-coding-agent/diagram-1-chat-loop.light.png" alt="You sit between the chat model and your workspace. Every step to your files, editor, and spreadsheet passes through you by hand, and the model never reaches into the workspace." />
<img class="theme-dark-only" src="/images/posts/set-up-your-ai-coding-agent/diagram-1-chat-loop.dark.png" alt="You sit between the chat model and your workspace. Every step to your files, editor, and spreadsheet passes through you by hand, and the model never reaches into the workspace." />
<figcaption>The model answers. You do all the work. It never touches your workspace.</figcaption>
</figure>

In both cases, when you tried it out in the chat box the first time, it felt like magic. Maybe it still feels like magic but...

"There's a lot you can do beyond that chat box."

## Why use a Coding Agent?

A coding agent exactly closes this gap. It can reach into your workspace and do the work itself. You still ask in plain words and it handles the rest.

<figure class="diagram">
<img class="theme-light-only" src="/images/posts/set-up-your-ai-coding-agent/diagram-2-coding-agent.light.png" alt="You describe the task once. The coding agent, backed by an AI model, writes and runs code in your workspace, reads the result or error, and fixes and reruns it. The loop happens without you passing each step by hand." />
<img class="theme-dark-only" src="/images/posts/set-up-your-ai-coding-agent/diagram-2-coding-agent.dark.png" alt="You describe the task once. The coding agent, backed by an AI model, writes and runs code in your workspace, reads the result or error, and fixes and reruns it. The loop happens without you passing each step by hand." />
<figcaption>You describe the task. The agent works in your workspace and runs the loop itself.</figcaption>
</figure>

You can easily swap the 2 modules - Coding Agent and AI Model. In this doc you'll learn how to set up various combinations of the agent and the model and how much each pairing will cost - starting from the most expensive to the least (free). The quality and performance will not be the same, so you can choose based on your budget and use case.

<figure class="diagram">
<img class="theme-light-only" src="/images/posts/set-up-your-ai-coding-agent/diagram-3-swap.light.png" alt="The coding-agent slot can be Claude Code, Codex, or Open Code. The agent uses an AI model, and that slot can be Claude, ChatGPT, Open Router, or a local model through Ollama. Either side swaps without changing the other." />
<img class="theme-dark-only" src="/images/posts/set-up-your-ai-coding-agent/diagram-3-swap.dark.png" alt="The coding-agent slot can be Claude Code, Codex, or Open Code. The agent uses an AI model, and that slot can be Claude, ChatGPT, Open Router, or a local model through Ollama. Either side swaps without changing the other." />
<figcaption>Pick an agent and a model provider of your choice.</figcaption>
</figure>

