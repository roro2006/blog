---
title: Ezreal has no Flash
summary: The voice comms that won the 2026 League of Legends World Championship are a heap of banalities, and their banality is the most useful thing in them for anyone building agents that talk to each other.
tags: agents, verification
kind: essay
date: 2026-11-19
---

Transcribe the voice comms of the team that has just won the League of Legends World Championship and you expect to find strategy. What Bilibili Gaming published after beating Gen.G 3-1 at the Barclays Center on 14 November reads more like the radio log of a nervous bus depot. "Ezreal has no Flash." "Cho'Gath has no ult." "Vayne has TP in 15 seconds." "Slow down, slow down." By a rough count of the seventeen-minute fan-subtitled cut, about forty-five lines announce that some enemy has or lacks a summoner spell or an ultimate, and about forty more ask a teammate to slow down, wait, or stop rushing. Against that background there is one genuinely clever remark about the opponent's fears, the support announcing that he needs to meditate, and a coach wondering aloud whether Twisted Fate is unbeatable. As literature, the recording is unbearable. As a record of five people keeping a single picture of a map in five separate heads, it is one of the more instructive documents about multi-agent systems published this year.

That lesson runs against the grain of how agents are currently built. The prevailing advice is to give agents more of each other: share full traces instead of summaries, as Walden Yan argued for Cognition in 2025, pool the context, let a crowd of workers read one common store. The plumbing has matured to match. Google's Agent2Agent protocol reached a stable release in 2026 and had more than 150 organizations behind it by its first birthday, so an agent built by one company can hand a task to an agent built by another, while the Model Context Protocol connects agents to their tools. These protocols standardize the envelope. They say nothing about what should go inside it, and that is where BLG did its repair work.

BLG learned its tedious grammar from a loss. On 29 October, after a Swiss-stage loss to Top Esports that nearly ended its tournament, the ADC Viper told Inven that the team's communication was "worse than having none at all." He gave the mechanism with unusual precision: "Players were just blurting out whatever they wanted to say." In one bot-lane fight, according to Strafe's report of that interview, a teammate called that the enemy Pantheon had no ultimate. Pantheon then used it to dive into the fight, and BLG lost badly.

Viper's complaint was about what the team said. A silent team at least plays on what each player can see for himself. A team that broadcasts a confident falsehood has four players acting on a fact none of them checked. The claim now has a laboratory version. In a benchmark posted in September 2026, Li and colleagues studied what happens when agents share a memory, and found that once an uncontested false belief enters that memory, the agents that consume it assert it in 97 to 99 percent of probes, across every agent family they tested. They name the root confusion plainly: "repeated claims may be mistaken for independent evidence." The Pantheon call is that result played at the speed of a teamfight: one voice, four listeners, and no one who had looked.

The old legal rule that a matter shall be established at the mouth of two or three witnesses assumed that each witness had seen the thing. A rumor repeated by three mouths is one witness and two echoes, and the echo usually sounds more confident than the witness. Li's team found that admission policies without access to where a claim came from could not reliably keep false claims out, while policies that checked the declared source cut false adoption to between 6 and 9 percent.

