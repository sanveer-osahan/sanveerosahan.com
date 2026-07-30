---
title: "Set Up your AI Coding Agent: From Premium to Free"
description: "A setup guide to the major AI coding agents across price tiers, from premium down to free."
publishDate: 2026-07-30
draft: false
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

<div class="table-wrap">
<table>
<thead>
<tr>
<th>Tier</th>
<th>Price</th>
<th>Best for</th>
</tr>
</thead>
<tbody>
<tr>
<td><a href="#the-infinite-spend-option-coding-agents-on-api-billing">API Billing</a></td>
<td>Pay per use, no ceiling</td>
<td>Occasional or unpredictable use</td>
</tr>
<tr>
<td><a href="#the-high-cost-option-coding-agents-on-premium-billing">Premium</a></td>
<td>$100–$200/month</td>
<td>Heavy, daily use</td>
</tr>
<tr>
<td><a href="#the-entry-level-option-coding-agents-on-standard-billing">Entry-Level</a></td>
<td>$20/month</td>
<td>A few sessions a week — most people start here</td>
</tr>
<tr>
<td><a href="#the-zero-cost-option-coding-agents-on-openrouter">Zero-Cost</a></td>
<td>Free</td>
<td>Just want to try it out</td>
</tr>
</tbody>
</table>
</div>

## The Infinite Spend Option: Coding Agents on API Billing

The costliest option is a coding agent like Claude Code or Codex paired with API-based billing from the companies behind Claude (Anthropic) and ChatGPT (OpenAI).

Here you are charged based on which model you use and how much you use it. There is no fixed monthly fee. You pay for exactly what you use, and there is no upper limit.

These are language models, so all text is broken down into tokens. To keep it simple, assume 1 word = 1 token. What you send to the model are input tokens. What the model
sends back are output tokens.

<figure class="diagram">
<img class="theme-light-only" src="/images/posts/set-up-your-ai-coding-agent/diagram-4-tokens.light.png" alt="Your files, prompts, and chat window all feed into the AI model as input tokens. The model sends back reasoning and responses as output tokens, and the responses flow back into the chat window." />
<img class="theme-dark-only" src="/images/posts/set-up-your-ai-coding-agent/diagram-4-tokens.dark.png" alt="Your files, prompts, and chat window all feed into the AI model as input tokens. The model sends back reasoning and responses as output tokens, and the responses flow back into the chat window." />
<figcaption>Everything you send in is input tokens. Everything the model sends back is output tokens.</figcaption>
</figure>

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

## The High Cost Option: Coding Agents on Premium Billing

The next step down is a premium subscription.

Claude has a cheaper Pro plan and a premium Max plan. Codex has a cheaper Plus plan and a premium Pro plan. We discuss the cheaper entry plans in the next section.

The premium plans come in two options, 5X and 20X. Here is the pricing:

<div class="table-wrap">
<table>
<thead>
<tr>
<th>Provider</th>
<th>Plan</th>
<th>Per month (USD)</th>
<th>Per month (INR)</th>
</tr>
</thead>
<tbody>
<tr>
<td rowspan="3">Anthropic</td>
<td>Claude Pro</td>
<td>$20</td>
<td>₹2,399</td>
</tr>
<tr>
<td>Claude Max 5X</td>
<td>$100</td>
<td>₹11,999</td>
</tr>
<tr>
<td>Claude Max 20X</td>
<td>$200</td>
<td>₹23,999</td>
</tr>
<tr>
<td rowspan="3">OpenAI</td>
<td>ChatGPT Plus</td>
<td>$20</td>
<td>₹1,999</td>
</tr>
<tr>
<td>ChatGPT Pro 5X</td>
<td>$100</td>
<td>₹10,699</td>
</tr>
<tr>
<td>ChatGPT Pro 20X</td>
<td>$200</td>
<td>₹19,900</td>
</tr>
</tbody>
</table>
</div>

The subscription plans come with usage limits, and the premium plans simply provide 5X and 20X of the entry level's usage limits.

When you send your first message, the 5-hour session window starts, and there is a limit to how much you can use the agent in this window. There is also a weekly limit, and your combined 5-hour session usage contributes to it. If you reach a limit, you'll have to wait for it to reset to continue, or you can use API billing to continue the task.

<figure class="diagram">
<img class="theme-light-only" src="/images/posts/set-up-your-ai-coding-agent/diagram-5-limits.light.png" alt="A five-hour session window that refills sits on top of two weekly caps that drain, one covering all models and one covering a single model. The session window draws from both weekly caps, and either one running empty stops the agent." />
<img class="theme-dark-only" src="/images/posts/set-up-your-ai-coding-agent/diagram-5-limits.dark.png" alt="A five-hour session window that refills sits on top of two weekly caps that drain, one covering all models and one covering a single model. The session window draws from both weekly caps, and either one running empty stops the agent." />
<figcaption>The session window refills every few hours. The weekly caps only reset once a week.</figcaption>
</figure>

