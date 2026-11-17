---
title: Retries are a bet against your checker
summary: The number that decides a product is how often the checker approves a wrong answer after k tries, and escalation should be a budgeted resource.
tags: verification, agents, inference
kind: opinion
date: 2026-08-26
---

The common view is that a generate-and-filter loop gets better as it samples more. Draw ten candidates, keep the one that passes, and the solve rate climbs. I think that is right about coverage and wrong about trust. What a product ships is the set of answers the checker approved, and that set grows with every retry, including the wrong answers the checker let through. The number I would track is the rate at which the verifier approves a wrong answer after k tries. Everything else in the design should follow from that rate.

Repeated sampling has a recent literature, and the good news in it is real. [Brown et al., 2024](https://arxiv.org/abs/2407.21787) measured coverage, the share of problems that at least one of many samples solves. Coverage grew with the number of samples over four orders of magnitude, and on SWE-bench Lite it rose from 15.9 percent with one sample to 56 percent with 250. The older form of the idea is pass@k from the Codex paper, where [Chen et al., 2021](https://arxiv.org/abs/2107.03374) reported 28.8 percent of HumanEval problems solved with one sample and 70.2 percent with 100 samples per problem.

Both numbers share a blind spot. Coverage is measured against reference answers, and a production pipeline has none. A coverage of 56 percent means a correct attempt exists somewhere among 250. It says nothing about whether the pipeline picks that attempt, or whether it picks a wrong one that a weak check accepted. Pass@k assumes the judge is right, and each added sample gives an imperfect judge one more chance to be wrong.

The arithmetic makes this concrete, using a checker I have invented for the purpose. Suppose it wrongly passes one bad candidate in a hundred, and that failures are independent from one candidate to the next. Across 10 candidates, the chance that at least one bad candidate gets through is about 10 percent. Across 100 it is about 63 percent. The retry budget is therefore also a budget for false approvals, and the checker's error rate decides how many retries are safe. By the same arithmetic, a checker that passes one in a thousand can afford roughly ten times as many candidates for the same risk. A checker that passes one in ten should not retry at all, because two candidates already give it a 19 percent chance of a false approval.

```chart
title: Chance a bad candidate slips through, 1-in-100 checker
unit: %
source: Derived: 1 - 0.99^n, for the hypothetical checker above
note: Assumes independent failures. Not a measurement of the real pipeline.
1 candidate: 1
10 candidates: 9.6
50 candidates: 39.5
100 candidates: 63.4
```

The clearest public case I know is a coding agent that samples patches for a GitHub issue and keeps the ones that pass the repository's tests. [Jimenez et al., 2023](https://arxiv.org/abs/2310.06770) built SWE-bench from 2,294 problems drawn from real GitHub issues across 12 Python repositories, and the benchmark scores a patch by running its tests. Take that loop into production and the tests become the checker, which makes the checker's failure modes the first thing to design.

A patch that crashes the test runner, times out, or fails to apply has to be recorded as a failure, since a missing answer would hide it. A broken harness then can only shrink the set of accepted patches. If errors were read as passes, the harness would approve most often on the hard cases, which are the cases most likely to break it.

The first proposal is to set the retry budget from the checker's measured false-pass rate. Most retry limits I have seen are a number chosen for cost, perhaps five attempts because five felt reasonable. I would derive the budget from the arithmetic above, so a team can say which risk it accepts and what that risk costs. The consequence is that a weaker checker earns fewer retries, and a stronger one can earn more. That sounds backwards to anyone who thinks of retries as a way to rescue a weak filter, and it is the reason the rule matters. A retry on a weak checker mostly buys more false approvals.

```diagram
title: Generate, check, retry, then escalate
caption: The loop approves a candidate that passes, retries a failure up to a fixed limit, and then hands the closest candidate to a person.
<svg viewBox="0 0 640 240" xmlns="http://www.w3.org/2000/svg">
  <g class="step1">
    <rect x="16" y="30" width="150" height="70" rx="6" class="box"/>
    <text x="91" y="58" text-anchor="middle" class="lbl">Generate</text>
    <text x="91" y="78" text-anchor="middle" class="sub">one candidate</text>
    <path d="M166 65 H226" class="edge" marker-end="url(#arr)"/>
  </g>
  <g class="step2">
    <rect x="226" y="30" width="150" height="70" rx="6" class="box hi"/>
    <text x="301" y="58" text-anchor="middle" class="lbl">Checker</text>
    <text x="301" y="78" text-anchor="middle" class="sub">tests or judge</text>
    <path d="M376 65 H436" class="edge good" marker-end="url(#arr)"/>
    <text x="406" y="56" text-anchor="middle" class="sub">pass</text>
    <path d="M301 100 V150" class="edge bad" marker-end="url(#arr)"/>
    <text x="311" y="130" class="sub">fail</text>
  </g>
  <g class="step3">
    <rect x="436" y="30" width="150" height="70" rx="6" class="box good"/>
    <text x="511" y="58" text-anchor="middle" class="lbl">Approve</text>
    <text x="511" y="78" text-anchor="middle" class="sub">result ships</text>
  </g>
  <g class="step4">
    <rect x="226" y="150" width="150" height="70" rx="6" class="box"/>
    <text x="301" y="176" text-anchor="middle" class="lbl">Retry</text>
    <text x="301" y="196" text-anchor="middle" class="sub">attempt k of N</text>
    <path d="M226 185 H91 V100" class="edge" marker-end="url(#arr)"/>
    <text x="150" y="178" class="sub">retry</text>
    <path d="M376 185 H436" class="edge bad" marker-end="url(#arr)"/>
    <text x="406" y="178" text-anchor="middle" class="sub">after N</text>
    <rect x="436" y="150" width="150" height="70" rx="6" class="box hi"/>
    <text x="511" y="176" text-anchor="middle" class="lbl">Escalate</text>
    <text x="511" y="196" text-anchor="middle" class="sub">closest candidate</text>
    <text x="511" y="212" text-anchor="middle" class="sub">and failed checks</text>
  </g>
</svg>
```

The objection deserves a real hearing. A checker with a very low false-pass rate can afford a generous budget, and some tasks are only solved late in the sample sequence, as the coverage curve shows. I would still set the number from the checker, and let a low solve rate argue for a better checker instead of a bigger budget.

Where no test suite exists, teams fall back on an LLM judge that reads the output and decides whether it is right. [Zheng et al., 2023](https://arxiv.org/abs/2306.05685) found that GPT-4 agreed with human preference in over 80 percent of comparisons, the same level of agreement humans reached with each other. The same paper examines position, verbosity and self-enhancement biases, along with limited reasoning ability. I would expect those biases to matter more inside a retry loop. If the judge favors longer answers, the generator drifts toward longer answers, and each retry gives the biased judge another draw at the same preference.

Fail-closed handles part of the judge problem. A judge that errors, times out, or returns a malformed verdict should count as a rejection, and that is the easy case. It does nothing about a judge that answers confidently and is wrong. For high-stakes outputs I would not let the judge be the only gate, and I would require a deterministic check wherever one exists.

Passing a gate and being right are different properties. [Ray, 2026](https://arxiv.org/abs/2605.26128) measured small models, all under 3 billion parameters, under hard schema decoding against a baseline. Schema validity rose from 61.5 percent to 100 percent, while answer accuracy fell from 19.7 percent to 11.0 percent. The share of outputs that were valid but wrong rose from 49.5 percent to 88.9 percent. A pipeline that counted validity as success would have reported improvement on its gate metric while the answers got worse.

The second proposal is to publish three service levels for any agent loop together: the false-approve rate, the escalation rate, and the cost per approved result. Each one can be gamed alone. A loop can drive false approvals to zero by escalating everything, and it can drive escalations to zero by lowering the checker's bar. Cost per approved result shows what either move costs. Measuring false approvals needs labeled examples, and labels are expensive, so most teams will estimate the rate from a small sample with wide error bars. I would publish the interval with the point estimate. A rate of zero from twenty labels tells a reader very little, and a reader who sees only the point will trust it more than it deserves.

```diagram
title: Three service levels, each with a lever
caption: Each service level can be gamed alone, so the three are published together with the lever that moves each one.
<svg viewBox="0 0 640 170" xmlns="http://www.w3.org/2000/svg">
  <rect x="16" y="30" width="188" height="120" rx="6" class="box"/>
  <text x="110" y="58" text-anchor="middle" class="lbl">False approvals</text>
  <text x="110" y="78" text-anchor="middle" class="sub">bad answers that pass</text>
  <text x="110" y="104" text-anchor="middle" class="sub">moves with</text>
  <rect x="28" y="110" width="164" height="30" rx="6" class="box hi"/>
  <text x="110" y="130" text-anchor="middle" class="sub">checker, retry budget</text>
  <rect x="226" y="30" width="188" height="120" rx="6" class="box"/>
  <text x="320" y="58" text-anchor="middle" class="lbl">Escalation rate</text>
  <text x="320" y="78" text-anchor="middle" class="sub">share sent to a person</text>
  <text x="320" y="104" text-anchor="middle" class="sub">moves with</text>
  <rect x="238" y="110" width="164" height="30" rx="6" class="box hi"/>
  <text x="320" y="130" text-anchor="middle" class="sub">checker strictness</text>
  <rect x="436" y="30" width="188" height="120" rx="6" class="box"/>
  <text x="530" y="58" text-anchor="middle" class="lbl">Cost per approval</text>
  <text x="530" y="78" text-anchor="middle" class="sub">spend per accepted answer</text>
  <text x="530" y="104" text-anchor="middle" class="sub">moves with</text>
  <rect x="448" y="110" width="164" height="30" rx="6" class="box hi"/>
  <text x="530" y="130" text-anchor="middle" class="sub">samples and retries</text>
</svg>
```

Process reward models push the same logic into the middle of a reasoning chain. [Lightman et al., 2023](https://arxiv.org/abs/2305.20050) trained a process-supervised model that solves 78 percent of a representative subset of MATH test problems, and released PRM800K, a set of 800,000 step-level human labels. The labels are the part of the method that teams tend to leave out of the budget. A verifier at that grain is a dataset project before it is a model project.

The third proposal treats the escalation queue as product surface. Most designs treat escalation as a fallback, a list that receives whatever the loop gave up on. I would hand the person the closest candidate, the checks it failed, and the reason each one failed. A reviewer who sees that can resolve an item in minutes instead of re-deriving the problem. Every entry costs a person's attention, so a loop that escalates too often teaches its reviewers to click approve, and that failure is the one I worry about most.

The reviewer also has to fail differently from the checker. [Madaan et al., 2023](https://arxiv.org/abs/2303.17651) report an improvement of about 20 percent absolute, on average, when a model critiques and revises its own outputs. The gain is real in the paper. In that loop the critic is the generator, so the checker shares its blind spots and every retry repeats them. A second model from the same family is a weak choice for the reviewer role for the same reason.

I would put the queue on the same dashboard as the three service levels and check it first each morning. An empty queue on a loop that handles hard inputs is a reason to doubt the checker before praising the agent. Sampling is cheap. Trust is the budget, and it is spent every time a wrong answer passes.

```video
youtube: DrLdvbkgmeA
title: John Yang: SWE-bench, Can Language Models Resolve Real-World GitHub Issues?
caption: The SWE-bench lead author on how tasks are built from real issues and scored by the repository's own tests, which is the checker this essay leans on.
```

## References

1. Brown, B. et al. (2024). Large Language Monkeys: Scaling Inference Compute with Repeated Sampling. arXiv. https://arxiv.org/abs/2407.21787
2. Chen, M. et al. (2021). Evaluating Large Language Models Trained on Code. arXiv. https://arxiv.org/abs/2107.03374
3. Jimenez, C. E. et al. (2023). SWE-bench: Can Language Models Resolve Real-World GitHub Issues? arXiv. https://arxiv.org/abs/2310.06770
4. Lightman, H. et al. (2023). Let's Verify Step by Step. arXiv. https://arxiv.org/abs/2305.20050
5. Madaan, A. et al. (2023). Self-Refine: Iterative Refinement with Self-Feedback. arXiv. https://arxiv.org/abs/2303.17651
6. Ray, J. (2026). The Constraint Tax: Measuring Validity-Correctness Tradeoffs in Structured Outputs for Small Language Models. arXiv. https://arxiv.org/abs/2605.26128
7. Zheng, L. et al. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. arXiv. https://arxiv.org/abs/2306.05685