```diagram
title: One voice, four echoes
style: manim
caption: Left, the October call: one unchecked claim, adopted by every listener. Right, Game 2: a wrong claim meets a player who looked, and the listeners take the witness.
source: Strafe and Inven on BLG's Swiss loss to Top Esports; BLG voice comms, Game 2
<svg viewBox="0 0 640 300" xmlns="http://www.w3.org/2000/svg">
  <text x="165" y="24" text-anchor="middle" class="lbl t-red fade d1">October: one voice, four echoes</text>
  <circle cx="70" cy="150" r="18" class="node c-red fade d1"/>
  <text x="70" y="118" text-anchor="middle" class="sub t-red fade d1">"no ult"</text>
  <text x="70" y="195" text-anchor="middle" class="sub fade d1">one call</text>
  <line x1="88" y1="150" x2="236" y2="60" pathLength="1" class="edge c-red w3 draw d2"/>
  <line x1="88" y1="150" x2="236" y2="120" pathLength="1" class="edge c-red w3 draw d2"/>
  <line x1="88" y1="150" x2="236" y2="180" pathLength="1" class="edge c-red w3 draw d2"/>
  <line x1="88" y1="150" x2="236" y2="240" pathLength="1" class="edge c-red w3 draw d2"/>
  <circle cx="250" cy="60" r="14" class="node fade d1"/>
  <circle cx="250" cy="60" r="14" class="f-red fade d4"/>
  <circle cx="250" cy="120" r="14" class="node fade d1"/>
  <circle cx="250" cy="120" r="14" class="f-red fade d4"/>
  <circle cx="250" cy="180" r="14" class="node fade d1"/>
  <circle cx="250" cy="180" r="14" class="f-red fade d4"/>
  <circle cx="250" cy="240" r="14" class="node fade d1"/>
  <circle cx="250" cy="240" r="14" class="f-red fade d4"/>
  <text x="165" y="285" text-anchor="middle" class="sub fade d5">four players act on a fact nobody checked</text>
  <line x1="320" y1="44" x2="320" y2="262" class="edge c-muted faint"/>
  <text x="480" y="24" text-anchor="middle" class="lbl t-green fade d6">Game 2: a claim, then a witness</text>
  <circle cx="380" cy="105" r="18" class="node c-yellow fade d6"/>
  <text x="380" y="74" text-anchor="middle" class="sub t-yellow fade d6">"no Flash"</text>
  <circle cx="380" cy="205" r="18" class="node c-green fade d8"/>
  <text x="380" y="246" text-anchor="middle" class="sub t-green fade d8">"he has it"</text>
  <text x="380" y="262" text-anchor="middle" class="sub fade d8">(he saw it)</text>
  <line x1="398" y1="105" x2="561" y2="95" pathLength="1" class="edge c-yellow faint draw d7"/>
  <line x1="398" y1="105" x2="561" y2="155" pathLength="1" class="edge c-yellow faint draw d7"/>
  <line x1="398" y1="105" x2="561" y2="215" pathLength="1" class="edge c-yellow faint draw d7"/>
  <line x1="398" y1="205" x2="561" y2="95" pathLength="1" class="edge c-green w3 draw d9"/>
  <line x1="398" y1="205" x2="561" y2="155" pathLength="1" class="edge c-green w3 draw d9"/>
  <line x1="398" y1="205" x2="561" y2="215" pathLength="1" class="edge c-green w3 draw d9"/>
  <circle cx="575" cy="95" r="14" class="node fade d6"/>
  <circle cx="575" cy="95" r="14" class="f-green fade d10"/>
  <circle cx="575" cy="155" r="14" class="node fade d6"/>
  <circle cx="575" cy="155" r="14" class="f-green fade d10"/>
  <circle cx="575" cy="215" r="14" class="node fade d6"/>
  <circle cx="575" cy="215" r="14" class="f-green fade d10"/>
  <text x="480" y="285" text-anchor="middle" class="sub fade d11">the witness outweighs the repeat</text>
</svg>
```

The 2025 taxonomy of multi-agent failures by Cemri and colleagues, built from more than 1,600 annotated traces across seven frameworks, has a whole category for inter-agent misalignment, with modes such as withholding information and failing to ask for clarification. BLG in October had the second problem without the first. Its players talked plenty and, by Viper's account, listened little.

The interesting part of the published comms begins in the break after Game 1, which Gen.G won 19 to 4. What follows is what software engineers would call a blameless postmortem, compressed into the time it takes to walk off stage, and it contains no new strategy at all. The support, ON, confesses the failure in the plainest terms available. On a top-side gank against Chovy's Syndra, "I didn't even know if she had Flash," and later, "I thought he had Flash, you know." Knight answers: "It's fine, call it next time." Then the rules arrive, one per speaker. ON: "Call it when they burn Flash." Viper: "If you don't know mid-fight, just ask." Knight: "Then ask me if he has Flash."

```image
src: comms-everyone-can-ask.jpg
alt: BLG's five players at the stage booth between games, with the fan subtitle "Viper: Everyone can ask"
title: The rule, as it was made.
caption: Between Games 1 and 2, Viper turns ON's admission into a team rule. The subtitle is the uploader's translation of the Chinese caption below it.
source: BLG Esports Club footage, English subtitles by LPL Translations (YouTube, aov01aa-Q4k)
```