Every model has its own usage cost.

You pick the model based on the complexity of the task. A larger model gives you better results but consumes usage faster.

Here is roughly how many prompts a single 5-hour window gets you, model by model:

<div class="table-wrap">
<table>
<thead>
<tr>
<th>Provider</th>
<th>Model</th>
<th>Size</th>
<th>Entry</th>
<th>5X</th>
<th>20X</th>
</tr>
</thead>
<tbody>
<tr>
<td rowspan="4">Anthropic</td>
<td>Haiku 4.5</td>
<td>S</td>
<td>25–110</td>
<td>125–550</td>
<td>500–2,200</td>
</tr>
<tr>
<td>Sonnet 5</td>
<td>M</td>
<td>10–45</td>
<td>50–225</td>
<td>200–900</td>
</tr>
<tr>
<td>Opus 4.8</td>
<td>L</td>
<td>8–34</td>
<td>40–170</td>
<td>160–680</td>
</tr>
<tr>
<td>Fable 5</td>
<td>XL</td>
<td>4–17</td>
<td>20–85</td>
<td>80–340</td>
</tr>
<tr>
<td rowspan="3">OpenAI</td>
<td>GPT-5.6 Luna</td>
<td>S</td>
<td>50–280</td>
<td>250–1,400</td>
<td>1,000–5,600</td>
</tr>
<tr>
<td>GPT-5.6 Terra</td>
<td>M</td>
<td>20–110</td>
<td>100–550</td>
<td>400–2,200</td>
</tr>
<tr>
<td>GPT-5.6 Sol</td>
<td>L</td>
<td>15–90</td>
<td>75–450</td>
<td>300–1,800</td>
</tr>
</tbody>
</table>
</div>

On the mid-size model, those ranges feel like this:

| Tier | Feels like |
|---|---|
| Entry | An hour or two of back and forth, then you wait for the window to reset. |
| Premium 5X | A solid working day, most days of the week. |
| Premium 20X | All week, unless you keep the agent running almost constantly. |

### Setting It Up

