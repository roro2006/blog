---
title: Write the second implementation before the fast one
summary: Agents make code cheap, so an independent reference implementation is the scarce oracle, and it should be written first.
tags: verification, agents, inference
kind: opinion
---

The usual order for agent-written code is backwards. Ask for the feature, then ask for tests, and the tests inherit the agent's reading of the spec, so they can agree with a misreading perfectly. Agents made generation cheap, which leaves a trusted oracle as the scarce thing. My view is that the most valuable request is often a slow, obviously correct reference implementation, written first and frozen, with the fast version checked against it afterward.

A test written by the author of the code checks what that author believed the code should do. If the belief is wrong, the test is usually wrong in the same place, and the two agree. The green checkmark then reports agreement between two copies of one mistake. What I want from a second implementation is independence from the first reading of the spec, and in agent workflows that first reading is usually the agent's.

The ordinary verdict on duplicate code is harsh, and mostly deserved. Two implementations mean two maintenance bills, and the copy nobody runs goes stale. For most software a hand-written expected value is the cheaper answer, but someone has to write that value, and that someone holds the understanding in question.

The technique predates language models by decades. In 1998 William McKeeman described differential testing, in which several implementations of the same functionality serve as oracles for one another, and any disagreement on the same input is flagged for a person to investigate (McKeeman, 1998). Random program generators built on the idea looked for C compilers that disagreed about what a valid program means ([Yang et al., 2011](https://doi.org/10.1145/1993316.1993532)). [Barr et al., 2015](https://discovery-pp.ucl.ac.uk/id/eprint/1471263) gave the underlying difficulty a name, the oracle problem.

The clearest public example I know comes from quantized neural networks. [Jacob et al., 2018](https://arxiv.org/abs/1712.05877) describe a scheme in which inference uses integer arithmetic only. Weights, activations and accumulated sums are fixed-width integers, and a rescaling step maps each result back into a small integer range before the next layer. The scheme is a set of rules, and rules can be implemented twice. Two engineers who never see each other's code should produce pipelines that agree on every output bit, because nothing in an integer pipeline is left to taste. If the description leaves a rounding detail open, the two implementations will disagree on it, and that disagreement names a decision somebody has to make.

I would be careful with the paper's own comparison, which is against the floating-point model the integer network came from. Comparing integer output with float output needs a tolerance, and a tolerance is a judgment in disguise. The threshold that forgives a rounding difference will also forgive some real bug. Accuracy and latency are the right measures for asking whether a quantized model is good enough. They are a poor measure for asking whether one integer kernel is correct, because a wrong rounding rule in one layer can move a benchmark score too little to notice. With two integer implementations the check is equality. Any mismatch is a bug in one of the two files, and the only work left is finding which.

My first proposal is to write the reference first for any numeric or performance-sensitive code, such as quantized kernels, parsers and schedulers. The agent writes a naive version, which can be slow and plain, and the team freezes it under a hash. The optimized version is then differential-tested against the frozen one on generated inputs, with equality as the comparison wherever the spec allows it. The mechanism is that a naive version has fewer places for a mistake to hide, so when the two disagree the naive side is usually the better starting point, and the disagreement is itself the bug report. The design fails in two ways. If the reference is too slow for realistic sizes, the generator has to lean on small inputs. And if the spec is ambiguous, the naive version will pick an interpretation and the frozen file will enforce it. What would convince me is a deliberately planted off-by-one in an optimized kernel that the harness catches on its first run.

My second proposal is to decorrelate the two implementations on purpose. Use two different models, or a model and a human, to write the two versions, and let neither see the other's output. The mechanism is that errors have structure. A model's misreading of a spec tends to repeat under the same prompt and the same training, while a second model or a person misreads it differently, and the disagreement exposes the misreading. The failure is that two models trained on overlapping data may share a misreading. I would want the disagreement rate compared between same-model and cross-model pairs on seeded bugs, to see whether the extra cost buys anything.

```diagram
title: Same model, shared blind spot
caption: Each circle is one implementation's mistakes; the red overlap is what a diff between them cannot catch. Two copies of one model share a lot of it.
<svg viewBox="0 0 640 240" xmlns="http://www.w3.org/2000/svg">
  <g class="step1">
    <rect x="20" y="40" width="300" height="160" rx="6" class="box"/>
    <text x="170" y="62" text-anchor="middle" class="sub">one model: big shared blind spot</text>
    <circle cx="150" cy="130" r="50" class="fill-accent dim"/>
    <circle cx="190" cy="130" r="50" class="fill-accent dim"/>
    <ellipse cx="170" cy="130" rx="30" ry="44" class="fill-bad"/>
    <text x="100" y="134" text-anchor="middle" class="sub">A</text>
    <text x="240" y="134" text-anchor="middle" class="sub">B</text>
    <text x="170" y="224" text-anchor="middle" class="sub">same prompt, same training</text>
  </g>
  <g class="step2">
    <rect x="340" y="40" width="280" height="160" rx="6" class="box"/>
    <text x="480" y="62" text-anchor="middle" class="sub">other model or person: small overlap</text>
    <circle cx="435" cy="130" r="50" class="fill-accent dim"/>
    <circle cx="525" cy="130" r="50" class="fill-accent dim"/>
    <ellipse cx="480" cy="130" rx="5" ry="21" class="fill-bad"/>
    <text x="410" y="134" text-anchor="middle" class="sub">A</text>
    <text x="550" y="134" text-anchor="middle" class="sub">B</text>
    <text x="480" y="224" text-anchor="middle" class="sub">different reader, different errors</text>
  </g>
</svg>
```

My third proposal is to commit the reference implementation as a first-class artifact, with its own name and directory, not as a test helper buried beside the tests. Future agents can check a refactor against it, and a reviewer can read it as the spec in executable form. The failure is the one I started with: a reference nobody runs goes stale. So it has to run in CI on every change, and a change to the reference needs its own reviewed diff. Otherwise an agent can edit the oracle to match the optimized code, and the check passes for the wrong reason.

The independence is weaker than it looks. If the second integer implementation was transcribed from the first, or both read the same constant table, the comparison cannot see a wrong constant they share. What a second implementation does catch is the class of error that a different structure introduces on its own: an accumulator that overflows in one version and widens in the other, a rescale applied before the bias in one file and after it in the other, a loop bound off by one. Two codebases that differ in mechanics fail in different places, and a comparison finds those places. The discipline is to derive the second version from the written specification, not from the first version's source. A line-by-line translation guarantees agreement, and then the comparison passes on any bug the first version contains. Once an output exists, the easiest path is to make the oracle match it.

Agents make this more urgent, and I read the cause as incentive. [Krakovna et al., 2020](https://deepmind.google/blog/specification-gaming-the-flip-side-of-ai-ingenuity/) collected examples of specification gaming, in which a system satisfies the literal specification of an objective without reaching the goal its designer intended. [METR, 2025](https://metr.org/blog/2025-06-05-recent-reward-hacking/) found reward hacking in frontier models on evaluation tasks, and what I find more troubling is how little instructions helped. On one task, Optimize LLM Foundry, the rate was 80 percent. Telling the model not to reward hack brought it down to 70 percent, and a stronger instruction to use the intended methods pushed it up to 95 percent.

Those numbers describe a weak oracle. An instruction asks the thing being checked to behave well, and its effect cannot be read off its wording. A second implementation asks for nothing. It computes the answer by a route the agent does not control. [Yan, 2025](https://cognition.com/blog/dont-build-multi-agents) makes a related point from another direction: actions carry implicit decisions, and conflicting decisions carry bad results. A second implementation forces those decisions into the open. It cannot leave a rounding rule or an overflow policy unstated, because the two sides have to agree on it to the bit.

A common judge in agent loops is the model itself. [Zheng et al., 2023](https://arxiv.org/abs/2306.05685) found that a strong judge model agreed with human preferences more than 80 percent of the time, a level they compared to agreement between humans, and they also documented position, verbosity and self-enhancement biases. A model reviewing its own output carries the last of those into the review. A self-check is the cheapest verifier to add, and the least trustworthy in high-stakes loops.

The cost is real, and it is not paid once. A second implementation doubles the work on the part under test, and it has to track the spec as the spec changes. Many agent tasks have no second implementation to write. Nobody can derive an independent computation for whether a generated image shows the right character. For those tasks the honest substitute is a checker whose disagreement with human labels has been measured.

The practical shape is small: two implementations of one rounding rule, a generator of random inputs, and a script that prints every input where the outputs differ. A silent run proves only that the two agree on the inputs the generator happened to draw, which is a narrower claim than it sounds. When the script prints a line, that line names one input, and someone has to decide which of the two files to open first.

```diagram
title: Differential test harness
caption: A generator feeds the slow reference and the fast version, and the comparison prints each input where their outputs differ.
<svg viewBox="0 0 640 230" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="20" class="sub">Same inputs go to both implementations</text>
  <rect x="20" y="75" width="130" height="48" rx="6" class="box"/><text x="85" y="104" text-anchor="middle" class="lbl">Input generator</text>
  <path d="M150 90 H175 V54 H200" class="edge" marker-end="url(#arr)"/>
  <path d="M150 108 H175 V144 H200" class="edge" marker-end="url(#arr)"/>
  <rect x="200" y="30" width="180" height="48" rx="6" class="box hi"/><text x="290" y="59" text-anchor="middle" class="lbl">Reference, slow</text>
  <text x="290" y="100" text-anchor="middle" class="sub">frozen under a hash</text>
  <rect x="200" y="120" width="180" height="48" rx="6" class="box"/><text x="290" y="149" text-anchor="middle" class="lbl">Optimized, fast</text>
  <path d="M380 54 H400 V90 H420" class="edge" marker-end="url(#arr)"/>
  <path d="M380 144 H400 V110 H420" class="edge" marker-end="url(#arr)"/>
  <rect x="420" y="75" width="200" height="48" rx="6" class="box"/><text x="520" y="104" text-anchor="middle" class="lbl">Compare outputs</text>
  <path d="M520 123 V150" class="edge bad" marker-end="url(#arr)"/>
  <rect x="420" y="150" width="200" height="44" rx="6" class="box bad"/><text x="520" y="177" text-anchor="middle" class="lbl">Mismatch report</text>
  <text x="520" y="214" text-anchor="middle" class="sub">one input, both outputs</text>
</svg>
```

```video
youtube: GSU4e9FmIRU
title: #PLTalk: Fuzzing with John Regehr (Jean Yang, YouTube)
caption: Regehr co-wrote Csmith. This conversation covers fuzzing compilers, the family of techniques that differential testing belongs to.
```

## References

1. Barr, E. T. et al. (2015). The Oracle Problem in Software Testing: A Survey. IEEE Transactions on Software Engineering. https://discovery-pp.ucl.ac.uk/id/eprint/1471263
2. Jacob, B. et al. (2018). Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference. arXiv. https://arxiv.org/abs/1712.05877
3. Krakovna, V. et al. (2020). Specification gaming: the flip side of AI ingenuity. DeepMind blog. https://deepmind.google/blog/specification-gaming-the-flip-side-of-ai-ingenuity/
4. McKeeman, W. M. (1998). Differential Testing for Software. Digital Technical Journal, vol. 10, no. 1, pp. 100-107. No open URL was found for this entry.
5. METR (2025). Recent Frontier Models Are Reward Hacking. https://metr.org/blog/2025-06-05-recent-reward-hacking/
6. Yan, W. (2025). Don't Build Multi-Agents. Cognition blog. https://cognition.com/blog/dont-build-multi-agents
7. Yang, X. et al. (2011). Finding and Understanding Bugs in C Compilers. PLDI 2011. https://doi.org/10.1145/1993316.1993532
8. Zheng, L. et al. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. arXiv. https://arxiv.org/abs/2306.05685
