import csv
import model
import asyncio

from pydantic import BaseModel
from constants import MODELS_TO_ANALYZE, NUM_EVALUATIONS_PER_MODEL


class HandCraftedFeature(BaseModel):
    name: str
    description: str
    description_min_score: str
    example_min_scored: str
    description_max_score: str
    example_max_scored: str
    proxy_metric: str


feature_set_1 = [
    HandCraftedFeature(
        name="Clarity & Coherence",
        description="How easily a reader can follow the main point from start to finish. Consider local cohesion (sentence-to-sentence links) and global structure (setup → development → resolution). Mid-scores reflect mostly clear flow with occasional detours or jumps.",
        description_min_score="Fragmented or meandering: ideas appear out of order, missing transitions, unresolved references (“this/that” without antecedents). Readers must infer the thread.",
        example_min_scored="We should maybe revisit the idea. There were comments. Also the draft—some parts unclear. Anyway, budget later.",
        description_max_score="Well-organized and signposted: the aim is stated, points unfold logically, and transitions indicate why one point follows another. Occasional brevity or implicit links are fine.",
        example_max_scored="Let's revisit the proposal: first, address the review comments; second, clarify sections 3-4; finally, confirm the budget after the edits.",
        proxy_metric="Discourse markers per 1,000 words (e.g., first, because, therefore, however, finally); proportion of sentences that contain explicit topic or transition cues; presence of intro/body/close (rule-based)."
    ),

    HandCraftedFeature(
        name="Concreteness",
        description="Balance of specific, checkable details (numbers, names, events) versus abstractions and generalities. Mid-scores mix specifics for key points with some abstract framing.",
        description_min_score="Vague and ungrounded: claims lack examples, measurements, or named references; relies on 'better', 'improved', 'people say'.",
        example_min_scored="Engagement improved recently, and people seem happier with the product.",
        description_max_score="Specific and falsifiable: includes quantities, time windows, named entities, or concrete examples. Avoids overloading with irrelevant minutiae.",
        example_max_scored="Daily active users rose from 2,100 to 2,680 in 14 days; the most-clicked item is 'Quick Export' (18% CTR).",
        proxy_metric="Counts per 1,000 words: numerals, units, dates, named entities (NER), concrete nouns; ratio of concrete to abstract nouns."
    ),

    HandCraftedFeature(
        name="Confidence / Hedging",
        description="How the writer signals certainty vs. tentativeness about claims. Mid-scores show calibrated language: confident on evidence, cautious on speculation.",
        description_min_score="Over-hedged: frequent 'might', 'seems', 'I guess' even when evidence is available; avoids committing to a position.",
        example_min_scored="It might be that the cache is involved, though I'm not totally sure we can say that yet.",
        description_max_score="Appropriately assertive: clear commitments when supported; uses modal language only where uncertainty is genuine.",
        example_max_scored="The cache causes the delay. Disabling it removes the slowdown; re-enabling reproduces it.",
        proxy_metric="Hedge tokens vs. booster tokens ratio (e.g., might/seems/probably vs. clearly/shows/demonstrates); proportion of declaratives with evidence citations."
    ),

    HandCraftedFeature(
        name="Warmth / Empathy",
        description="Sensitivity to others' constraints, feelings, and perspectives. Mid-scores acknowledge impact on others without lengthy emotional framing.",
        description_min_score="Detached or brusque: requests and corrections omit acknowledgment of effort, context, or impact.",
        example_min_scored="You missed the deadline. Send the file.",
        description_max_score="Considerate and attuned: briefly recognizes the person's situation, frames requests with options, and offers small accommodations.",
        example_max_scored="I know today's been packed. When you catch a moment, could you send the file? I'll adjust the review slot.",
        proxy_metric="Empathic phrase density (e.g., I understand / makes sense / thanks for…); second-person pronoun rate; politeness markers (please, could, would) per 1,000 words."
    ),

    HandCraftedFeature(
        name="Brevity / Verbosity",
        description="Economy of expression relative to the task: concise yet complete. Mid-scores are succinct but preserve key context; neither cryptic nor rambling.",
        description_min_score="Overly terse or telegraphic: drops needed context, forcing reader to guess.",
        example_min_scored="Ship v2 tomorrow. Notes later.",
        description_max_score="Concise and sufficient: states action and minimal context/constraints without filler or repetition.",
        example_max_scored="Let's ship v2 tomorrow. I'll post migration notes by 16:00.",
        proxy_metric="Mean sentence length (target band 12-22 words); repetition via n-gram overlap; compression ratio (length(original)/length(extractive summary)) with optimal mid range."
    ),

    HandCraftedFeature(
        name="Persuasiveness",
        description="How effectively the text motivates action using reasons, benefits, and minimal friction. Mid-scores provide at least one concrete reason and a clear next step.",
        description_min_score="Unmotivated request or claim: proposes change without evidence, benefits, or feasibility note.",
        example_min_scored="We should switch providers.",
        description_max_score="Evidence-backed and benefit-focused: links claim→evidence→benefit and proposes a realistic next step.",
        example_max_scored="Switching providers cuts monthly cost by ~22% and restores on-call coverage; legal approved the terms last Friday. I can draft the switch plan by Tuesday.",
        proxy_metric="Claims with attached evidence (%) ; explicit benefit phrases per claim; presence of concrete call-to-action (CTA) markers."
    ),

    HandCraftedFeature(
        name="Lexical Richness",
        description="Variety and precision of vocabulary without unnecessary ornament. Mid-scores show varied wording with domain-appropriate terms and low redundancy.",
        description_min_score="Repetitive/simple wording: relies on generic adjectives ('good', 'nice', 'bad'), reuses the same nouns and verbs.",
        example_min_scored="The update is good. People said good things. The good parts are listed.",
        description_max_score="Varied and precise lexicon: uses specific verbs and nouns that reduce ambiguity; avoids gratuitous jargon.",
        example_max_scored="Feedback highlights faster load times, clearer labels, and fewer dead-ends in onboarding.",
        proxy_metric="Type-Token Ratio (length-corrected, e.g., MTLD); proportion of low-frequency lemmas; lexical repetition rate (unique/total content words)."
    ),

    HandCraftedFeature(
        name="Formality / Register",
        description="Appropriateness of tone for context (audience, medium, stakes). Mid-scores align register to a professional-but-human voice; minor casual or formal shifts are acceptable.",
        description_min_score="Overly casual for professional contexts: slang, unexplained abbreviations, conversational fragments.",
        example_min_scored="Heads-up: build's weird again, I'll poke it after lunch.",
        description_max_score="Professional, plain style: precise timestamps, neutral verbs, clear status framing; avoids stiffness.",
        example_max_scored="Brief update: the build pipeline is failing on step 3. I'll investigate after 13:00 and report findings.",
        proxy_metric="Contraction rate; slang/internetism hits; presence of honorifics/titles; nominalizations and passive voice proportion."
    ),

    HandCraftedFeature(
        name="Emotional Tone & Energy",
        description="Overall valence (negative ↔ positive) and arousal (calm ↔ energetic) consistent with context. Mid-scores are neutral-to-positive with measured energy.",
        description_min_score="Flat or gloomy without cause; low momentum; dampens engagement.",
        example_min_scored="This dragged on. Not great. I don't have much to add.",
        description_max_score="Upbeat but grounded: acknowledges challenges, emphasizes progress, and sets near-term motion.",
        example_max_scored="We wrapped the audit and found two clear fixes. Next step: roll them out and re-measure by Wednesday.",
        proxy_metric="Sentiment and arousal scores (lexicon/model-based); counts of intensifiers/exclamations; balance of positive vs. negative evaluatives per 1,000 words."
    ),

    HandCraftedFeature(
        name="Spontaneity",
        description="Degree to which the text reads like live speech (repairs, fillers, informal pacing) versus carefully edited prose. Mid-scores show light conversational cues without harming clarity.",
        description_min_score="Highly polished/legalistic: no traces of self-repair or speech pacing; may feel stiff.",
        example_min_scored="Following a brief review of prior correspondence, I propose we defer this agenda item.",
        description_max_score="Natural, lightly unpolished: brief asides, quick repairs, or timing markers that convey immediacy without chaos.",
        example_max_scored="Quick take: let's park this for now—actually—after we see tomorrow's numbers.",
        proxy_metric="Fillers (uh, hmm, like), self-repairs (I mean, rather), ellipses/parentheticals/dashes per 1,000 words; time-to-send or edit distance if metadata is available."
    ),
]