<div class="tabset">
<input class="tabr" type="radio" name="pagent" id="pagent-cc" checked>
<input class="tabr" type="radio" name="pagent" id="pagent-cx">
<div class="tabnav">
<label for="pagent-cc">Claude Code</label>
<label for="pagent-cx">Codex</label>
</div>
<div class="tabpanes">
<div class="pane pane-pagent-cc">
<h4>1. Subscribe to Claude Max</h4>
<ol>
<li><a href="https://claude.ai">Sign up or log in</a> to Claude.</li>
<li>Open <a href="https://claude.ai/settings/billing">Settings and Billing</a> and upgrade to Max. Pick 5X to start. You can move up later without losing anything.</li>
<li>There is no API key here and nothing to copy. The plan is attached to the account you just logged in with.</li>
</ol>
<h4>2. Install and sign in</h4>
<div class="tabset">
<input class="tabr" type="radio" name="pcc-os" id="pcc-mac" checked>
<input class="tabr" type="radio" name="pcc-os" id="pcc-win">
<input class="tabr" type="radio" name="pcc-os" id="pcc-lin">
<div class="tabnav">
<label for="pcc-mac">macOS</label>
<label for="pcc-win">Windows</label>
<label for="pcc-lin">Linux</label>
</div>
<div class="tabpanes">
<div class="pane pane-pcc-mac">
<p><strong>Open the terminal:</strong> press Cmd+Space, type Terminal, and press Enter.</p>
<p>Install Claude Code:</p>
<pre><code>curl -fsSL https://claude.ai/install.sh | bash</code></pre>
<p>Check it worked:</p>
<pre><code>claude --version</code></pre>
<p class="note">If you followed the previous section, remove the API key first or it will keep billing your API account instead of your plan. Delete the <code>ANTHROPIC_API_KEY</code> line from <code>~/.zshrc</code>, then run <code>unset ANTHROPIC_API_KEY</code>.</p>
<p>Start it and sign in through the browser when it asks:</p>
<pre><code>claude</code></pre></div>
<div class="pane pane-pcc-win">
<p><strong>Open PowerShell:</strong> press the Windows key, type PowerShell, and open Windows PowerShell (not Command Prompt).</p>
<p>Install Claude Code:</p>
<pre><code>irm https://claude.ai/install.ps1 | iex</code></pre>
<p>Check it worked:</p>
<pre><code>claude --version</code></pre>
<p class="note">If you followed the previous section, clear the API key first or it will keep billing your API account instead of your plan. Run <code>setx ANTHROPIC_API_KEY ""</code>, then close and reopen PowerShell.</p>
<p>Start it and sign in through the browser when it asks:</p>
<pre><code>claude</code></pre></div>
<div class="pane pane-pcc-lin">
<p><strong>Open the terminal:</strong> press Ctrl+Alt+T.</p>
<p>Install Claude Code:</p>
<pre><code>curl -fsSL https://claude.ai/install.sh | bash</code></pre>
<p>Check it worked:</p>
<pre><code>claude --version</code></pre>
<p class="note">If you followed the previous section, remove the API key first or it will keep billing your API account instead of your plan. Delete the <code>ANTHROPIC_API_KEY</code> line from <code>~/.bashrc</code>, then run <code>unset ANTHROPIC_API_KEY</code>.</p>
<p>Start it and sign in through the browser when it asks:</p>
<pre><code>claude</code></pre></div>
</div>
</div>
<h4>3. Start it on a task</h4>
<p>Confirm it is running on your plan and not on an API key:</p>
<pre><code>/status</code></pre>
<p>Make a folder for your project and go into it:</p>
<pre><code>mkdir sales-check
cd sales-check</code></pre>
<p>Start Claude Code from inside that folder:</p>
<pre><code>claude</code></pre>
<p>Pick a model. Bigger models eat your allowance faster, so start in the middle:</p>
<pre><code>/model</code></pre>
<p>Now give it a task. Drop two sales reports into the folder, the same sales recorded by two different sources, then type:</p>
<pre><code>Compare website-sales.csv and store-sales.csv.
List the rows that do not match and save them to a file called mismatches.csv.</code></pre>
</div>
<div class="pane pane-pagent-cx">
<h4>1. Subscribe to ChatGPT Pro</h4>
<ol>
<li><a href="https://chatgpt.com">Sign up or log in</a> to ChatGPT.</li>
<li>Open your account settings and upgrade to Pro. Choose 5X to start. Pro 20X is the same plan with a larger allowance.</li>
<li>Nothing to copy here either. Codex reads the plan from the account you sign in with.</li>
</ol>
<h4>2. Install and sign in</h4>
<div class="tabset">
<input class="tabr" type="radio" name="pcx-os" id="pcx-mac" checked>
<input class="tabr" type="radio" name="pcx-os" id="pcx-win">
<input class="tabr" type="radio" name="pcx-os" id="pcx-lin">
<div class="tabnav">
<label for="pcx-mac">macOS</label>
<label for="pcx-win">Windows</label>
<label for="pcx-lin">Linux</label>
</div>
<div class="tabpanes">
<div class="pane pane-pcx-mac">
<p><strong>Open the terminal:</strong> press Cmd+Space, type Terminal, and press Enter.</p>
<p>Install Codex:</p>
<pre><code>curl -fsSL https://chatgpt.com/codex/install.sh | sh</code></pre>
<p>Check it worked:</p>
<pre><code>codex --version</code></pre>
<p class="note">If you followed the previous section, remove the API key first. Delete the <code>OPENAI_API_KEY</code> line from <code>~/.zshrc</code>, then run <code>unset OPENAI_API_KEY</code>.</p>
<p>Now run the plain login, the one the previous section told you to skip:</p>
<pre><code>codex login</code></pre></div>
<div class="pane pane-pcx-win">
<p><strong>Open PowerShell:</strong> press the Windows key, type PowerShell, and open Windows PowerShell (not Command Prompt).</p>
<p>Install Codex:</p>
<pre><code>powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"</code></pre>
<p>Check it worked:</p>
<pre><code>codex --version</code></pre>
<p class="note">If you followed the previous section, clear the API key first. Run <code>setx OPENAI_API_KEY ""</code>, then close and reopen PowerShell.</p>
<p>Now run the plain login, the one the previous section told you to skip:</p>
<pre><code>codex login</code></pre></div>
<div class="pane pane-pcx-lin">
<p><strong>Open the terminal:</strong> press Ctrl+Alt+T.</p>
<p>Install Codex:</p>
<pre><code>curl -fsSL https://chatgpt.com/codex/install.sh | sh</code></pre>
<p>Check it worked:</p>
<pre><code>codex --version</code></pre>
<p class="note">If you followed the previous section, remove the API key first. Delete the <code>OPENAI_API_KEY</code> line from <code>~/.bashrc</code>, then run <code>unset OPENAI_API_KEY</code>.</p>
<p>Now run the plain login, the one the previous section told you to skip:</p>
<pre><code>codex login</code></pre></div>
</div>
</div>
<h4>3. Start it on a task</h4>
<p>Confirm it is signed in with your subscription:</p>
<pre><code>codex login status</code></pre>
<p>Make a folder for your project and go into it:</p>
<pre><code>mkdir sales-check
cd sales-check</code></pre>
<p>Start Codex from inside that folder:</p>
<pre><code>codex</code></pre>
<p>Pick a model. Bigger models eat your allowance faster, so start in the middle:</p>
<pre><code>/model</code></pre>
<p>Now give it a task. Drop two sales reports into the folder, the same sales recorded by two different sources, then type:</p>
<pre><code>Compare website-sales.csv and store-sales.csv.
List the rows that do not match and save them to a file called mismatches.csv.</code></pre>
</div>
</div>
</div>