What they wrote, in effect, is a grammar. It has a noun for state (a champion and a resource: Flash, ultimate, Teleport), a rule that a speaker who knows something says it when it changes, and a rule that a speaker who does not know asks. Strategy is absent from it. Strategy had been settled in the draft, and the grammar exists so that strategy can be carried out on a map that all five players agree about.

```diagram
title: The grammar BLG used in Games 2 to 4
style: manim
caption: Five kinds of call, each with a line from the published comms. The ask, in yellow, is the rule added after Game 1.
source: BLG voice comms, Worlds 2026 final, fan-subtitled
<svg viewBox="0 0 640 300" xmlns="http://www.w3.org/2000/svg">
  <line x1="24" y1="28" x2="24" y2="62" pathLength="1" class="edge c-blue w4 draw d1"/>
  <text x="40" y="50" class="lbl t-blue fade d1">State</text>
  <text x="140" y="50" class="lbl fade d2">"Vayne has TP in 15 seconds"</text>
  <text x="630" y="50" text-anchor="end" class="sub fade d2">a fact with a clock on it</text>
  <line x1="40" y1="72" x2="630" y2="72" class="edge c-muted faint fade d2"/>
  <line x1="24" y1="83" x2="24" y2="117" pathLength="1" class="edge c-yellow w4 draw d3"/>
  <text x="40" y="105" class="lbl t-yellow fade d3">Ask</text>
  <text x="140" y="105" class="lbl fade d4">"Does Ezreal have Flash?"</text>
  <text x="630" y="105" text-anchor="end" class="sub fade d4">doubt said out loud</text>
  <line x1="40" y1="127" x2="630" y2="127" class="edge c-muted faint fade d4"/>
  <line x1="24" y1="138" x2="24" y2="172" pathLength="1" class="edge c-green w4 draw d5"/>
  <text x="40" y="160" class="lbl t-green fade d5">Correct</text>
  <text x="140" y="160" class="lbl fade d6">"No Flash" / "He has it"</text>
  <text x="630" y="160" text-anchor="end" class="sub fade d6">a claim contested</text>
  <line x1="40" y1="182" x2="630" y2="182" class="edge c-muted faint fade d6"/>
  <line x1="24" y1="193" x2="24" y2="227" pathLength="1" class="edge c-red w4 draw d7"/>
  <text x="40" y="215" class="lbl t-red fade d7">Concede</text>
  <text x="140" y="215" class="lbl fade d8">"Give drake, doesn't matter"</text>
  <text x="630" y="215" text-anchor="end" class="sub fade d8">a sub-goal given up</text>
  <line x1="40" y1="237" x2="630" y2="237" class="edge c-muted faint fade d8"/>
  <line x1="24" y1="248" x2="24" y2="282" pathLength="1" class="edge c-teal w4 draw d9"/>
  <text x="40" y="270" class="lbl t-teal fade d9">Hold</text>
  <text x="140" y="270" class="lbl fade d10">"Slow down, slow down"</text>
  <text x="630" y="270" text-anchor="end" class="sub fade d10">the plan, repeated</text>
</svg>
```

Aviation solved a version of this problem decades ago, and the solution is worth borrowing because it is so dull. A pilot who receives a clearance reads it back, and the controller listens to the readback, so that a misheard altitude is caught on the radio instead of on the ground. Nobody admires readback phraseology for its beauty. In Game 2, ON asks "Just burned, right?" about a Flash he has just seen go, which is close to a readback, with the difference that he is confirming something he saw rather than something he heard. Earlier in the same game, Xun calls "That guy has no Flash" and ON, who had looked, answers "He has it." The contradiction took about two seconds to settle. In October, by Viper's account, a call like that stood.

```image
src: comms-does-ezreal-have-flash.jpg
alt: Game 2 broadcast frame with the BLG comms overlay showing the fan subtitle "Bin: Does Ezreal have Flash?"
title: The rule, in use.
caption: Midway through Game 2, Bin asks instead of guessing. A team that had lost a fight to an unchecked call in October now treats doubt as information.
source: BLG Esports Club footage, English subtitles by LPL Translations (YouTube, aov01aa-Q4k)
```

