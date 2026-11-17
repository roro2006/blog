---
title: Application teams should design around the KV cache
summary: Application teams should shape prompts and agent loops around the KV cache, since it decides what a server can reuse and what each token costs.
tags: inference, hardware
kind: opinion
date: 2026-09-28
---

Most teams file the KV cache under infrastructure, a detail for the serving group to worry about while the application group writes prompts. I think that split is backwards. The cache decides how many requests a server can hold, how much of a prompt it can reuse, and what a long agent session costs to keep going. Each of those depends on choices the application makes: where the stable text sits in the prompt, whether tools are listed in the same order every time, and whether an agent rewrites its own history. The serving team cannot repair those choices from below. Application teams should design prompts and agent loops around the cache, and they should report its behavior with the same care they give model quality.

Every token the model has already processed leaves a key vector and a value vector at every layer. A new token attends to all of them, so the server keeps them until the sequence ends. The cache grows with each sequence's length, multiplies by the number of sequences served at once, and competes with the weights for the same accelerator memory. Two levers have shaped the field's answer. The first is packing. [Kwon et al., 2023](https://arxiv.org/abs/2309.06180) describe earlier systems that reserved one contiguous region per request, sized for the longest output it might produce, so much of the memory sat empty. Their system, vLLM, splits the cache into blocks that need not sit together, borrowing paging from operating systems. The abstract reports that vLLM "improves the throughput of popular LLMs by 2-4x with the same level of latency." The gain comes from fitting more sequences into memory that was already there.

The second lever is sharing. Many requests begin with the same system prompt, the same few-shot examples or the same document. If the cache for that prefix is kept and indexed, a later request can skip recomputing it. [Zheng et al., 2023](https://arxiv.org/abs/2312.07104) organize cached prefixes in a radix tree, so partial matches count as well as exact ones. Their abstract says SGLang "achieves up to 6.4x higher throughput compared to state-of-the-art inference systems," but it does not say how much of that comes from prefix reuse, so I would not hang the 6.4 on that mechanism. Sharing has one rule that matters for application design: a prefix can only be reused from its first token forward, so the first token that differs ends the match. The same logic reaches across machines. [Qin et al., 2024](https://arxiv.org/abs/2407.00079) built Mooncake around a KVCache-centric design, where the scheduler asks where a request's prefix already lives before it asks which GPU is free.

The first thing I would change is the order of the prompt, because the cache rewards a fixed order. Stable content goes first: system instructions, tool definitions, and reference documents that recur across requests. Volatile content goes last: the current user turn, a timestamp, a snippet retrieved for this query. The common mistake is a timestamp at the top of the system prompt, which turns every request into a miss from its first token. For agents the rule is stronger. Context should be append-only, so each turn extends the prefix the previous turn left in cache. When an agent summarizes or compacts its history, it rewrites that prefix and discards the reuse, so I would compact rarely and in batches, and count the misses a compaction causes alongside the tokens it saves. The mechanism is simple, and so is the risk. A stable prefix can freeze stale instructions, and a model may attend more reliably to material near the end of a long context. What would convince me is a comparison on one evaluation set in which the new layout raises the hit rate and leaves task success flat or better. If the hit rate rises and success falls, the layout is wrong, however cheap its tokens look.

```diagram
title: Stable prefix, appended turns
caption: Stable content goes first, so each new turn only adds to the end of a prefix the cache already holds.
<svg viewBox="0 0 640 220" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="24" class="sub">Prompt layout: stable content first, volatile content last</text>
  <rect x="20" y="34" width="100" height="40" rx="6" class="box good"/><text x="70" y="59" text-anchor="middle" class="lbl">system</text>
  <rect x="130" y="34" width="100" height="40" rx="6" class="box good"/><text x="180" y="59" text-anchor="middle" class="lbl">tools</text>
  <rect x="240" y="34" width="100" height="40" rx="6" class="box good"/><text x="290" y="59" text-anchor="middle" class="lbl">docs</text>
  <g class="step1">
    <rect x="360" y="34" width="85" height="40" rx="6" class="box hi"/><text x="402" y="59" text-anchor="middle" class="lbl">turn 1</text>
  </g>
  <g class="step2">
    <rect x="453" y="34" width="85" height="40" rx="6" class="box hi"/><text x="495" y="59" text-anchor="middle" class="lbl">turn 2</text>
  </g>
  <g class="step3">
    <rect x="546" y="34" width="85" height="40" rx="6" class="box hi"/><text x="588" y="59" text-anchor="middle" class="lbl">turn 3</text>
  </g>
  <text x="20" y="100" class="sub">stable prefix, reused by every turn</text>
  <text x="360" y="100" class="sub">appended in order</text>
  <path d="M290 74 V126" class="edge" marker-end="url(#arr)"/>
  <rect x="20" y="126" width="600" height="40" rx="6" class="box"/><text x="320" y="151" text-anchor="middle" class="lbl">Next request reuses everything left of the first new token</text>
  <text x="20" y="194" class="sub">Append-only context keeps the prefix valid for the next turn.</text>
</svg>
```

```diagram
title: A timestamp at the top breaks the prefix
caption: A timestamp at the top turns every request into a miss. Moved to the end, the shared prefix still hits.
<svg viewBox="0 0 640 200" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="24" class="sub">Timestamp at the top</text>
  <rect x="20" y="34" width="110" height="36" rx="6" class="box bad"/><text x="75" y="57" text-anchor="middle" class="lbl">timestamp</text>
  <rect x="140" y="34" width="90" height="36" rx="6" class="box"/><text x="185" y="57" text-anchor="middle" class="lbl">system</text>
  <rect x="240" y="34" width="90" height="36" rx="6" class="box"/><text x="285" y="57" text-anchor="middle" class="lbl">tools</text>
  <rect x="340" y="34" width="90" height="36" rx="6" class="box"/><text x="385" y="57" text-anchor="middle" class="lbl">docs</text>
  <rect x="440" y="34" width="90" height="36" rx="6" class="box"/><text x="485" y="57" text-anchor="middle" class="lbl">turn</text>
  <text x="20" y="88" class="sub">First token differs, so the whole prompt misses</text>
  <text x="20" y="124" class="sub">Timestamp at the end</text>
  <rect x="20" y="134" width="90" height="36" rx="6" class="box good"/><text x="65" y="157" text-anchor="middle" class="lbl">system</text>
  <rect x="120" y="134" width="90" height="36" rx="6" class="box good"/><text x="165" y="157" text-anchor="middle" class="lbl">tools</text>
  <rect x="220" y="134" width="90" height="36" rx="6" class="box good"/><text x="265" y="157" text-anchor="middle" class="lbl">docs</text>
  <rect x="320" y="134" width="90" height="36" rx="6" class="box"/><text x="365" y="157" text-anchor="middle" class="lbl">turn</text>
  <rect x="420" y="134" width="110" height="36" rx="6" class="box"/><text x="475" y="157" text-anchor="middle" class="lbl">timestamp</text>
  <text x="20" y="186" class="sub">Shared prefix stays cached, only the tail is recomputed</text>
</svg>
```

The second thing I would build is a determinism test for reuse. Reuse is a claim that cached state equals recomputed state, and no throughput chart checks that claim. The test runs a prompt cold, runs it again against a warm cache, and compares the outputs. Greedy decoding should match token for token. Batch composition is the subtle risk. A kernel whose accumulation order depends on which other sequences share its batch can give slightly different logits for the same prefix, and a warm request may land in a different batch from the cold one. Greedy tokens can agree while logits drift, so I would compare logits against a recorded tolerance and write that tolerance down. I would also run the check under concurrent load, because an idle server batches differently from a busy one and can pass a test that production fails. The check I trust most is one that fails on purpose. If I shift the position IDs of a cached prefix by one, the test should catch it, and a determinism test that misses a planted off-by-one is decoration. Its weak point is that many products sample rather than decode greedily, so a greedy test covers less than it appears to.

Third, I would put the prefix hit rate beside throughput in every serving benchmark, and report the speedup from reuse as a function of that rate. A speedup belongs to the system and the traffic together. The same cache that gives a chat product large gains can give a batch job over unrelated documents almost nothing, so one multiplier describes neither workload. I'd bet many published comparisons would look different if they printed the hit rate beside the speed. Nobody has to be dishonest for that to happen, since the chart simply drops the variable. The failure I would worry about is that a benchmark can inflate the hit rate by replaying identical prompts, which is the easiest way to make any cache look good. So the benchmark should draw prompts from a trace with realistic sharing, and publish the trace with the result. What would convince me is two teams with different traffic reporting hit rates and speedups that fall on one curve. At that point the curve, not the headline multiplier, becomes the thing to compare across systems.

Here the common view has a fair point, and it deserves more room than I have given it. Much of the cache's size is set before the product exists. [Ainslie et al., 2023](https://arxiv.org/abs/2305.13245) showed that a multi-head checkpoint can be uptrained into grouped-query attention, where several query heads share one key head and one value head, using 5% of the original pre-training compute. That is a cheap retrofit compared with pretraining. [DeepSeek-AI, 2024](https://arxiv.org/abs/2405.04434) went further with a decision made before training. Its multi-head latent attention reduces the KV cache by 93.3% relative to DeepSeek 67B, and the abstract pairs that with 5.76 times the maximum generation throughput. As I read the paper, the model stores a compressed latent per token and rebuilds keys and values from it. Latent attention is a bet placed before anyone knows whether the rest of the model will work, and a team that treats the cache as plumbing cannot make that bet later. My claim therefore has a limit. Application teams can shape how the cache is used, but the training run fixes its size, and every server inherits that choice.

There is also a place where my own advice could backfire. A prefix cache shared across users makes one request faster when another user has already sent the same prefix, and that difference in speed can be observed from outside. For public material such as a shared document this is harmless. For a prompt carrying private instructions or retrieved records, it is a side channel I would not accept by default. I would keep reuse inside a tenant boundary unless the prefix is known to be public, and accept the lower hit rate that costs. That trade belongs to the product owner, who knows what the prompt contains, rather than to the serving team, which only sees the cache.

The model file is identical on every server in a fleet. What differs between the servers is the cache: how full it is, which prefixes it holds, and what it evicts when a new user arrives. The cheapest token is one you already computed, and the place to make it reusable is the text the application writes. That is where I would look first.

```video
youtube: 5ZlavKF_98U
title: Fast LLM Serving with vLLM and PagedAttention (Anyscale)
caption: The vLLM team on paging the KV cache, the starting point for treating cache layout as something applications should design around.
```

## References

1. Kwon et al. (2023). Efficient Memory Management for Large Language Model Serving with PagedAttention. arXiv. https://arxiv.org/abs/2309.06180
2. Zheng et al. (2023). SGLang: Efficient Execution of Structured Language Model Programs. arXiv. https://arxiv.org/abs/2312.07104
3. Ainslie et al. (2023). GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints. arXiv. https://arxiv.org/abs/2305.13245
4. DeepSeek-AI (2024). DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model. arXiv. https://arxiv.org/abs/2405.04434
5. Qin et al. (2024). Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving. arXiv. https://arxiv.org/abs/2407.00079