### The Catch

Go for a premium option if you have heavy coding tasks, starting out with a 5X plan first.

If you expect to have few coding tasks in your week, go for an entry-level plan. We cover that in the next section.

## The Entry-Level Option: Coding Agents on Standard Billing

This is the sweet spot. If you're not sure where to start, this is it.

We have already discussed how the usage limits and pricing work in the previous section.

If you are already using the free plans, in Claude you'll have to upgrade to Claude Pro to access Claude Code. But in ChatGPT, you already get limited Codex access; upgrade to ChatGPT Plus to get expanded Codex usage.

### Setting It Up

<div class="tabset">
<input class="tabr" type="radio" name="eagent" id="eagent-cc" checked>
<input class="tabr" type="radio" name="eagent" id="eagent-cx">
<div class="tabnav">
<label for="eagent-cc">Claude Code</label>
<label for="eagent-cx">Codex</label>
</div>
<div class="tabpanes">
<div class="pane pane-eagent-cc">
<h4>1. Subscribe to Claude Pro</h4>
<ol>
<li><a href="https://claude.ai">Sign up or log in</a> to Claude.</li>
<li>Claude Code needs a paid plan. Open <a href="https://claude.ai/settings/billing">Settings and Billing</a> and upgrade to Pro.</li>
<li>There is no API key here and nothing to copy. The plan is attached to the account you just logged in with.</li>
</ol>
<h4>2. Install and sign in</h4>
<div class="tabset">
<input class="tabr" type="radio" name="ecc-os" id="ecc-mac" checked>
<input class="tabr" type="radio" name="ecc-os" id="ecc-win">
<input class="tabr" type="radio" name="ecc-os" id="ecc-lin">
<div class="tabnav">
<label for="ecc-mac">macOS</label>
<label for="ecc-win">Windows</label>
<label for="ecc-lin">Linux</label>
</div>
<div class="tabpanes">
<div class="pane pane-ecc-mac">
<p><strong>Open the terminal:</strong> press Cmd+Space, type Terminal, and press Enter.</p>
<p>Install Claude Code:</p>
<pre><code>curl -fsSL https://claude.ai/install.sh | bash</code></pre>
<p>Check it worked:</p>
<pre><code>claude --version</code></pre>
<p class="note">If you followed an earlier section, remove the API key first or it will keep billing your API account instead of your plan. Delete the <code>ANTHROPIC_API_KEY</code> line from <code>~/.zshrc</code>, then run <code>unset ANTHROPIC_API_KEY</code>.</p>
<p>Start it and sign in through the browser when it asks:</p>
<pre><code>claude</code></pre></div>
<div class="pane pane-ecc-win">
<p><strong>Open PowerShell:</strong> press the Windows key, type PowerShell, and open Windows PowerShell (not Command Prompt).</p>
<p>Install Claude Code:</p>
<pre><code>irm https://claude.ai/install.ps1 | iex</code></pre>
<p>Check it worked:</p>
<pre><code>claude --version</code></pre>
<p class="note">If you followed an earlier section, clear the API key first or it will keep billing your API account instead of your plan. Run <code>setx ANTHROPIC_API_KEY ""</code>, then close and reopen PowerShell.</p>
<p>Start it and sign in through the browser when it asks:</p>
<pre><code>claude</code></pre></div>
<div class="pane pane-ecc-lin">
<p><strong>Open the terminal:</strong> press Ctrl+Alt+T.</p>
<p>Install Claude Code:</p>
<pre><code>curl -fsSL https://claude.ai/install.sh | bash</code></pre>
<p>Check it worked:</p>
<pre><code>claude --version</code></pre>
<p class="note">If you followed an earlier section, remove the API key first or it will keep billing your API account instead of your plan. Delete the <code>ANTHROPIC_API_KEY</code> line from <code>~/.bashrc</code>, then run <code>unset ANTHROPIC_API_KEY</code>.</p>
<p>Start it and sign in through the browser when it asks:</p>
<pre><code>claude</code></pre></div>
</div>
</div>
<h4>3. Start it on a task</h4>
<p>Confirm it is running on your plan and not on an API key:</p>
<pre><code>/status</code></pre>
<p>Make a folder for your project and go into it:</p>
<pre><code>mkdir sales-check
cd sales-check</code></pre>
<p>Start Claude Code from inside that folder:</p>
<pre><code>claude</code></pre>
<p>Pick a model. Type this and choose one from the list:</p>
<pre><code>/model</code></pre>
<p>Now give it a task. Drop two sales reports into the folder, the same sales recorded by two different sources, then type:</p>
<pre><code>Compare website-sales.csv and store-sales.csv.
List the rows that do not match and save them to a file called mismatches.csv.</code></pre>
</div>
<div class="pane pane-eagent-cx">
<h4>1. Subscribe to ChatGPT Plus</h4>
<ol>
<li><a href="https://chatgpt.com">Sign up or log in</a> to ChatGPT.</li>
<li>You already get limited Codex access on the free plan. Open your account settings and upgrade to Plus for expanded usage.</li>
<li>Nothing to copy here either. Codex reads the plan from the account you sign in with.</li>
</ol>
<h4>2. Install and sign in</h4>
<div class="tabset">
<input class="tabr" type="radio" name="ecx-os" id="ecx-mac" checked>
<input class="tabr" type="radio" name="ecx-os" id="ecx-win">
<input class="tabr" type="radio" name="ecx-os" id="ecx-lin">
<div class="tabnav">
<label for="ecx-mac">macOS</label>
<label for="ecx-win">Windows</label>
<label for="ecx-lin">Linux</label>
</div>
<div class="tabpanes">
<div class="pane pane-ecx-mac">
<p><strong>Open the terminal:</strong> press Cmd+Space, type Terminal, and press Enter.</p>
<p>Install Codex:</p>
<pre><code>curl -fsSL https://chatgpt.com/codex/install.sh | sh</code></pre>
<p>Check it worked:</p>
<pre><code>codex --version</code></pre>
<p class="note">If you followed an earlier section, remove the API key first. Delete the <code>OPENAI_API_KEY</code> line from <code>~/.zshrc</code>, then run <code>unset OPENAI_API_KEY</code>.</p>
<p>Sign in with your account:</p>
<pre><code>codex login</code></pre></div>
<div class="pane pane-ecx-win">
<p><strong>Open PowerShell:</strong> press the Windows key, type PowerShell, and open Windows PowerShell (not Command Prompt).</p>
<p>Install Codex:</p>
<pre><code>powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"</code></pre>
<p>Check it worked:</p>
<pre><code>codex --version</code></pre>
<p class="note">If you followed an earlier section, clear the API key first. Run <code>setx OPENAI_API_KEY ""</code>, then close and reopen PowerShell.</p>
<p>Sign in with your account:</p>
<pre><code>codex login</code></pre></div>
<div class="pane pane-ecx-lin">
<p><strong>Open the terminal:</strong> press Ctrl+Alt+T.</p>
<p>Install Codex:</p>
<pre><code>curl -fsSL https://chatgpt.com/codex/install.sh | sh</code></pre>
<p>Check it worked:</p>
<pre><code>codex --version</code></pre>
<p class="note">If you followed an earlier section, remove the API key first. Delete the <code>OPENAI_API_KEY</code> line from <code>~/.bashrc</code>, then run <code>unset OPENAI_API_KEY</code>.</p>
<p>Sign in with your account:</p>
<pre><code>codex login</code></pre></div>
</div>
</div>
<h4>3. Start it on a task</h4>
<p>Confirm it is signed in with your subscription:</p>
<pre><code>codex login status</code></pre>
<p>Make a folder for your project and go into it:</p>
<pre><code>mkdir sales-check
cd sales-check</code></pre>
<p>Start Codex from inside that folder:</p>
<pre><code>codex</code></pre>
<p>Pick a model. Type this and choose one from the list:</p>
<pre><code>/model</code></pre>
<p>Now give it a task. Drop two sales reports into the folder, the same sales recorded by two different sources, then type:</p>
<pre><code>Compare website-sales.csv and store-sales.csv.
List the rows that do not match and save them to a file called mismatches.csv.</code></pre>
</div>
</div>
</div>