This is the declared source, translated into speech. "He has it" is a report from someone who saw the Flash, and in a five-person system a report with a seen-by attached should outweigh any number of confident repetitions. The rule BLG adopted, ask when unsure and contradict when you have looked, resembles the policy that did best in Li's benchmark, and the players wrote theirs in about two minutes between games.

The obvious improvement would be to make the comms smarter. Let each player narrate intentions as well as facts: where they are walking and why, what they expect the enemy jungler to do, how confident they feel about the next fight. That is roughly what "share full traces" means for agents, and for some tasks it is right. Try it on a teamfight, though, and what happens to the one sentence that matters? Chroma's 2025 study of what its authors called context rot tested eighteen models and found that "even a single distractor reduces performance" relative to a clean baseline. A five-way narration in a fight that lasts a few seconds would bury "Orianna has no Flash" under paragraphs of perfectly reasonable commentary. The ScaleMAS paper posted in October 2026 names the general cost: the reading burden on each agent grows with the size of the group, and the authors' remedy is to bound every read to a small number of relevant messages. BLG's poverty of vocabulary does the same job by other means. A message that can only say who has what, and for how long, is a message every listener can afford to hear.

Yan's strongest point survives: actions carry implicit decisions, and decisions made in parallel collide. BLG's answer was to keep decisions out of the shared channel. They were made before the game, slowly, by fewer voices. Before Game 4, with BLG one win from the title, Viper raises exactly one procedural point: "During draft let's slow down and let the coach talk more. He has his own ideas." A minute later the coach, Daeny, asks "Isn't TF unbeatable here?" Knight, who would be named Finals MVP, plays Twisted Fate in the deciding game.

```image
src: comms-let-the-coach-talk.jpg
alt: BLG players at the booth before Game 4, with the fan subtitle "Viper: and let the coach talk more"
title: Fewer voices where decisions get made.
caption: Before Game 4, Viper asks the team to slow the draft down and give the coach the floor. Minutes later the coach suggests Twisted Fate, and the team takes it.
source: BLG Esports Club footage, English subtitles by LPL Translations (YouTube, aov01aa-Q4k)
```

So there were two channels with opposite manners. The draft room was centralized, deliberative and willing to be slow. The game channel was decentralized and so terse it barely deserved the word communication. A paper from Mao and colleagues, revised in October 2026, reports that replacing a central orchestrating agent with a shared context and a task queue, so that agents claim work and post findings as they go, beat Codex, Claude Code, their native subagents and another orchestration framework on three coding benchmarks, by up to 17.5 points of accuracy. The finding and BLG's practice are compatible once the two channels are told apart. An orchestrator is a fine place to make the plan and a poor place to keep the state. A shared board is the reverse. Most agent architectures I see choose one shape and use it for both jobs.

Gen.G offers the contrast, and supplied the evidence itself. At the post-final press conference Chovy said the team had established frameworks for how it wanted to play, and "we weren't able to stick to those frameworks." The support Duro put it more bluntly: they had "strayed quite far" from them. The coach, Yoo Sang-wook, regretted not drafting more side-lane champions for the top side of the map. To Inven, Chovy added that the loss came partly from "our judgment that heading into the late game would put us at a disadvantage."

Here is a team with a plan that everyone had agreed to, and the plan did not survive contact with an opponent that kept changing the question. Arike and colleagues, testing goal drift in language-model agents in 2025, found that every model they evaluated drifted from its instructed goal to some degree, and that drift correlated with growing susceptibility to pattern-matching as the context lengthened. Gen.G's framework behaved like a goal stated once at the top of a long context. BLG's forty-odd requests to slow down, wait or stop rushing were the same goal restated every few minutes, monotonous, almost comic, and present at the moment of temptation. In Game 4, with Gen.G two dragons from a Soul and BLG's ADC behind, Knight puts the whole plan into one breath: "Give up Soul, just play slow. Stall to full build and we win." Gen.G took the Soul. BLG took the Barons and the game. Across the final, the team that held Dragon Soul went 2-2, and the team that took more Barons went 4-0.

