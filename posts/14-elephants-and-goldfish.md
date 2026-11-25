---
title: In multi-agent systems, the brief is the unit of engineering
summary: Engineer multi-agent work as reviewable briefs for stateless workers, because a brief can be checked and a shared memory cannot.
tags: agents, workflow
kind: opinion
date: 2026-11-17
---

The common view is that multi-agent design is an org chart. Give one agent a manager's title, another a researcher's, a third a reviewer's, and expect the division of labor to produce better work. I think that view points at the wrong unit. The unit of engineering is the brief, meaning the text a worker receives when it starts. Stateless workers with complete briefs should beat workers that share a long memory, and the reason is practical. A brief can be reviewed, versioned and tested. A memory cannot.

Start with the strongest evidence on the other side. [Anthropic's account of its research system (2025)](https://www.anthropic.com/engineering/multi-agent-research-system) reports that a multi-agent setup outperformed single-agent Claude Opus 4 by 90.2% on an internal research evaluation. Each subagent there gets a fresh context window, works one branch, and returns a summary to the lead, so the lead's window never holds the dead ends. The worker is a goldfish on purpose. It forgets its search when it returns, and the lead keeps the finding. That arrangement is the real design, and the titles sit on top of it.

The same post says agents typically use about 4x more tokens than chat interactions, and multi-agent systems about 15x. It also says that token usage by itself explains 80% of the variance in the BrowseComp evaluation. I read that as a warning about what the gain is. Most of it is spend, and the roles are a way of buying separate context windows, not a way of buying expertise.

```chart
title: Token use relative to one chat interaction
unit: x
source: Anthropic, 2025
Agent: 4
Multi-agent system: 15
note: Anthropic gives both as "about" figures; the baseline is one chat interaction.
```

Context is not neutral storage. Every call rereads the whole window, so a bloated transcript is a cost paid on each turn, not once. [Liu et al. (2023)](https://arxiv.org/abs/2307.03172) found that performance can degrade significantly when the position of relevant information changes, and that it is often highest when that information sits at the beginning or end of the input. Anthropic's [context engineering post (2025)](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) calls the related failure "context rot" and sets the goal as the "smallest possible set of high-signal tokens." Tools add to the bill. Anthropic's [guide to writing tools for agents (2025)](https://anthropic.com/engineering/writing-tools-for-agents) reports that Claude Code caps tool responses at 25,000 tokens by default, and warns that "more tools don't always lead to better outcomes." A worker's brief is the context it reasons from, so the brief is where that curation has to happen.

I think the role names are overrated. A reviewer persona mostly changes the prompt text. What changes behavior is which tokens each model call receives. Give the same model the same tools and the same brief under a neutral name, and I would bet the difference is small. Most of what looks like specialization is context partitioning, and partitioning is a decision the planner makes, whether or not anyone writes it down.

My first proposal is to make the planner write every brief as a file in the repository, with four parts: scope, sources, acceptance test, and what not to do. Review those files in a pull request, the way you would review code, before any worker starts. The mechanism is that the gaps become visible while they are still cheap. A reviewer can see that a brief asks for a search of three directories and never says which were already searched, or that its acceptance test is "the summary reads well." Those gaps cost tokens to find after the run, and a reviewer finds them in minutes at no token cost. Inside the file, I would put the acceptance test and the do-not-do list at the start or the end, where Liu et al. report performance is often highest, and keep the middle for background. The file also outlives the run, so the next brief for a similar task can start from a reviewed one instead of from memory.

```diagram
title: What a brief contains
caption: The four parts of a brief, kept as one reviewable file. The acceptance test is highlighted because a reviewer can check it before any worker starts.
<svg viewBox="0 0 640 290" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="120" width="120" height="50" rx="6" class="box"/>
  <text x="80" y="142" text-anchor="middle" class="lbl">Planner</text>
  <text x="80" y="160" text-anchor="middle" class="sub">writes it</text>
  <path d="M140 145 H170" class="edge" marker-end="url(#arr)"/>
  <rect x="170" y="20" width="300" height="248" rx="6" class="box"/>
  <text x="320" y="46" text-anchor="middle" class="lbl">The brief, as a file</text>
  <rect x="186" y="58" width="268" height="42" rx="6" class="box"/>
  <text x="320" y="76" text-anchor="middle" class="lbl">Scope</text>
  <text x="320" y="92" text-anchor="middle" class="sub">what this worker answers</text>
  <rect x="186" y="110" width="268" height="42" rx="6" class="box"/>
  <text x="320" y="128" text-anchor="middle" class="lbl">Sources</text>
  <text x="320" y="144" text-anchor="middle" class="sub">background to read, not paste</text>
  <rect x="186" y="162" width="268" height="42" rx="6" class="box hi"/>
  <text x="320" y="180" text-anchor="middle" class="lbl">Acceptance test</text>
  <text x="320" y="196" text-anchor="middle" class="sub">a check the output can pass or fail</text>
  <rect x="186" y="214" width="268" height="42" rx="6" class="box"/>
  <text x="320" y="232" text-anchor="middle" class="lbl">What not to do</text>
  <text x="320" y="248" text-anchor="middle" class="sub">out of scope, files not to touch</text>
  <path d="M470 145 H500" class="edge" marker-end="url(#arr)"/>
  <rect x="500" y="120" width="120" height="50" rx="6" class="box"/>
  <text x="560" y="142" text-anchor="middle" class="lbl">Worker</text>
  <text x="560" y="160" text-anchor="middle" class="sub">reads only this</text>
</svg>
```

Two things could make this fail. The first is bloat. Briefs can grow into specifications nobody reads, and the review turns into a rubber stamp. I would cap a brief at what a reviewer can read in a few minutes, and point the worker at background sources instead of pasting them in. The second is shared blind spots. A planner writes the acceptance test from its own reading of the task, so a brief reviewed by the same planner can encode a misreading with confidence. A second reader helps, but only partly. What would convince me is a measurement, not a feeling: the share of first-pass worker results that fail their acceptance test, compared before and after brief review, on the same kinds of task. If that share does not move, I would drop the review step, because it would be ceremony.

The same habit applies after a failure. The worker's output is evidence about the brief before it is evidence about the worker. When a worker returns something wrong, I would read its brief before its output. If the brief did not say what was already ruled out, the worker repeated a search it could not have known to skip, and the fix belongs in the brief. I'd bet a retry with the same brief repeats the mistake.

```diagram
title: Planner, briefs and stateless workers
caption: The planner writes one brief per worker and each worker sees only its brief. A failed result goes back through the planner to the brief, not to the worker.
<svg viewBox="0 0 640 300" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="60" width="130" height="170" rx="6" class="box hi"/>
  <text x="85" y="130" text-anchor="middle" class="lbl">Planner</text>
  <text x="85" y="150" text-anchor="middle" class="sub">keeps the memory</text>
  <text x="85" y="168" text-anchor="middle" class="sub">writes, reviews</text>
  <g class="step1">
    <path d="M150 85 H190" class="edge flow" marker-end="url(#arr)"/>
    <rect x="190" y="60" width="130" height="50" rx="6" class="box"/>
    <text x="255" y="82" text-anchor="middle" class="lbl">Brief B1</text>
    <text x="255" y="100" text-anchor="middle" class="sub">self-contained</text>
    <path d="M150 155 H190" class="edge flow" marker-end="url(#arr)"/>
    <rect x="190" y="130" width="130" height="50" rx="6" class="box"/>
    <text x="255" y="152" text-anchor="middle" class="lbl">Brief B2</text>
    <text x="255" y="170" text-anchor="middle" class="sub">self-contained</text>
    <path d="M150 225 H190" class="edge flow" marker-end="url(#arr)"/>
    <rect x="190" y="200" width="130" height="50" rx="6" class="box"/>
    <text x="255" y="222" text-anchor="middle" class="lbl">Brief B3</text>
    <text x="255" y="240" text-anchor="middle" class="sub">self-contained</text>
  </g>
  <g class="step2">
    <path d="M320 85 H370" class="edge flow" marker-end="url(#arr)"/>
    <rect x="370" y="60" width="110" height="50" rx="6" class="box"/>
    <text x="425" y="82" text-anchor="middle" class="lbl">Worker W1</text>
    <text x="425" y="100" text-anchor="middle" class="sub">reads B1 only</text>
    <path d="M320 155 H370" class="edge flow" marker-end="url(#arr)"/>
    <rect x="370" y="130" width="110" height="50" rx="6" class="box"/>
    <text x="425" y="152" text-anchor="middle" class="lbl">Worker W2</text>
    <text x="425" y="170" text-anchor="middle" class="sub">reads B2 only</text>
    <path d="M320 225 H370" class="edge flow" marker-end="url(#arr)"/>
    <rect x="370" y="200" width="110" height="50" rx="6" class="box"/>
    <text x="425" y="222" text-anchor="middle" class="lbl">Worker W3</text>
    <text x="425" y="240" text-anchor="middle" class="sub">reads B3 only</text>
  </g>
  <g class="step3">
    <path d="M480 85 H510" class="edge" marker-end="url(#arr)"/>
    <rect x="510" y="60" width="110" height="50" rx="6" class="box bad"/>
    <text x="565" y="82" text-anchor="middle" class="lbl">Result R1</text>
    <text x="565" y="100" text-anchor="middle" class="sub">fails check</text>
    <path d="M480 155 H510" class="edge" marker-end="url(#arr)"/>
    <rect x="510" y="130" width="110" height="50" rx="6" class="box good"/>
    <text x="565" y="152" text-anchor="middle" class="lbl">Result R2</text>
    <text x="565" y="170" text-anchor="middle" class="sub">passes</text>
    <path d="M480 225 H510" class="edge" marker-end="url(#arr)"/>
    <rect x="510" y="200" width="110" height="50" rx="6" class="box good"/>
    <text x="565" y="222" text-anchor="middle" class="lbl">Result R3</text>
    <text x="565" y="240" text-anchor="middle" class="sub">passes</text>
  </g>
  <g class="step4">
    <path d="M565 250 V290 H85 V230" class="edge" marker-end="url(#arr)"/>
    <text x="325" y="284" text-anchor="middle" class="sub">results return; planner reviews each one</text>
    <path d="M85 60 V36 H255 V60" class="edge bad" marker-end="url(#arr)"/>
    <text x="170" y="28" text-anchor="middle" class="sub">failed result: fix the brief</text>
  </g>
</svg>
```

My second proposal is about scope. Use goldfish for work that can be fully briefed: bounded research, drafting from a fixed set of sources, and narrow edits. Keep judgment that spans many files with the planner. The test is simple to state. Can the brief name the inputs, the output and the check in a paragraph? If it cannot, the task is not yet a goldfish task, because the worker will have to make decisions the planner has not made. The mechanism is that a decision made inside one worker is invisible to the others. Anthropic's research branches were largely independent, so their summaries could be combined without collision. Two workers editing the same module can each make a reasonable choice that the other contradicts. The failure here is misclassification. A task that looks narrow can touch a file another worker is changing, and the goldfish will produce a clean local edit that breaks the whole. I would require the planner to list the files each worker may touch, and to run no two workers in parallel on the same file. To know whether the boundary is right, I would compare redone edits from goldfish runs against a single thread on the same narrow tasks. If the goldfish runs need more redos, the boundary is in the wrong place.

The strongest case against all of this is Walden Yan's [Don't Build Multi-Agents (Cognition, 2025)](https://cognition.com/blog/dont-build-multi-agents). He argues for sharing context and full agent traces, not just individual messages, and he writes that "actions carry implicit decisions, and conflicting decisions carry bad results." I think he is right about coding, and it changes my argument in one place. A brief cannot carry the decisions a worker makes while it works. For coding, where nearly every edit is a decision, the planner has to keep more of the work or sequence it through one thread. Brief-first design is strongest for research and drafting, where the output is a summary that can be checked against the brief. It is weakest where the output is a set of edits that have to agree with each other.

My third proposal is to price the design before anyone builds it. The 15x figure is Anthropic's number for one research system against a chat interaction. It is not a multiplier to expect on every task. Each worker rereads its brief and its tool output, and the lead rereads every summary, so the cost grows with the number of workers and the size of what they return. Parallel workers also finish at about the same time, so wall-clock time can fall while the bill rises. The useful question is whether the parallelism earns that bill. I would put a token budget in each brief, and compare cost per accepted result against a single agent with the same tools on the same tasks. [Anthropic's guidance on building effective agents (2024)](https://www.anthropic.com/research/building-effective-agents) says that agentic systems often trade latency and cost for better task performance, and that trade is the one to measure. The failure case is a team that never runs the comparison and reports its agent costs only as a line item. Neither source gives a break-even point, so I won't invent one. A team's own cost per accepted result is the number that can settle it.

Where does this leave the planner? Its job is to write down what the worker cannot know, including the searches that came up empty and the decisions already made. What the planner did not write down, the worker cannot know, and I think that is a feature, because it is the one part of the system a person can read and fix. Start with the next failure. Open its brief and count the lines that say what was already ruled out. If the count is zero, the worker was not the problem.

```video
youtube: uhJJgc-0iTQ
title: Building more effective AI agents (Anthropic)
caption: Anthropic on simple, composable agent patterns, including when a single agent is enough.
```

## References

1. Anthropic (2024). Building effective agents. Anthropic blog. https://www.anthropic.com/research/building-effective-agents
2. Anthropic (2025). How we built our multi-agent research system. Anthropic engineering blog. https://www.anthropic.com/engineering/multi-agent-research-system
3. Anthropic (2025). Effective context engineering for AI agents. Anthropic engineering blog. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
4. Liu, N. F. et al. (2023). Lost in the Middle: How Language Models Use Long Contexts. arXiv. https://arxiv.org/abs/2307.03172
5. Anthropic (2025). Writing effective tools for AI agents (with agents). Anthropic engineering blog. https://anthropic.com/engineering/writing-tools-for-agents
6. Yan, W. (2025). Don't Build Multi-Agents. Cognition blog. https://cognition.com/blog/dont-build-multi-agents