### The Catch

If you are using the Claude and ChatGPT chats along with the coding agent, note that both will contribute towards usage limits. So try to have only one source of interaction to avoid surprises.

Coding agents can do general chats and research too. If you are researching something and then need to implement a solution based on it, it's better to do both in the same coding agent session instead of switching between chat and agent.

## The Zero-Cost Option: Coding Agents on OpenRouter

If you are a student who wants to try out a coding agent at zero cost and with minimal setup, <a href="https://openrouter.ai">OpenRouter</a> is the answer.

OpenRouter works just like <a href="#the-infinite-spend-option-coding-agents-on-api-billing">a coding agent with API billing</a>. It is a service that gives you unified access to different models through a single API.

<figure class="diagram">
<img class="theme-light-only" src="/images/posts/set-up-your-ai-coding-agent/diagram-6-openrouter.light.png" alt="OpenRouter sits between your coding agent and many model providers. One API key plugs in, and OpenRouter reaches Claude, GPT, and open-source models on the other side, several of which cost nothing to use." />
<img class="theme-dark-only" src="/images/posts/set-up-your-ai-coding-agent/diagram-6-openrouter.dark.png" alt="OpenRouter sits between your coding agent and many model providers. One API key plugs in, and OpenRouter reaches Claude, GPT, and open-source models on the other side, several of which cost nothing to use." />
<figcaption>One key fits every provider behind it. A few of those models are free.</figcaption>
</figure>