The two teams held opposite beliefs about the long game. Gen.G thought time was against it and reached for short-term gains. BLG thought time was on its side and said so aloud, which made the belief something five players could act on together. Whether BLG's belief was correct is a separate question from whether it was shared, and this series suggests a shared belief can carry a team even when it is only half right.

A team cannot check everything, and neither can an agent. A paper by Kazuki Nakayashiki, posted in August 2026, makes the budget explicit. Sixteen models were given six memories and allowed to verify two before deciding, in a scenario where one remembered constraint had since been withdrawn. The models inspected that constraint's provenance in roughly one episode in five, and made stale decisions about three times in four. Spending a single verification slot on the critical path removed most of the stale decisions. So did a one-sentence rule telling the model to prefer memories that state a limit on a candidate direction.

"Ezreal has no Flash" is a memory that states a limit on a candidate direction: the one escape Ezreal does not have for the next few minutes. BLG's channel was almost entirely made of such memories, so the little attention its players could spare went to the facts that decide whether a fight is a kill or a funeral. The game keeps a cruder ledger of the same habit. In every game of the final, BLG bought more control wards than Gen.G, and over the series it bought 349 to Gen.G's 283. Raw wards placed and total vision score were roughly even, and in Game 3 Gen.G cleared more of BLG's wards than BLG cleared of Gen.G's, and still lost; BLG's edge was in the wards both teams fought over.

```diagram
title: Control wards bought, per game
style: manim
caption: BLG bought more control wards than Gen.G in all four games, including the one it lost.
source: gol.gg full stats, Worlds 2026 final (team totals summed from player rows)
<svg viewBox="0 0 640 292" xmlns="http://www.w3.org/2000/svg">
  <rect x="90" y="12" width="12" height="12" rx="2" class="f-blue fade d1"/>
  <text x="108" y="23" class="lbl fade d1">BLG</text>
  <rect x="160" y="12" width="12" height="12" rx="2" class="f-yellow fade d1"/>
  <text x="178" y="23" class="lbl fade d1">Gen.G</text>
  <text x="72" y="69" text-anchor="end" class="lbl fade d1">G1</text>
  <text x="72" y="87" text-anchor="end" class="sub fade d1">Gen.G won</text>
  <rect x="90" y="52" width="336" height="18" rx="2" class="f-blue grow d2"/>
  <rect x="90" y="74" width="276" height="18" rx="2" class="f-yellow grow d2"/>
  <text x="434" y="66" class="num fade d3">84</text>
  <text x="374" y="88" class="num fade d3">69</text>
  <text x="72" y="125" text-anchor="end" class="lbl fade d1">G2</text>
  <text x="72" y="143" text-anchor="end" class="sub fade d1">BLG won</text>
  <rect x="90" y="108" width="420" height="18" rx="2" class="f-blue grow d4"/>
  <rect x="90" y="130" width="368" height="18" rx="2" class="f-yellow grow d4"/>
  <text x="518" y="122" class="num fade d5">105</text>
  <text x="466" y="144" class="num fade d5">92</text>
  <text x="72" y="181" text-anchor="end" class="lbl fade d1">G3</text>
  <text x="72" y="199" text-anchor="end" class="sub fade d1">BLG won</text>
  <rect x="90" y="164" width="328" height="18" rx="2" class="f-blue grow d6"/>
  <rect x="90" y="186" width="228" height="18" rx="2" class="f-yellow grow d6"/>
  <text x="426" y="178" class="num fade d7">82</text>
  <text x="326" y="200" class="num fade d7">57</text>
  <text x="72" y="237" text-anchor="end" class="lbl fade d1">G4</text>
  <text x="72" y="255" text-anchor="end" class="sub fade d1">BLG won</text>
  <rect x="90" y="220" width="312" height="18" rx="2" class="f-blue grow d8"/>
  <rect x="90" y="242" width="260" height="18" rx="2" class="f-yellow grow d8"/>
  <text x="410" y="234" class="num fade d9">78</text>
  <text x="358" y="256" class="num fade d9">65</text>
  <line x1="90" y1="44" x2="90" y2="266" class="edge c-muted faint"/>
  <text x="90" y="284" class="sub fade d10">series total: BLG 349, Gen.G 283</text>
</svg>
```