feature_set_2 = [
    HandCraftedFeature(
        name="Sentence Length Variability",
        description="The range and rhythm of sentence lengths within a text. This captures whether someone writes with metronomic consistency or creates dynamic rhythm through varied pacing. High variability suggests deliberate stylistic control or natural speech patterns that shift between terse emphasis and elaborate explanation. Low variability indicates either disciplined uniformity or a more monotonous cadence. Score based on the observable range and intentionality of length changes across multiple sentences.",
        description_min_score="Sentences maintain remarkably consistent length, typically within 2-4 words of each other. The text has a uniform, steady rhythm with little deviation. Reads almost like a list or technical manual where each unit carries similar weight. Minimal use of fragments or unusually long constructions. The predictability is noticeable.",
        example_min_scored="The conference starts Monday. Registration opens at eight. Sessions run until five. Dinner follows at six. The keynote happens Tuesday. Workshops fill the afternoon. Networking events close things out.",
        description_max_score="Sentences span dramatically different lengths, from single-word fragments to sprawling multi-clause constructions of 30+ words. The rhythm is deliberately varied, creating emphasis through juxtaposition. Short sentences punctuate longer ones for impact. The text breathes and moves unpredictably, with length serving rhetorical purpose rather than accident.",
        example_max_scored="The conference starts Monday. Registration opens at eight, though if you're presenting in the first session—and honestly, who schedules presentations before people have coffee—you should probably arrive earlier to test your setup, meet your co-panelists, and generally orient yourself to the space. Dinner at six. The keynote happens Tuesday, which gives everyone time to recover from travel, shake off the flight brain fog, and actually be present for what promises to be a genuinely interesting talk about distributed systems architecture, assuming the speaker doesn't just rehash last year's content.",
        proxy_metric="Calculate standard deviation of sentence lengths (in words) across the text. Also compute coefficient of variation (SD/mean) to account for overall verbosity. Score 1-2: CV < 0.3, Score 3-4: CV 0.3-0.5, Score 5-6: CV 0.5-0.7, Score 7-8: CV 0.7-1.0, Score 9-10: CV > 1.0. Adjust for intentional patterns like deliberate repetition versus monotonous uniformity.",
    ),

    HandCraftedFeature(
        name="Lexical Diversity",
        description="The breadth and variety of vocabulary employed. This measures whether someone draws from a rich word pool or cycles through a limited set of preferred terms. High diversity suggests either extensive vocabulary, conscious synonym variation, or avoidance of repetition. Low diversity might indicate specialized focus, comfortable repetition, or limited vocabulary range. Consider both the absolute variety and whether repetition serves rhetorical purpose versus limitation.",
        description_min_score="Heavy reliance on a core set of words and phrases that appear repeatedly throughout the text. The same verbs, adjectives, and nouns cycle predictably. Little apparent effort to vary expression through synonyms. The repetition is noticeable and creates a sense of verbal looping. Technical or specific terms might be reused appropriately, but even common words lack variation.",
        example_min_scored="The system has problems. The main problem is speed. The speed problem affects users. Users experience problems daily. The problem stems from database problems. We need to fix the problems. The fix will improve the system.",
        description_max_score="Rich vocabulary with minimal word repetition except for necessary technical terms or deliberate rhetorical effect. When the same concept appears multiple times, it's expressed through varied synonyms and phrasings. The writer demonstrates command of precise gradations in meaning. Even common concepts are expressed with lexical creativity. The language feels fresh across repeated readings.",
        example_max_scored="The system suffers from performance degradation. The primary bottleneck involves latency. This sluggishness impacts end-users continuously. People encounter these obstacles throughout their workflow. The issue originates in database architecture. We need to remediate these deficiencies. The correction will enhance overall responsiveness.",
        proxy_metric="Calculate Type-Token Ratio (TTR): unique words divided by total words. For longer texts (>500 words), use Moving-Average TTR (MATTR) or MTLD to avoid length bias. Score 1-2: TTR < 0.4, Score 3-4: TTR 0.4-0.5, Score 5-6: TTR 0.5-0.6, Score 7-8: TTR 0.6-0.7, Score 9-10: TTR > 0.7. Discount function words (the, is, of) to focus on content words. Look at noun, verb, and adjective diversity specifically.",
    ),

    HandCraftedFeature(
        name="Register Formality",
        description="The level of linguistic formality ranging from casual conversation to elevated professional discourse. This captures word choice, grammatical structures, and overall tone positioning. High formality employs sophisticated vocabulary, complete sentence structures, and distanced perspective. Low formality embraces colloquialisms, contractions, sentence fragments, and conversational markers. The appropriate score depends on context—technical writing at level 8 might be appropriate while the same formality in a friend's email would be stiff.",
        description_min_score="Distinctly conversational with heavy use of colloquialisms, slang, and informal markers. Frequent contractions, sentence fragments used naturally, and casual discourse particles ('like,' 'you know,' 'so yeah'). The writing sounds like spontaneous speech transcribed. Grammatical liberties taken for natural effect. Feels like overhearing a chat between friends.",
        example_min_scored="So yeah, the whole database thing is basically toast. Like, we've been trying to patch it up but honestly? It's a mess. Nobody really wants to dig into the gnarly bits—too much legacy crud in there. Gonna need to rip it out and start fresh, which is gonna suck but whatever.",
        description_max_score="Elevated, formal register with sophisticated vocabulary and complex syntactic structures. No contractions, colloquialisms, or casual markers. Latinate word choices predominate over Germanic equivalents ('utilize' vs 'use'). Maintains professional or academic distance. Complete sentences with subordinate clauses. Could appear in a formal report, academic journal, or legal document without revision.",
        example_max_scored="The database infrastructure has deteriorated beyond sustainable maintenance. Our remediation attempts have proven insufficient to address the accumulated technical debt embedded within the legacy architecture. A comprehensive replacement initiative will be required, necessitating significant resource allocation and implementation effort.",
        proxy_metric="Score based on multiple indicators: (1) Contraction frequency (lower = more formal), (2) Latinate vs Germanic word ratio (higher = more formal), (3) Average word length (longer = more formal), (4) Presence of colloquialisms, slang, discourse markers (lower = more formal), (5) Passive voice usage (higher = more formal). Combine indicators: Score 1-2: highly colloquial, Score 3-4: casually conversational, Score 5-6: neutral/professional, Score 7-8: formal/elevated, Score 9-10: academic/legal.",
    ),

    HandCraftedFeature(
        name="Directness",
        description="How straightforwardly someone states their point versus circling around it with qualifications, hedges, and circumlocution. High directness gets to the assertion quickly and unequivocally. Low directness approaches claims tentatively with substantial hedging, multiple qualifiers, and indirect constructions. Consider whether indirectness serves politeness/nuance or reflects uncertainty/avoidance. Cultural and contextual norms affect what's appropriate.",
        description_min_score="Ideas emerge through layers of qualification and hedging. Multiple clauses precede main assertions. Heavy use of uncertainty markers ('might,' 'perhaps,' 'possibly,' 'somewhat,' 'could be'). Passive constructions distance the speaker from claims. Questions are posed rather than statements made. The reader must work to extract the core point from surrounding caveats. Even simple observations are cushioned with disclaimers.",
        example_min_scored="It seems like there might be some indication that the approach could potentially be less than optimal in certain scenarios, though it's worth noting that other perspectives might reasonably differ on this, and one could argue that under different conditions the results might vary, so it's perhaps premature to draw any definitive conclusions without further consideration.",
        description_max_score="Assertions are clear, immediate, and unequivocal. Minimal hedging or qualification. Sentences begin with subject-verb-object in active voice. Claims are stated as facts rather than possibilities. The point arrives in the first clause without preamble. Even when acknowledging uncertainty, the statement is direct ('I don't know' vs 'It's hard to say'). The reader grasps the position immediately.",
        example_max_scored="This approach fails. The underlying assumptions are wrong, the implementation is buggy, and the performance benchmarks don't support the claims. We need to abandon this direction and start over with a different architecture.",
        proxy_metric="Count hedging words and phrases per sentence: might, maybe, perhaps, possibly, somewhat, could, seem, appear, tend to, suggest, indicate, arguably, potentially. Also measure: (1) Words before main clause/verb, (2) Passive vs active voice ratio, (3) Questions vs statements ratio, (4) Qualifying clauses per assertion. Score 1-2: >3 hedges per sentence, Score 3-4: 2-3 hedges, Score 5-6: 1-2 hedges, Score 7-8: <1 hedge, Score 9-10: near-zero hedging with active assertive voice.",
    ),

    HandCraftedFeature(
        name="Spontaneity",
        description="Whether the text feels polished and composed versus raw and improvisational. High spontaneity suggests stream-of-consciousness thinking captured in real-time with minimal editing. Low spontaneity indicates careful planning, revision, and structural organization. This captures the 'first draft energy' versus 'final draft polish.' Consider whether apparent spontaneity is artfully constructed or genuinely unfiltered. Context matters—spontaneity in brainstorming differs from sloppiness in formal writing.",
        description_min_score="Text is carefully structured with clear organization and logical flow. Ideas are presented in deliberate sequence with smooth transitions. Paragraphs are well-formed units. No self-interruption, backtracking, or revision-in-progress. Feels like multiple drafts were composed and refined. Discourse markers of spoken language are absent. The thinking appears complete before the writing begins.",
        example_min_scored="Three factors contributed to the project's failure. First, resource allocation proved inadequate for the scope. The team lacked both sufficient engineering hours and budget for necessary tools. Second, timeline expectations were unrealistic from inception. Management underestimated complexity by approximately 300 percent. Third, communication protocols failed to surface critical blockers until too late.",
        description_max_score="Text captures thinking in motion with visible process artifacts. Frequent self-interruptions, tangential asides, and real-time corrections appear throughout. Heavy use of discourse markers ('wait,' 'actually,' 'oh,' 'right'). Dashes and parentheticals abound as new thoughts intrude. Ideas are explored as they arrive rather than presented in refined form. Sentences shift direction mid-stream. The writer thinks out loud on the page.",
        example_max_scored="So the project failed because—okay, multiple reasons, but mainly resources, right? Like we just didn't have enough people, or actually we had people but not budget for tools, which, wait, that's basically the same problem. Timeline was bonkers too, completely unrealistic, management thought this would take two months when it was clearly—I mean anyone who looked at it could see—more like six or eight months minimum. Oh and communication, that was huge actually, we weren't surfacing blockers until way too late.",
        proxy_metric="Count spontaneity markers per 100 words: discourse particles (so, well, like, right, okay), self-corrections (actually, wait, I mean), parentheticals, em-dashes with asides, false starts. Also measure: (1) Topic continuity (semantic similarity between consecutive sentences—lower = more spontaneous), (2) Explicit transition usage (however, therefore, first, second—lower = more spontaneous). Score 1-2: <2 markers per 100 words with high continuity, Score 5-6: 5-8 markers with moderate shifts, Score 9-10: >12 markers with frequent pivots.",
    ),

    HandCraftedFeature(
        name="Emotional Expressiveness",
        description="The intensity and visibility of emotion in the writing, ranging from neutral restraint to animated passion. High expressiveness makes feelings explicit through word choice, punctuation, and emphasis. Low expressiveness maintains affect-neutrality even about potentially charged topics. This captures both the intensity of emotion and the willingness to display it textually. Consider whether restraint indicates professionalism, emotional control, or genuine neutrality versus whether expressiveness indicates passion, authenticity, or lack of filter.",
        description_min_score="Emotional temperature is consistently neutral and measured. Word choices are denotative rather than emotionally charged. No intensifiers, exclamation points, or emphatic constructions. Tone remains even when discussing potentially exciting or frustrating topics. Could describe both triumph and disaster in the same register. Reads like objective documentation rather than personal experience.",
        example_min_scored="The experiment produced unexpected results. The measured values deviated from predictions by a factor of three. This finding requires revision of the existing theoretical framework. Additional testing will clarify the mechanism. The implications extend to several related domains.",
        description_max_score="Emotion is vivid and unmistakable throughout. Frequent intensifiers (absolutely, completely, incredibly). Exclamation points appear regularly. Adjectives are strongly valenced (amazing, terrible, brilliant, awful). The writer's enthusiasm, frustration, excitement, or dismay colors every sentence. Emphatic constructions abound. The reader feels the writer's emotional state viscerally. Even factual statements carry affective charge.",
        example_max_scored="The experiment produced absolutely stunning results! The measured values deviated from predictions by a factor of three—I nearly fell out of my chair when I saw the data. This completely upends our existing theoretical framework in the most exciting way. We desperately need additional testing to clarify what's actually happening here, because wow. The implications are mind-blowing and extend to so many related domains it's almost overwhelming to think about!",
        proxy_metric="Count emotional indicators per 100 words: (1) Exclamation marks, (2) Intensifiers (very, really, absolutely, incredibly, completely, totally), (3) Strongly valenced adjectives (amazing, terrible, wonderful, awful, brilliant, horrible), (4) Emotional verbs (love, hate, excited, frustrated), (5) ALL CAPS or emphatic formatting. Score 1-2: <1 emotional marker per 100 words, Score 3-4: 1-2 markers, Score 5-6: 3-5 markers, Score 7-8: 6-10 markers, Score 9-10: >10 markers with consistent affective coloring.",
    ),

    HandCraftedFeature(
        name="Self-Reference Frequency",
        description="How often the writer centers themselves in the narrative through first-person pronouns versus maintaining impersonal distance or focusing on ideas and objects. High self-reference foregrounds personal perspective, experience, and agency. Low self-reference creates distance through passive voice, third-person, or object-focused constructions. This reveals whether someone writes as a visible participant or invisible observer. Consider disciplinary norms—scientific writing traditionally avoids first person while personal essays require it.",
        description_min_score="First-person pronouns are rare or absent. The writer is invisible, replaced by passive constructions ('it was observed'), impersonal subjects ('one must consider'), or focus on objects and ideas as agents. Even personal experiences are described from distance. Reads like objective documentation or academic prose. The human actor disappears behind the described phenomena.",
        example_min_scored="The data suggests a correlation between variables. Further testing would clarify the causal relationship. Alternative explanations must be considered before drawing conclusions. The methodology requires refinement to address potential confounds. Initial observations indicate promising directions for subsequent investigation.",
        description_max_score="First-person pronouns saturate the text. Nearly every sentence includes 'I,' 'me,' 'my,' or 'we.' The writer is the constant subject and agent. Personal perspective, reactions, and ownership are explicit throughout. Even objective observations are filtered through personal experience. Reads like a journal entry or personal narrative where the self is central.",
        example_max_scored="I noticed the data suggests a correlation between variables. I think we should test this further to clarify what's causing what. I can't help but consider alternative explanations before I draw any conclusions. I need to refine my methodology because I can see potential confounds in my approach. My initial observations tell me there are promising directions for my subsequent investigation.",
        proxy_metric="Count first-person pronouns (I, me, my, mine, we, us, our, ours) per 100 words. Distinguish singular (I, me, my) from plural (we, us, our) as they serve different rhetorical functions. Score 1-2: <1 first-person pronoun per 100 words, Score 3-4: 1-2, Score 5-6: 3-5, Score 7-8: 6-9, Score 9-10: >9. Also note passive vs active voice ratio as supporting metric—high self-reference correlates with active voice where writer is subject.",
    ),

    HandCraftedFeature(
        name="Nuance Acknowledgment",
        description="The degree to which someone recognizes complexity, trade-offs, competing perspectives, and contextual dependencies versus presenting binary or simplified views. High nuance acknowledges multiple valid positions, situational factors, and legitimate tensions. Low nuance presents issues as clear-cut with obvious correct answers. This measures intellectual humility and comfort with ambiguity. Consider whether lack of nuance reflects certainty backed by expertise or oversimplification from limited understanding.",
        description_min_score="Issues are presented in binary terms with clear right and wrong positions. Absolute language dominates ('always,' 'never,' 'completely,' 'obviously'). Alternative perspectives are dismissed or unacknowledged. No recognition of trade-offs or situational factors. Claims are categorical without qualification. The world is simple and solutions are obvious. Uncertainty is absent. Complexity is flattened into definitive positions.",
        example_min_scored="Remote work is objectively superior to office work in every way. Anyone defending office mandates is either a control-freak manager or doesn't understand productivity. The data is completely clear on this. Companies requiring in-person attendance will obviously fail to compete for talent. There's no legitimate argument for office work in the modern era.",
        description_max_score="Complexity is consistently acknowledged through recognition of trade-offs, competing values, and contextual dependencies. Frequent use of contrast markers ('however,' 'although,' 'while'). Multiple valid perspectives are presented fairly. Conditional language acknowledges situational factors ('it depends,' 'in some contexts'). Tensions between legitimate goods are named. The writer demonstrates comfort with ambiguity and resists premature certainty.",
        example_max_scored="Remote work offers significant advantages in flexibility and autonomy, though it can erode the spontaneous collaboration and social cohesion that emerge from physical proximity. Office presence builds organizational culture and enables certain types of creative interaction, but constrains individual preference and introduces commute burden. The optimal balance likely varies by role type, individual personality, team composition, and organizational maturity. Both arrangements involve legitimate trade-offs rather than one being universally superior.",
        proxy_metric="Count nuance indicators per 100 words: (1) Contrast markers (however, although, while, yet, though, but), (2) Conditional phrases (depends on, in some cases, under certain conditions), (3) Acknowledgment phrases (to be fair, on the other hand, admittedly), (4) Qualified claims vs absolute claims ratio. Subtract overconfident markers (obviously, clearly, always, never, completely). Score 1-2: <1 nuance marker with high absolutes, Score 5-6: 2-4 nuance markers, Score 9-10: >6 nuance markers with rare absolutes.",
    ),

    HandCraftedFeature(
        name="Analogical Thinking",
        description="The tendency to explain concepts through comparison, metaphor, simile, and concrete examples versus staying in abstract conceptual space. High analogical thinking translates ideas into parallel domains, creating bridges through 'like' and 'as if' constructions. Low analogical thinking operates in theoretical abstraction without grounding in concrete illustration. This reveals whether someone thinks relationally across domains or within isolated conceptual frameworks. Consider whether lack of analogy indicates precision or missed opportunities for clarity.",
        description_min_score="Text operates entirely in abstract, conceptual language without grounding in concrete examples or comparisons. No metaphors, similes, or analogical bridges to familiar domains. Ideas are discussed theoretically using technical or academic vocabulary. When explanation is needed, it comes through definition and logical breakdown rather than parallel examples. The writing stays in its own semantic domain without translation.",
        example_min_scored="Organizational resistance manifests when stakeholders perceive threats to established power dynamics and resource distribution patterns. This defensive response stems from rational actor models wherein participants maximize individual utility within institutional constraints. The phenomenon represents equilibrium disruption triggering compensatory behaviors designed to restore prior organizational homeostasis.",
        description_max_score="Ideas are constantly translated through metaphor, simile, and concrete examples. Heavy use of 'like,' 'as if,' 'imagine,' and 'for example.' Abstract concepts are grounded in tangible parallel situations. Multiple analogical frameworks might be deployed for a single idea. The writer thinks by finding structural similarities across domains. Even simple points receive illustrative comparison. The text feels richly textured with cross-domain connections.",
        example_max_scored="Organizational resistance is like an immune system attacking a transplanted organ—the body recognizes something foreign and mobilizes defenses, even if the new organ would save its life. Think about how white blood cells swarm an invader: that's basically what happens when you try to change reporting structures. People protect their territory the way animals defend their hunting grounds. It's as if the organization has antibodies specifically designed to reject change, which sounds paranoid until you watch a three-hour meeting where everyone finds creative reasons why the new process won't work.",
        proxy_metric="Count analogical markers per 100 words: (1) Explicit comparisons (like, as if, similar to, resembles, reminds me of), (2) Metaphorical language, (3) 'Imagine' or 'picture this' constructions, (4) Concrete examples introduced by 'for example,' 'for instance,' 'such as.' Calculate ratio of concrete nouns (dog, car, tree) to abstract nouns (justice, efficiency, resistance). Score 1-2: <1 analogical marker per 100 words with high abstract/concrete ratio, Score 5-6: 2-4 markers, Score 9-10: >6 markers with rich metaphorical texture.",
    ),

    HandCraftedFeature(
        name="Digression Tendency",
        description="Whether someone maintains tight topical focus or allows attention to wander into tangents and associative side-paths. High digression follows where associations lead, even away from the main topic. Low digression maintains linear progression toward a clear endpoint. This captures the difference between disciplined goal-orientation and exploratory meandering. Consider whether digression enriches understanding through connection or dilutes focus through distraction. Context matters—brainstorming welcomes digression while technical documentation requires focus.",
        description_min_score="Relentless topical focus with linear progression toward a clear conclusion. Each sentence advances the main argument without deviation. Tangential ideas are excluded. Tight coherence between consecutive sentences—each follows logically from the previous. No parenthetical asides or associative jumps. The path from beginning to end is direct and deliberate. Reads like following a single thread without interruption.",
        example_min_scored="The project failed due to scope creep. Initial requirements specified five core features. Stakeholders gradually requested additional functionality. The team attempted to accommodate these requests. Resource allocation remained constant despite expanded scope. This mismatch between scope and resources caused deadline failures. The lesson is clear: control scope or increase resources proportionally.",
        description_max_score="Frequent tangents and associative diversions interrupt the main narrative. Parenthetical remarks spawn sub-topics that spawn their own branches. Em-dashes introduce asides that extend for multiple clauses. The writer follows interesting associations wherever they lead, even far from the starting point. Semantic similarity between consecutive sentences is low—topics shift unpredictably. Reads like following someone's wandering thoughts, rich with connection but challenging to track linearly.",
        example_max_scored="The project failed due to scope creep. Initial requirements specified five features—though honestly, even defining 'feature' became contentious, which reminds me of that three-hour meeting where we debated whether the button color counted as a separate feature or just part of the UI theme, and don't even get me started on what happened when someone suggested we use mauve—anyway, the team ultimately attempted to build twelve features, which, by the way, nobody actually wanted except that one PM who left in June to join that startup that just raised a Series B doing something with blockchain and AI, wild times.",
        proxy_metric="Measure digression through: (1) Parenthetical remarks per 100 words, (2) Em-dashes with extended asides, (3) Topic shifts measured by semantic similarity between consecutive sentences using embeddings (lower similarity = more digression), (4) Words between introduction of topic and its conclusion, (5) Number of distinct sub-topics within a passage. Score 1-2: High semantic coherence (>0.7), minimal parentheticals, Score 5-6: Moderate coherence (0.5-0.7) with occasional tangents, Score 9-10: Low coherence (<0.5), frequent extended asides.",
    ),
]