In the API Billing option, you are locked into the provider of the models. With Claude Code, you can only use Claude models, and with Codex, you can only use ChatGPT models.

With OpenRouter, you get the flexibility of switching between models, with the option of choosing from models that are free to use.

<div class="table-wrap">
<table>
<thead>
<tr>
<th>Model</th>
<th>What to expect</th>
<th>Switch in Claude Code</th>
<th>Switch in Codex</th>
</tr>
</thead>
<tbody>
<tr>
<td>Nemotron 3 Ultra</td>
<td>A large, general-purpose model marketed for agent and coding use. More headroom for bigger tasks, but expect slower replies than the two below.</td>
<td><code>/model nvidia/nemotron-3-ultra-550b-a55b:free</code></td>
<td><code>codex --model nvidia/nemotron-3-ultra-550b-a55b:free</code></td>
</tr>
<tr>
<td>North Mini Code</td>
<td>Built specifically for coding agents. Handles multi-step tasks and tool calls well, and tested faster than some larger models.</td>
<td><code>/model cohere/north-mini-code:free</code></td>
<td><code>codex --model cohere/north-mini-code:free</code></td>
</tr>
<tr>
<td>Laguna S 2.1</td>
<td>Made by a startup that only builds coding-agent models. Good at multi-step reasoning.</td>
<td><code>/model poolside/laguna-s-2.1:free</code></td>
<td><code>codex --model poolside/laguna-s-2.1:free</code></td>
</tr>
</tbody>
</table>
</div>

Free models get delisted and added often, so check <a href="https://openrouter.ai/collections/free-models">OpenRouter's live free-model list</a> before you rely on one for the long run.

### Setting It Up