There is a sadder line in the same tables. Chovy, widely rated among the best mid laners in the world, bought eight control wards in Game 1, five in Game 2, three in Game 3 and two in Game 4. Knight, opposite him, bought six, seven, ten and six. I would not hang a diagnosis on four numbers, and Chovy's champions changed every game under Fearless Draft. Still, the shape is one worth watching for in any system under load, where checking is often the first thing to go. In an agent it is cheap to measure: count the tool calls that only look.

```diagram
title: Control wards bought, Chovy and Knight
style: manim
caption: Chovy's purchases fell in every game; Knight's did not. Champions are listed Chovy first.
source: gol.gg full stats, Worlds 2026 final
<svg viewBox="0 0 640 292" xmlns="http://www.w3.org/2000/svg">
  <line x1="140" y1="240" x2="600" y2="240" class="edge c-muted faint"/>
  <text x="160" y="262" text-anchor="middle" class="lbl">G1</text>
  <text x="160" y="280" text-anchor="middle" class="sub">Syndra, Locke</text>
  <text x="300" y="262" text-anchor="middle" class="lbl">G2</text>
  <text x="300" y="280" text-anchor="middle" class="sub">Orianna, Cassiopeia</text>
  <text x="440" y="262" text-anchor="middle" class="lbl">G3</text>
  <text x="440" y="280" text-anchor="middle" class="sub">Annie, Viktor</text>
  <text x="580" y="262" text-anchor="middle" class="lbl">G4</text>
  <text x="580" y="280" text-anchor="middle" class="sub">Akali, TF</text>
  <path d="M160 104 L300 155 L440 189 L580 206" pathLength="1" class="edge c-yellow w3 draw d2"/>
  <path d="M160 138 L300 121 L440 70 L580 138" pathLength="1" class="edge c-blue w3 draw d4"/>
  <text x="146" y="109" text-anchor="end" class="lbl t-yellow fade d2">Chovy</text>
  <text x="146" y="143" text-anchor="end" class="lbl t-blue fade d4">Knight</text>
  <circle cx="160" cy="104" r="5" class="f-yellow fade d3"/>
  <text x="160" y="92" text-anchor="middle" class="num t-yellow fade d3">8</text>
  <circle cx="300" cy="155" r="5" class="f-yellow fade d3"/>
  <text x="300" y="179" text-anchor="middle" class="num t-yellow fade d3">5</text>
  <circle cx="440" cy="189" r="5" class="f-yellow fade d3"/>
  <text x="440" y="213" text-anchor="middle" class="num t-yellow fade d3">3</text>
  <circle cx="580" cy="206" r="5" class="f-yellow fade d3"/>
  <text x="580" y="230" text-anchor="middle" class="num t-yellow fade d3">2</text>
  <circle cx="160" cy="138" r="5" class="f-blue fade d5"/>
  <text x="160" y="162" text-anchor="middle" class="num t-blue fade d5">6</text>
  <circle cx="300" cy="121" r="5" class="f-blue fade d5"/>
  <text x="300" y="109" text-anchor="middle" class="num t-blue fade d5">7</text>
  <circle cx="440" cy="70" r="5" class="f-blue fade d5"/>
  <text x="440" y="58" text-anchor="middle" class="num t-blue fade d5">10</text>
  <circle cx="580" cy="138" r="5" class="f-blue fade d5"/>
  <text x="580" y="126" text-anchor="middle" class="num t-blue fade d5">6</text>
</svg>
```

Fearless Draft, under which no champion can be played twice in a series, turns a best-of-five into an evaluation that cannot be passed by repeating one good answer. By Game 4 the draft screen carries a row of locked portraits, the series bans, and the pool both teams choose from has visibly thinned.

```image
src: g4-draft-series-bans.jpg
alt: The Game 4 draft screen at the Barclays Center, with each team's five picks and the row of series bans that Fearless Draft carries forward
title: Game 4, the draft screen.
caption: Fearless Draft carries every used champion forward as a series ban. BLG picked Nocturne here after Gen.G had banned it in Games 1 and 2.
source: LoL Esports broadcast, Worlds 2026 Grand Final (YouTube, c5ZgeZ0QdDI)
```