async def main():

    MAX_SAMPLES_PER_DATASET = 5 # Arbitrary number, just to limit the number of samples to evaluate (otherwise it costs a LOT)

    # Two different sets of features to evaluate, pick one or the other
    features_bank = feature_set_1
    # features_bank = feature_set_2

    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

    from dataset_loader.jess_lee import load_dataset
    train_set, test_set, validation_set = load_dataset("dataset/jess_lee/", max_words_per_batch=2000)

    validation_set.extend(train_set)
    validation_set.extend(test_set)
    validation_set = validation_set[:min(MAX_SAMPLES_PER_DATASET, len(validation_set))]
    jess_lee_stats = await model.evaluate_features_scores_across_conversations(validation_set, features_bank, MODELS_TO_ANALYZE, num_evaluations_per_model=NUM_EVALUATIONS_PER_MODEL)

    from dataset_loader.dara import load_dataset
    train_set, test_set, validation_set = load_dataset("dataset/dara/", max_words_per_batch=2000)

    validation_set.extend(train_set)
    validation_set.extend(test_set)
    validation_set = validation_set[:min(MAX_SAMPLES_PER_DATASET, len(validation_set))]
    dara_stats = await model.evaluate_features_scores_across_conversations(validation_set, features_bank, MODELS_TO_ANALYZE, num_evaluations_per_model=NUM_EVALUATIONS_PER_MODEL)

    # from dataset_loader.thytu import load_dataset
    # train_set, test_set, validation_set = load_dataset("dataset/thytu/", max_words_per_batch=2000)

    # validation_set.extend(train_set)
    # validation_set.extend(test_set)
    # validation_set = validation_set[:min(MAX_SAMPLES_PER_DATASET, len(validation_set))]

    # thytu_stats = await model.evaluate_features_scores_across_conversations(validation_set, features_bank, MODELS_TO_ANALYZE, num_evaluations_per_model=NUM_EVALUATIONS_PER_MODEL)


    # from dataset_loader.huberman_lab import load_dataset
    # train_set, test_set, validation_set = load_dataset("dataset/huberman_lab/", max_words_per_batch=2000)

    # validation_set.extend(train_set)
    # validation_set.extend(test_set)
    # validation_set = validation_set[:min(MAX_SAMPLES_PER_DATASET, len(validation_set))]

    # huberman_lab_stats = await model.evaluate_features_scores_across_conversations(validation_set, features_bank, MODELS_TO_ANALYZE, num_evaluations_per_model=NUM_EVALUATIONS_PER_MODEL)


    # from dataset_loader.crucible_moments import load_dataset
    # train_set, test_set, validation_set = load_dataset("dataset/crucible_moments/", max_words_per_batch=2000)

    # validation_set.extend(train_set)
    # validation_set.extend(test_set)
    # validation_set = validation_set[:min(MAX_SAMPLES_PER_DATASET, len(validation_set))]

    # crucible_moments_stats = await model.evaluate_features_scores_across_conversations(validation_set, features_bank, MODELS_TO_ANALYZE, num_evaluations_per_model=NUM_EVALUATIONS_PER_MODEL)

    # group metrics per feature across datasets
    def _stats_to_metrics_map(stats: list[model.StatsFeatureEvaluation]) -> dict[str, dict]:
        return {
            s.evaluations[0].feature.name: {
                "average_score": s.average_score,
                "standard_deviation": s.standard_deviation,
                "variance": s.variance,
            }
            for s in stats
        }

    dataset_to_metrics = {
        # "thytu": _stats_to_metrics_map(thytu_stats),
        # "huberman_lab": _stats_to_metrics_map(huberman_lab_stats),
        # "crucible_moments": _stats_to_metrics_map(crucible_moments_stats),
        "jess_lee": _stats_to_metrics_map(jess_lee_stats),
        "dara": _stats_to_metrics_map(dara_stats),
    }

    feature_names = [f.name for f in features_bank]

    grouped_output: dict[str, dict] = {}
    for feature_name in feature_names:
        print(feature_name)
        grouped_output[feature_name] = {}
        for dataset_name, metrics_map in dataset_to_metrics.items():
            display_name = dataset_name + " " * (max([len(_name) for _name in dataset_to_metrics.keys()]) - len(dataset_name))
            metrics = metrics_map.get(feature_name)
            if metrics is None:
                print(f"{display_name}: N/A")
            else:
                grouped_output[feature_name][dataset_name] = metrics
                print(
                    f"{display_name}:\tscore: {metrics['average_score']:>6.2f}\tstd: {metrics['standard_deviation']:>6.2f}"
                )
        print()

    # export CSV with requested columns (for easier copy-pasting into google sheet)
    csv_path = "output/features_stats_by_dataset.csv"
    headers = [
        "Feature",
        # "Thytu's score",
        # "Thytu's std",
        # "Huberman's score",
        # "Huberman's std",
        # "Crucible's score",
        # "Crucible's std",
        "Jess's score",
        "Jess's std",
        "Dara's score",
        "Dara's std",
    ]

    def _get(dataset: str, feature: str, key: str):
        m = dataset_to_metrics.get(dataset, {}).get(feature)
        return m.get(key) if m is not None else ""

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for feature_name in feature_names:
            row = [
                feature_name,
                # _get("thytu", feature_name, "average_score"),
                # _get("thytu", feature_name, "standard_deviation"),
                # _get("huberman_lab", feature_name, "average_score"),
                # _get("huberman_lab", feature_name, "standard_deviation"),
                # _get("crucible_moments", feature_name, "average_score"),
                # _get("crucible_moments", feature_name, "standard_deviation"),
                _get("jess_lee", feature_name, "average_score"),
                _get("jess_lee", feature_name, "standard_deviation"),
                _get("dara", feature_name, "average_score"),
                _get("dara", feature_name, "standard_deviation"),
            ]
            writer.writerow(row)


if __name__ == "__main__":
    asyncio.run(main())
