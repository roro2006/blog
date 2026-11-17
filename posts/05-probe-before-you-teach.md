---
title: Measure the edge before you teach or edit
summary: Tutors and coding agents should locate the edge of what the user knows before explaining or editing, since a guessed plan only looks efficient.
tags: agents, verification
kind: opinion
date: 2026-09-11
---

Most tutors and coding agents start helping the moment a request arrives, on the theory that a question is friction and a fast answer is respect. I think that theory has the cost backwards. The most under-built phase in both kinds of tool is measurement before action: spending real budget to find where the user's knowledge, or the codebase's actual behavior, stops matching the tool's model of it. A plan built on an unchecked starting point looks efficient for a few steps. Then the error surfaces somewhere the tool never looked, and gets blamed on the wrong thing.

Consider a tutor asked to explain eigenvectors. The quick answer opens with the idea that some directions survive a matrix unchanged, then works an example. That opening assumes the learner can multiply a matrix by a vector, can say what a direction means, and can keep a scalar multiple in view without losing the thread. If one of those is missing, nothing in the explanation reveals it, and the confusion appears three steps later, labelled as a problem with eigenvalues.

A probe is a question whose wrong answer is informative. Can the learner compute the product for a two by two matrix? What happens to the vector along the x axis under a shear? The questions ask for something specific because a fluent description of understanding is cheap to produce, while a wrong answer to a specific question is hard to fake. The probe is a search, and its stopping rule does the work. If every answer is right, the questions were too easy, so it escalates until something breaks. One miss is not enough to act on, so it asks around the miss. Is the gap a missing definition, or the rule that links two definitions? The output is an edge rather than a score. A score says the learner got seven of ten. An edge says the learner can multiply the matrix by the vector but cannot yet say what the result means for the direction. Teaching then starts one node below the goal instead of three.

```diagram
title: Climb until a miss, then probe around it
caption: Questions climb while answers are right; a miss at rung E starts a probe between D and E, which locates the edge at D.
<svg viewBox="0 0 640 280" xmlns="http://www.w3.org/2000/svg">
  <text x="40" y="28" class="sub">Six rungs, easiest at left</text>
  <g class="step1">
    <rect x="40" y="44" width="84" height="56" rx="6" class="box good"/><text x="82" y="68" text-anchor="middle" class="lbl">Rung A</text><text x="82" y="86" text-anchor="middle" class="sub">correct</text>
    <rect x="136" y="44" width="84" height="56" rx="6" class="box good"/><text x="178" y="68" text-anchor="middle" class="lbl">Rung B</text><text x="178" y="86" text-anchor="middle" class="sub">correct</text>
    <rect x="232" y="44" width="84" height="56" rx="6" class="box good"/><text x="274" y="68" text-anchor="middle" class="lbl">Rung C</text><text x="274" y="86" text-anchor="middle" class="sub">correct</text>
  </g>
  <g class="step2">
    <rect x="328" y="44" width="84" height="56" rx="6" class="box good"/><text x="370" y="68" text-anchor="middle" class="lbl">Rung D</text><text x="370" y="86" text-anchor="middle" class="sub">correct</text>
    <rect x="424" y="44" width="84" height="56" rx="6" class="box bad"/><text x="466" y="68" text-anchor="middle" class="lbl">Rung E</text><text x="466" y="86" text-anchor="middle" class="sub">wrong</text>
  </g>
  <rect x="520" y="44" width="84" height="56" rx="6" class="box"/><text x="562" y="68" text-anchor="middle" class="lbl">Rung F</text><text x="562" y="86" text-anchor="middle" class="sub">not asked</text>
  <g class="step3">
    <path d="M370 102 V140" class="edge" marker-end="url(#arr)"/>
    <path d="M466 102 V140" class="edge" marker-end="url(#arr)"/>
    <rect x="270" y="140" width="300" height="44" rx="6" class="box hi"/>
    <text x="420" y="160" text-anchor="middle" class="lbl">Probe around the miss</text>
    <text x="420" y="176" text-anchor="middle" class="sub">missing definition or missing link?</text>
  </g>
  <g class="step4">
    <path d="M420 184 V208" class="edge" marker-end="url(#arr)"/>
    <rect x="240" y="208" width="360" height="56" rx="6" class="box hi"/>
    <text x="420" y="232" text-anchor="middle" class="lbl">Edge found at rung D</text>
    <text x="420" y="250" text-anchor="middle" class="sub">teach from here, not the middle</text>
  </g>
</svg>
```

