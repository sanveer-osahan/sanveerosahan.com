---
title: "Set Up your AI Coding Agent: From Premium to Free"
description: "A setup guide to the major AI coding agents across price tiers, premium down to free, with a tokens-per-second and output-quality comparison run on the same coding task."
publishDate: 2026-07-18
draft: true
tags: ["ai", "coding-agents", "guide"]
---

You open [ChatGPT](https://chatgpt.com) or [Claude](https://claude.ai) and ask it to do something for you.

Let's say it's part of your job, to do a comparison of two spreadsheets which has the same data from two different sources, every week. You have to find out and report the mismatches in the data. To save your time, you paste the spreadsheets into ChatGPT and ask it to do it for you, trusting that each time ChatGPT will do it with 100% accuracy. 

Another way is to ask ChatGPT for a formula that finds the mismatches and helps you generate a report. This is more accurate but you will have to do the process again if it's a different set of data in another domain.

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

## The Infinite Spend Option: Coding Agents on API Billing

The costliest option is a coding agent like Claude Code or Codex paired with API-based billing from the companies behind Claude (Anthropic) and ChatGPT (OpenAI).

Here you are charged based on which model you use and how much you use it. There is no fixed monthly fee. You pay for exactly what you use, and there is no upper limit.

These are language models, so all text is broken down into tokens. To keep it simple, assume 1 word = 1 token. What you send to the model are input tokens. What the model
sends back are output tokens.

Every model sets its own input and output prices, and output costs more than input.

You pick the model based on the complexity of the task. A larger model gives you better results but costs more.

Here is the pricing for popular models as of July 2026:

<div class="table-wrap">
<table>
<thead>
<tr>
<th>Provider</th>
<th>Model</th>
<th>Size</th>
<th>Input (per 1M tokens)</th>
<th>Output (per 1M tokens)</th>
</tr>
</thead>
<tbody>
<tr>
<td rowspan="4">Anthropic</td>
<td>Haiku 4.5</td>
<td>S</td>
<td>$1</td>
<td>$5</td>
</tr>
<tr>
<td>Sonnet 5</td>
<td>M</td>
<td>$3</td>
<td>$15</td>
</tr>
<tr>
<td>Opus 4.8</td>
<td>L</td>
<td>$5</td>
<td>$25</td>
</tr>
<tr>
<td>Fable 5</td>
<td>XL</td>
<td>$10</td>
<td>$50</td>
</tr>
<tr>
<td rowspan="3">OpenAI</td>
<td>GPT-5.6 Luna</td>
<td>S</td>
<td>$1</td>
<td>$6</td>
</tr>
<tr>
<td>GPT-5.6 Terra</td>
<td>M</td>
<td>$2.50</td>
<td>$15</td>
</tr>
<tr>
<td>GPT-5.6 Sol</td>
<td>L</td>
<td>$5</td>
<td>$30</td>
</tr>
</tbody>
</table>
</div>

The sizes above map to what each model can do:

| Size | Capability |
|---|---|
| S | Answers short questions, makes small code edits, and writes simple scripts. |
| M | Handles most everyday coding and writing tasks, including ones that take a few steps. |
| L | Writes and fixes complex code and works through problems that require many steps. |
| XL | Handles the toughest tasks and the longest jobs that run with little input from you. |

### Setting It Up

<div class="tabset">
<input class="tabr" type="radio" name="agent" id="agent-cc" checked>
<input class="tabr" type="radio" name="agent" id="agent-cx">
<div class="tabnav">
<label for="agent-cc">Claude Code</label>
<label for="agent-cx">Codex</label>
</div>
<div class="tabpanes">
<div class="pane pane-agent-cc">
<h4>1. Get your Anthropic API key</h4>
<ol>
<li><a href="https://platform.claude.com">Sign up or log in</a> to the Anthropic Console.</li>
<li>Open the <a href="https://platform.claude.com/settings/billing">Billing page</a>, add a card, and buy some prepaid credits. Your usage is drawn from this balance, and you can turn on auto-reload so it tops up on its own when it runs low.</li>
<li>Open the <a href="https://platform.claude.com/settings/keys">API keys page</a>, click <strong>Create Key</strong>, give it a name, and copy the key. It starts with <code>sk-ant-</code> and is shown only once, so paste it somewhere safe.</li>
</ol>
<h4>2. Install and save your key</h4>
<div class="tabset">
<input class="tabr" type="radio" name="cc-os" id="cc-mac" checked>
<input class="tabr" type="radio" name="cc-os" id="cc-win">
<input class="tabr" type="radio" name="cc-os" id="cc-lin">
<div class="tabnav">
<label for="cc-mac">macOS</label>
<label for="cc-win">Windows</label>
<label for="cc-lin">Linux</label>
</div>
<div class="tabpanes">
<div class="pane pane-cc-mac">
<p><strong>Open the terminal:</strong> press Cmd+Space, type Terminal, and press Enter.</p>
<p>Install Claude Code:</p>
<pre><code>curl -fsSL https://claude.ai/install.sh | bash</code></pre>
<p>Check it worked:</p>
<pre><code>claude --version</code></pre>
<p>Save your key so it is remembered (replace with your own key):</p>
<pre><code>echo 'export ANTHROPIC_API_KEY="sk-ant-your-key"' &gt;&gt; ~/.zshrc
source ~/.zshrc</code></pre></div>
<div class="pane pane-cc-win">
<p><strong>Open PowerShell:</strong> press the Windows key, type PowerShell, and open Windows PowerShell (not Command Prompt).</p>
<p>Install Claude Code:</p>
<pre><code>irm https://claude.ai/install.ps1 | iex</code></pre>
<p>Check it worked:</p>
<pre><code>claude --version</code></pre>
<p>Save your key (replace with your own), then close and reopen PowerShell:</p>
<pre><code>setx ANTHROPIC_API_KEY "sk-ant-your-key"</code></pre></div>
<div class="pane pane-cc-lin">
<p><strong>Open the terminal:</strong> press Ctrl+Alt+T.</p>
<p>Install Claude Code:</p>
<pre><code>curl -fsSL https://claude.ai/install.sh | bash</code></pre>
<p>Check it worked:</p>
<pre><code>claude --version</code></pre>
<p>Save your key so it is remembered (replace with your own key):</p>
<pre><code>echo 'export ANTHROPIC_API_KEY="sk-ant-your-key"' &gt;&gt; ~/.bashrc
source ~/.bashrc</code></pre></div>
</div>
</div>
<h4>3. Start it on a task</h4>
<p>Make a folder for your project and go into it:</p>
<pre><code>mkdir sales-check
cd sales-check</code></pre>
<p>Start Claude Code from inside that folder:</p>
<pre><code>claude</code></pre>
<p>On the first run, approve using the API key, then type <code>/status</code> to confirm it shows your API key.</p>
<p>Pick a model. Type this and choose one from the list:</p>
<pre><code>/model</code></pre>
<p>Now give it a task. Drop two sales reports into the folder, the same sales recorded by two different sources, then type:</p>
<pre><code>Compare website-sales.csv and store-sales.csv.
List the rows that do not match and save them to a file called mismatches.csv.</code></pre>
</div>
<div class="pane pane-agent-cx">
<h4>1. Get your OpenAI API key</h4>
<ol>
<li><a href="https://platform.openai.com">Sign up or log in</a> to the OpenAI developer platform. This is separate from a ChatGPT subscription.</li>
<li>Open the <a href="https://platform.openai.com/settings/organization/billing/overview">Billing page</a>, add a card, and buy some prepaid credits. Your usage is drawn from this balance, and you can turn on auto-recharge so it tops up on its own when it runs low. This is billed here, not through ChatGPT.</li>
<li>Open the <a href="https://platform.openai.com/api-keys">API keys page</a>, click <strong>Create new secret key</strong>, and copy it. It starts with <code>sk-</code> and is shown only once, so paste it somewhere safe.</li>
</ol>
<p class="note">Do not run plain <code>codex login</code>. That signs in with a ChatGPT subscription instead of your API key. Use the steps below.</p>
<h4>2. Install and connect</h4>
<div class="tabset">
<input class="tabr" type="radio" name="cx-os" id="cx-mac" checked>
<input class="tabr" type="radio" name="cx-os" id="cx-win">
<input class="tabr" type="radio" name="cx-os" id="cx-lin">
<div class="tabnav">
<label for="cx-mac">macOS</label>
<label for="cx-win">Windows</label>
<label for="cx-lin">Linux</label>
</div>
<div class="tabpanes">
<div class="pane pane-cx-mac">
<p><strong>Open the terminal:</strong> press Cmd+Space, type Terminal, and press Enter.</p>
<p>Install Codex:</p>
<pre><code>curl -fsSL https://chatgpt.com/codex/install.sh | sh</code></pre>
<p>Check it worked:</p>
<pre><code>codex --version</code></pre>
<p>Save your key (replace with your own key):</p>
<pre><code>echo 'export OPENAI_API_KEY="sk-your-key"' &gt;&gt; ~/.zshrc
source ~/.zshrc</code></pre>
<p>Connect the key to Codex:</p>
<pre><code>printenv OPENAI_API_KEY | codex login --with-api-key</code></pre></div>
<div class="pane pane-cx-win">
<p><strong>Open PowerShell:</strong> press the Windows key, type PowerShell, and open Windows PowerShell (not Command Prompt).</p>
<p>Install Codex:</p>
<pre><code>powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"</code></pre>
<p>Check it worked:</p>
<pre><code>codex --version</code></pre>
<p>Save your key (replace with your own), then close and reopen PowerShell:</p>
<pre><code>setx OPENAI_API_KEY "sk-your-key"</code></pre>
<p>Connect the key to Codex:</p>
<pre><code>$env:OPENAI_API_KEY | codex login --with-api-key</code></pre></div>
<div class="pane pane-cx-lin">
<p><strong>Open the terminal:</strong> press Ctrl+Alt+T.</p>
<p>Install Codex:</p>
<pre><code>curl -fsSL https://chatgpt.com/codex/install.sh | sh</code></pre>
<p>Check it worked:</p>
<pre><code>codex --version</code></pre>
<p>Save your key (replace with your own key):</p>
<pre><code>echo 'export OPENAI_API_KEY="sk-your-key"' &gt;&gt; ~/.bashrc
source ~/.bashrc</code></pre>
<p>Connect the key to Codex:</p>
<pre><code>printenv OPENAI_API_KEY | codex login --with-api-key</code></pre></div>
</div>
</div>
<h4>3. Start it on a task</h4>
<p>Make a folder for your project and go into it:</p>
<pre><code>mkdir sales-check
cd sales-check</code></pre>
<p>Start Codex from inside that folder, then confirm it is using your API key:</p>
<pre><code>codex
codex login status</code></pre>
<p>Pick a model. Type this and choose one from the list:</p>
<pre><code>/model</code></pre>
<p>Now give it a task. Drop two sales reports into the folder, the same sales recorded by two different sources, then type:</p>
<pre><code>Compare website-sales.csv and store-sales.csv.
List the rows that do not match and save them to a file called mismatches.csv.</code></pre>
</div>
</div>
</div>

### The Catch

This is the most expensive option because it has no ceiling. The more you run the agent, the more you pay.

So if you expect to lean on a coding agent often, a subscription is usually the better deal. That is the next option: Claude Max or ChatGPT Pro. You pay a flat monthly fee and get a large allowance of use, spread across session and weekly limits. 

If you hit a limit and need to keep going before it resets, you can switch the same agent over to API billing to cover the gap. A subscription for the bulk of the work, API billing for the overflow, is what the next section sets up.