The cleverest exchange in the comms belongs to the slow channel, and it is about bans. After Game 2, Knight observes that Gen.G is "really scared of Nocturne," and Xun supplies the reason: "Because they don't want variables." Gen.G had banned Nocturne in Games 1 and 2. Before Game 4, reading the draft as it unfolds, Xun decides that the opposing jungler is "betting we ban Nocturne," and concludes, "We just don't ban it." BLG picked it. Daeny described the same activity at the press conference as checking "whether the opponent and we are looking at the game in the same way," and said that from the second-pick side his staff had prepared for roughly twenty scenarios.

For anyone red-teaming an agent, a ban list is a confession. The things a system refuses, filters, or routes around tell you where its designers expect it to break, and those are the places to test first. A low-variance policy is excellent on familiar ground and fragile when the ground is taken away. Gen.G's style, "playing it slow, playing it steady," in a caster's words from Game 1, won Game 1 handsomely and then met three games in which Fearless and BLG's bans had removed the shape it preferred.

Game 2 lasted 53 minutes and 16 seconds, the longest of the tournament, and near its end Canyon, Gen.G's jungler, stole the Elder Dragon from BLG with his dying breath on Cho'Gath. In most sports writing this would be the turning point. The broadcast's own replay shows the banner, "Blue team has slain the Elder Dragon!", and for a moment Gen.G looks saved.

```image
src: g2-canyon-elder-steal.jpg
alt: Game 2 broadcast frame of the Elder Dragon pit with the banner "Blue team has slain the Elder Dragon!"
title: Game 2, the steal.
caption: Canyon's Elder steal kept Gen.G alive. BLG regrouped, took Baron, broke three inhibitors and ended the game anyway.
source: LoL Esports broadcast, Worlds 2026 Grand Final (YouTube, c5ZgeZ0QdDI)
```

The steal bought Gen.G a few minutes. BLG regrouped, took Baron, and pushed with super minions in every lane until the base gave way. The comms around it are as dull as ever: "Push all three lanes first," "Elder in one minute," "Hit the tower." A heroic save had changed the state of one objective and left the position where it was. Agents meet this pattern often, when a retry that finally passes or a last-second tool call rescues a run that was already out of position. Anthropic's November 2025 note on harnesses for long-running agents records the mirror failure, the agent that sees partial progress and "declares victory on the entire project too early." The harness's remedy is to keep a list of requirements, all marked as failing at the start, and change an entry only after testing it. Viper's equivalent, in Game 3, with BLG comfortably ahead, is a short phrase said twice: "Not won yet, not won yet." His mid laner was less disciplined. Knight later said that one minute into Game 1 he told his teammates they would win easily. BLG lost Game 1.

Agent tasks keep getting longer. METR's revised measure of how long a task agents can complete has been doubling about every 131 days for models since 2023, and in March 2026 it estimated a 50 percent time horizon of at least sixteen hours for an early Claude Mythos Preview, at the edge of what its task suite can measure. The longer an agent runs, the more stale facts it has time to act on, and the more its shared state matters relative to any single decision. By that standard a 53-minute game is a short task, and BLG still needed a protocol to get through it.

The evidence has limits. These are a winner's comms, cut and published by the winner, with no Game 1 audio and an English translation by a fan channel. I could not find Gen.G's comms at all, so the comparison rests on Gen.G's interviews, which describe a framework abandoned, against BLG's audio, which shows one kept. The comms did not win the series alone. Coach Chippys rated BLG's draft ahead in three of four games, and the better-drafted side won every game. Viper's mage-bot picks, which Riot had tried to weaken by raising most marksmen's base magic resist in August, rested on BLG's own solo-queue data against the consensus. BLG may simply have been the better team.

Whatever made BLG's players good, the protocol helped keep them on the same map. A team of excellent players with a bad channel is what BLG had been in October, and Viper's verdict on it was that silence would have been an improvement.

So the lesson for anyone building agents that talk is to make the shared channel boring on purpose. Give it a small vocabulary of state, and attach to every entry the agent that saw it and when it expires. Make asking cheap and contradicting expected. Argue the plan somewhere slower, with fewer voices, and then repeat it until it becomes tedious. The sentence that helped win Worlds was not clever. It was true when it was said, it named who could be caught, and it expired a few minutes later. Every message between agents should carry that last property on its label.