The tutor I would want to see built has three parts. It probes until the edge is located. It then shows the learner a short dependency plan, the chain of ideas between the learner's edge and the goal, before teaching begins. Finally it teaches one step at a time with a quiz after each step, so the plan changes on evidence instead of hope. The middle part matters most to me. A learner who has seen and agreed to the chain can dispute a link, and a disputed link tells the tutor something it did not know. A chain the learner never saw can only be trusted or ignored, and neither outcome helps much. The lineage here is old. [Bloom, 1984](https://www.gwern.net/doc/psychology/1984-bloom.pdf) asked whether group instruction could match one-to-one tutoring, and that question presupposes a tutor who knows the person in front of them. [Corbett and Anderson, 1994](https://link.springer.com/doi/10.1007/BF01099821) turned the presupposition into a model in which each answer updates an estimate of the learner's mastery, and the next item comes from that estimate. [Roediger and Karpicke, 2006](https://psychology.ecu.edu/wp-content/pv-uploads/sites/216/2019/03/Roediger-Karpicke-2006.pdf) add a reason the probe does some teaching of its own, since pulling material back out of memory is a form of practice. I think the design gap sits in the plan step, which almost no tutor shows the learner.

The obvious way this fails is for the probe to become a quiz show. A tutor that asks forty questions before saying a word has moved the cost onto the learner, who leaves. I would test the tutor on how few questions it needs to locate the edge, and on whether learners who start from the located edge do better on a delayed check than learners who start from a comfortable middle. If the edge is found in three or four questions and the delayed check improves, I would believe the design. Until then it is a sensible guess.

The coding agent case is where I expect the change to pay off soonest. Suppose an agent is asked why a parser rejects a valid input. The common path is to find an expression that looks too strict, loosen it, and watch the test go green. That is an edit made before any probe. A green test is evidence only about the cases somebody chose to include, and a loosened expression is cheap to write and expensive to undo once other code depends on it. I would make the first deliverable a failing reproduction. Run the input alone, shorten it until the smallest failing case remains, and name the assumption about encoding or whitespace that the parser is making. Only then edit. The rule I would add is that "could not reproduce" counts as a result. The agent reports the inputs it tried and what they showed, and it does not route around the gap by editing.

```diagram
title: Reproduce before editing
caption: The agent edits only after a failing input is reproduced; if the bug will not reproduce, the agent reports what it tried and stops.
<svg viewBox="0 0 640 230" xmlns="http://www.w3.org/2000/svg">
  <rect x="15" y="60" width="130" height="52" rx="6" class="box"/><text x="80" y="82" text-anchor="middle" class="lbl">Reproduce</text><text x="80" y="100" text-anchor="middle" class="sub">smallest input</text>
  <rect x="175" y="60" width="130" height="52" rx="6" class="box"/><text x="240" y="82" text-anchor="middle" class="lbl">Locate</text><text x="240" y="100" text-anchor="middle" class="sub">name assumption</text>
  <rect x="335" y="60" width="130" height="52" rx="6" class="box"/><text x="400" y="82" text-anchor="middle" class="lbl">Fix</text><text x="400" y="100" text-anchor="middle" class="sub">edit after repro</text>
  <rect x="495" y="60" width="130" height="52" rx="6" class="box good"/><text x="560" y="82" text-anchor="middle" class="lbl">Rerun repro</text><text x="560" y="100" text-anchor="middle" class="sub">input now passes</text>
  <path d="M145 86 H175" class="edge" marker-end="url(#arr)"/>
  <path d="M305 86 H335" class="edge" marker-end="url(#arr)"/>
  <path d="M465 86 H495" class="edge" marker-end="url(#arr)"/>
  <path d="M80 112 V150" class="edge bad" marker-end="url(#arr)"/>
  <text x="90" y="138" class="sub">not reproduced</text>
  <rect x="15" y="150" width="260" height="52" rx="6" class="box hi"/><text x="145" y="172" text-anchor="middle" class="lbl">Could not reproduce: report</text><text x="145" y="190" text-anchor="middle" class="sub">list inputs tried, no edit</text>
</svg>
```

Budget is the second reason. [Anthropic, 2025](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) describes context rot, the decline in recall as a context window fills, and recommends keeping context to the smallest set of high-signal tokens that does the job. An agent that reads a whole repository before it knows what it is looking for pays that cost on every turn. A probe decides what to load. [Liu et al., 2023](https://arxiv.org/abs/2307.03172) adds that performance can degrade significantly when relevant information moves, and is often highest when it sits at the beginning or end of a long input. An agent that wanders a large codebase may be reading the relevant file in the middle, where the paper's results suggest models use it less reliably.

The third idea is a setting. I would expose a probe budget, a fraction of the tokens an agent may spend reading and testing before its first edit, and let people tune it per task. A rename in a small module should run with almost no probe. A change to a shared parser should run with a large one. Making the budget a number instead of a habit matters because a number can be audited. If a change ships a regression after a thin probe, the budget explains it. If it ships one after a thorough probe, the team learns that the probe asked the wrong questions, which is the more useful finding and points at the probe rather than the model.

The fourth reason is about the human. The [METR, 2025](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) study found that experienced open-source developers expected AI tools to speed them up by 24 percent. Measured, they took 19 percent longer. After the study they still believed the tools had sped them up by 20 percent. The [METR, 2026](https://metr.org/blog/2026-02-24-uplift-update/) follow-up changed the experiment design and gives the 2025 result a confidence interval from +2 to +39 percent, so the number is a snapshot, not a law. The lesson I take is narrower. A person's sense of their own state is a weak instrument. An assistant that never probes the developer is guessing about that state, and the developer's own report is not reliable enough to settle the guess. A question with a right answer will tell the tool more than a question about confidence.

The objection survives in part, and I think it should change the design. A probe that asks everything is a failure of its own. Anthropic's 2024 guidance is to find the simplest solution possible and add complexity only when it is needed, and that advice applies to probes as much as to architectures. A tutor that quizzes a student through the alphabet before one sentence wastes the session. For an agent the cost is tokens, since each round of questions stays in context for the next step. So the common view is right for small, reversible tasks, where starting immediately is cheap and a wrong start is easy to undo. It is wrong for changes that are expensive to reverse. The probe budget should scale with the price of being wrong, not sit at one default for everything.

The probe buys a plan that can be checked. An approved chain with a marked edge is something the learner can dispute. A reproduced failure with a minimal input is something the agent's eventual change can be measured against. I would take either over a quick answer nobody can check. The picture I keep returning to is a tutor that puts the chain on screen and says the learner can multiply the matrix but cannot yet say what it does to a direction, and a coding agent that reports, before any edit, the three inputs on which the bug did not reproduce. Both stop early, and both show exactly where the work should start.

```video
youtube: hJP5GqnTrNo
title: How AI Could Save (Not Destroy) Education, Sal Khan (TED)
caption: The case for AI tutors that question the student before explaining, which is the probe-first habit argued for here.
```

## References

1. Anthropic (2025). Effective context engineering for AI agents. Anthropic Engineering. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
2. Anthropic (2024). Building effective agents. Anthropic. https://www.anthropic.com/research/building-effective-agents
3. Bloom, B. S. (1984). The 2 Sigma Problem: The Search for Methods of Group Instruction as Effective as One-to-One Tutoring. Educational Researcher, 13(6), 4-16. https://www.gwern.net/doc/psychology/1984-bloom.pdf
4. Corbett, A. T. and Anderson, J. R. (1994). Knowledge tracing: Modeling the acquisition of procedural knowledge. User Modeling and User-Adapted Interaction, 4(4), 253-278. https://link.springer.com/doi/10.1007/BF01099821
5. Liu, N. F. et al. (2023). Lost in the Middle: How Language Models Use Long Contexts. arXiv. https://arxiv.org/abs/2307.03172
6. METR (2025). Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity. METR blog. https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/
7. METR (2026). We are Changing our Developer Productivity Experiment Design. METR blog. https://metr.org/blog/2026-02-24-uplift-update/
8. Roediger, H. L. and Karpicke, J. D. (2006). Test-Enhanced Learning: Taking Memory Tests Improves Long-Term Retention. Psychological Science, 17(3), 249-255. https://psychology.ecu.edu/wp-content/pv-uploads/sites/216/2019/03/Roediger-Karpicke-2006.pdf
