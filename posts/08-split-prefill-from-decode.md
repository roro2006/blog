---
title: Disaggregation should be judged by the cache it moves
summary: Disaggregated serving should be judged by the KV cache it moves across the network, not by the throughput multiplier in its headline.
tags: inference, hardware
kind: opinion
date: 2026-10-06
---

The common view is that disaggregated serving, which runs prefill and decode on separate pools of hardware, is a niche for very large deployments. I think that is close to backwards. Splitting the two phases is the first step toward running inference like a distributed database, and agent workloads, with long contexts, short answers and repeated prefixes, will push the idea much further than chat did. The split also has a cost that most published tables leave out. The cache has to cross a network between prefill and decode, and that transfer is the part of the design I would argue hardest about.

Each request is two jobs run back to back on the same GPU. Prefill reads the whole prompt at once, which becomes large matrix multiplications that keep the arithmetic units busy. Decode writes the answer one token per step, and each step streams the model weights and the stored keys and values through memory. [Leviathan et al., 2023](https://arxiv.org/abs/2211.17192) state the serial part plainly: "decoding K tokens takes K serial runs of the model." Prefill is therefore limited mostly by arithmetic and decode mostly by memory traffic. On one device the two share a queue. A long prompt admitted into a batch of decoding users takes a slice of the device, and those users feel it as a pause between their tokens.

```diagram
title: One request, two pools, one transfer
caption: Each request crosses two pools, and the cache transfer between them is the cost most tables leave out.
<svg viewBox="0 0 640 160" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="24" class="sub">Prefill and decode on separate pools</text>
  <rect x="20" y="34" width="170" height="56" rx="6" class="box hi"/><text x="105" y="58" text-anchor="middle" class="lbl">Prefill GPUs</text><text x="105" y="76" text-anchor="middle" class="sub">compute-bound</text>
  <path d="M190 62 H270" class="edge" marker-end="url(#arr)"/>
  <text x="230" y="54" text-anchor="middle" class="sub">KV cache</text>
  <rect x="270" y="34" width="130" height="56" rx="6" class="box"/><text x="335" y="58" text-anchor="middle" class="lbl">KV transfer</text><text x="335" y="76" text-anchor="middle" class="sub">over the network</text>
  <path d="M400 62 H480" class="edge" marker-end="url(#arr)"/>
  <rect x="480" y="34" width="140" height="56" rx="6" class="box hi"/><text x="550" y="58" text-anchor="middle" class="lbl">Decode GPUs</text><text x="550" y="76" text-anchor="middle" class="sub">memory-bound</text>
  <path d="M20 104 V110 H400 V104" class="edge"/>
  <text x="20" y="126" class="sub">TTFT, time to first token</text>
  <text x="20" y="142" class="sub">waits for prefill and the transfer</text>
  <path d="M480 104 V110 H620 V104" class="edge"/>
  <text x="480" y="126" class="sub">TPOT, per token</text>
  <text x="480" y="142" class="sub">one token per step</text>
</svg>
```

That mechanism is what [Zhong et al., 2024](https://arxiv.org/abs/2401.09670) build around. DistServe optimizes for goodput, meaning requests that meet their latency targets, rather than raw throughput. They report that it can serve "7.4x more requests or 12.6x tighter SLO, compared to state-of-the-art systems," while "staying within latency constraints for > 90% of requests." The choice of metric is most of the argument. Raw throughput can look healthy while a tail of users waits behind somebody else's prompt.

The colocated alternative deserves its due. Keep one pool and one scheduler, and tune it hard by capping prompt length, reordering the queue and managing memory. [Kwon et al., 2023](https://arxiv.org/abs/2309.06180) report that vLLM "improves the throughput of popular LLMs by 2-4x with the same level of latency," and a large part of that comes from managing the KV cache so little memory is wasted. Better paging is a real gain. It does not give prefill its own arithmetic, and it does not stop a compute-heavy burst from landing inside a memory-heavy loop. Colocation can be tuned a long way, but eventually the two phases' bottlenecks collide, and that is where I think the split starts to pay.

The first thing I would change is the product spec, before anyone picks a topology. Time to first token and time per output token are different promises to different users. A coding agent waiting on its next step cares about the first token. A streamed answer cares about a steady rhythm once it starts. Once those two numbers are written for each product surface, the disaggregation decision becomes a calculation: split where the colocated system misses the targets during the bursts that matter. The mechanism is that a goodput scheduler can only trade one user's latency against another's if someone has said whose latency counts. The failure is that targets written in advance can be set loosely enough that a team passes its own dashboard. What would convince me is a plot of the targets against real traffic, showing the colocated system missing them at the peaks. Without that plot, the SLO is a number chosen to justify the design.

Agent traffic is more prefill-heavy than chat was. Each turn resends a long prefix, most of it already seen, and appends a short step, so prefill dominates the work per request while the cache built by earlier turns gets reused. I would size the two pools from the token mix of real traffic: prompt tokens against output tokens, and the reuse rate of prefixes. The ratio should come from the trace, not from a reference architecture. Placement matters as much as sizing. [Qin et al., 2024](https://arxiv.org/abs/2407.00079) frame Mooncake around a KVCache-centric design, which changes the question from which GPU runs this request to where the request's prefix already lives. That is a placement and eviction problem with bandwidth limits, and the scheduler has to solve it on every turn. The failure mode is that agent traces change shape quickly, so a ratio tuned this month can be wrong the next. What would convince me is a replay of recent agent traces against the planned split, reporting prefill and decode utilization separately. If one pool idles while the other queues, the ratio is wrong whatever the diagram says.

```diagram
title: Agent turns route to the node holding the prefix
caption: Each turn sends a long prefix and gets a short answer, so routing to the node that already holds the prefix can skip recomputing it.
<svg viewBox="0 0 640 230" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="24" class="sub">One agent turn, routed by where its prefix lives</text>
  <rect x="20" y="40" width="130" height="56" rx="6" class="box"/><text x="85" y="64" text-anchor="middle" class="lbl">Long input</text><text x="85" y="82" text-anchor="middle" class="sub">shared prefix</text>
  <path d="M150 68 H190" class="edge flow" marker-end="url(#arr)"/>
  <rect x="190" y="40" width="110" height="56" rx="6" class="box hi"/><text x="245" y="64" text-anchor="middle" class="lbl">Router</text><text x="245" y="82" text-anchor="middle" class="sub">finds prefix</text>
  <path d="M300 68 H330" class="edge flow" marker-end="url(#arr)"/>
  <rect x="330" y="40" width="150" height="56" rx="6" class="box good"/><text x="405" y="64" text-anchor="middle" class="lbl">Holds prefix</text><text x="405" y="82" text-anchor="middle" class="sub">cache hit, fast</text>
  <path d="M245 96 V152 H330" class="edge flow" marker-end="url(#arr)"/>
  <rect x="330" y="124" width="150" height="56" rx="6" class="box dim"/><text x="405" y="148" text-anchor="middle" class="lbl">Other node</text><text x="405" y="166" text-anchor="middle" class="sub">recomputes prefix</text>
  <path d="M480 68 H510" class="edge" marker-end="url(#arr)"/>
  <path d="M480 152 H495 V80 H510" class="edge" marker-end="url(#arr)"/>
  <rect x="510" y="40" width="120" height="56" rx="6" class="box"/><text x="570" y="64" text-anchor="middle" class="lbl">Short output</text><text x="570" y="82" text-anchor="middle" class="sub">few tokens</text>
  <text x="20" y="214" class="sub">Long input, short output: most of the cost is reading the prefix</text>
</svg>
```

There is a strong objection, and it can reverse the design. Moving a cache costs time, and for a short prompt the transfer can take longer than recomputing the prefill on the decode machine. The break-even depends on how big the cache is, and the model architecture sets that size. [DeepSeek-AI, 2024](https://arxiv.org/abs/2405.04434) report that their attention design "reduces the KV cache by 93.3%" compared with DeepSeek 67B. If the cache is 6.7 percent of its former size, the handoff is about fifteen times smaller (100 divided by 6.7, derived). A choice made in the model layers therefore changes whether the split pays. A team running a model with a large cache over a slow link should expect the transfer to dominate, and I would measure that before reading any multiplier. Disaggregation is also not free at small scale. Two pools need their own provisioning, a router that knows where each cache lives, and enough load to keep both busy. A single GPU serving a handful of users should stay colocated.

Vendors push in the other direction. [NVIDIA, 2025](https://developer.nvidia.com/blog/introducing-nvidia-dynamo-a-low-latency-distributed-inference-framework-for-scaling-reasoning-ai-models/) says Dynamo boosts "the number of requests served by up to 30x" when running DeepSeek-R1 on Blackwell, and separately that it "more than doubled the throughput performance" when serving Llama 70B on Hopper. Treat both as vendor claims. The academic numbers have the same problem. [Patel et al., 2023](https://arxiv.org/abs/2311.18677) say phase splitting can deliver "1.4x higher throughput at 20% lower cost than current designs," and separately "2.35x more throughput with the same cost and power budgets." Those are two points on one cost curve. One spends the gain on cheaper hardware and the other on more tokens from the same machines, so a team that reads only the 2.35 buys a different cluster than one that reads only the 1.4. I would require every multiplier to come with its baseline, its SLO and its unit. The NVIDIA product page labels the 30x as tokens per second per GPU, while the blog calls it requests served, which is exactly the habit that needs to end.

```chart
title: Reported disaggregation gains (headline multipliers)
unit: x
source: Patel et al., 2023; Zhong et al., 2024; NVIDIA, 2025
Splitwise, lower cost: 1.4
Splitwise, same cost: 2.35
DistServe, more requests: 7.4
Dynamo, requests (vendor): 30
note: Different workloads, hardware and metrics, so the bars are not comparable.
```

The chart is the thing I would not show without its note. Each bar is a best case from a different setup, and the Dynamo bar is a vendor's best case on the newest hardware. Read side by side, the bars suggest a ranking that the sources never measured. The honest version of a headline names the workload, the latency target and the cost per token, and most published tables give only the first two.

Prefill and decode can share one GPU for years without anyone asking what crosses between them. Once they run on separate machines, every request's cache has to cross the gap, and in most architecture diagrams that arrow is the thinnest line on the page. I would start every architecture review by asking how many bytes that arrow carries per request.

```video
youtube: Bh-jlh5vlF0
title: DistServe: Disaggregating Prefill and Decoding for Goodput-optimized LLM Inference (PyTorch Foundation)
caption: The DistServe authors on goodput under latency targets and why the two phases want separate resources.
```

## References

1. Leviathan et al. (2023). Fast Inference from Transformers via Speculative Decoding. arXiv. https://arxiv.org/abs/2211.17192
2. Zhong et al. (2024). DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving. arXiv. https://arxiv.org/abs/2401.09670
3. Kwon et al. (2023). Efficient Memory Management for Large Language Model Serving with PagedAttention. arXiv. https://arxiv.org/abs/2309.06180
4. Qin et al. (2024). Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving. arXiv. https://arxiv.org/abs/2407.00079
5. DeepSeek-AI (2024). DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model. arXiv. https://arxiv.org/abs/2405.04434
6. Patel et al. (2023). Splitwise: Efficient generative LLM inference using phase splitting. arXiv. https://arxiv.org/abs/2311.18677
7. NVIDIA (2025). Introducing NVIDIA Dynamo, A Low-Latency Distributed Inference Framework for Scaling Reasoning AI Models. NVIDIA Developer Blog. https://developer.nvidia.com/blog/introducing-nvidia-dynamo-a-low-latency-distributed-inference-framework-for-scaling-reasoning-ai-models/