<div class="tabset">
<input class="tabr" type="radio" name="zagent" id="zagent-cc" checked>
<input class="tabr" type="radio" name="zagent" id="zagent-cx">
<div class="tabnav">
<label for="zagent-cc">Claude Code</label>
<label for="zagent-cx">Codex</label>
</div>
<div class="tabpanes">
<div class="pane pane-zagent-cc">
<h4>1. Create an OpenRouter API key</h4>
<ol>
<li><a href="https://openrouter.ai/keys">Sign up or log in</a> to OpenRouter.</li>
<li>Click <strong>Create Key</strong> and copy it. It starts with <code>sk-or-</code> and is shown only once, so paste it somewhere safe.</li>
</ol>
<h4>2. Install and point Claude Code at OpenRouter</h4>
<div class="tabset">
<input class="tabr" type="radio" name="zcc-os" id="zcc-mac" checked>
<input class="tabr" type="radio" name="zcc-os" id="zcc-win">
<input class="tabr" type="radio" name="zcc-os" id="zcc-lin">
<div class="tabnav">
<label for="zcc-mac">macOS</label>
<label for="zcc-win">Windows</label>
<label for="zcc-lin">Linux</label>
</div>
<div class="tabpanes">
<div class="pane pane-zcc-mac">
<p><strong>Open the terminal:</strong> press Cmd+Space, type Terminal, and press Enter.</p>
<p>Install Claude Code:</p>
<pre><code>curl -fsSL https://claude.ai/install.sh | bash</code></pre>
<p>Check it worked:</p>
<pre><code>claude --version</code></pre>
<p class="note">If you followed an earlier section, remove the old key first. Delete the <code>ANTHROPIC_API_KEY</code> line from <code>~/.zshrc</code>, then run <code>unset ANTHROPIC_API_KEY</code>.</p>
<p>Point it at OpenRouter (replace with your own key):</p>
<pre><code>echo 'export OPENROUTER_API_KEY="sk-or-your-key"' &gt;&gt; ~/.zshrc
echo 'export ANTHROPIC_BASE_URL="https://openrouter.ai/api"' &gt;&gt; ~/.zshrc
echo 'export ANTHROPIC_AUTH_TOKEN="$OPENROUTER_API_KEY"' &gt;&gt; ~/.zshrc
echo 'export ANTHROPIC_API_KEY=""' &gt;&gt; ~/.zshrc
source ~/.zshrc</code></pre>
<p class="note">OpenRouter says Claude Code works most reliably with Anthropic-hosted models routed through it. Pick a free, non-Anthropic model instead, and tool calls may not behave as well.</p></div>
<div class="pane pane-zcc-win">
<p><strong>Open PowerShell:</strong> press the Windows key, type PowerShell, and open Windows PowerShell (not Command Prompt).</p>
<p>Install Claude Code:</p>
<pre><code>irm https://claude.ai/install.ps1 | iex</code></pre>
<p>Check it worked:</p>
<pre><code>claude --version</code></pre>
<p class="note">If you followed an earlier section, clear the old key first. Run <code>setx ANTHROPIC_API_KEY ""</code>, then close and reopen PowerShell.</p>
<p>Point it at OpenRouter (replace with your own key), then close and reopen PowerShell:</p>
<pre><code>setx OPENROUTER_API_KEY "sk-or-your-key"
setx ANTHROPIC_BASE_URL "https://openrouter.ai/api"
setx ANTHROPIC_AUTH_TOKEN "sk-or-your-key"
setx ANTHROPIC_API_KEY ""</code></pre>
<p class="note">OpenRouter says Claude Code works most reliably with Anthropic-hosted models routed through it. Pick a free, non-Anthropic model instead, and tool calls may not behave as well.</p></div>
<div class="pane pane-zcc-lin">
<p><strong>Open the terminal:</strong> press Ctrl+Alt+T.</p>
<p>Install Claude Code:</p>
<pre><code>curl -fsSL https://claude.ai/install.sh | bash</code></pre>
<p>Check it worked:</p>
<pre><code>claude --version</code></pre>
<p class="note">If you followed an earlier section, remove the old key first. Delete the <code>ANTHROPIC_API_KEY</code> line from <code>~/.bashrc</code>, then run <code>unset ANTHROPIC_API_KEY</code>.</p>
<p>Point it at OpenRouter (replace with your own key):</p>
<pre><code>echo 'export OPENROUTER_API_KEY="sk-or-your-key"' &gt;&gt; ~/.bashrc
echo 'export ANTHROPIC_BASE_URL="https://openrouter.ai/api"' &gt;&gt; ~/.bashrc
echo 'export ANTHROPIC_AUTH_TOKEN="$OPENROUTER_API_KEY"' &gt;&gt; ~/.bashrc
echo 'export ANTHROPIC_API_KEY=""' &gt;&gt; ~/.bashrc
source ~/.bashrc</code></pre>
<p class="note">OpenRouter says Claude Code works most reliably with Anthropic-hosted models routed through it. Pick a free, non-Anthropic model instead, and tool calls may not behave as well.</p></div>
</div>
</div>
<h4>3. Start it on a task</h4>
<p>Make a folder for your project and go into it:</p>
<pre><code>mkdir sales-check
cd sales-check</code></pre>
<p>Start Claude Code from inside that folder:</p>
<pre><code>claude</code></pre>
<p>Confirm it is using OpenRouter:</p>
<pre><code>/status</code></pre>
<p>Switch to one of the free models from the table above by typing its slug:</p>
<pre><code>/model cohere/north-mini-code:free</code></pre>
<p>Now give it a task. Drop two sales reports into the folder, the same sales recorded by two different sources, then type:</p>
<pre><code>Compare website-sales.csv and store-sales.csv.
List the rows that do not match and save them to a file called mismatches.csv.</code></pre>
</div>
<div class="pane pane-zagent-cx">
<h4>1. Create an OpenRouter API key</h4>
<ol>
<li><a href="https://openrouter.ai/keys">Sign up or log in</a> to OpenRouter.</li>
<li>Click <strong>Create Key</strong> and copy it. It starts with <code>sk-or-</code> and is shown only once, so paste it somewhere safe.</li>
</ol>
<h4>2. Install and point Codex at OpenRouter</h4>
<div class="tabset">
<input class="tabr" type="radio" name="zcx-os" id="zcx-mac" checked>
<input class="tabr" type="radio" name="zcx-os" id="zcx-win">
<input class="tabr" type="radio" name="zcx-os" id="zcx-lin">
<div class="tabnav">
<label for="zcx-mac">macOS</label>
<label for="zcx-win">Windows</label>
<label for="zcx-lin">Linux</label>
</div>
<div class="tabpanes">
<div class="pane pane-zcx-mac">
<p><strong>Open the terminal:</strong> press Cmd+Space, type Terminal, and press Enter.</p>
<p>Install Codex:</p>
<pre><code>curl -fsSL https://chatgpt.com/codex/install.sh | sh</code></pre>
<p>Check it worked:</p>
<pre><code>codex --version</code></pre>
<p class="note">If you followed an earlier section, remove the old key first. Delete the <code>OPENAI_API_KEY</code> line from <code>~/.zshrc</code>, then run <code>unset OPENAI_API_KEY</code>.</p>
<p>Save your OpenRouter key (replace with your own key):</p>
<pre><code>echo 'export OPENROUTER_API_KEY="sk-or-your-key"' &gt;&gt; ~/.zshrc
source ~/.zshrc</code></pre>
<p>Pick a slug from the table above, or browse <a href="https://openrouter.ai/collections/free-models">OpenRouter's free models</a> for another. Then create <code>~/.codex/config.toml</code> with this, swapping in the slug you picked:</p>
<pre><code>model_provider = "openrouter"
model = "cohere/north-mini-code:free"

