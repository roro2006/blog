---
title: The teacher that could see everything
summary: In robotics, the most useful teacher for distillation is often a privileged one that reads the simulator's state, and the hard part of transfer learning is what the student forgets and what the pipeline silently corrupts.
tags: robotics, training, verification
kind: opinion
date: 2026-11-07
---

Knowledge distillation is usually told as a story about size. A large model, the teacher, produces soft targets, and a small model, the student, learns to match them, so you keep most of the capability and pay for a fraction of the compute. [Hinton, Vinyals and Dean (2015)](https://arxiv.org/abs/1503.02531) gave that story its modern form, and it still describes most of what gets called distillation in language models. I think robotics needs a different version of it. In the robot work I have been doing, the teacher that mattered most was not bigger than the student. It was a short scripted program that could read the simulator's exact state, and the student was a vision-language-action model that could only see pixels. The question that kept coming up was not how much the student could compress. It was where the student went once it stopped following the teacher's path, and whether the signal from the teacher reached it intact.

The project is [Perspective](https://github.com/roro2006/Perspective), which I call Curio in the code. It is a robot that fuses a co-worker's first-person view with its own cameras, so it can resolve "the red one on my left" from the person's side of the table and pick up blocks it cannot see itself. Everything below runs in MuJoCo with a simulated SO-101 arm and scripted demonstrations. None of it has touched real people or real hardware yet, and some of the experiments in the later sections are not pushed to the repository.

The system has two learned parts, and they map onto the two halves of this essay. A grounder decides which block the person means. It is a LoRA adapter on Qwen3-VL-4B, which is transfer learning in the plain sense: take a foundation model and fit it to a narrow job. A policy then picks the block up. It is SmolVLA fine-tuned on demonstrations from a scripted expert, which is distillation, even though nobody would call a forty-line pick script a teacher model.

The grounder is the success story, and it shows what transfer buys. On the project's 350-item benchmark, the second adapter, given Curio's geometry, scores 0.92 overall. A keyword rule scores 0.77, and the same base model asked to work out perspective from both camera views on its own scores 0.78. On phrasings the adapter never trained on, it scores 0.80 against the first adapter's 0.56. Latency stayed at about 110 ms. Those are the numbers in the repo's own summary, and they make the usual case for fine-tuning a foundation model: the base model already knows what "left" and "nearest" mean, so a small adapter only has to learn which frame of reference the person is using.

```chart
title: Grounding accuracy on the Curio benchmark
source: Perspective, docs/target5-summary.md (350 items, simulation)
Keyword rule: 0.77
Base VLM, both views, no geometry: 0.78
LoRA v2 with Curio geometry: 0.92
```

The same adapter also lost something. Requests like "that one," which rely on where the person is looking, fell from 0.55 to 0.45 on the held-out deictic set in the second adapter. The cause is visible in the data recipe. The v2 training mix was weighted toward free wording and hidden objects, with 600 deictic rows added so that "that one" would not be dropped entirely, and 600 was not enough. [Biderman et al. (2024)](https://arxiv.org/abs/2405.09673) found that LoRA "learns less and forgets less" than full fine-tuning, and that it maintains the base model's performance outside the target domain better than weight decay or dropout do. My regression is not a contradiction of that result. The behavior that was lost was not the base model's. It was the first adapter's, learned in an earlier round of the same narrow training, and low rank protects the pretrained weights, not the previous fine-tune.

```chart
title: What the second grounding adapter gained and lost
source: Perspective, tasks/notes/T5-06.md and docs/target5-summary.md
Unseen phrasing, adapter v1: 0.56
Unseen phrasing, adapter v2: 0.80
"That one", adapter v1: 0.55
"That one", adapter v2: 0.45
```

The obvious fix is more deictic rows and a retrain, and that is on the list. The more interesting fix comes from a result by Kevin Lu at [Thinking Machines (2025)](https://thinkingmachines.ai/blog/on-policy-distillation/). In on-policy distillation, the student samples its own outputs and a teacher grades every token, with a per-token reverse KL as the loss. Lu's post includes a forgetting experiment. Mid-training Qwen3-8B on internal documents raised an internal QA score but dropped instruction following on IF-eval from 85% to 79%. A short round of on-policy distillation, with the earlier Qwen3-8B as teacher, brought IF-eval back to 83% while keeping the new knowledge. Fine-tuning on the model's own samples could not do this at any practical learning rate. The earlier model is a free teacher for the skill you broke.

I tried the same move on the grounder. I used adapter v1 as the teacher on deictic prompts only, let v2 answer them, and trained v2 toward v1's distribution over the answer letter, while keeping v2's own training objective on the rest of the mix. The deictic rows were mixed one to three with v2's original training rows, for about 200 steps at the v2 learning rate. Because the grounder answers with a single letter token, the per-token reverse KL is just the KL between two small categorical distributions, which makes this the cheapest possible version of the technique. "That one" moved from 0.45 to 0.53, and unseen phrasing went from 0.80 to 0.79. That recovered most of the regression for a point of new phrasing, a trade I would make again.

The policy is where the teacher changes character. Curio's scripted expert picks 99.6% of blocks in open scenes and 87% of blocks hidden behind a box. It can do that because it reads the block's true position from the simulator. SmolVLA, the student, gets the robot's camera, the wrist camera, and a ring drawn on the target pixel, which is how the grounder tells it which block to take. This is the arrangement that [Chen et al. (2019)](https://arxiv.org/abs/1912.12294) called "learning by cheating" for driving: first train a privileged agent that sees the ground-truth state, then use it to supervise a sensorimotor agent that only sees what a real one would. The teacher's advantage is information. [SmolVLA (Shukor et al., 2025)](https://arxiv.org/abs/2506.01844) is a 450M-parameter model with an action expert of about 100M, and in my fine-tunes the vision-language backbone stayed frozen, leaving 99.9M trainable parameters. The student is small because reading a ring and closing a gripper should not need more, and distillation had nothing to do with it.

What went wrong is the classic failure of copying a teacher's demonstrations. End to end, with the v2 grounder choosing the block and SmolVLA picking it, target picks rose across five training runs from 0.14 to 0.42, 0.46, 0.515 and 0.57. The grounder was never the limit: the policy picked the wrong block only 1 to 2% of the time, and its success stayed within a point of the true-target ring in every run. Every run from the second on missed its pre-registered gate. The most common miss, in a 30-scene diagnosis, was the gripper closing 2 to 3 cm too high with a jaw resting on the block, and the policy seldom rose to try again. That state never appears in the expert's demonstrations, because the expert never makes that mistake. Behavior cloning trains the student only on states the teacher visits, so the student has no data for the states its own errors create. [Ross, Gordon and Bagnell (2011)](https://arxiv.org/abs/1011.0686) showed that the errors compound along the trajectory, and proposed DAgger: run the student, ask the expert what it would do in the states the student reached, and add those labels to the data.

```diagram
title: Copying the expert versus asking it
style: manim
caption: Off-policy, the student only learns states the expert visits, so its own mistakes lead somewhere with no labels. On-policy, the student's states are sent back to the expert, which can label any of them because it reads the simulator.
source: Perspective, docs/target5-summary.md; Ross et al. (2011); Chen et al. (2019)
<svg viewBox="0 0 640 252" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="24" class="lbl t-yellow fade d1">Off-policy: learn from the expert's demos</text>
  <rect x="20" y="38" width="170" height="58" rx="6" class="node c-blue fade d1"/>
  <text x="105" y="62" text-anchor="middle" class="lbl fade d1">Scripted expert</text>
  <text x="105" y="82" text-anchor="middle" class="sub fade d1">reads the sim state</text>
  <line x1="192" y1="67" x2="233" y2="67" pathLength="1" class="edge c-muted draw d2"/>
  <rect x="235" y="38" width="170" height="58" rx="6" class="node c-blue fade d2"/>
  <text x="320" y="62" text-anchor="middle" class="lbl fade d2">SmolVLA student</text>
  <text x="320" y="82" text-anchor="middle" class="sub fade d2">reads pixels and a ring</text>
  <line x1="407" y1="67" x2="448" y2="67" pathLength="1" class="edge c-muted draw d3"/>
  <rect x="450" y="38" width="170" height="58" rx="6" class="node c-red fade d4"/>
  <text x="535" y="62" text-anchor="middle" class="lbl t-red fade d4">A state off the demos</text>
  <text x="535" y="82" text-anchor="middle" class="sub fade d4">jaw on block, 2 cm high</text>
  <text x="20" y="134" class="lbl t-green fade d5">On-policy: the expert labels the student's own states</text>
  <rect x="20" y="148" width="170" height="58" rx="6" class="node c-green fade d6"/>
  <text x="105" y="172" text-anchor="middle" class="lbl fade d6">Student rollout</text>
  <text x="105" y="192" text-anchor="middle" class="sub fade d6">in the simulator</text>
  <line x1="192" y1="177" x2="233" y2="177" pathLength="1" class="edge c-green draw d7"/>
  <rect x="235" y="148" width="170" height="58" rx="6" class="node c-green fade d7"/>
  <text x="320" y="172" text-anchor="middle" class="lbl fade d7">States it reaches</text>
  <text x="320" y="192" text-anchor="middle" class="sub fade d7">including its mistakes</text>
  <line x1="407" y1="177" x2="448" y2="177" pathLength="1" class="edge c-green draw d8"/>
  <rect x="450" y="148" width="170" height="58" rx="6" class="node c-green fade d8"/>
  <text x="535" y="172" text-anchor="middle" class="lbl fade d8">Expert labels each</text>
  <text x="535" y="192" text-anchor="middle" class="sub fade d8">from the true state</text>
  <path d="M535 208 V236 H105 V208" pathLength="1" class="edge c-green draw d9"/>
</svg>
```

A privileged teacher makes DAgger unusually cheap, and this is the point I would most like other robot builders to take from the project. A human expert gets tired of being asked what they would do in a state they would never have reached. A scripted expert in simulation does not tire, and since it reads the true state it can label any frame the student produces, including the awkward ones. The language-model world has rediscovered the same idea as on-policy distillation, and by late 2026 papers were applying it to flow-based robot policies. [Ni et al. (2026)](https://arxiv.org/abs/2610.21522) distill several frozen specialist policies into one student that keeps collecting fresh experience, and their best variant supervises the teacher's velocity field along the student's own generated flow trajectories. They report absolute success gains over the starting point of 22.55 points on LIBERO-40, 33.4 on five-instruction CALVIN sequences and 22.6 on Meta-World MT50, with larger gains on longer sequences.

SmolVLA predicts action chunks with flow matching, so the label from my expert is an action chunk, not a token distribution. I ran three rounds of DAgger-style relabelling, with the unpinned loader described below. Each round rolled out the current SmolVLA checkpoint on 100 training scenes, recorded every state it reached, asked the scripted expert for the chunk it would execute from each one, and fine-tuned on the union of the old demonstrations and the new labels. I did not try the velocity-loss variant. Target picks went from 0.57 to 0.66 on the same 100 evaluation scenes, and in a fresh 30-scene diagnosis the high close accounted for 2 of 10 misses, down from 6 of 14. That cleared the 0.60 gate, the first run since the second to clear its pre-registered bar. The part I did not expect was the new leading miss: the student learned to commit to the close earlier and lower, and started nudging the block off its ringed position on the way in.

Transfer has a second failure mode that has nothing to do with what the student learns. Alongside SmolVLA, I also tried pi0 ([Black et al., 2024](https://arxiv.org/abs/2410.24164)), Physical Intelligence's VLA, through LeRobot. I fine-tuned only its action expert, 578M trainable parameters, on 800 relabelled demonstrations, and left the PaliGemma backbone frozen. Freezing the backbone was a cheap approximation of an idea from [Driess et al. (2025)](https://arxiv.org/abs/2505.23705) at Physical Intelligence, who found that bolting a continuous action expert onto a pretrained VLM can damage the backbone's knowledge and slow training. Their fix is to stop the gradient from the action expert to the backbone, while training the backbone on discrete actions so it still carries action information. Mine stopped everything, which is cruder, but it keeps the backbone exactly as it arrived.

Training looked perfect. Loss fell to about 0.001 over 22,000 steps. At test time pi0 lifted no block in any of 300 rollouts. The checkpoint predicted joint targets near zero even on training frames, and the arm sagged toward its rest pose. Held-out loss had been the warning all along: 1.18 at step 2,000, then 0.71, then wandering between 0.96 and 1.43 until the end, while the training loss sat at 0.001. The root cause, found in a later pass, was a host-to-GPU copy race in the data loader. Batches used pinned memory, and the copy to the GPU ran asynchronously while the previous step was still computing, so the normalizer often saw an action chunk that did not belong to the current batch. In an exact rerun, 5 of 8 checked steps scored a different loss on the same batch once it was re-read after a synchronize. pi0 had learned from corrupted targets and logged a beautiful curve while doing it.

```chart
title: pi0 held-out loss, before and after the loader fix
source: Perspective, tasks/notes/T5-28.md and T5-30.md
Before fix, step 2,000: 1.18
After fix, step 2,000: 0.106
Before fix, step 4,000: 0.71
After fix, step 4,000: 0.093
note: The logged training loss before the fix was about 0.001, which is why it looked healthy.
```

This is a distillation failure in the most literal sense. The teacher's labels were correct, and the student never received them. With pin_memory turned off, the loader corrupted 0 of 60 checked steps, and the retrain's held-out loss fell to 0.106 at 2,000 steps and 0.076 at 8,000. The rule I took from it now lives in a check script in the repo: before trusting a checkpoint, reproduce its logged loss from the saved weights on a known batch. If the number does not come back, nothing else about the run is evidence. The same note records an open worry. The SmolVLA training script also used pinned memory, so runs 2 to 5 may have learned from partly corrupted actions too. The race check found corrupted action chunks on 4 of 40 checked steps in the run 5 configuration, far fewer than pi0's 5 of 8, and retraining run 5's recipe with the unpinned loader moved target picks from 0.57 to 0.60, which is inside the noise.

The third kind of transfer I tried is the one people mean when they say a policy "transfers": take a network trained somewhere else and run it here. I ported a Unitree Go2 navigation policy trained in NVIDIA Isaac Lab, published by kouylty under an MIT license, into numpy and MuJoCo. The port was exact in the narrow sense. The numpy network matched the TorchScript original to within 7.6e-6 on the walking policy and 1.9e-6 on the navigation policy. The behavior did not transfer. The dog reached within 0.3 m of the goal on 18 of 20 trials, then fell on 13 of them, because the policy could not stop. Its raw actions exceeded the walker's range on 97 to 99% of steps, so near the goal it flipped between extremes five times a second. Its own training statistics explained why: it had almost never been asked to stand still. The network came across intact and its competence did not, because the competence lived in the distribution it was trained on, and that distribution had no "arrive and stop."

Compression in the usual sense is the last piece, and the field moved fast on it in 2026. [Shi et al. (2026)](https://arxiv.org/abs/2605.16241) distill OpenVLA-7B into a 158M-parameter student, a 44x reduction, using a VLM only offline as a semantic supervisor. They report a 0.27% average relative gap to the teacher across three LIBERO suites and a 3.28x inference speedup. With pi0.5 as the teacher, their student outperforms it on two suites. For Curio, the target is the grounder. At 110 ms it is fast enough for a demo, but the live runtime starts the arm moving on a partial transcript and lets the grounder confirm or redirect mid-motion, so every millisecond the grounder saves is motion that does not need correcting. I distilled the LoRA v2 grounder into Qwen3-VL-2B-Instruct with its own LoRA, using its answer-letter distributions on 6,000 generated scenes as soft targets. The student scores 0.88 overall and 0.72 on unseen phrasing at a p50 of 64 ms, and the place it loses accuracy is distance phrasings such as "the one that is harder for me to reach," where the larger model seems to need its extra capacity.

Put the three projects side by side and the shape of the problem changes. The size story about distillation assumes the teacher's knowledge is a fixed thing, and the only question is how compactly a student can hold it. In robotics the teacher's knowledge is tied to states. A scripted expert knows what to do from the states it reaches. A navigation policy knows what to do from the states its simulator produced. A fine-tuned adapter knows the phrasings and gestures its data mix happened to contain. Each of my failures was a student meeting a state its teacher had never been asked about: a gripper resting on a block, a dog that has already arrived, a person pointing. The gains came from asking the teacher about the student's states, or, in the pi0 case, from checking that the teacher's answers arrived at all.

Two cautions belong next to that. Everything here is simulation, and a privileged teacher only exists where the state is known. On a real bench nobody hands the policy the block's position, so the cheap version of DAgger becomes an expensive one, with a person teleoperating corrections. And on-policy distillation inherits the teacher's limits along with its knowledge. Lu's post calls reverse KL mode-seeking, and a student that copies a scripted expert exactly will also copy its habit of never needing to recover, because the expert never fails in the first place. For grasping in particular, I suspect the next gain comes from a teacher that knows how to recover from a bad close, not one that never makes one. Run 5 added scripted recovery demonstrations and gained 0.07 in target picks, within about 1.5 standard errors, so the hint is there but the result is not yet.

The habit I would keep from all of this is small. Before training a student on a teacher, write down which states the teacher was ever asked about. Then run the student and count how many of the states it reaches are on that list.

## References

1. Hinton, G., Vinyals, O. and Dean, J. (2015). Distilling the Knowledge in a Neural Network. arXiv. https://arxiv.org/abs/1503.02531
2. Ross, S., Gordon, G. and Bagnell, J. A. (2011). A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning. AISTATS. https://arxiv.org/abs/1011.0686
3. Chen, D., Zhou, B., Koltun, V. and Krähenbühl, P. (2019). Learning by Cheating. CoRL. https://arxiv.org/abs/1912.12294
4. Biderman, D. et al. (2024). LoRA Learns Less and Forgets Less. TMLR. https://arxiv.org/abs/2405.09673
5. Lu, K. and Thinking Machines (2025). On-Policy Distillation. https://thinkingmachines.ai/blog/on-policy-distillation/
6. Black, K. et al. (2024). π0: A Vision-Language-Action Flow Model for General Robot Control. arXiv. https://arxiv.org/abs/2410.24164
7. Shukor, M. et al. (2025). SmolVLA: A Vision-Language-Action Model for Affordable and Efficient Robotics. arXiv. https://arxiv.org/abs/2506.01844
8. Driess, D. et al. (2025). Knowledge Insulating Vision-Language-Action Models: Train Fast, Run Fast, Generalize Better. NeurIPS. https://arxiv.org/abs/2505.23705
9. Ni, L. et al. (2026). Multi-Teacher On-Policy Distillation for Flow-Based Vision-Language-Action Models. arXiv. https://arxiv.org/abs/2610.21522
10. Shi, J. et al. (2026). Offline Semantic Guidance for Efficient Vision-Language-Action Policy Distillation. arXiv. https://arxiv.org/abs/2605.16241
11. Reddy, R. (2026). Perspective (Curio). GitHub. https://github.com/roro2006/Perspective
12. kouylty (n.d.). Isaac-Go2-Navigation-Rough-v0. Hugging Face. https://huggingface.co/kouylty/Isaac-Go2-Navigation-Rough-v0
