---
title: Schema validity is the wrong finish line for agents
summary: Build agent interfaces so invalid actions cannot exist, and report wrong answers that still pass validation, since validity alone now misleads.
tags: verification, inference
kind: opinion
date: 2026-08-11
---

Schema validity is the wrong finish line for agents. Structured outputs made it nearly free to guarantee that a tool call parses and names a registered function, and a team that stops there has measured the easiest property of the action. I think the larger gain comes from designing interfaces so that invalid actions have nowhere to come from. Each gain of that kind moves the error into the meaning of the call, where checks are harder to write. The number to watch is the rate of wrong answers that are still valid.

Take an agent with four registered tools, asked to file a support ticket. It emits a call to `create_ticket_v2`. The name is plausible because many real APIs use that pattern, the arguments are well formed, and the JSON parses. A dispatcher rejects the call, the agent invents another name, and the transcript looks like ordinary flailing. Nothing about the output is malformed in the sense a parser cares about. The error becomes visible only when someone compares each name against the registry after the fact.

The usual response is a check: validate, log the failures, retry or reject, and measure how often the check fires. I think this remains the right first move, since it bolts onto an existing system without changing it. Its weakness is that it is only as complete as the list of things its author thought to check. A rate measured on a sample says how often an error occurred in that sample, and nothing about inputs nobody wrote down.

