---
title: Build the benchmark you will be judged by
summary: Public agent leaderboards saturate quickly, so teams should own private task suites and measure real uplift instead.
tags: agents, verification
kind: opinion
date: 2026-11-02
---

The standard advice is to pick the model at the top of SWE-bench. I think that advice is wrong for most teams, and wrong in a predictable way. A public leaderboard measures someone else's tasks, run through someone else's harness, and its usefulness expires once the tasks stop separating models. A team should own the measure instead: a private suite built from its own work, refreshed often, and read beside a small study of what the tools do to its own speed.

In 2023, [Jimenez et al. (2024)](https://arxiv.org/abs/2310.06770) released SWE-bench: 2,294 software engineering problems drawn from real GitHub issues in 12 popular Python repositories. The best model in the paper, Claude 2, resolved 1.96% of them. Each task has a test that decides pass or fail, and the score is the share that pass. While the tasks are hard, that score separates models. Once models pass most of them, the remaining failures are often broken tests or ambiguous issues, and the score starts measuring the benchmark's defects. The [SWE-bench project page](https://swebench.com/verified.html) describes the usual repair, a human-validated subset of 500 instances.

The headline numbers show the drift. [Anthropic (2025)](https://www.anthropic.com/news/claude-3-7-sonnet) reported 70.3% for Claude 3.7 Sonnet with a high-compute scaffold and 63.7% without one, on a 489-task subset rather than the full 500. The scaffold is worth 6.6 points (derived: 70.3 minus 63.7), which says as much about the harness as about the model. A leaderboard row names the model, but the score belongs to the model, the scaffold, the subset and the compute budget together.

The budget matters more than most write-ups admit. [Brown et al. (2024)](https://arxiv.org/abs/2407.21787) raised SWE-bench Lite from 15.9% with one sample to 56% with 250. Repeated sampling is a legitimate method, but a score that moves that far with the budget partly reports how many tries were paid for. A model that needs 250 attempts is a different product from one that succeeds on the first, even when a table puts them on the same row.

A different measure changes the unit. [Kwa et al. (2025)](https://arxiv.org/abs/2503.14499) ask how long a task a model can finish about half the time. They report that frontier time horizons have doubled about every seven months since 2019, and that Claude 3.7 Sonnet has a 50% time horizon of around 50 minutes. Seven months per doubling is roughly 3.3 times a year (derived: 2 to the power of 12/7). I find this more useful than a pass rate, because it asks how big a job an agent can take off a developer's hands. It is still a fit to a trend, and a smooth line over a few years can bend.

The measure I care about most asks whether developers get faster. [METR (2025)](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) studied 16 experienced developers on 246 completed issues in large open-source repositories. With AI tools, the work took 19% longer. The developers had expected a 24% speedup, and afterward still believed AI had sped them up by 20%.

```chart
title: Expected versus measured speedup, METR 2025 study
unit: %
source: METR, 2025
Forecast before the study: 24
Developers' belief after: 20
Measured effect: -19
note: Positive means faster. Developers expected and afterwards believed AI made them faster; measured task time was 19% longer.
```

[METR's 2026 update](https://metr.org/blog/2026-02-24-uplift-update/) says the 2025 interval ran from 2% to 39% longer. Its later data, from 57 developers across 143 repositories and more than 800 tasks, estimates a speedup of minus 18%, with an interval from 38% slower to 9% faster. That interval includes zero, so even the direction is open. The 2025 figure was a snapshot of a moving target, and no leaderboard score would have predicted it.

The first thing I would build is a private suite harvested from the team's own resolved issues. Those tasks carry the team's repositories, review standards and the mistakes its agents actually make, and a public set cannot. Add new issues every month, and the suite stays ahead of memorization, since each refresh contains tasks that postdate the models in use. The failure I expect is selection: teams tend to harvest tasks they already solve, which flatters the status quo. A few dozen tasks is also noisy, so two models a few points apart look identical. A second failure is more serious. If the agent can read the suite, it can game it. Krakovna et al. (2020) had collected around 60 examples of specification gaming by 2020, and METR found that o3 reward-hacked in every trajectory it generated on one RE-Bench task. The suite's test files should sit out of the agent's reach. What would convince me is a holdout check: keep the latest quarter's issues out, rank the candidate tools on the rest, and see whether that ranking predicts which patches a maintainer accepted on the held-out set.

```diagram
title: Private suite pipeline, rebuilt monthly
caption: Resolved issues become held-out tasks with hidden tests, and the public leaderboard sits beside the pipeline as a sanity check.
<svg viewBox="0 0 640 250" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="28" class="sub">Private suite, rebuilt every month</text>
  <rect x="20" y="44" width="130" height="60" rx="6" class="box"/>
  <text x="85" y="70" text-anchor="middle" class="lbl">Resolved issues</text>
  <text x="85" y="88" text-anchor="middle" class="sub">from our own repo</text>
  <path d="M152 74 H174" class="edge" marker-end="url(#arr)"/>
  <rect x="176" y="44" width="130" height="60" rx="6" class="box"/>
  <text x="241" y="70" text-anchor="middle" class="lbl">Strip the fix</text>
  <text x="241" y="88" text-anchor="middle" class="sub">bug report kept</text>
  <path d="M308 74 H330" class="edge" marker-end="url(#arr)"/>
  <rect x="332" y="44" width="130" height="60" rx="6" class="box"/>
  <text x="397" y="70" text-anchor="middle" class="lbl">Task and tests</text>
  <text x="397" y="88" text-anchor="middle" class="sub">tests hidden</text>
  <path d="M464 74 H486" class="edge" marker-end="url(#arr)"/>
  <rect x="488" y="44" width="130" height="60" rx="6" class="box hi"/>
  <text x="553" y="70" text-anchor="middle" class="lbl">Held-out check</text>
  <text x="553" y="88" text-anchor="middle" class="sub">newest issues out</text>
  <path d="M553 104 V140 H85 V105" class="edge" marker-end="url(#arr)"/>
  <text x="319" y="158" text-anchor="middle" class="sub">each refresh adds the month's new issues</text>
  <rect x="20" y="190" width="250" height="44" rx="6" class="box dim"/>
  <text x="145" y="217" text-anchor="middle" class="lbl">Public leaderboard</text>
  <text x="290" y="217" class="sub">kept as a sanity check, not a buying guide</text>
</svg>
```

I would also report a time horizon on the team's own tasks, following Kwa et al. Estimate how long each task would take a competent developer, plot success against that length, and read off the length where the agent succeeds half the time. The mechanism is planning. A team can ask whether an agent can take an afternoon's ticket unsupervised, and a pass rate cannot answer that. Two models with similar pass rates can have very different horizons, and the horizon decides which tickets to hand over. The weak point is the estimate. Human guesses at task length are noisy, and a curve fitted to a handful of long tasks can mislead. I would report the sample budget beside every horizon, as Brown et al. do, because a horizon reached with 250 attempts is not the one reached with one. The result that would convince me is a crossing: if two models' curves cross inside the team's data, the ranking depends on task length, and a single pass rate hides exactly that.

Before adopting a tool, a team should run a small randomized comparison on its own work. Assign issues at random to tool or no tool, and measure the time from issue to a patch a maintainer would accept, counting review and rework. METR measured task time directly, and the gap between developers' beliefs and the clock is the reason to do it. Teams that rely on impressions will overrate the tool, and I'd expect developers who feel faster to keep using it anyway. The obvious failures are sample size, since a team of eight produces few issues per arm, and contamination, since developers learn the tool across the study and reviewers may recognize which patches used it. I would blind reviewers where I can. What would convince me is a pre-registered comparison whose interval excludes zero. I'd want the interval, not the point estimate, because the METR figures show how far a point estimate can move.

```diagram
title: Randomized comparison on our own issues
caption: Issues go to the tool or to no tool at random, the clock runs to an accepted patch, and a self-report is not evidence.
<svg viewBox="0 0 640 260" xmlns="http://www.w3.org/2000/svg">
  <g class="step1">
    <rect x="20" y="92" width="140" height="52" rx="6" class="box"/>
    <text x="90" y="115" text-anchor="middle" class="lbl">Issue pool</text>
    <text x="90" y="132" text-anchor="middle" class="sub">comparable issues</text>
    <path d="M162 118 H196" class="edge flow" marker-end="url(#arr)"/>
  </g>
  <g class="step2">
    <rect x="200" y="92" width="150" height="52" rx="6" class="box hi"/>
    <text x="275" y="115" text-anchor="middle" class="lbl">Random assignment</text>
    <text x="275" y="132" text-anchor="middle" class="sub">coin flip per issue</text>
    <path d="M350 110 H375 V66 H396" class="edge" marker-end="url(#arr)"/>
    <path d="M350 130 H375 V174 H396" class="edge" marker-end="url(#arr)"/>
  </g>
  <g class="step3">
    <rect x="400" y="40" width="220" height="52" rx="6" class="box"/>
    <text x="510" y="63" text-anchor="middle" class="lbl">With the AI tool</text>
    <text x="510" y="80" text-anchor="middle" class="sub">clock to accepted patch</text>
    <rect x="400" y="148" width="220" height="52" rx="6" class="box"/>
    <text x="510" y="171" text-anchor="middle" class="lbl">Without the tool</text>
    <text x="510" y="188" text-anchor="middle" class="sub">clock to accepted patch</text>
  </g>
  <g class="step4">
    <path d="M510 200 V218" class="edge" marker-end="url(#arr)"/>
    <rect x="240" y="218" width="380" height="36" rx="6" class="box hi"/>
    <text x="430" y="241" text-anchor="middle" class="lbl">Compare the interval, not the average</text>
  </g>
  <rect x="20" y="218" width="200" height="36" rx="6" class="box dim"/>
  <text x="120" y="235" text-anchor="middle" class="lbl">Self-report: felt faster</text>
  <text x="120" y="249" text-anchor="middle" class="sub">not evidence</text>
</svg>
```

The common view is right about something. Public benchmarks are cheap, shared, and the only yardstick that lets outsiders check a claim. A private suite can flatter a team's habits and becomes easy to tune to, which is the same failure any metric shows once it becomes a target. So I would keep one public benchmark as an anchor and read it as a sanity check, not as a basis for buying. When a private suite and the public number disagree sharply, the private suite is the first suspect, though sometimes the public one has simply gone stale. That concession changes the proposal. The private suite needs its own audit, which is why the holdout matters more than the suite's size.

My table for a team wiki would have two columns. The public figure sits on the left, printed with its scaffold, subset and sample budget. The team's own figures sit on the right: held-out pass rate, time horizon, and minutes from issue to accepted patch. The gap between the columns is what to read. The 1.96% from 2023 is a reminder of how quickly the left column moves. A benchmark you do not own measures someone else's work.

```video
youtube: 9QSm_mRGpN8
title: Measuring Exponential Trends Rising (in AI), Joel Becker of METR (Latent Space)
caption: METR on time horizons and measuring real uplift, the two measurements I would adopt for a private suite.
```

## References

1. Jimenez et al. (2024). SWE-bench: Can Language Models Resolve Real-World GitHub Issues? ICLR 2024. https://arxiv.org/abs/2310.06770
2. SWE-bench team. SWE-bench Verified (project page). swebench.com. https://swebench.com/verified.html
3. Anthropic (2025). Claude 3.7 Sonnet and Claude Code. Anthropic news. https://www.anthropic.com/news/claude-3-7-sonnet
4. Brown et al. (2024). Large Language Monkeys: Scaling Inference Compute with Repeated Sampling. arXiv. https://arxiv.org/abs/2407.21787
5. Kwa et al. (2025). Measuring AI Ability to Complete Long Software Tasks. arXiv. https://arxiv.org/abs/2503.14499
6. METR (2025). Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity. METR blog. https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/
7. METR (2026). We are Changing our Developer Productivity Experiment Design (uplift update). METR blog. https://metr.org/blog/2026-02-24-uplift-update/
8. Krakovna et al. (2020). Specification gaming: the flip side of AI ingenuity. DeepMind blog. https://deepmind.google/blog/specification-gaming-the-flip-side-of-ai-ingenuity/
9. METR (2025). Recent Frontier Models Are Reward Hacking. METR blog. https://metr.org/blog/2025-06-05-recent-reward-hacking/
