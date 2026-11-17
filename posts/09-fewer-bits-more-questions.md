---
title: Quantized models need task tests, not just perplexity
summary: A quantized model should earn release on the tasks it must do, and perplexity is too coarse to grant that.
tags: inference, verification
kind: opinion
date: 2026-10-15
---

If perplexity barely moves after quantization, I don't think that tells you the model is fine. It tells you the model changed. Whether the change matters depends on the jobs you deployed it for, and perplexity averages over a corpus that probably contains none of them. Teams lean on a small perplexity delta as a clean bill of health, and I think that habit is the weakest link in most quantization decisions.

Quantization is attractive for a simple reason. A weight stored in 16 bits takes twice the space of one stored in 8, and during decode the GPU reads the weights for every token it produces. Fewer bytes means less memory traffic in the memory-bound phase, which is the hard part of serving. The byte count is the easy half. The rounding is the harder half, and the account I would start from is [Dettmers et al., 2022](https://arxiv.org/abs/2208.07339). Their LLM.int8 work reports that it can "cut the memory needed for inference by half while retaining full precision performance." The reason it works is a small set of "highly systematic emergent features" in transformer language models. A few dimensions carry values far larger than the rest, and scaling a whole matrix to fit them destroys precision in the ordinary values. LLM.int8 isolates those dimensions and computes them in 16 bits, so a model described as 8-bit is partly 16-bit. I don't think that is a scandal. The label names the format of most of the arithmetic and says nothing about which values were left alone, and those are where the damage would concentrate.

Weight-only methods make a different trade. [Frantar et al., 2022](https://arxiv.org/abs/2210.17323) describe GPTQ as a post-training method that rounds the weights one layer at a time and adjusts the rest of the layer to absorb each rounding error. They report that a 175-billion-parameter model can be quantized in "approximately four GPU hours," with end-to-end speedups over FP16 of "around 3.25x" on an A100 and "4.5x" on an A6000. Same method, same model, two GPUs, and the speedup moves by about a third. I read that as a warning. A speedup belongs to a stack of format, kernels and card, and a single number in an abstract hides the stack. [Lin et al., 2023](https://arxiv.org/abs/2306.00978) argue that "protecting only 1% salient weights can greatly reduce quantization error," and their TinyChat runtime is reported at "more than 3x speedup over the Huggingface FP16 implementation." That baseline tells you how much faster this runtime is than one particular FP16 implementation. It says little about how close either one is to what the hardware allows. [Xiao et al., 2022](https://arxiv.org/abs/2211.10438) report "up to 1.56x speedup and 2x memory reduction" with "negligible loss in accuracy." Both hedges matter. "Up to" marks the best case, and "negligible" is judged on the accuracy benchmarks the authors chose.

The bars below come from different methods, models and GPUs, so read them with the note underneath.

```chart
title: Reported speedups over FP16 (quantized inference)
unit: x
source: Frantar et al., 2022; Xiao et al., 2022; Lin et al., 2023
GPTQ, A100: 3.25
GPTQ, A6000: 4.5
SmoothQuant, best case: 1.56
AWQ TinyChat, more than: 3
note: Different methods, models and GPUs; only the two GPTQ bars share a method.
```

The most informative pair in that chart is the two GPTQ bars. The same method moved from 3.25 to 4.5 across two cards, and that gap is the number a release note should report as a range.

The more interesting results do not quantize after the fact. [Ma et al., 2024](https://arxiv.org/abs/2402.17764) train models whose weights are ternary, with "every single parameter (or weight) of the LLM" taking a value in {-1, 0, 1}, and report that the model "matches the full-precision (i.e., FP16 or BF16) Transformer LLM with the same model size and training tokens." The question becomes whether low precision is a viable place to train at all. Block formats push the same question into hardware. NVIDIA describes NVFP4 as storing "one 4-bit value plus minor overhead of one FP8 scale per 16 values (4.5 bits per value)," and reports a footprint about 3.5x smaller than FP16. That is a vendor claim. [Abecassis et al., 2025](https://arxiv.org/abs/2509.25149) train a 12-billion-parameter model on 10 trillion tokens and report "training loss and downstream task accuracies comparable to an FP8 baseline." That is good evidence at one scale and one recipe. The detail I would watch is block size: 16 values here against 32 in the [MX formats described by Rouhani et al., 2023](https://arxiv.org/abs/2310.10537).

Now the argument I came to make. Perplexity averages how well a model predicts each next token. A quantization error can be small per token and still change the few tokens that decide a task: a digit in an arithmetic answer, a bracket that closes a function, a field name in a tool call. Take two quantized variants with the same corpus perplexity, where one emits a malformed tool call in a small share of runs. The average cannot separate them, because the failure is rare enough to vanish into it. That is a thought experiment, and I'd bet it describes real releases.

```diagram
title: Same build, two readings
caption: The average barely moves while a tool call breaks, so the same build gets two readings that disagree.
<svg viewBox="0 0 640 176" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="24" width="290" height="110" rx="6" class="box good"/>
  <text x="165" y="58" text-anchor="middle" class="lbl">Perplexity moves a little</text>
  <text x="165" y="82" text-anchor="middle" class="sub">averaged over a general corpus</text>
  <text x="165" y="102" text-anchor="middle" class="sub">reads as a clean bill of health</text>
  <rect x="330" y="24" width="290" height="110" rx="6" class="box bad"/>
  <text x="475" y="58" text-anchor="middle" class="lbl">A tool call breaks</text>
  <text x="475" y="82" text-anchor="middle" class="sub">a rare failure, lost in the average</text>
  <text x="475" y="102" text-anchor="middle" class="sub">the deployed agent stops working</text>
  <text x="320" y="162" text-anchor="middle" class="sub">Both readings describe the same quantized build.</text>
</svg>
```

So I think quantization is a verification problem before it is an engineering one. A quantized deployment makes an equivalence claim: on the tasks that matter, it behaves like the original. Checking that claim needs an oracle, and the full-precision model is the natural one. It needs a task suite whose failures you care about, run on the exact kernels and hardware you will ship, because the GPTQ pair already shows that speed does not transfer. Perplexity still earns a place as a cheap signal that something moved. It is a poor release gate, because it says the model changed and says nothing about whether it still works.

Here is what I'd build, in three pieces. The first is a quantization canary suite: a few hundred tool calls, structured outputs, long-context lookups and arithmetic problems that every quantized build must pass before it ships. These categories are where rare errors become visible. A malformed field or a wrong digit does little to perplexity and a lot to a deployed agent. The suite should also be run against a deliberately damaged quantization, such as one with a bad scale or a truncated outlier path, so the team knows the suite catches the failure it exists to catch. It can fail in two ways. The team can tune the quantization recipe until the suite passes, which turns the canaries into a target, and the suite goes stale as the product's prompts change. I'd rotate some canaries every release and keep a held-out set that nobody tunes against. What would convince me is simple: the suite flags variants that pass perplexity, and a product owner agrees the flagged outputs are real defects.

The second piece is a differential test against the full-precision model on the same prompts. The full-precision model is the oracle, and divergence localizes the problem to specific prompts, which a corpus average cannot do. The obvious failure is noise. Under sampling, two faithful models will diverge on exact tokens, so the comparison should use greedy decoding or compare task outcomes instead of strings. The full-precision model is sometimes wrong too, so a divergence is not automatically a regression. I would flag divergence where a rater judges the quantized output worse, not merely different. I would keep this piece only if its divergence rate on product prompts tracks the canary failures.

The third piece is organizational. I'd treat FP4 and NVFP4 as release decisions with a named owner, not as compiler flags. The release note should state the task list, the GPU, the kernel path and the baseline the speed was timed against, because the GPTQ result shows those four things move the speedup. The failure here is bureaucratic. A sign-off step that nobody reads gets rubber-stamped, and teams then avoid low precision altogether. I would judge the process by whether a release has ever been held back. If none has, the gate is decoration.

```diagram
title: Release gate for a quantized model
caption: Both models run the same canary suite, the outputs are diffed on each task, and only a clean diff ships.
<svg viewBox="0 0 640 300" xmlns="http://www.w3.org/2000/svg">
  <g class="step1">
    <rect x="20" y="36" width="230" height="44" rx="6" class="box"/>
    <text x="135" y="56" text-anchor="middle" class="lbl">FP16 model</text>
    <text x="135" y="72" text-anchor="middle" class="sub">the oracle</text>
    <rect x="390" y="36" width="230" height="44" rx="6" class="box hi"/>
    <text x="505" y="56" text-anchor="middle" class="lbl">FP4 model</text>
    <text x="505" y="72" text-anchor="middle" class="sub">the candidate</text>
  </g>
  <g class="step2">
    <path d="M135 80 V110" class="edge" marker-end="url(#arr)"/>
    <path d="M505 80 V110" class="edge" marker-end="url(#arr)"/>
    <rect x="20" y="110" width="600" height="44" rx="6" class="box"/>
    <text x="320" y="136" text-anchor="middle" class="lbl">Canary suite: tool calls, JSON, long context, arithmetic</text>
  </g>
  <g class="step3">
    <path d="M320 154 V182" class="edge" marker-end="url(#arr)"/>
    <rect x="170" y="182" width="300" height="40" rx="6" class="box hi"/>
    <text x="320" y="207" text-anchor="middle" class="lbl">Diff the two outputs on each task</text>
  </g>
  <g class="step4">
    <path d="M270 222 L205 246" class="edge good" marker-end="url(#arr)"/>
    <path d="M370 222 L435 246" class="edge bad" marker-end="url(#arr)"/>
    <rect x="120" y="246" width="170" height="44" rx="6" class="box good"/>
    <text x="205" y="266" text-anchor="middle" class="lbl">Ship</text>
    <text x="205" y="282" text-anchor="middle" class="sub">no task regressed</text>
    <rect x="350" y="246" width="170" height="44" rx="6" class="box bad"/>
    <text x="435" y="266" text-anchor="middle" class="lbl">Hold</text>
    <text x="435" y="282" text-anchor="middle" class="sub">a task regressed</text>
  </g>
</svg>
```

The concession is that most of these methods do work. LLM.int8, GPTQ, AWQ and SmoothQuant have been used widely, and their abstracts make claims specific enough to test. My complaint is narrower. The reported numbers answer how much smaller and how much faster, and the release decision depends on a third question that the same papers answer only for their chosen benchmarks. The concession also changes the proposal. Canaries and a differential run cost real time, and a small team may only afford a small suite. I would rather ship a small suite that rotates honestly than a large one the team optimizes against.

So here is what I'd do with a release note that says "4-bit." Ask which tasks it was checked on and which GPU it was timed on. If the answer is one perplexity figure and one speedup, you have learned how large the file is and nothing about whether the model still works. A 4.5-bit weight is a smaller object than the one it replaced. Whether it is still the same model is a question for the canary suite, and I'd want its results printed beside the file size before anyone calls the release done.

```video
youtube: dcINVsqxQgQ
title: AWQ: Activation-aware Weight Quantization (MIT HAN Lab, MLSys 2024)
caption: The AWQ authors' talk on which weights matter most, which is the kind of claim a quantization canary suite should test.
```

## References

1. Dettmers, T. et al. (2022). LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale. arXiv. https://arxiv.org/abs/2208.07339
2. Frantar, E. et al. (2022). GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers. arXiv. https://arxiv.org/abs/2210.17323
3. Lin, J. et al. (2023). AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration. arXiv. https://arxiv.org/abs/2306.00978
4. Xiao, G. et al. (2022). SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models. arXiv. https://arxiv.org/abs/2211.10438
5. Ma, S. et al. (2024). The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits. arXiv. https://arxiv.org/abs/2402.17764
6. NVIDIA (2025). Introducing NVFP4 for Efficient and Accurate Low-Precision Inference. NVIDIA Developer Blog. https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/
7. Abecassis, F. et al. (2025). Pretraining Large Language Models with NVFP4. arXiv. https://arxiv.org/abs/2509.25149
8. Rouhani, B. D. et al. (2023). Microscaling Data Formats for Deep Learning. arXiv. https://arxiv.org/abs/2310.10537