The stronger move is to shape the output space so the error has no slot to occupy. Where the legal outputs form a small, known set, you encode legality in the decoder or the network. The language-model version is the best developed. [Willard and Louf, 2023](https://arxiv.org/abs/2307.09702) showed that a regular expression or context-free grammar can guide text generation with little added cost per token. In practice, at each step the sampler works out which tokens could still lead to a string the grammar accepts, and every other token gets zero probability. Tool names and JSON arguments are a natural target. [Geng et al., 2025](https://arxiv.org/abs/2501.10868) assembled JSONSchemaBench, 10K real-world JSON schemas run through six constrained decoding frameworks, and observed that systematic evaluation of these frameworks has barely begun. The guarantee is easy to sell. The measurement is where it thins out.

The pointer idea is older. [Vinyals et al., 2015](https://arxiv.org/abs/1506.03134) used attention as a pointer that selects a member of the input as the output, so the number of output classes depends on how long the input is. The output vocabulary becomes the input itself. [Zaheer et al., 2017](https://arxiv.org/abs/1703.06114) characterized the functions that are invariant to permutations of a set, which supplies the other half of the argument. If the candidates form a set, the model should have no way to read their order.

The sharpest recent result is the one that complicates the story. [Ray (2026)](https://arxiv.org/abs/2605.26128) studied small models under 3B parameters. Under hard answer-only schema decoding, schema validity rose from 61.5% to 100.0%, while answer accuracy fell from 19.7% to 11.0%. The share of wrong outputs that still passed the schema rose from 49.5% to 88.9%. The paper's own summary is that "the error is semantic, not structural." A constraint can remove one class of error and leave the wrong answer well formed, and sometimes better formed than before.

```chart
title: What hard schema decoding bought and cost (models under 3B)
unit: %
source: [Ray, 2026](https://arxiv.org/abs/2605.26128)
note: Baseline versus hard answer-only schema decoding. Validity went up; accuracy went down.
Schema-valid, baseline: 61.5
Schema-valid, constrained: 100
Correct, baseline: 19.7
Correct, constrained: 11
```

The distortion has a source that a decoder cannot reach. [Tam et al., 2024](https://arxiv.org/abs/2408.02442) found a significant decline in LLM reasoning under format restrictions, and stricter restrictions generally produced greater degradation. A later paper, [Lee et al., 2026](https://arxiv.org/abs/2604.03616), argues that much of this cost enters at the prompt: format-requesting instructions alone cause most of the accuracy loss before any decoder constraint is applied. Those findings locate the cost in different places, and a designer who only masks the decoder has not touched the second one.

My first proposal is to make the pointer idea literal in agent APIs. Tools would return opaque handles, such as file ids, row ids and card ids, and every later call could pass back only handles the agent was actually given. The action space then equals the set of things the agent has seen. What I would build is a thin layer in front of the write tools that rejects any identifier outside the handle set before the request leaves the process. The mechanism is simple: an invented identifier has no handle behind it, so it cannot be formed from the registry's public names or from a guess about numbering. The design could fail in three ways. Handles go stale when another writer changes the record, so they need expiry and an error the agent can act on. Some workflows start from an identifier a user typed, which has to pass through an explicit lookup tool. And sequential handles leak information, so they should be random. I would be convinced by a before-and-after run on a fixed task set where calls naming unseen identifiers drop to zero and task success does not fall.

```diagram
title: Handles, not free-text names
caption: Each call may reuse only the handles the tool issued, so a name the agent invented has no handle and the boundary rejects it.
<svg viewBox="0 0 640 210" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="20" class="sub">Agent context holds only issued handles</text>
  <g class="step1">
    <rect x="20" y="40" width="130" height="40" rx="6" class="box"/><text x="85" y="65" text-anchor="middle" class="lbl">list_files</text>
    <path d="M150 60 H210" class="edge" marker-end="url(#arr)"/>
    <rect x="210" y="40" width="80" height="40" rx="6" class="box good"/><text x="250" y="65" text-anchor="middle" class="lbl">h1</text>
    <rect x="300" y="40" width="80" height="40" rx="6" class="box good"/><text x="340" y="65" text-anchor="middle" class="lbl">h2</text>
    <rect x="390" y="40" width="80" height="40" rx="6" class="box good"/><text x="430" y="65" text-anchor="middle" class="lbl">h3</text>
  </g>
  <g class="step2">
    <path d="M340 80 V130" class="edge" marker-end="url(#arr)"/>
    <rect x="260" y="130" width="160" height="40" rx="6" class="box hi"/><text x="340" y="155" text-anchor="middle" class="lbl">write(h2)</text>
    <path d="M420 150 H470" class="edge good" marker-end="url(#arr)"/>
    <rect x="470" y="130" width="150" height="40" rx="6" class="box good"/><text x="545" y="155" text-anchor="middle" class="lbl">accepted</text>
  </g>
  <g class="step3">
    <rect x="20" y="130" width="190" height="40" rx="6" class="box bad"/><text x="115" y="155" text-anchor="middle" class="lbl">report_final.txt</text>
    <path d="M210 150 H260" class="edge bad" marker-end="url(#arr)"/>
    <text x="115" y="190" text-anchor="middle" class="sub">free text, never issued</text>
  </g>
</svg>
```

My second proposal runs the other way round. Let the model reason in unconstrained text, then emit only the final answer under the schema, with the reasoning still in context. The Tam and Lee findings both point toward keeping the format request out of the reasoning, and the second one points to the prompt as the place where the cost lands. So the design moves the format request to the last turn and leaves the thinking free. The failure I worry about is disagreement. The reasoning concludes one answer, the schema forces a different one, and the final decode rewrites the answer without saying so. I would log both and treat each disagreement as a finding. I am also not convinced this matters for every model, since Lee et al. report that most recent closed-weight models show little to no format tax. The first step is to measure the tax on your own model before adding a second phase.

```diagram
title: Reason freely, then constrain the answer
caption: Reasoning stays unconstrained and the schema applies only to the final answer, while a semantic check still judges whether that answer is right.
<svg viewBox="0 0 640 200" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="20" class="sub">Reasoning is free; only the final turn carries the schema</text>
  <rect x="20" y="50" width="150" height="40" rx="6" class="box"/><text x="95" y="75" text-anchor="middle" class="lbl">Reason freely</text>
  <text x="95" y="108" text-anchor="middle" class="sub">no format request</text>
  <path d="M170 70 H210" class="edge" marker-end="url(#arr)"/>
  <rect x="210" y="50" width="190" height="40" rx="6" class="box hi"/><text x="305" y="75" text-anchor="middle" class="lbl">Constrain the answer</text>
  <path d="M400 70 H440" class="edge" marker-end="url(#arr)"/>
  <rect x="440" y="50" width="180" height="40" rx="6" class="box good"/><text x="530" y="75" text-anchor="middle" class="lbl">Schema-valid output</text>
  <path d="M530 90 V120" class="edge" marker-end="url(#arr)"/>
  <rect x="440" y="120" width="180" height="40" rx="6" class="box"/><text x="530" y="145" text-anchor="middle" class="lbl">Is it right?</text>
  <text x="530" y="180" text-anchor="middle" class="sub">semantic check still runs</text>
</svg>
```

My third proposal concerns evaluation. Every structured-output eval should report wrong-but-valid next to validity, with the counts behind both. The Ray result shows why a validity figure alone is misleading: it would have read as a clean win. The failure mode is that a share can rise because its denominator shrank, so a team could mistake a shrinking pool of wrong answers for a worse constraint. Absolute counts guard against that. What would convince me is that the wrong-but-valid figure separates constraints that help from constraints that only reshape errors, across more than one task family and model size.

The ordinary objection deserves its weight. A learned constraint can cover cases the designer never wrote down, while a built-in invariant covers only what you are sure of. "A call must name a registered tool" is a fact about the interface, so the head is correct by definition. "An agent never calls the same tool twice in one turn" is usually true and sometimes false, and a hard constraint would forbid the retry that was needed. The invariant is only as true as its input, so a stale registry produces a decoder faithfully restricted to tools that no longer exist. I would still build the invariant, but the team has to name who owns the registry, or the constraint becomes a confident way of being wrong.

Construction pays most where a wrong output is expensive to notice downstream and the legal set is small. An agent choosing among a handful of tools has a candidate list short enough to point at directly, and an unregistered name has no slot to point to. A dispatcher usually fails loudly on an unknown name, which is a cheap error. The expensive one is a call to the wrong real tool with valid arguments, and no decoder touches that. The check I still have to run is whether the agent picked the tool the task needed, and I do not think any architecture settles that for me. The practical consequence is that the dispatcher's log will eventually go quiet. That silence should start the next review, not end this one.

## References

1. Willard, B. T., and Louf, R. (2023). Efficient Guided Generation for Large Language Models. arXiv. https://arxiv.org/abs/2307.09702
2. Geng, S., et al. (2025). JSONSchemaBench: A Rigorous Benchmark of Structured Outputs for Language Models. arXiv. https://arxiv.org/abs/2501.10868
3. Vinyals, O., Fortunato, M., and Jaitly, N. (2015). Pointer Networks. arXiv. https://arxiv.org/abs/1506.03134
4. Zaheer, M., et al. (2017). Deep Sets. arXiv. https://arxiv.org/abs/1703.06114
5. Tam, Z. R., et al. (2024). Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models. arXiv. https://arxiv.org/abs/2408.02442
6. Lee, I. Y., D'Antoni, L., and Berg-Kirkpatrick, T. (2026). The Format Tax. arXiv. https://arxiv.org/abs/2604.03616
7. Ray, J. (2026). The Constraint Tax: Measuring Validity-Correctness Tradeoffs in Structured Outputs for Small Language Models. arXiv. https://arxiv.org/abs/2605.26128