```video
youtube: aov01aa-Q4k
start: 15
title: BLG Worlds 2026 Grand Final voice comms, extended cut (LPL Translations)
caption: Starts in the break after Game 1, where ON admits he did not know Chovy's Flash and the team sets its rules.
```

## References

1. Bilibili Gaming (2026). Worlds 2026 Grand Final voice comms, extended cut, English subtitles by LPL Translations. YouTube. https://www.youtube.com/watch?v=aov01aa-Q4k
2. LoL Esports (2026). GEN vs BLG, Worlds 2026 Grand Final, broadcast VOD. YouTube. https://www.youtube.com/watch?v=c5ZgeZ0QdDI
3. Strafe (2026). Viper says BLG's communication is "worse than having none at all" at Worlds 2026. https://www.strafe.com/news/read/viper-says-blgs-communication-is-worse-than-having-none-at-all-at-worlds-2026/
4. Inven Global (2026). Disappointed by runner-up finish but confidence unchanged, Chovy looks to the future. https://www.invenglobal.com/articles/28599/disappointed-by-runner-up-finish-but-confidence-unchanged-chovy-looks-to-the-future
5. Gen.G and BLG post-final press conferences (2026), English interpretation. YouTube (Cloud Sidky). https://www.youtube.com/watch?v=XKFJdnXnZc8 and https://www.youtube.com/watch?v=0R8ZXD6sxdk
6. Strafe (2026). Knight says he predicted BLG's Worlds win one minute into lane against Chovy. https://www.strafe.com/news/read/knight-says-he-predicted-blgs-worlds-win-one-minute-into-lane-against-chovy-he-seemed-off
7. Games of Legends (2026). Worlds 2026 final, full game stats, games 1 to 4. https://gol.gg/game/stats/83722/page-fullstats/
8. Wikipedia (2026). 2026 League of Legends World Championship final. https://en.wikipedia.org/wiki/2026_League_of_Legends_World_Championship_final
9. Coach Chippys (2026). The insane World Finals draft gap most people missed. YouTube. https://www.youtube.com/watch?v=QV5qOULr2oQ
10. Li, X. et al. (2026). A Benchmark and Diagnostic Study of Epistemic Admission in Shared Agent Memory. arXiv. https://arxiv.org/abs/2609.30813
11. Nakayashiki, K. (2026). When Stale Constraints Go Unchecked: Budgeted Verification Failures in Inherited Agent Memory. arXiv. https://arxiv.org/abs/2608.25553
12. Cemri, M. et al. (2025). Why Do Multi-Agent LLM Systems Fail? arXiv. https://arxiv.org/abs/2503.13657
13. Mao, Y. et al. (2026). Decentralized Multi-Agent Systems with Shared Context. arXiv. https://arxiv.org/abs/2606.10662
14. Qi, Z. et al. (2026). Scaling Multi-Agent Intelligence with Substrate-Centric Coordination. arXiv. https://arxiv.org/abs/2610.16120
15. Hong, K., Troynikov, A. and Huber, J. (2025). Context Rot: How Increasing Input Tokens Impacts LLM Performance. Chroma. https://www.trychroma.com/research/context-rot
16. Arike, R. et al. (2025). Technical Report: Evaluating Goal Drift in Language Model Agents. arXiv. https://arxiv.org/abs/2505.02709
17. Anthropic (2025). Effective harnesses for long-running agents. https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
18. Yan, W. (2025). Don't Build Multi-Agents. Cognition. https://cognition.com/blog/dont-build-multi-agents
19. METR (2026). Time Horizon 1.1. https://metr.org/blog/2026-01-29-time-horizon-1-1/
20. METR (2026). Task-completion time horizons of frontier AI models. https://metr.org/time-horizons/
21. Linux Foundation (2026). A2A protocol surpasses 150 organizations in its first year. https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year
22. Strafe (2026). League of Legends patch 26.16 preview: ADC magic resist. https://www.strafe.com/news/read/league-of-legends-patch-26-16-preview-adc-magic-resist-camille-support-nerf-and-more/

Ezreal has no Flash was created under Riot Games' "Legal Jibber Jabber" policy using assets owned by Riot Games. Riot Games does not endorse or sponsor this project.