[model_providers.openrouter]
name = "OpenRouter"
base_url = "https://openrouter.ai/api/v1"
env_key = "OPENROUTER_API_KEY"</code></pre></div>
<div class="pane pane-zcx-win">
<p><strong>Open PowerShell:</strong> press the Windows key, type PowerShell, and open Windows PowerShell (not Command Prompt).</p>
<p>Install Codex:</p>
<pre><code>powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"</code></pre>
<p>Check it worked:</p>
<pre><code>codex --version</code></pre>
<p class="note">If you followed an earlier section, clear the old key first. Run <code>setx OPENAI_API_KEY ""</code>, then close and reopen PowerShell.</p>
<p>Save your OpenRouter key (replace with your own), then close and reopen PowerShell:</p>
<pre><code>setx OPENROUTER_API_KEY "sk-or-your-key"</code></pre>
<p>Pick a slug from the table above, or browse <a href="https://openrouter.ai/collections/free-models">OpenRouter's free models</a> for another. Then create <code>~/.codex/config.toml</code> with this, swapping in the slug you picked:</p>
<pre><code>model_provider = "openrouter"
model = "cohere/north-mini-code:free"

[model_providers.openrouter]
name = "OpenRouter"
base_url = "https://openrouter.ai/api/v1"
env_key = "OPENROUTER_API_KEY"</code></pre></div>
<div class="pane pane-zcx-lin">
<p><strong>Open the terminal:</strong> press Ctrl+Alt+T.</p>
<p>Install Codex:</p>
<pre><code>curl -fsSL https://chatgpt.com/codex/install.sh | sh</code></pre>
<p>Check it worked:</p>
<pre><code>codex --version</code></pre>
<p class="note">If you followed an earlier section, remove the old key first. Delete the <code>OPENAI_API_KEY</code> line from <code>~/.bashrc</code>, then run <code>unset OPENAI_API_KEY</code>.</p>
<p>Save your OpenRouter key (replace with your own key):</p>
<pre><code>echo 'export OPENROUTER_API_KEY="sk-or-your-key"' &gt;&gt; ~/.bashrc
source ~/.bashrc</code></pre>
<p>Pick a slug from the table above, or browse <a href="https://openrouter.ai/collections/free-models">OpenRouter's free models</a> for another. Then create <code>~/.codex/config.toml</code> with this, swapping in the slug you picked:</p>
<pre><code>model_provider = "openrouter"
model = "cohere/north-mini-code:free"

[model_providers.openrouter]
name = "OpenRouter"
base_url = "https://openrouter.ai/api/v1"
env_key = "OPENROUTER_API_KEY"</code></pre></div>
</div>
</div>
<h4>3. Start it on a task</h4>
<p>Make a folder for your project and go into it:</p>
<pre><code>mkdir sales-check
cd sales-check</code></pre>
<p>Start Codex from inside that folder:</p>
<pre><code>codex</code></pre>
<p>To try a different free model without editing the file again, override it for one run:</p>
<pre><code>codex --model poolside/laguna-s-2.1:free</code></pre>
<p>Now give it a task. Drop two sales reports into the folder, the same sales recorded by two different sources, then type:</p>
<pre><code>Compare website-sales.csv and store-sales.csv.
List the rows that do not match and save them to a file called mismatches.csv.</code></pre>
</div>
</div>
</div>

### The Catch

If you are using a free model variant (with an ID ending in <code>:free</code>), then OpenRouter applies the following limits: 20 requests per minute and 50 requests per day.

A coding agent will consume this quickly, hence only go with this option if you just want to try it out.

There is another way of having unlimited usage, but it requires an investment in hardware to run the AI models locally. I will write another blog soon on how to set up coding agents with models running locally on various hardware options. It will compare their performance on each option against the models from providers like Anthropic and OpenAI.



