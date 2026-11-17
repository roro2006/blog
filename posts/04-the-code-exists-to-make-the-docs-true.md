---
title: Treat the spec as the artifact and the code as its cache
summary: A spec earns trust only when its status column records which claims the code has satisfied, and specs deserve the same review as code.
tags: workflow, agents
kind: opinion
---

The common view is that docs drift and the code is the truth. Anyone who has opened a README describing a feature removed two releases ago knows the failure, and I would not argue with the complaint. I think the conclusion is wrong for teams that now have agents writing most of their code. When generation is cheap, the thing a regenerated implementation gets checked against is the durable artifact. The code becomes something closer to a cache that can be rebuilt. The spec is what deserves versioning, review and tests, with the rigor we once reserved for code.

The idea predates agents by a long way, and each step in its history adds one constraint. [Preston-Werner, 2010](https://tom.preston-werner.com/2010/08/23/readme-driven-development.html) argued that the README should be written first, because until you have written about the software you cannot know what you are going to code. [Bryar and Carr, 2021](https://www.aboutamazon.com/news/workplace/an-insider-look-at-amazons-culture-and-processes) describe Amazon's working-backwards process, which asks for a short press release and a bounded FAQ before anything is built. [GitHub, 2025](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/) launched Spec Kit that year and moved the field's slogan from code as the source of truth to intent as the source of truth. Preston-Werner fixes the order, Amazon fixes the length, and the Spec Kit launch fixes what counts as authoritative. I underrate the length cap most. A document that cannot be read in one sitting is rarely checked against the code afterward.

The first proposal is a rule for the status table. Every claim in a spec either links to a test that exercises it, or appears in the table marked stubbed or untested, and CI fails when a claim has neither. The table never says the product works. It says which sentences are true today, which is a smaller claim and a more useful one. Working means the module has run end to end on the target it was built for. Stubbed means the interface exists and returns placeholder results. Untested means the code is written and may be correct, but nothing has exercised it.

```diagram
title: Claims table and CI gate
caption: Each claim either links to a test or carries a status, and the gate fails the row that has neither.
<svg viewBox="0 0 640 240" xmlns="http://www.w3.org/2000/svg">
  <text x="16" y="32" class="sub">Claim</text>
  <text x="196" y="32" class="sub">Evidence</text>
  <text x="352" y="32" class="sub">Status</text>
  <rect x="16" y="40" width="168" height="36" rx="6" class="box"/>
  <text x="100" y="62" text-anchor="middle" class="sub">Refund date shown</text>
  <rect x="196" y="40" width="140" height="36" rx="6" class="box"/>
  <text x="266" y="62" text-anchor="middle" class="sub">fixture test</text>
  <rect x="352" y="40" width="96" height="36" rx="6" class="box hi"/>
  <text x="400" y="62" text-anchor="middle" class="lbl">stubbed</text>
  <path d="M448 58 H476" class="edge" marker-end="url(#arr)"/>
  <rect x="16" y="88" width="168" height="36" rx="6" class="box"/>
  <text x="100" y="110" text-anchor="middle" class="sub">Retries hit gateway</text>
  <rect x="196" y="88" width="140" height="36" rx="6" class="box"/>
  <text x="266" y="110" text-anchor="middle" class="sub">none</text>
  <rect x="352" y="88" width="96" height="36" rx="6" class="box bad"/>
  <text x="400" y="110" text-anchor="middle" class="lbl">untested</text>
  <path d="M448 106 H476" class="edge" marker-end="url(#arr)"/>
  <rect x="16" y="136" width="168" height="36" rx="6" class="box"/>
  <text x="100" y="158" text-anchor="middle" class="sub">Brief reaches worker</text>
  <rect x="196" y="136" width="140" height="36" rx="6" class="box"/>
  <text x="266" y="158" text-anchor="middle" class="sub">CI run link</text>
  <rect x="352" y="136" width="96" height="36" rx="6" class="box good"/>
  <text x="400" y="158" text-anchor="middle" class="lbl">working</text>
  <path d="M448 154 H476" class="edge" marker-end="url(#arr)"/>
  <rect x="16" y="184" width="168" height="36" rx="6" class="box"/>
  <text x="100" y="206" text-anchor="middle" class="sub">Tracking page is live</text>
  <rect x="196" y="184" width="140" height="36" rx="6" class="box bad"/>
  <text x="266" y="206" text-anchor="middle" class="sub">none</text>
  <rect x="352" y="184" width="96" height="36" rx="6" class="box bad"/>
  <text x="400" y="206" text-anchor="middle" class="lbl">missing</text>
  <path d="M448 202 H476" class="edge bad" marker-end="url(#arr)"/>
  <rect x="476" y="40" width="148" height="180" rx="6" class="box hi"/>
  <text x="550" y="70" text-anchor="middle" class="lbl">CI gate</text>
  <text x="550" y="96" text-anchor="middle" class="sub">fails any row with</text>
  <text x="550" y="112" text-anchor="middle" class="sub">neither evidence</text>
  <text x="550" y="128" text-anchor="middle" class="sub">nor a status</text>
  <rect x="488" y="158" width="124" height="40" rx="6" class="box bad"/>
  <text x="550" y="183" text-anchor="middle" class="lbl">build fails</text>
</svg>
```

The untested row carries most of the value. Suppose a payment retry path is marked untested because it was written against a mock gateway and has never run against the real one. A planner reading that cell knows the launch carries an integration risk. A coding agent asked to extend the retry logic reads the same cell and learns that finishing it means a run against the real gateway. If the row said only that retries exist, a reader would assume the path had run end to end, and the first real failure would be a surprise instead of a checkpoint. Working and working against a mock are two different claims, and a good table keeps both in the same column so a reader cannot mistake one for the other.

The second proposal is a press release and a FAQ before handing work to an agent. The press release is the acceptance test. If it describes a customer-visible behavior, the agent is finished when that behavior holds, and a reviewer can check the sentence against a run. The FAQ holds the edge cases the release has to survive. Take a hypothetical feature that shows a customer when a returned parcel will be refunded. The release says the refund date appears as soon as the carrier scans the parcel. The FAQ is where that sentence gets checked. Which service computes the date? Has it run on real returns, or only on fixtures? What happens when the scan never arrives? With a status column attached, the sentence becomes stubbed if the calculation exists but returns a fixed value, and untested if nothing has yet run against live returns. The example shows the form and says nothing about any real document. I think the length caps matter for the same reason the status column does. A document short enough to reread is one whose marks get updated.

```diagram
title: Forward build, backward trace
caption: Work starts from the PR/FAQ, the agent builds to it, and each test that runs points back to the claim it checks.
<svg viewBox="0 0 640 190" xmlns="http://www.w3.org/2000/svg">
  <g class="step1">
    <rect x="16" y="50" width="120" height="60" rx="6" class="box hi"/>
    <text x="76" y="76" text-anchor="middle" class="lbl">PR/FAQ</text>
    <text x="76" y="96" text-anchor="middle" class="sub">claims, status</text>
    <path d="M136 80 H176" class="edge" marker-end="url(#arr)"/>
  </g>
  <g class="step2">
    <rect x="176" y="50" width="120" height="60" rx="6" class="box"/>
    <text x="236" y="76" text-anchor="middle" class="lbl">Agent</text>
    <text x="236" y="96" text-anchor="middle" class="sub">builds to spec</text>
    <path d="M296 80 H336" class="edge" marker-end="url(#arr)"/>
  </g>
  <g class="step3">
    <rect x="336" y="50" width="120" height="60" rx="6" class="box"/>
    <text x="396" y="76" text-anchor="middle" class="lbl">Code</text>
    <text x="396" y="96" text-anchor="middle" class="sub">regenerable</text>
    <path d="M456 80 H496" class="edge" marker-end="url(#arr)"/>
  </g>
  <g class="step4">
    <rect x="496" y="50" width="120" height="60" rx="6" class="box good"/>
    <text x="556" y="76" text-anchor="middle" class="lbl">Tests</text>
    <text x="556" y="96" text-anchor="middle" class="sub">run per claim</text>
    <path d="M556 110 V150 H76 V110" class="edge flow" marker-end="url(#arr)"/>
    <text x="316" y="168" text-anchor="middle" class="sub">each test names the claim it checks</text>
  </g>
</svg>
```

The third proposal is an order of review. Put the spec diff ahead of the code diff in the pull request, and let the reviewer agree on what the change promises before reading how it was built. Code review tends to anchor on whatever the code already does, and an agent in a repository with no stated target infers one from the code it finds. That inference is a bad default when existing behavior is itself a bug. [Anthropic, 2025](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) describes context rot, where recall declines as the window fills, and argues for the smallest set of high-signal tokens that still carries what matters. A spec diff is dense in that sense. [Liu et al., 2023](https://arxiv.org/abs/2307.03172) found that performance can degrade significantly when the position of relevant information changes, and that it is often highest at the start or end of the input. I do not know whether the status table belongs at the top for that reason alone. My guess is that a product description first and a table second suits a model reading top down, and I would test that guess before building a process around it.

The order has a cost. A reviewer who reads the promise first can approve a claim the code cannot keep, and then the code review feels like a formality. That is why the spec diff should carry its status column beside the prose, not just the prose alone.

The fourth proposal is a guard against Goodhart's law. [Goodhart, 1975](https://econbiz.de/Record/problems-of-monetary-management-the-u-k-experience-goodhart-charles/10002525062) observed, in a monetary setting, that a statistical regularity tends to stop being reliable once it is used as a control. A status column is one. When Working is the word everyone wants to see, a green test in simulation starts standing in for the hardware run, and the column drifts toward the answer people hope for. Agents make this worse, because an agent asked to fill a table will make each cell true in the cheapest way available. So each cell should hold an evidence link, not a checkmark. A link to a hardware log with a date and a commit is hard to fake without doing the work. A checkmark is one edit. [Cognition, 2025](https://cognition.com/blog/dont-build-multi-agents) argues that agents should share context and full traces, and the same applies here. A spec that each agent meets only as a digest can drift between them, and then the docs become one more silo.

The objection that deserves the most weight is cost. [Anthropic, 2024](https://www.anthropic.com/research/building-effective-agents) recommends finding the simplest solution possible. For two people and one module, a spec-first process can be overhead that does nothing for the next run. Keeping the table honest takes time that the code never rewards, and the status column is usually the first thing to fall behind when a week goes to plumbing. I would accept that price for a document that has to stay true. For work small enough to hold in one head, I would drop the process.

Docs-first is a claim about sentences more than about order. Any sentence without a matching row counts as unverified, including the ones I like best. Write the target down, because agents can only hit what is written. The row I would change first is the one for the hardware run. When it changes, the change should be a single status word that lands in the same commit as the measurement behind it. A reader who finds the cell still saying untested should not trust the rest of that module. A reader who finds it changed should check the measurement before believing the word. Until someone changes a row, the spec is a guess, and a guess that says so is worth keeping.

## References

1. Bryar, C. and Carr, B. (2021). Working Backwards: PR/FAQ process (excerpt). Amazon News. https://www.aboutamazon.com/news/workplace/an-insider-look-at-amazons-culture-and-processes
2. Anthropic (2025). Effective context engineering for AI agents. Anthropic Engineering. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
3. Cognition (2025). Don't Build Multi-Agents. Cognition blog. https://cognition.com/blog/dont-build-multi-agents
4. Anthropic (2024). Building effective agents. Anthropic. https://www.anthropic.com/research/building-effective-agents
5. GitHub (2025). Spec-driven development with AI: Get started with a new open source toolkit. GitHub Blog. https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/
6. Goodhart, C. A. E. (1975). Problems of Monetary Management: The U.K. Experience. Papers in Monetary Economics, Reserve Bank of Australia. https://econbiz.de/Record/problems-of-monetary-management-the-u-k-experience-goodhart-charles/10002525062
7. Liu, N. F. et al. (2023). Lost in the Middle: How Language Models Use Long Contexts. arXiv. https://arxiv.org/abs/2307.03172
8. Preston-Werner, T. (2010). Readme Driven Development. Blog. https://tom.preston-werner.com/2010/08/23/readme-driven-development.html
