# Foundation Models & Amazon Bedrock Core — Deep-Dive Study Guide

## Document Metadata

| Field | Value |
|-------|-------|
| Target Exam | AWS Certified Generative AI Developer - Professional (AIP-C01) |
| Exam Domains Covered | Domain 1: FM Integration, Data Management, and Compliance (31%), Domain 2: Implementation and Integration (26%) |
| Primary Tasks | Task 1.1, Task 1.2, Task 2.2, Task 2.4 |
| Study Guide | Guide 01 of the AIP-C01 Study Strategy |
| Priority Level | CRITICAL — foundation for all subsequent guides |
| Prerequisite Knowledge | General AWS (Lambda, API Gateway, IAM, S3, CloudWatch), basic ML concepts |
| Source Material | Official AIP-C01 Exam Guide, Amazon Bedrock User Guide, AIP strategy + blueprint, MCP-researched AWS documentation |

This is Guide 01 in the AIP-C01 series; read it before the RAG, prompt engineering, agents, safety, optimization, and testing guides.

---

## How to Use This Guide

This is the first guide in the AIP-C01 textbook series and the one everything else builds on. Amazon Bedrock is the single most heavily tested service on the exam, and nearly every scenario question assumes you already know how to select a model, invoke it correctly, choose an inference mode, and make the invocation resilient. Read this guide before the RAG, prompt engineering, agents, safety, optimization, and testing guides.

Each section is written in textbook-depth prose that teaches the reasoning behind each design choice, supplemented by comparison tables and described diagrams. Every section ends with an Exam-Relevant Distinctions checklist and a Knowledge Check quiz. Work the quizzes before reading answers — active recall is what moves this material into long-term memory.

---

## Table of Contents

- Section 1: Foundation Model Foundations
- Section 2: Model Selection
- Section 3: Inference Parameters
- Section 4: Invocation APIs
- Section 5: Inference Modes
- Section 6: Resilience and Cross-Region Inference
- Section 7: FM Customization and Lifecycle
- Section 8: Resilient FM API Integration
- Section 9: Exam Patterns and Quick Reference
- AWS Documentation References

---

## Section 1: Foundation Model Foundations

### What a Foundation Model Is, and Why It Changes the ML Equation

For most of the history of applied machine learning, building a model meant building it for one job. If you wanted to classify support tickets, you collected labeled tickets, engineered features, trained a classifier, and deployed something that did exactly that one thing and nothing else. A separate task — say, summarizing those same tickets — meant a separate dataset, a separate model, and a separate deployment. The intelligence was narrow, and the cost of each new capability was paid up front in data collection and training.

A foundation model breaks that pattern. A foundation model (FM) is a large deep-learning neural network trained on a massive, broad dataset — much of the public internet, books, code, and more — so that it learns general structure in language (and often images, audio, and video) rather than a single task. Because it has absorbed such broad patterns, the same model can summarize text, answer questions, translate languages, write code, extract structured data, and hold a conversation, all steered by the prompt you give it rather than by retraining. The model is a general-purpose starting point that you adapt through prompting, retrieval, or light customization, instead of a single-purpose artifact you build from scratch.

This is the conceptual shift the AIP-C01 exam is built around. Your job as a generative AI developer is no longer to train models — the exam guide explicitly places model development and training out of scope for the candidate. Your job is to integrate pre-built foundation models into applications and business workflows: choosing the right one, invoking it well, grounding it in your data, keeping it safe, and running it cost-effectively in production. That reframing is why the exam is a developer and architect exam, not a data science exam.

### Why a Managed, Multi-Model Service Exists

Once you accept that you will consume FMs rather than build them, a practical problem appears immediately. There are many foundation models, from many providers, each with its own API shape, its own hosting requirements (large models need substantial GPU memory), its own strengths, and its own release cadence. If you integrated directly against each provider, every model swap would mean rewriting code, re-provisioning infrastructure, and renegotiating security and data-handling terms.

Amazon Bedrock exists to remove that friction. Bedrock is a fully managed, serverless service that provides access to a large catalog of foundation models from multiple providers — Amazon (the Nova and Titan families), Anthropic (Claude), Meta (Llama), Mistral, Cohere, AI21 Labs, and others — through a unified set of APIs. You do not provision or manage the GPU infrastructure; you call an API and pay for what you use. Crucially, because Bedrock fronts many models behind a consistent API surface, you can swap one model for another without rewriting your application. That portability is not a minor convenience — it is a core architectural property the exam rewards, because it underpins resilience (failing over to another model or Region), cost optimization (routing cheap queries to cheap models), and future-proofing (adopting a newer model by changing an identifier).

It helps to hold a clear mental separation between the two planes of Bedrock. The control plane (the `bedrock` endpoint) is where you manage resources — listing models, creating custom models, purchasing Provisioned Throughput, configuring evaluation jobs, and setting up logging. The runtime plane (the `bedrock-runtime` endpoint) is where you actually send prompts and receive completions — the InvokeModel and Converse families of operations. Many exam questions hinge on knowing which actions and permissions belong to which plane.

### Tokens, Context Windows, and Why They Govern Everything

You cannot reason about cost, latency, or failure modes on this exam without understanding tokens, so it is worth slowing down here. A token is the unit a model reads and writes. It is not quite a word and not quite a character — it is a chunk produced by the model's tokenizer, where common words may be a single token and rarer words split into several. As a rough working figure for English, a token is about four characters, and 1,000 tokens is roughly 750 words, but the exact mapping is model-specific.

Tokens matter for three reasons that recur throughout the exam:

First, cost. On-demand Bedrock pricing is charged per token, and input tokens and output tokens are usually priced differently. Every word of context you send and every word the model generates has a price. This is why prompt compression, context pruning, and response-length limits are genuine cost levers, not micro-optimizations.

Second, latency. A model generates output one token at a time, so a longer response takes proportionally longer to produce. Time-to-first-token and tokens-per-second are the latency metrics that matter for user experience, and they are why streaming responses (covered in Section 4) exist.

Third, the context window. Every model has a maximum number of tokens it can consider at once — the context window — which must hold the system prompt, the conversation history, any retrieved documents, and the generated response combined. When you exceed it, you do not get a graceful warning; you get truncation, errors, or degraded responses. A large fraction of Domain 5 troubleshooting scenarios trace back to context-window overflow, and the remedies — dynamic chunking, summarizing history, trimming retrieved context — all follow from understanding this single limit.

### Generative Models Versus Embedding Models

Bedrock's catalog contains two fundamentally different kinds of model, and confusing them is a classic exam trap. A generative model takes a prompt and produces new content — text, an image, a structured JSON object. These are the Claude, Llama, Nova, and Mistral models you reach for when you want an answer, a summary, or a decision.

An embedding model does something that looks unrelated but is the quiet engine behind retrieval. It takes a piece of text (or an image) and returns a vector — a fixed-length list of numbers that captures the semantic meaning of the input. Two texts that mean similar things produce vectors that sit close together in that high-dimensional space. You do not read an embedding; you compare it. Embeddings (such as the Amazon Titan Text Embeddings models) are what make semantic search and Retrieval Augmented Generation possible: you embed your documents once, store the vectors, and at query time embed the user's question and find the nearest document vectors. Guide 02 covers RAG and vector stores in depth; for now, the essential distinction is that generative models produce answers while embedding models produce searchable representations, and a RAG architecture uses both — an embedding model to retrieve, then a generative model to answer.

**Diagram (described):** This diagram shows the two model types inside the Amazon Bedrock model catalog and the two distinct paths through them. The first path: a Prompt flows into a generative model (such as Claude, Llama, Nova, or Mistral), which produces generated text or JSON as output. The second, separate path: a piece of text or an image flows into an embedding model (such as Titan Embeddings), which produces a vector embedding; that vector then flows into a vector store, where it is held for later retrieval. The key takeaway the diagram conveys is that generative models output content while embedding models output vectors destined for a searchable store.

### The Model Families on Bedrock

The exam is deliberately written to avoid testing transient version numbers — model versions change far faster than the exam updates, so you should learn capability categories rather than memorize that a particular Claude or Nova point-release exists. At the category level, the catalog gives you a few recognizable archetypes. There are flagship reasoning models that excel at complex, multi-step problems and nuanced instruction-following but cost more and are slower. There are balanced mid-tier models that handle the bulk of production work at moderate cost and latency. There are small, fast, inexpensive models ideal for high-volume, simpler tasks and for the first tier of a cascade. There are multimodal models that accept images, documents, or video alongside text. There are embedding models for retrieval. And there are image and video generation models for content creation.

What matters for the exam is the reasoning skill: given a scenario, match the requirement (lowest cost, lowest latency, largest context, multimodal input, highest reasoning quality, on-premises or edge constraint) to the category of model, and remember that Bedrock's unified API lets you change your mind later by swapping an identifier. Section 2 turns this into a repeatable selection methodology.

### Designing a GenAI Solution: The Task 1.1 Process

Task 1.1 of the exam — analyze requirements and design GenAI solutions — is about disciplined design before you write a line of integration code. The exam expects you to reason in roughly this order. Start from the business need and the technical constraints: what is the user trying to accomplish, what latency and cost budget exists, what data is involved and where must it live, and what accuracy and safety bar must be cleared. From those constraints, derive an architecture — which integration pattern (direct invocation, RAG, agent), which deployment strategy, and which class of model. Validate feasibility with a proof-of-concept on Bedrock before committing to full build-out, because a quick PoC surfaces latency, quality, and cost realities that a design document cannot. And standardize the reusable pieces so that multiple workloads share consistent components rather than each team reinventing the integration.

AWS gives this process a named reference: the AWS Well-Architected Framework Generative AI Lens, accessed through the Well-Architected Tool. The Lens applies the familiar pillars — operational excellence, security, reliability, performance efficiency, cost optimization, and sustainability — to the specifics of generative AI workloads. When an exam question asks how to ensure a GenAI design aligns with best practices or how to systematically review a generative AI workload, the Generative AI Lens is the intended answer, just as the broader Well-Architected Framework is the answer for general architecture questions.

### Exam-Relevant Distinctions

| If the exam says... | The answer is... | Why |
|---|---|---|
| "Need to summarize, classify, and answer with one model" | A single foundation model steered by prompts | FMs are general-purpose; the task is set by the prompt, not by retraining |
| "Swap models without rewriting the app" | Amazon Bedrock unified API (Converse) | Bedrock fronts many models behind one API surface |
| "Convert documents into searchable vectors" | An embedding model, not a generative model | Embeddings produce vectors for similarity search, not answers |
| "Systematically review a GenAI workload's best practices" | Well-Architected Generative AI Lens (WA Tool) | The Lens applies WA pillars to generative AI |
| "Responses get cut off / errors on long inputs" | Context-window overflow | All context plus output must fit the token limit |
| "Manage models, buy throughput, configure logging" | Control plane (bedrock endpoint) | Resource management is control plane, not runtime |

- A token is roughly four English characters; ~1,000 tokens ≈ ~750 words, but the exact mapping is model-specific.
- Input tokens and output tokens are usually priced differently on on-demand pricing.
- The context window must hold system prompt + history + retrieved context + the generated output, all together.
- Model development and training are out of scope for the candidate — the exam tests integration, not training.
- The runtime endpoint is `bedrock-runtime` (invoke/converse); the control endpoint is `bedrock` (manage resources).

### Knowledge Check

**Q1:** A team wants their application to use a cheaper foundation model next quarter without changing application code. Which property of Amazon Bedrock makes this possible?
- A) Bedrock automatically retrains models on your data
- B) Bedrock exposes many models behind a unified API, so swapping a model is an identifier change
- C) Bedrock converts all models to a single proprietary format at runtime
- D) Bedrock requires a separate SDK per model provider

**A:** B — Bedrock's value here is the unified API surface (especially the Converse API). Because many models sit behind one consistent contract, changing models is largely a matter of changing the model identifier rather than rewriting integration code. A is wrong (Bedrock does not auto-retrain), C misstates how it works, and D is the opposite of the truth.

**Q2:** True or False — An embedding model is the right choice when you need the system to generate a written answer to a user's question.

**A:** False. An embedding model converts text into vectors for similarity search; it does not produce written answers. Generating an answer is the job of a generative model. In a RAG system you use both: an embedding model to retrieve relevant context, then a generative model to write the answer grounded in that context.

**Q3:** A chatbot starts returning truncated and incoherent responses only after long multi-turn conversations. What is the most likely root cause?

**A:** Context-window overflow. As the conversation grows, the accumulated history plus the system prompt plus the new response eventually exceeds the model's maximum token context. The fixes are to summarize or trim older turns, cap response length, and manage the running token budget — all of which follow from understanding that everything must fit in one fixed token window.

**Q4:** Which task is OUT of scope for the AIP-C01 candidate, per the exam guide?
- A) Selecting and configuring foundation models
- B) Designing RAG architectures
- C) Training and developing foundation models from scratch
- D) Integrating FMs into business workflows

**A:** C — The exam guide explicitly lists model development and training, advanced ML techniques, and data/feature engineering as out of scope. The candidate's role is to integrate, deploy, secure, and optimize existing foundation models. A, B, and D are all in scope.

> **Source attribution:** This section combines the AIP-C01 strategy/blueprint material with MCP-researched AWS documentation (Amazon Bedrock "What is Bedrock", "Models at a glance", "What are Foundation Models"). Token/context-window framing is standard FM knowledge applied to the exam's cost, latency, and troubleshooting themes.

---

## Section 2: Model Selection

### Selection Is an Engineering Decision, Not a Preference

A surprising number of exam questions are, at heart, model-selection questions wearing a costume. They describe a workload — a customer-facing chatbot that must respond in under a second, a nightly job that summarizes ten thousand documents, a legal-research assistant that must reason carefully over dense contracts — and ask you to pick the model or the approach. The wrong instinct is to reach for the most capable model every time. The right instinct is to treat selection as a constrained optimization: find the cheapest, fastest model that still clears the quality bar for this specific task. The exam consistently rewards that discipline and punishes over-provisioning.

To make that decision repeatable, evaluate every candidate model against the same set of dimensions.

Capability fit is whether the model is actually good enough at the task. A flagship reasoning model and a small fast model can both write a polite email, but only one of them reliably reasons through a multi-step legal analysis. Match the model's strength to the hardest thing the task requires, not the easiest.

Cost is the price per input token and per output token. These are usually different numbers, and for high-volume workloads the gap between a small model and a flagship model compounds into the dominant line item. Always estimate cost at expected volume, not per call.

Latency is how quickly the model responds, which splits into time-to-first-token (what the user perceives as responsiveness, especially with streaming) and overall generation time. Smaller models are generally faster. For interactive use cases, AWS also offers latency-optimized configurations of certain models.

Context window is the maximum tokens the model can hold. A task that stuffs large retrieved documents or long histories into the prompt needs a model with enough room; a short-prompt task does not pay for a large window it will not use.

Modality is which input and output types the model handles. If the task involves analyzing images, scanned documents, or video, you need a multimodal model; a text-only model is simply disqualified regardless of its other strengths.

Availability is whether the model is offered in the Regions you need and whether it supports the inference profiles (including cross-Region inference) your resilience and data-residency requirements demand. A perfect model that is not available where your data must stay is the wrong model.

### Using Benchmarks and Bedrock Model Evaluation

The exam expects you to ground selection in evidence rather than reputation, which maps to Skill 1.2.1 — assess and choose FMs using performance benchmarks, capability analysis, and limitation evaluation. Public benchmarks give you a first-pass shortlist, but they rarely reflect your actual data and task. The AWS-native way to close that gap is Amazon Bedrock model evaluation, which lets you compare models on your own prompts before you commit.

Bedrock evaluations come in three flavors, and knowing them is directly testable. Programmatic (automatic) evaluations compute metrics over a built-in or custom prompt dataset across task types like open-ended generation, summarization, question answering, and classification. Human-based evaluations bring your own employees or subject-matter experts in to rate and compare outputs, which is the right choice when quality is subjective or domain-specific. LLM-as-a-judge evaluations use a second model to score the first model's responses and explain the scores, giving you much of the nuance of human evaluation at a fraction of the time and cost. The same evaluation machinery extends to RAG sources and knowledge bases (covered in Guide 02 and Guide 08), where it measures retrieval relevance and answer correctness against ground-truth data.

The exam-relevant takeaway: when a question asks how to choose between two models for a specific use case, or how to validate that a model is good enough before production, the answer is a Bedrock model evaluation job using a dataset representative of your workload — not a public leaderboard, and not intuition.

### The First-Class Decision: RAG vs Fine-Tuning vs Prompt Engineering

Before you even pick a model, there is a more consequential architectural fork that the exam returns to again and again: how will you get the model to behave the way you need? There are three levers, and they are not interchangeable.

Prompt engineering steers the model purely through instructions, examples, and formatting in the prompt. It changes no infrastructure, costs nothing beyond the tokens, and iterates in seconds. It is the right first move for controlling tone, format, and behavior. Its ceiling is that it cannot give the model knowledge it never had.

RAG (Retrieval Augmented Generation) supplies the model with relevant facts at query time by retrieving them from your own data and inserting them into the prompt. It is the right choice when the model needs current, private, or frequently-changing information — a product catalog, internal policies, last week's tickets. It keeps data fresh (update the store, not the model), keeps source data auditable, and avoids the cost and rigidity of retraining. RAG is the default answer to "the model does not know our facts."

Fine-tuning adjusts the model's own parameters by training it on labeled examples, baking behavior, tone, or domain style into the weights. It is the right choice when you need consistent specialized behavior or format that prompting cannot reliably enforce, or when you want to reduce prompt size by teaching the model a task once. It is the most expensive and least flexible option: it costs training tokens and storage, it must be redone when the base model updates, and a fine-tuned Bedrock model requires Provisioned Throughput to invoke (Section 5 and Section 7). Fine-tuning is rarely the answer to a freshness problem — that is what RAG is for.

**Diagram (described):** This is a decision tree branching on the question "What does the model need?" There are three branches. If the need is tone, format, or behavior only, the answer is prompt engineering — no infrastructure, instant to apply. If the need is current or private facts, the answer is RAG — retrieve facts at query time. If the need is baked-in specialized behavior, the answer is fine-tuning — train the weights, which then requires Provisioned Throughput to serve. The diagram visually reinforces that the three levers map to three distinct kinds of need.

The single most common trap in this area is choosing fine-tuning when the real requirement is fresh or private knowledge. If the scenario stresses that information changes often or must be kept current, RAG wins on cost, freshness, and simplicity almost every time.

### Model Cascading and Tiering

Selection does not have to pick one model for all traffic. A powerful cost pattern — which the exam treats as both a selection strategy (Skill 1.2) and a cost-optimization strategy (Skill 4.1.2) — is to tier models by query complexity. Send every request first to a small, cheap, fast model. If that model can answer confidently, you are done at a fraction of the cost. If the query is too complex, or a confidence check fails, escalate to a larger, more capable model. Because most real-world traffic is routine, the cascade routes the bulk of requests to the cheap tier and reserves the expensive model for the minority that genuinely need it. The result is a large cost reduction with little quality loss. Section 8 covers the routing mechanics (static, dynamic, and metric-based) that implement cascading in practice.

### Selection Decision Matrix

| Requirement emphasized in the scenario | Selection guidance |
|---|---|
| Lowest possible cost at high volume | Smallest model that clears the quality bar; add a cascade |
| Lowest latency / real-time UX | Small or latency-optimized model + streaming |
| Largest context (big documents, long history) | Model with the largest context window; consider RAG to limit context |
| Image, document, or video input | A multimodal model (text-only models are disqualified) |
| Hardest reasoning / nuanced instructions | Flagship reasoning model, accept higher cost/latency |
| Model must not know our private data yet does | RAG, not fine-tuning |
| Consistent specialized format/behavior prompting cannot enforce | Fine-tuning (remember Provisioned Throughput) |
| Validate "good enough" before production | Bedrock model evaluation on a representative dataset |

### Exam-Relevant Distinctions

| If the exam says... | The answer is... | Why |
|---|---|---|
| "Information changes daily / is private" | RAG | Freshness and private data are RAG's domain, not fine-tuning |
| "Choose between two models for our use case" | Bedrock model evaluation job | Evidence on your data beats public benchmarks |
| "Subjective or domain-expert quality judgment" | Human-based evaluation | Some quality is not machine-measurable |
| "Score responses cheaply at scale with explanations" | LLM-as-a-judge evaluation | A judge model approximates human rating at lower cost |
| "Reduce cost with minimal quality loss across mixed traffic" | Model cascading / tiering | Cheap model first, escalate only the hard queries |
| "Need to analyze scanned invoices (images)" | Multimodal model | Modality requirement disqualifies text-only models |

- Always estimate cost at expected volume, not per single call — token pricing compounds.
- A fine-tuned Bedrock model has no base-model on-demand path — serve it via Provisioned Throughput (steady high volume, guaranteed throughput) or a custom model deployment for on-demand inference (variable/low traffic) *(point-in-time)*.
- Public benchmarks build the shortlist; Bedrock evaluation makes the decision.
- "Latency-optimized" model configurations exist for time-sensitive interactive workloads.

### Knowledge Check

**Q1:** A retailer's assistant must answer questions about a product catalog that changes several times a day. Engineers propose fine-tuning a model nightly on the latest catalog. What is the better approach and why?
- A) Fine-tune more frequently, every hour instead of nightly
- B) Use RAG to retrieve current catalog data at query time
- C) Switch to the largest available model
- D) Increase the model's temperature

**A:** B — When information changes frequently, RAG is the correct pattern: update the vector store and the model immediately reflects current data, with no retraining cost or lag. Nightly (or hourly) fine-tuning is expensive, slow to reflect changes, and brittle. C and D address neither freshness nor knowledge. This RAG-vs-fine-tuning-for-freshness trap is one of the most common on the exam.

**Q2:** You need to decide which of two foundation models performs better for your specific summarization use case, and quality is somewhat subjective. Which Bedrock capability fits best?

**A:** A Bedrock model evaluation job. For subjective, domain-specific quality, a human-based evaluation (your employees or subject-matter experts rating outputs) is ideal; for faster, cheaper scoring at scale, an LLM-as-a-judge evaluation works. Either way the decision is grounded in a Bedrock evaluation on a dataset representative of your workload, not a public benchmark.

**Q3:** A support application sees 90% routine FAQ queries and 10% complex troubleshooting. Leadership wants to cut FM cost without hurting answer quality. Which pattern applies?

**A:** Model cascading / tiering. Route all traffic to a small, cheap model first; escalate only the queries it cannot handle confidently to a larger model. Because most traffic is routine, the bulk is served cheaply and the expensive model handles only the 10% that need it — a large cost reduction with minimal quality impact.

**Q4:** True or False — Prompt engineering can give a foundation model knowledge of your company's private documents that it was never trained on.

**A:** False. Prompt engineering steers behavior, tone, and format using instructions and examples, but it cannot inject knowledge the model never had unless you also place that knowledge in the prompt — which is exactly what RAG automates by retrieving and inserting relevant private data at query time. Prompting alone changes how the model responds, not what facts it knows.

> **Source attribution:** Selection methodology and the RAG/fine-tune/prompt decision are synthesized from the AIP-C01 blueprint (Skills 1.2.1, 4.1.2) and MCP-researched Amazon Bedrock evaluation documentation (programmatic, human, and LLM-as-a-judge evaluations).

---

## Section 3: Inference Parameters

### Why These Knobs Exist

When a foundation model generates text, it does not simply "know" the next word. At each step it computes a probability distribution over all possible next tokens — for the prompt "I hear the hoofbeats of", it might assign 0.7 to "horses", 0.2 to "zebras", and 0.1 to "unicorns" — and then it samples one token from that distribution. Inference parameters are the controls that reshape that distribution or limit the final output. They do not change the model's knowledge; they change how it chooses among the possibilities it already sees. Understanding them is what lets you make the same model behave deterministically for data extraction and creatively for marketing copy, and the exam tests this directly under Skill 4.2.4 (appropriate temperature and top-k/top-p selection based on requirements).

A critical caveat up front: default values and valid ranges are model-specific. Temperature might range 0–1 on one model family and 0–2 on another. The exam tests the conceptual effect of each parameter, not a specific numeric default, so learn the direction of each knob rather than memorizing a number.

### Randomness and Diversity: Temperature, Top K, Top P

Temperature controls how sharply the model favors its highest-probability tokens. Technically, it reshapes the probability mass function over next tokens. A low temperature steepens the distribution, concentrating probability on the most likely tokens and producing more deterministic, repeatable, conservative output. A high temperature flattens the distribution, raising the chance of lower-probability tokens and producing more varied, creative, surprising output. In the hoofbeats example, raising temperature increases the chance the model picks "unicorns" and decreases the dominance of "horses". Use low temperature when you want consistency and correctness (extraction, classification, factual answering); use higher temperature when you want diversity (brainstorming, creative writing).

Top K limits how many candidate tokens the model is even allowed to consider, by count. If Top K is 50, the model samples only from the 50 most probable next tokens and ignores the long tail entirely. A lower Top K narrows the pool to safer, higher-probability options; a higher Top K admits more unusual choices. In the example, Top K of 2 means the model considers only "horses" and "zebras" and never "unicorns".

Top P (nucleus sampling) limits the candidate pool by cumulative probability rather than by fixed count. If Top P is 0.7, the model considers only the smallest set of top tokens whose probabilities add up to 70%, then samples from that set. In the example, Top P of 0.7 admits only "horses" (0.7 alone reaches the threshold), while Top P of 0.9 admits "horses" and "zebras". The advantage of Top P over Top K is that the pool size adapts to the model's confidence: when the model is very sure, the nucleus is tiny; when it is uncertain, the nucleus widens automatically.

Temperature, Top K, and Top P interact, and tuning all three aggressively at once tends to produce unpredictable results. A common, stable practice is to fix one sampling strategy and adjust temperature as the primary creativity dial.

### Length and Repetition Controls

The second family of parameters limits the output rather than reshaping the distribution.

Maximum response length (max tokens) caps how many tokens the model may generate. This is both a cost control (you pay per output token) and a safeguard against runaway generation. Set it deliberately: too low and you truncate useful answers, too high and you risk cost and latency.

Stop sequences tell the model to halt generation as soon as it produces a specified string. They are invaluable for structured output — if you want a single JSON object, a stop sequence can end generation right after the closing brace so the model does not ramble on.

Penalties discourage particular patterns in the output. Frequency and presence penalties reduce the likelihood of repeating tokens that have already appeared, which combats the repetitive, looping output that low-temperature generation can sometimes produce. Length penalties influence how strongly the model is pushed toward shorter or longer responses.

### Parameter Effect Summary

| Parameter | Effect of lower value | Effect of higher value |
|---|---|---|
| Temperature | More deterministic; favors high-probability tokens | More random/creative; admits low-probability tokens |
| Top K | Smaller candidate pool; safer tokens | Larger candidate pool; more unusual tokens |
| Top P | Smaller nucleus; safer tokens | Larger nucleus; more unusual tokens |
| Max tokens | Shorter, possibly truncated output | Longer output; higher cost and latency |

### Mapping Parameters to Use Cases

The exam frequently gives a use case and asks for settings. Reason from the requirement to the knobs:

Deterministic, factual, or structured tasks — data extraction, classification, SQL generation, anything that must be repeatable — call for low temperature (often near zero) and a narrow Top P or Top K. You want the model to make the safe, high-probability choice every time. Pair this with a JSON-oriented prompt and a stop sequence when you need structured output.

Balanced conversational tasks — a general assistant or support chatbot — use moderate temperature so responses feel natural without going off the rails.

Creative tasks — brainstorming, marketing copy, story generation, generating varied alternatives — call for higher temperature and a wider Top P to let the model explore less obvious choices.

A useful memory aid: if the scenario rewards the same answer every time, turn the randomness down; if it rewards variety, turn it up.

### Exam-Relevant Distinctions

| If the exam says... | The answer is... | Why |
|---|---|---|
| "Responses must be consistent and repeatable" | Low temperature (near 0) | Steep distribution favors the safe, high-probability token |
| "Output is too repetitive / loops" | Raise temperature or add frequency/presence penalty | Penalties discourage repeated tokens; flatter distribution adds variety |
| "Need creative, varied options" | Higher temperature, wider Top P | Admits lower-probability, more diverse tokens |
| "Limit a single JSON object, stop after it" | Stop sequence + low temperature | Stop sequence halts generation at the closing token |
| "Control cost per response" | Lower max tokens | You pay per output token; capping length caps cost |
| "What is the default temperature for model X" | It is model-specific | The exam tests effects, not specific numeric defaults |

- Default values and valid ranges differ by model — learn the direction of each knob, not a number.
- Top P adapts pool size to model confidence; Top K uses a fixed count regardless of confidence.
- Tuning temperature, Top K, and Top P all at once aggressively produces unpredictable output — adjust one primary dial.
- Stop sequences are an output-shaping tool, not a safety filter (safety is Guardrails, covered in the safety guide).

### Knowledge Check

**Q1:** An application extracts invoice fields into a fixed JSON schema and must return identical output for identical inputs. Which inference settings are most appropriate?
- A) High temperature, high Top P
- B) Low temperature (near 0), narrow Top P, plus a stop sequence
- C) High temperature, low max tokens
- D) Default temperature with frequency penalty maximized

**A:** B — Deterministic, structured extraction wants the model to make the safest, highest-probability choice every time. Low temperature steepens the distribution toward determinism, a narrow Top P keeps the candidate pool tight, and a stop sequence cleanly ends the JSON. High temperature (A, C) introduces variability, which is exactly what you do not want for repeatable extraction.

**Q2:** Fill in the blank — ___ limits the candidate token pool by cumulative probability, so the pool automatically shrinks when the model is confident and widens when it is uncertain.

**A:** Top P (nucleus sampling). Unlike Top K, which always considers a fixed number of tokens, Top P considers the smallest set of top tokens whose probabilities sum to the threshold (e.g., 0.9), so the effective pool size adapts to the model's confidence at each step.

**Q3:** A marketing team complains that a copy-generation feature keeps producing nearly identical, repetitive phrasing. Which two adjustments most directly help?

**A:** Raise the temperature (flattening the distribution so the model explores more varied, lower-probability tokens) and/or apply a frequency/presence penalty (which directly discourages repeating tokens that have already appeared). Both push the output toward more diverse phrasing, which is what a creative task wants.

**Q4:** True or False — Setting temperature to 0.2 on Bedrock guarantees the same numeric meaning across every model in the catalog.

**A:** False. Parameter ranges and defaults are model-specific; a temperature of 0.2 does not map to an identical distribution shape across all model families, and some models use different valid ranges. The exam tests the conceptual effect (lower = more deterministic), not a universal numeric meaning.

> **Source attribution:** Parameter definitions and the temperature/Top K/Top P/length controls are MCP-researched from the Amazon Bedrock "Influence response generation with inference parameters" documentation; use-case mapping reflects Skill 4.2.4 of the exam blueprint.

---

## Section 4: Invocation APIs

### Two Ways to Call a Model, and Why One Is Preferred

Once you have selected a model, you have to actually call it, and Bedrock's runtime plane gives you two families of operations to do so. The older, lower-level family is InvokeModel (and its streaming sibling InvokeModelWithResponseStream). The newer, higher-level family is the Converse API (Converse, and ConverseStream for streaming). Both reach a model on the bedrock-runtime endpoint, both produce a completion, and a question that asks "how do you invoke a Bedrock model" can be answered by either — but the exam wants you to understand why the Converse API is the recommended default.

The problem with InvokeModel is that its request and response bodies are model-specific. Each provider expects a different JSON shape for the prompt, the parameters, and the response. If you write your integration against Anthropic's body format and later want to try a Llama model, you rewrite the request construction and response parsing. That directly undermines the portability that made Bedrock attractive in the first place.

The Converse API solves this by providing a single, consistent request and response structure that works across all models that support messages. You write your code once — the same messages, roles, and inference configuration — and it works against different models. When a model has unique parameters that the unified structure does not cover, Converse lets you pass them through a model-specific escape hatch (additionalModelRequestFields) without abandoning the consistent core. The Converse API also natively supports tool use (function calling, central to agents in Guide 04) and guardrails (Guide 06), which is why it is the foundation that later capabilities build on. The practical rule: prefer Converse for portability; reach for InvokeModel only when you have a specific reason to work with a model's raw native format.

### The Shape of a Converse Request

The Converse API organizes a conversation as an array of messages, each with a role and content. The role is either user (input sent to the model) or assistant (the model's own responses). To maintain context across a multi-turn conversation, you resend the full message history on each call, appending the latest user message — Bedrock itself stores nothing between calls, so the conversation lives in your application and is replayed each turn. This statelessness is important: it is why long conversations grow the token count (and risk context-window overflow, Section 1) and why you, not Bedrock, own conversation history (often in DynamoDB, per the prompt-engineering guide).

Beyond messages, a Converse request carries a few key fields. The system field sets system prompts — instructions or persona that frame the whole conversation. The inferenceConfig field carries the model-agnostic inference parameters from Section 3 (temperature, top P, max tokens, stop sequences). The guardrailConfig field attaches a guardrail to the request, and toolConfig declares tools the model may call. The modelId in the request header specifies which model — or which inference profile — to invoke; swapping that identifier is exactly the low-friction model switch Section 1 described.

One exam-relevant nuance: when you use a prompt from Bedrock Prompt Management with Converse, you cannot also pass system, inferenceConfig, or toolConfig inline, because those are defined in the managed prompt; you supply promptVariables instead. Calling Converse requires the bedrock:InvokeModel permission, and calling ConverseStream requires bedrock:InvokeModelWithResponseStream — the streaming permission is distinct.

### Multimodal Content Blocks

Within a message, content is an array of content blocks, and this is how the Converse API handles more than plain text. A block can be text, an image, a document, or video (subject to the chosen model's capabilities — a text-only model rejects an image block). You provide the media either as raw bytes inline in the request or by pointing to an Amazon S3 URI, which is the better choice for larger files since it avoids inflating the request payload. This block structure is what makes multimodal pipelines (Skill 1.3.2) straightforward: the same Converse call that sends a question can also attach the scanned document the question is about. If you send an image block with no accompanying text, the model will simply describe the image.

### Synchronous, Streaming, and Asynchronous Patterns

How you invoke shapes the user experience, and the exam tests three interaction patterns.

Synchronous invocation is the simplest: call Converse, wait, receive the complete response. It fits request/response APIs and short completions where the caller can block briefly. Its weakness is perceived latency — for a long answer, the user stares at nothing until the entire response is generated.

Streaming invocation (ConverseStream) addresses that by delivering the response incrementally, token chunk by token chunk, as the model generates it. The user sees text appear almost immediately — the time-to-first-token experience of every modern chat interface. Streaming is what you build real-time delivery on: server-sent events (SSE) or WebSockets push chunks to a browser, and API Gateway can use chunked transfer encoding to relay them (Skill 2.4.2). When a scenario stresses immediate feedback or a typing-style UX, streaming is the answer.

Asynchronous invocation decouples the request from the response entirely, for workloads where the caller should not wait at all. You place requests on a queue (Amazon SQS), process them with workers using the language-specific AWS SDK, and deliver results when ready (Skill 2.4.1). This suits background processing and smoothing bursty traffic. For very large volumes of independent prompts, batch inference (Section 5) is the purpose-built asynchronous mechanism.

**Diagram (described):** This diagram shows an application choosing among three interaction patterns based on its interaction need. From the application, a decision node "Interaction need" branches three ways. If the need is short and the caller can wait, the path goes to synchronous Converse, which returns a full response. If the need is a real-time user experience, the path goes to ConverseStream (streaming), which then delivers chunks via server-sent events or WebSockets through API Gateway. If the need is no-wait background processing, the path goes to SQS plus SDK workers (asynchronous), and the result is delivered later. The diagram maps each interaction requirement to its matching invocation pattern.

### Exam-Relevant Distinctions

| If the exam says... | The answer is... | Why |
|---|---|---|
| "Write once, run across multiple models" | Converse API | Consistent request/response across all message-capable models |
| "Need a model's unique native parameter format" | InvokeModel (or Converse additionalModelRequestFields) | InvokeModel exposes raw model-specific bodies |
| "Show the response as it is typed, immediately" | ConverseStream + SSE/WebSockets | Streaming delivers chunks as generated |
| "Process many prompts in the background, no waiting" | Async via SQS + SDK (or batch inference) | Decouples request from response |
| "Maintain multi-turn context" | Resend full message history each call | Bedrock is stateless; the app owns history |
| "Attach a scanned document to the question" | A document/image content block (inline bytes or S3 URI) | Converse content blocks carry multimodal input |
| "Streaming call permission" | bedrock:InvokeModelWithResponseStream | Streaming uses a distinct permission from non-streaming |

- Converse requires bedrock:InvokeModel; ConverseStream requires bedrock:InvokeModelWithResponseStream.
- Bedrock stores no conversation state — the application replays history each turn.
- Larger media should be passed by S3 URI rather than inline bytes to keep payloads small.
- With a Prompt Management prompt, you cannot also pass system/inferenceConfig/toolConfig inline — use promptVariables.
- The Converse API natively supports tool use and guardrails; InvokeModel is lower-level.

### Knowledge Check

**Q1:** A team wants to build their integration once and be able to switch among Claude, Llama, and Nova models with minimal code changes. Which API should they standardize on?
- A) InvokeModel, with a separate code path per provider
- B) The Converse API
- C) A custom wrapper that calls each provider's native REST endpoint
- D) InvokeModelWithResponseStream only

**A:** B — The Converse API provides a consistent request/response structure across all message-capable models, so switching models is largely a modelId change. InvokeModel (A) uses model-specific body formats that force per-provider code. C reintroduces exactly the friction Bedrock removes, and D is just the streaming variant of the low-level API.

**Q2:** A chatbot built on Converse "forgets" everything from earlier in the conversation on each new turn. What is the most likely cause?

**A:** The application is not resending the prior message history. Bedrock is stateless and stores no conversation context between calls, so the application must include the full array of previous user/assistant messages (plus the new message) on each Converse request. Maintaining context is the caller's responsibility, which is also why long conversations accumulate tokens.

**Q3:** Which interaction pattern best fits a customer-facing assistant that must show the answer appearing in real time as it is generated?
- A) Synchronous Converse, returning the full response
- B) ConverseStream delivering chunks over SSE or WebSockets
- C) Batch inference via S3
- D) SQS-based asynchronous processing

**A:** B — Real-time, incremental display is exactly what streaming (ConverseStream) provides, with chunks pushed to the client via server-sent events or WebSockets (often relayed through API Gateway). Synchronous (A) makes the user wait for the whole response. Batch (C) and async SQS (D) are for background, no-wait workloads, not interactive UX.

**Q4:** True or False — To analyze a scanned PDF with a question about it, you must first run OCR yourself and send only extracted text to the model.

**A:** False (for multimodal models). The Converse API supports document and image content blocks, so you can attach the document directly (inline bytes or an S3 URI) alongside your text question, and a multimodal model can process it. You would only need separate OCR if you deliberately chose a text-only model or a dedicated extraction service like Amazon Textract for a specific pipeline reason.

> **Source attribution:** API behavior is MCP-researched from the Amazon Bedrock "Inference using Converse API" documentation (messages/roles/content blocks, system, inferenceConfig, guardrailConfig, Prompt Management restrictions, streaming, permissions). Interaction patterns map to Skills 2.4.1 and 2.4.2 of the exam blueprint.

---

## Section 5: Inference Modes

### The Same Model, Three Economic Models

Selecting a model and calling it correctly still leaves one decision that drives both cost and behavior: how you provision capacity for inference. Amazon Bedrock offers three modes — on-demand, Provisioned Throughput, and batch — and the exam tests when each is appropriate because the wrong choice either wastes money or fails to meet throughput and latency requirements. The same model can be served under any of these modes; what changes is the billing model, the throughput guarantee, and the operational constraints.

### On-Demand: Pay Per Token, No Commitment

On-demand is the default mode and the one most applications start with. You call the model, and you are billed per token — input tokens and output tokens, at the model's published rates — with no upfront commitment and no minimum. Capacity is shared, subject to account-level rate quotas, and a sudden burst can encounter throttling (ThrottlingException), which you handle with retries and backoff (Section 8) or by smoothing traffic.

On-demand is the right answer when traffic is variable or unpredictable, when you are prototyping, or when volume is low to moderate. Its great virtue is that you pay only for what you use and never for idle capacity. Its limitation is that it offers no dedicated throughput guarantee and no protection from shared-capacity throttling at high scale, and it cannot serve a custom (fine-tuned) model.

### Provisioned Throughput: Dedicated Capacity at a Fixed Cost

Provisioned Throughput reserves dedicated model-invocation capacity for a fixed hourly price. You purchase it in units of Model Units (MUs). A Model Unit delivers a specific, guaranteed level of throughput for the chosen model — defined as a number of input tokens it can process per minute and a number of output tokens it can generate per minute, aggregated across all your requests in that minute. Buy more MUs to get more guaranteed throughput.

Two operational details are heavily testable. First, before you can purchase Provisioned Throughput with a commitment, you must request a Model Unit quota increase through AWS Support — MUs are not available by default in arbitrary quantity. Second, you choose a commitment term: no commitment (delete any time), one month, or six months, with longer commitments earning a deeper hourly discount. Billing is hourly and continues until you delete the provisioned model.

The single most important rule about Provisioned Throughput on this exam: a customized (fine-tuned, distilled, or imported) model can only be used through Provisioned Throughput. You cannot invoke a custom Bedrock model on-demand. This is the link back to Section 2 and forward to Section 7 — whenever a scenario involves a fine-tuned model in production, Provisioned Throughput is implied. Beyond that hard requirement, Provisioned Throughput is the right choice for steady, high-volume, latency-sensitive production traffic where guaranteed throughput justifies the fixed cost, and where on-demand throttling would be unacceptable.

### Batch Inference: Asynchronous Bulk Processing via S3

Batch inference is built for processing a large number of prompts efficiently when you do not need any of them answered in real time. You format your inputs as files (using the InvokeModel or Converse format), upload them to Amazon S3, submit a single batch job pointing at that bucket, and Bedrock processes the prompts asynchronously and writes the responses back to S3. You can be notified of completion via EventBridge rather than polling. Because it processes in bulk off the interactive path, batch is typically offered at a lower price than on-demand for the same model, which makes it the cost-optimal choice for large offline workloads like document summarization, bulk classification, or dataset enrichment.

Batch carries constraints the exam likes to test. Batch inference is not supported for provisioned models — it is its own mode, not something you layer on Provisioned Throughput. And batch does not support tool calling (function calling) or structured output / response_format, because each record is processed independently with no multi-turn interaction; anything that requires back-and-forth between model and client is unavailable in batch. So a scenario that needs an agent to call tools, or a strictly enforced JSON schema via response_format, rules batch out.

### Comparison of Inference Modes

| Dimension | On-Demand | Provisioned Throughput | Batch Inference |
|---|---|---|---|
| Billing model | Per token, no commitment | Hourly per Model Unit, optional 1/6-month commitment | Per token, typically discounted vs on-demand |
| Throughput | Shared, subject to quotas/throttling | Dedicated, guaranteed by MUs | High aggregate, asynchronous |
| Latency profile | Real-time | Real-time, guaranteed capacity | Not real-time (async) |
| Custom models | Not supported | Required for custom models | Not supported for provisioned; check model support |
| Tool calling / structured output | Supported | Supported | Not supported |
| Best-fit use case | Variable/low-moderate traffic, prototyping | Steady high-volume, latency-sensitive, custom models | Large offline bulk jobs, cost-sensitive |

### Connecting to Cost Optimization

Inference-mode choice is one of the clearest levers in Domain 4 (cost and performance). The reasoning the exam rewards: do not pay for dedicated capacity you do not consistently use (avoid Provisioned Throughput for spiky low volume), do not let critical high-volume traffic suffer shared-capacity throttling (do use Provisioned Throughput when volume is steady and high), and push anything that can tolerate delay onto batch to capture the lower price. Provisioned throughput optimization and batching strategies are named cost techniques in the blueprint precisely because mode selection moves the bill substantially.

### Exam-Relevant Distinctions

| If the exam says... | The answer is... | Why |
|---|---|---|
| "Use a fine-tuned/custom model in production" | Provisioned Throughput (steady high volume) or custom model deployment (on-demand, variable traffic) | Custom models need their own serving surface — never the base-model ARN |
| "Spiky, unpredictable, or low traffic" | On-demand | Pay per use, no idle commitment |
| "Steady high volume, guaranteed throughput, no throttling" | Provisioned Throughput | Dedicated MU capacity |
| "Summarize 100,000 documents overnight, cheapest" | Batch inference | Async bulk via S3 at a lower price |
| "Agent must call tools / strict JSON schema" | Not batch | Batch supports neither tool calling nor structured output |
| "Lower hourly price for provisioned capacity" | Longer commitment term (1 or 6 months) | Longer commitment = deeper discount |

- Provisioned Throughput is sold in Model Units (MUs); each MU guarantees input and output tokens per minute.
- You must request an MU quota increase via AWS Support before purchasing committed Provisioned Throughput.
- Provisioned Throughput billing is hourly and continues until you delete the provisioned model.
- Batch inference is not supported for provisioned models, and does not support tool calling or structured output.
- Batch input/output flows through Amazon S3; completion can be signaled via EventBridge.

### Knowledge Check

**Q1:** A company fine-tuned a foundation model in Bedrock and now wants to serve steady, high-volume production traffic with guaranteed throughput. Which inference mode fits?
- A) On-demand
- B) Batch inference
- C) Provisioned Throughput
- D) Any mode; it makes no difference

**A:** C — Guaranteed throughput for a custom model means Provisioned Throughput. A custom model is never invoked via the base-model ARN; current docs give two serving surfaces — a custom model deployment for on-demand inference (pay-per-token, no throughput guarantee; variable/low traffic) and Provisioned Throughput (dedicated Model Units) — and the steady high-volume, guaranteed-throughput requirement selects Provisioned Throughput. Batch (B) is offline bulk; on-demand via a custom model deployment (A) cannot guarantee throughput. *(Point-in-time — the on-demand custom-model path is newer; re-verify near exam day.)*

**Q2:** Fill in the blank — Provisioned Throughput capacity is purchased in units called ___, each of which guarantees a defined number of input and output tokens per minute.

**A:** Model Units (MUs). You buy a number of MUs for a model, and each MU delivers a specific guaranteed throughput. Committed purchases require requesting an MU quota increase through AWS Support first, and longer commitment terms (1 or 6 months) lower the hourly price.

**Q3:** An offline pipeline must summarize 250,000 archived documents as cheaply as possible, with no latency requirement. An engineer proposes using a Bedrock Agent that calls tools to enrich each summary, run as a batch job. What is wrong with this plan?

**A:** Batch inference does not support tool calling (function calling) or structured output, because each record is processed independently with no multi-turn interaction. The bulk, no-latency, cost-sensitive part correctly points to batch, but the tool-calling agent requirement is incompatible with batch. Either drop the tool calling for the batch path, or run the tool-calling workflow through a real-time/async invocation path instead.

**Q4:** True or False — Choosing Provisioned Throughput for a low-volume, highly variable workload is a good cost-optimization decision.

**A:** False. Provisioned Throughput bills hourly for dedicated capacity whether or not you use it, so for spiky, low-volume traffic you would pay for idle capacity. On-demand (pay-per-token) is the cost-appropriate choice for variable or low traffic; Provisioned Throughput pays off only for steady, high, latency-sensitive volume (or when a custom model forces it).

> **Source attribution:** Inference-mode specifications are MCP-researched from Amazon Bedrock documentation (Provisioned Throughput / Model Units, Purchase Provisioned Throughput, and batch inference limitations). Cost framing maps to Skills 4.1.3 and 4.1.x of the exam blueprint.

---

## Section 6: Resilience and Cross-Region Inference

### The Resilience Problem Specific to Foundation Models

Traditional application resilience is about surviving infrastructure failure — an instance dies, a Region degrades, you fail over. Foundation models add two failure modes that are particular to GenAI. The first is capacity: a popular model in a single Region can hit capacity limits during a traffic burst, returning throttling errors even though your own code is fine. The second is availability: a given model may be offered in only a handful of Regions, so the Region where your application or your data lives may not host the model you need. Skills 1.2.2 and 1.2.3 of the exam are built around designing for both, and the answers center on cross-Region inference, dynamic model switching, and circuit-breaker patterns.

### Cross-Region Inference Profiles

A cross-Region (system-defined) inference profile lets Bedrock automatically distribute your inference requests across multiple AWS Regions to absorb traffic bursts and find available capacity. Two terms anchor the mechanic. The source Region is the Region from which you make the API call (specifying the inference profile instead of a bare model ID). A destination Region is any Region the profile may route your request to. When you invoke the profile, Bedrock performs real-time capacity checks — first in the source Region, then in other destination Regions if needed — and routes the request to wherever capacity is available, optimizing for performance.

Two properties make this attractive and are worth committing to memory. There is no additional routing or data-transfer cost for cross-Region inference — you pay normal inference pricing, and the cross-Region routing itself is free. And it requires no client-side load-balancing logic — you simply call the profile, and Bedrock handles distribution. This is why, when a scenario asks how to handle unpredictable bursts or limited single-Region capacity without building your own multi-Region balancer, the cross-Region inference profile is the intended answer.

There is a subtle behavior the exam can probe: when you use a cross-Region inference profile, your request may be processed in a destination Region even if you did not explicitly opt into that Region in your account. The profile's destination list, not your account's opt-in set, governs where requests can land.

### The SCP and IAM Requirement

Because a cross-Region inference profile can route to several Regions, your permissions and guardrails must permit inference in all of them. Service Control Policies (at the organization level) and IAM policies (at the principal level) work together to control where cross-Region inference is allowed. The rule that trips people up: if any destination Region in the chosen profile is blocked by an SCP, the request fails — even if other destination Regions remain allowed. To operate reliably you must allow the required Bedrock inference actions (for example bedrock:InvokeModel*) across every destination Region in the profile. A common "what went wrong" scenario is a cross-Region profile failing intermittently because an SCP permits the model in the source Region but blocks one of the destination Regions.

### Global Versus Geography-Scoped Profiles, and Data Residency

Cross-Region inference profiles come in scopes, and the distinction matters for compliance. A geography-scoped profile (for example US, EU, or APAC) routes only within that geography, and its destination Region list is fixed and will not change — which is exactly what you want when data-residency or regulatory requirements say data may not leave a jurisdiction. A Global profile, by contrast, can route to any commercial AWS Region and its destination set can expand over time as AWS adds Regions. So when a scenario emphasizes data sovereignty or residency, choose a geography-scoped profile (or single-Region inference); when it emphasizes maximum capacity and resilience with no residency constraint, a Global profile gives the widest routing. For compliance planning, you confirm a model's routing scope from its model detail page (the Regional availability table and inference-profile IDs).

**Diagram (described):** This diagram shows how a cross-Region inference profile routes a request. An application in the source Region calls a cross-Region inference profile. The profile passes the request into a capacity-check decision node. From that check, three outcomes branch out: if the source Region has capacity, the request is served in the source Region; if there is a burst or the source has limited capacity, the request is routed to destination Region A; or alternatively to destination Region B. Alongside this, a separate annotation indicates that SCP and IAM policies must allow Bedrock inference in all destination Regions, feeding into the profile — because a single blocked destination Region will fail the request.

### Application Inference Profiles

Distinct from the system-defined cross-Region profiles, an application inference profile is one you create yourself, typically derived from a cross-Region profile, to track cost and usage for a particular application or team. You reference it by ID or ARN at invocation time just like a model, and Bedrock attributes the resulting metrics and costs to that profile. When a scenario asks how to attribute Bedrock spend across multiple applications or cost centers while still using cross-Region inference, application inference profiles are the mechanism.

### Dynamic Model Switching Without Code Changes

Skill 1.2.2 asks for architectures that allow switching models or providers without modifying code. The pattern AWS intends combines a few familiar services. Put an abstraction layer in front of Bedrock — typically AWS Lambda fronted by Amazon API Gateway — so callers never address a model directly. Store the active model choice as external configuration in AWS AppConfig rather than hardcoding it. To change models, you update the AppConfig value; the Lambda reads the new configuration and routes to the new model, with no code deployment. This is the same portability theme from Section 1, operationalized: the Converse API makes models interchangeable in code, and AppConfig-driven configuration makes the choice changeable at runtime.

**Diagram (described):** This diagram shows the dynamic model-switching architecture as a left-to-right flow. A client calls API Gateway, which forwards to a Lambda function that acts as the abstraction layer. AWS AppConfig, holding the active model setting, feeds that setting into the Lambda. The Lambda then calls Bedrock, invoking the chosen model via the Converse API. The key idea conveyed is that the active model lives in AppConfig configuration rather than in code, so changing models is a configuration edit, not a redeploy.

### Circuit Breakers and Graceful Degradation

For resilience against service disruption (Skill 1.2.3), the exam expects classic reliability patterns adapted to FMs. A circuit breaker, often implemented with AWS Step Functions, stops sending requests to a model or dependency that is repeatedly failing — it "opens" after a failure threshold, gives the dependency time to recover, and prevents cascading failures and wasted retries. Graceful degradation means designing a fallback path so the application still does something useful when the primary model is unavailable: fail over to an alternate model or Region, return a cached or simpler response, or queue the request for later rather than erroring out entirely. Combined with cross-Region inference for capacity and an AppConfig-driven abstraction for switching, these patterns give you a GenAI system that bends rather than breaks. Section 8 covers the request-level mechanics (retries, backoff, routing) that complement these architectural patterns.

### Exam-Relevant Distinctions

| If the exam says... | The answer is... | Why |
|---|---|---|
| "Handle traffic bursts / limited single-Region capacity, no custom balancer" | Cross-Region inference profile | Bedrock auto-routes to available Regions, no extra cost |
| "Cross-Region inference fails intermittently" | Check SCP/IAM for a blocked destination Region | A blocked destination Region fails the request |
| "Data must not leave the EU/US/jurisdiction" | Geography-scoped profile (or single Region) | Geo profiles have a fixed destination list within the geography |
| "Maximum capacity, no residency constraint" | Global inference profile | Routes to any commercial Region; set can grow |
| "Attribute Bedrock cost across apps/teams" | Application inference profile | Created for cost/usage tracking |
| "Switch models with no code deployment" | Lambda + API Gateway abstraction + AppConfig | Config change reroutes without redeploy |
| "Stop hammering a failing dependency" | Circuit breaker (Step Functions) | Opens after failures to prevent cascading errors |

- Cross-Region inference adds no routing or data-transfer cost — only normal inference pricing applies.
- A request under a cross-Region profile can be processed in a destination Region you did not opt into.
- A blocked destination Region in an SCP fails the whole request even if other Regions are allowed.
- Geography-scoped profiles have a fixed destination list; Global profiles' destination set can expand over time.
- Application inference profiles are user-created (often from a cross-Region profile) for cost/usage tracking.

### Knowledge Check

**Q1:** An application experiences unpredictable traffic spikes that cause throttling on a popular model in a single Region. The team wants higher resilience without writing custom multi-Region load-balancing logic. What should they use?
- A) Purchase Provisioned Throughput in every Region manually
- B) A cross-Region (system-defined) inference profile
- C) Increase max tokens to reduce call count
- D) Switch all traffic to batch inference

**A:** B — A cross-Region inference profile automatically routes requests across destination Regions based on real-time capacity, absorbing bursts with no client-side load-balancing code and no extra routing/data-transfer cost. A is operationally heavy and still manual; C does not address capacity; D abandons real-time behavior.

**Q2:** A cross-Region inference profile works in testing but fails intermittently in production. CloudTrail shows AccessDenied-style failures for some requests. What is the most likely cause?

**A:** An SCP or IAM policy blocks Bedrock inference in one of the profile's destination Regions. Under a cross-Region profile, a request can be routed to any destination Region, and if any of them is blocked, that request fails even though the source Region and other destinations are allowed. The fix is to permit the required Bedrock inference actions across all destination Regions in the profile.

**Q3:** A financial customer requires that inference data never leave the EU. They still want resilience across Regions. Which inference profile choice fits?
- A) A Global inference profile
- B) An EU geography-scoped inference profile
- C) No inference profile is compatible with residency
- D) An application inference profile in any Region

**A:** B — A geography-scoped (EU) profile routes only within that geography and has a fixed destination list, satisfying data residency while still giving cross-Region resilience inside the EU. A Global profile (A) can route to any commercial Region, violating residency. C is incorrect — geo-scoped profiles exist precisely for this. D (application profile) is about cost tracking, not residency scope by itself.

**Q4:** A team must be able to change which foundation model their service uses without deploying new code. Which combination achieves this?

**A:** Front Bedrock with an abstraction layer (AWS Lambda behind Amazon API Gateway) and store the active model selection in AWS AppConfig. To switch models, update the AppConfig value; the Lambda reads the new configuration and routes to the new model via the Converse API — no code deployment required. The Converse API's model-agnostic contract is what makes the swap a configuration change rather than a rewrite.

> **Source attribution:** Cross-Region inference behavior, SCP/IAM requirements, Global vs geography scope, and application inference profiles are MCP-researched from Amazon Bedrock "Supported Regions and models for inference profiles". Dynamic switching and circuit-breaker patterns map to Skills 1.2.2 and 1.2.3 of the exam blueprint.

---

## Section 7: FM Customization and Lifecycle

### Where Customization Sits on the Spectrum

Section 2 introduced the three levers for shaping model behavior — prompt engineering, RAG, and fine-tuning — and established that fine-tuning is the heaviest of the three. This section goes deeper on customization itself, because Skill 1.2.4 expects you to handle not just the act of customizing a model but its full lifecycle: deploying it, versioning it, updating it through pipelines, rolling it back when an update goes wrong, and retiring it at end of life.

The mental ordering to carry into the exam is a cost-and-effort ladder. Prompt engineering is the cheapest and most flexible; try it first. RAG is next; reach for it when the gap is missing knowledge. Fine-tuning is last; justify it only when prompting and RAG cannot deliver the consistent specialized behavior, tone, or format you need, or when you want to bake a task into the model so deeply that prompts can be small and reliable. The exam wants you to resist fine-tuning when a cheaper lever would do, and to recognize the narrow cases where it is genuinely the right tool.

### Customization Methods on Bedrock

Amazon Bedrock provides several customization methods, and recognizing them by purpose is testable.

Supervised fine-tuning provides labeled input-output examples so the model learns to associate specific inputs with desired outputs. The model's parameters are adjusted, improving performance on the tasks your dataset represents. This is the default meaning of "fine-tuning" and the right choice when you have curated labeled examples of the behavior you want.

Reinforcement fine-tuning improves alignment through feedback rather than labeled pairs. Instead of supplying correct answers, you define reward functions (which can be implemented with AWS Lambda) that score response quality, and the model learns iteratively from those scores. It suits cases where "good" is easier to score than to demonstrate with labeled examples.

Distillation transfers knowledge from a larger, more capable teacher model to a smaller, faster, cheaper student model. You pick a teacher whose quality you want to approach and a student to fine-tune, provide representative prompts, and Bedrock uses the teacher's generated responses to fine-tune the student. The payoff is a small model that punches above its size for your use case — a direct cost-and-latency optimization.

Across all methods, remember the cost model: you are charged for training based on tokens processed (training-corpus tokens times epochs) plus monthly storage per custom model. Customization is never free, which reinforces why it sits last on the ladder.

### Parameter-Efficient Adaptation: LoRA and Adapters

Full fine-tuning updates all of a model's parameters, which is computationally expensive and produces a large artifact. Parameter-efficient adaptation techniques avoid that. Low-rank adaptation (LoRA) and adapters train only a small set of additional parameters layered onto the frozen base model, leaving the original weights untouched. The result captures most of the benefit of full fine-tuning at a fraction of the training cost, and the small adapter artifacts make it practical to maintain many task-specific variants of one base model. When the exam mentions efficient domain-specific model deployment or adapting a model without the cost of full retraining (Skill 1.2.4), LoRA and adapters are the named techniques.

### Deployment, Versioning, and the Provisioned Throughput Link

Customizing a model produces an artifact you then have to operate. On AWS, the deployment and lifecycle tooling centers on Amazon SageMaker AI for hosting domain-specific fine-tuned models, with SageMaker Model Registry as the system of record for versioning and promoting models. Model Registry lets you catalog model versions, track which version is approved, and deploy a chosen version — the backbone of controlled, auditable model rollout.

The fact to carry from Section 5: a customized Bedrock model is never invoked via a base-model ARN — it needs its own serving surface. Current docs give two: a custom model deployment for on-demand, pay-per-token inference (variable or low traffic, no throughput guarantee), or Provisioned Throughput (Model Units, commitment term, quota request) when traffic is steady and throughput must be guaranteed. A steady high-volume production design that includes a fine-tuned, distilled, or imported Bedrock model therefore still implies a Provisioned Throughput purchase — if you see "deploy our fine-tuned model to production at scale", Provisioned Throughput belongs on your mental checklist; for variable or exploratory traffic, the on-demand custom model deployment is the newer, cheaper-entry path *(point-in-time)*.

### Pipelines, Rollback, and Retirement

The lifecycle does not end at first deployment. Skill 1.2.4 calls out automated deployment pipelines to update models, rollback strategies for failed deployments, and lifecycle management to retire and replace models.

Automated pipelines (built with the AWS developer tools — CodePipeline, CodeBuild, CodeDeploy — covered more in the integration guide) let you promote a new model version through testing and into production repeatably, with quality gates that can include the Bedrock model evaluations from Section 2. Rollback strategies matter more for models than for ordinary code because a model regression can be subtle — outputs that are worse but not obviously broken. Keeping the previous version registered and deployable (for example via Model Registry and a deployment strategy that can revert quickly) lets you fall back the moment evaluation or monitoring shows a regression. Retirement and replacement close the loop: models age, base models update, and a disciplined lifecycle includes decommissioning superseded custom models (and releasing their Provisioned Throughput) so you are not paying to store and serve a model nothing uses.

**Diagram (described):** This diagram shows the customization lifecycle as a left-to-right flow with a rollback branch. Labeled or reward data flows into a customize step (fine-tune, reinforcement learning, distill, or LoRA). The customized model flows into SageMaker Model Registry for versioning. From the registry it flows into a deployment pipeline with quality gates, and then into serving via Provisioned Throughput. Two additional paths are shown: from the deployment pipeline, if a regression is detected, the flow branches back to roll back to a prior version; and from the served model, at end of life it flows to a retire-and-replace step. The diagram conveys the full path from training data through versioned, gated deployment, with rollback and retirement closing the loop.

### Exam-Relevant Distinctions

| If the exam says... | The answer is... | Why |
|---|---|---|
| "Adapt a model cheaply without full retraining" | LoRA / adapters (parameter-efficient adaptation) | Trains few added parameters on a frozen base |
| "Smaller, cheaper model with near-teacher quality" | Distillation | Teacher fine-tunes a smaller student |
| "Improve alignment using reward functions, not labels" | Reinforcement fine-tuning | Learns from reward scores (Lambda) not labeled pairs |
| "Version and promote model artifacts" | SageMaker Model Registry | System of record for versions and approval |
| "Deploy our fine-tuned model to production" | Implies Provisioned Throughput | Custom models cannot be served on-demand |
| "Recover quickly from a bad model update" | Rollback to a registered prior version | Model regressions are subtle; keep prior version deployable |

- Customization order of preference: prompt engineering → RAG → fine-tuning (cheapest/most flexible first).
- Bedrock customization methods: supervised fine-tuning, reinforcement fine-tuning, distillation.
- Training cost = tokens processed (corpus × epochs) + monthly per-model storage.
- A custom (fine-tuned/distilled/imported) Bedrock model requires Provisioned Throughput to invoke.
- Retiring a custom model should include releasing its Provisioned Throughput to stop charges.

### Knowledge Check

**Q1:** A team needs a domain-specialized model but wants to avoid the cost of full fine-tuning while maintaining several task-specific variants. Which technique fits best?
- A) Full supervised fine-tuning for each variant
- B) Low-rank adaptation (LoRA) / adapters
- C) Increasing the context window
- D) Distillation into one large model

**A:** B — LoRA and adapters train only a small set of added parameters on top of a frozen base model, capturing most of the benefit of fine-tuning at much lower cost, and the small adapter artifacts make maintaining many task-specific variants practical. Full fine-tuning (A) is the expensive option being avoided; C is unrelated; D produces a smaller model but does not address maintaining multiple efficient variants.

**Q2:** True or False — A fine-tuned model in Amazon Bedrock can be invoked on-demand just like a base foundation model.

**A:** False. Customized models (fine-tuned, distilled, or imported) can only be served through Provisioned Throughput; there is no on-demand option for them. Any production plan involving a custom Bedrock model must account for a Provisioned Throughput purchase, including Model Units, a commitment term, and a quota request.

**Q3:** An organization wants the quality of a large, expensive model but needs lower latency and cost in production. They have representative prompts available. Which customization method directly targets this goal?

**A:** Distillation. You designate the large model as the teacher and a smaller model as the student, supply representative prompts, and Bedrock uses the teacher's responses to fine-tune the student. The outcome is a smaller, faster, cheaper model that approaches the teacher's quality for your use case — exactly the cost/latency optimization described.

**Q4:** After deploying an updated fine-tuned model, monitoring shows subtly worse answer quality. What lifecycle capability should the team have in place, and how is it supported?

**A:** A rollback strategy backed by versioning. By keeping the previous model version registered in SageMaker Model Registry and using a deployment approach that can revert quickly, the team can fall back to the known-good version as soon as evaluation or monitoring detects the regression. Because model regressions are often subtle rather than hard failures, pairing deployment pipelines with quality gates (e.g., Bedrock evaluations) is what surfaces the problem in time to roll back.

> **Source attribution:** Customization methods (supervised fine-tuning, reinforcement fine-tuning, distillation) and the training cost model are MCP-researched from Amazon Bedrock "Customize your model" documentation. LoRA/adapters, Model Registry versioning, pipelines, rollback, and retirement map to Skill 1.2.4; the Provisioned Throughput dependency connects to Section 5.

---

## Section 8: Resilient FM API Integration

### From Architecture to the Request Itself

Section 6 covered resilience at the architectural level — cross-Region routing, model-switch abstractions, circuit breakers. This section drops down to the level of the individual API call: how a single invocation survives throttling and transient errors, how requests get routed to the right model, and how you see what is happening when something goes wrong. These map to Skills 2.4.3 (resilient FM systems), 2.4.4 (intelligent model routing), and the observability and deployment threads of Task 2.2 and Domain 4.

### Surviving Throttling and Transient Failures

At scale, on-demand Bedrock invocation will sometimes return errors that are not your fault: ThrottlingException when shared capacity is saturated, ModelTimeoutException, ServiceUnavailableException, InternalServerException, or transient network errors. The correct response is retry logic with exponential backoff. Rather than retrying immediately (which only adds load), you wait progressively longer between attempts — and add jitter (randomized delay) so that many clients backing off at once do not synchronize into a new spike, the "thundering herd". The AWS SDKs implement this for you: configuring the retry mode (standard or adaptive) and max attempts on the SDK client gives you backoff with little custom code. Adaptive mode additionally throttles client-side when it detects capacity pressure.

A crucial distinction the exam tests: retry only transient, server-side errors. Retrying a client error like ValidationException (your request is malformed) or AccessDeniedException (a permissions problem) is pointless — the request will fail identically every time, and retrying just wastes time and quota. Backoff is for errors that might succeed later, not for errors that are deterministically wrong.

When retries are not enough — a model or dependency is failing persistently — you layer in the architectural patterns from Section 6: a circuit breaker stops the retries from hammering a down dependency, and a fallback path provides graceful degradation (an alternate model, a cached response, or queuing for later). API Gateway can also enforce rate limiting (usage plans, throttling) in front of your integration so that a misbehaving client cannot exhaust your Bedrock quota and starve everyone else.

### Intelligent Model Routing

Routing decides which model handles a given request, and the exam (Skill 2.4.4) recognizes a spectrum of sophistication. Static routing hardcodes the mapping in application logic — simple, predictable, fine when the rules rarely change (and best combined with the AppConfig externalization from Section 6 so even "static" choices are changeable without redeploy). Dynamic, content-based routing inspects the request and chooses a model accordingly — for example using AWS Step Functions to send simple queries to a cheap model and complex ones to a flagship model, which is exactly how the model cascade from Section 2 is implemented. Metric-based routing chooses based on observed conditions such as latency or cost. And API Gateway with request transformations can implement routing logic at the edge, reshaping requests toward the right backend. The unifying idea: routing is where cost optimization (cascading), resilience (failover to an available model), and performance (sending latency-sensitive traffic to fast models) all get operationalized.

**Diagram (described):** This diagram shows intelligent model routing as a decision tree. An incoming request enters a routing-decision node. From that node, three branches fan out: a simple query routes to a small, cheap model; a complex query routes to a flagship model; and if the primary is unavailable, the request routes to an alternate model or Region. In addition, a dotted escalation path runs from the small cheap model to the flagship model, labeled "low confidence, escalate" — this is the model cascade in action, where the cheap tier handles routine traffic but hands off hard or low-confidence queries to the larger model.

### Observability for FM Calls

You cannot operate, debug, or optimize what you cannot see, and FM workloads have observability needs beyond ordinary services — you care not just about latency and errors but about token usage, prompt content, and response quality. Three AWS capabilities form the core.

Amazon Bedrock Model Invocation Logging is the foundational data source. It is disabled by default; once enabled in the Bedrock console, it captures full request data, response data, and metadata for the runtime operations (Converse, ConverseStream, InvokeModel, InvokeModelWithResponseStream) and publishes them to Amazon CloudWatch Logs and/or Amazon S3 (destinations must be in the same account and Region). This is what lets you analyze actual prompts and responses — essential for diagnosing prompt problems and detecting quality issues.

Amazon CloudWatch provides the metrics and dashboards: invocation count, latency, token usage, throttles, and errors, broken down by model, with alarms. CloudWatch generative AI observability builds pre-configured dashboards on top of the invocation logs. CloudWatch Logs Insights lets you query the logged prompts and responses to find patterns (Skill 2.5.6).

AWS X-Ray provides distributed tracing across service boundaries, so you can follow a request through API Gateway, Lambda, Bedrock, and any tools, and see where latency accumulates or where a failure originates (Skill 2.4.3). For a multi-step GenAI workflow, X-Ray is how you locate the slow or failing hop.

### Deployment Strategies Recap (Task 2.2)

Task 2.2 frames deployment as choosing the right serving substrate for the workload, and it ties this whole guide together. AWS Lambda is the natural host for on-demand, event-driven invocation of Bedrock models — stateless, scales to zero, ideal for spiky request/response traffic. Bedrock Provisioned Throughput is the choice when you need guaranteed capacity or must serve a custom model (Sections 5 and 7). Amazon SageMaker AI endpoints serve self-hosted or hybrid models — including fine-tuned models you operate outside Bedrock's managed serving — and are where you go when you need full control over the hosting environment. For self-hosted large models, container-based patterns (on ECS, EKS, or Fargate) optimized for memory footprint, GPU utilization, and token-processing throughput address the reality that LLMs have very different resource profiles from traditional services. The exam expects you to match the substrate to the requirement: Lambda for serverless on-demand, Provisioned Throughput for guaranteed/custom, SageMaker/containers for self-hosted control.

### Exam-Relevant Distinctions

| If the exam says... | The answer is... | Why |
|---|---|---|
| "Handle ThrottlingException at scale" | Retry with exponential backoff + jitter (SDK retry mode) | Transient capacity errors may succeed on retry |
| "Retrying ValidationException/AccessDenied" | Do not retry client errors | They fail deterministically; retrying wastes quota |
| "Route simple vs complex queries to different models" | Dynamic content-based routing (Step Functions) | Implements the cost-saving cascade |
| "Prevent one client from exhausting Bedrock quota" | API Gateway rate limiting (usage plans) | Throttles per-client at the edge |
| "Analyze actual prompts and responses" | Bedrock Model Invocation Logging → CloudWatch Logs/S3 | Captures full request/response data (off by default) |
| "Find which hop in a GenAI workflow is slow/failing" | AWS X-Ray tracing | Traces requests across service boundaries |
| "Serverless, spiky, on-demand model calls" | AWS Lambda | Scales to zero, event-driven |

- AWS SDK retry modes (standard/adaptive) give backoff with jitter without custom code; adaptive also self-throttles.
- Retry only transient/server errors (Throttling, Timeout, ServiceUnavailable, InternalServer); never client errors.
- Bedrock Model Invocation Logging is OFF by default; enable it to capture prompts/responses to CloudWatch/S3.
- Logging destinations (CloudWatch Logs, S3) must be in the same account and Region as the invocations.
- Deployment substrate: Lambda (on-demand serverless), Provisioned Throughput (guaranteed/custom), SageMaker/containers (self-hosted control).

### Knowledge Check

**Q1:** Under heavy load, an application receives frequent ThrottlingException responses from Bedrock. What is the correct first-line handling?
- A) Immediately retry the request in a tight loop
- B) Retry with exponential backoff and jitter (e.g., SDK adaptive retry mode)
- C) Treat it as a fatal client error and stop
- D) Switch the request to batch inference

**A:** B — ThrottlingException is a transient, server-side capacity error that may succeed on a later attempt, so the right handling is retry with exponential backoff plus jitter, easily configured via the AWS SDK retry mode. A tight retry loop (A) worsens the load; it is not a client error to abort on (C); and switching an interactive call to batch (D) changes the workload semantics rather than handling the throttle.

**Q2:** True or False — Retrying an AccessDeniedException with exponential backoff is a good resilience practice.

**A:** False. AccessDeniedException and ValidationException are client errors — the request is deterministically wrong (a permissions or input problem) and will fail identically on every retry. Backoff and retries are only appropriate for transient/server-side errors like ThrottlingException, ModelTimeoutException, ServiceUnavailableException, and InternalServerException.

**Q3:** A team needs to analyze the exact prompts users sent and the responses the model returned, to diagnose a quality issue. What must they enable, and where do the logs go?

**A:** Amazon Bedrock Model Invocation Logging, which is disabled by default. Once enabled, it captures full request data, response data, and metadata for runtime calls and publishes them to Amazon CloudWatch Logs and/or Amazon S3 (in the same account and Region). They can then use CloudWatch Logs Insights to query the prompts and responses for patterns.

**Q4:** A GenAI workflow chains API Gateway, Lambda, a Bedrock model, and a tool call. Latency is high but it is unclear which component is responsible. Which service pinpoints the slow hop?
- A) Cost Explorer
- B) AWS X-Ray
- C) AWS Config
- D) Amazon Macie

**A:** B — AWS X-Ray provides distributed tracing across service boundaries, so you can follow a single request through API Gateway, Lambda, Bedrock, and the tool, and see exactly where latency accumulates. Cost Explorer is for spend, Config is for resource configuration history, and Macie is for sensitive-data discovery — none trace request latency across services.

> **Source attribution:** Retry/backoff guidance and error-class distinctions are MCP-researched from the AWS re:Post Bedrock retry/exponential-backoff article; Model Invocation Logging and CloudWatch observability from Amazon Bedrock and CloudWatch documentation. Routing and deployment-substrate guidance map to Skills 2.4.3, 2.4.4, and Task 2.2.

---

## Section 9: Exam Patterns and Quick Reference

### How to Think Through an FM/Bedrock Question

The AIP-C01 exam rarely asks "what is X". It describes a production situation with competing constraints — cost, latency, freshness, data residency, safety, scale — and asks for the best design. For the foundation-model and Bedrock-core material in this guide, a reliable way to reason through such a question is to ask, in order: What does the model need to know (prompt / RAG / fine-tune)? Which model class fits the quality, latency, and modality bar? Which inference mode matches the volume and commitment profile? How is it invoked (Converse, streaming, async)? And how is it made resilient (cross-Region, switching, retries)? Most scenarios are really one or two of these five questions in disguise. The decision tree below captures the core forks.

**Diagram (described):** This master decision tree starts from a GenAI requirement and walks through the guide's core forks in order. First fork: does the model need facts it lacks? If it needs private or fresh facts, choose RAG; if it needs baked-in behavior, choose fine-tuning (which requires Provisioned Throughput); if it needs just tone or format, choose prompt engineering. The RAG and prompt-engineering paths then flow into a second fork on traffic profile, while fine-tuning flows directly to a "Provisioned Throughput required" outcome. The traffic-profile fork branches three ways: spiky or low traffic goes to on-demand; steady high volume goes to Provisioned Throughput; large offline batch goes to batch inference. The on-demand and Provisioned Throughput paths then flow into a final fork on resilience: if there is burst or capacity risk, use a cross-Region inference profile; if routing is residency-limited, use a geography-scoped profile. The tree captures, end to end, the knowledge-need then inference-mode then resilience decision sequence.

### Quick Decision Guide

| Scenario | Answer pattern |
|---|---|
| Model must use private data that changes often | RAG (not fine-tuning) |
| Consistent specialized format prompting cannot enforce | Fine-tuning + Provisioned Throughput |
| Switch models with no code deployment | Lambda + API Gateway abstraction + AppConfig |
| Write once, run across many models | Converse API |
| Show response as it is generated (typing UX) | ConverseStream over SSE/WebSockets |
| Process 100k+ prompts overnight, cheapest | Batch inference (S3 in/out) |
| Serve a fine-tuned model in production | Provisioned Throughput (required) |
| Absorb traffic bursts without custom load balancing | Cross-Region inference profile |
| Data must stay in one jurisdiction | Geography-scoped inference profile or single Region |
| Cut cost across mixed simple/complex traffic | Model cascading + dynamic routing |
| Handle ThrottlingException at scale | Retry with exponential backoff + jitter |
| Analyze actual prompts and responses | Enable Bedrock Model Invocation Logging |
| Find the slow hop in a multi-service GenAI flow | AWS X-Ray tracing |
| Decide which of two models is better for our task | Bedrock model evaluation job |
| Attribute Bedrock spend across teams | Application inference profile |

### Common Traps and Distractors

Trap 1 — Fine-tuning for fresh/private data. The most common GenAI trap. When information changes frequently or is private, the answer is RAG, not fine-tuning. Fine-tuning bakes a snapshot into weights, is expensive, and goes stale; RAG keeps data current by updating the store. If a distractor says "fine-tune nightly to stay current", it is wrong by design.

Trap 2 — Forgetting Provisioned Throughput for custom models. A scenario describes deploying a fine-tuned model on-demand to save cost. That is impossible — custom models require Provisioned Throughput. The cost-saving on-demand option does not exist for them.

Trap 3 — Using batch for tool calling or strict JSON. Batch is tempting for "cheap and bulk", but it supports neither tool calling nor structured output. A batch job that needs an agent to call tools, or response_format-enforced JSON, is a wrong answer.

Trap 4 — Cross-Region inference without fixing SCPs. A cross-Region profile that fails intermittently is almost always an SCP/IAM problem: a blocked destination Region fails the request. The fix is permitting inference in all destination Regions, not changing the model.

Trap 5 — Retrying client errors. Wrapping ValidationException or AccessDeniedException in exponential backoff looks resilient but is wrong; those errors are deterministic. Backoff is only for transient server-side errors.

Trap 6 — Reaching for the biggest model by default. The exam rewards the cheapest model that clears the quality bar, often combined with a cascade. Choosing a flagship model "to be safe" when a small model plus cascade meets the requirement is the wrong, costly answer.

### Inference Parameter Quick Reference

| Use case | Temperature | Top P | Other |
|---|---|---|---|
| Deterministic extraction / classification / SQL | Low (near 0) | Narrow | Stop sequence; low max tokens |
| General assistant / chatbot | Moderate | Moderate | Reasonable max tokens |
| Creative / brainstorming / varied copy | High | Wide | Frequency/presence penalty to reduce repetition |
| Repetitive looping output observed | Raise | — | Add frequency/presence penalty |
| Control cost per response | — | — | Lower max tokens |

### When to Use What

| Decision | Choose | Over |
|---|---|---|
| Invocation API | Converse (portable, tools, guardrails) | InvokeModel (only for raw native format) |
| Interactive UX | ConverseStream (streaming) | Synchronous Converse |
| No-wait bulk | Batch inference / async SQS | Synchronous calls |
| Variable/low traffic | On-demand | Provisioned Throughput |
| Steady high volume or custom model | Provisioned Throughput | On-demand |
| Burst resilience | Cross-Region inference profile | Manual multi-Region balancing |
| Data residency | Geo-scoped profile / single Region | Global profile |

### Mapping to AIP-C01 Domains and Tasks

| Guide Section | Tasks | Domain |
|---|---|---|
| 1. FM Foundations | 1.1 | D1 (31%) |
| 2. Model Selection | 1.2.1, 4.1.2 | D1 / D4 |
| 3. Inference Parameters | 4.2.4 | D4 (12%) |
| 4. Invocation APIs | 2.4.1, 2.4.2 | D2 (26%) |
| 5. Inference Modes | 2.2.1, 4.1.3 | D2 / D4 |
| 6. Resilience & Cross-Region | 1.2.2, 1.2.3 | D1 |
| 7. Customization & Lifecycle | 1.2.4 | D1 |
| 8. Resilient API Integration | 2.4.3, 2.4.4, 2.2.x | D2 |

### Knowledge Check

**Q1:** A scenario requires a production assistant grounded in a frequently-updated internal knowledge base, sub-second perceived response time, and the ability to attribute cost to the owning team. Which combination is best?
- A) Fine-tune nightly, synchronous Converse, single Region
- B) RAG, ConverseStream for streaming UX, application inference profile for cost attribution
- C) Batch inference with tool calling, Global profile
- D) Largest flagship model on-demand, no logging

**A:** B — Frequently-updated internal data points to RAG; sub-second perceived latency points to streaming (ConverseStream); team cost attribution points to an application inference profile. A misuses fine-tuning for fresh data; C uses batch (no tool calling, not interactive); D over-provisions and ignores cost attribution. This question chains several of the guide's core decisions.

**Q2:** Which single change most directly reduces cost for a workload where 85% of queries are simple FAQs and 15% are complex, with no quality regression allowed?

**A:** Introduce model cascading with dynamic content-based routing — send all traffic to a small, cheap model first and escalate only the complex 15% to a flagship model (for example, routing decided in Step Functions or application logic). Because the large majority of traffic is simple, most requests are served cheaply while quality is preserved for the queries that need the bigger model.

**Q3:** An exam option proposes serving a distilled custom model's steady high-volume production workload through an on-demand custom model deployment to minimize cost. What is the catch?

**A:** On-demand custom model deployments do exist (deploy the custom model, invoke its deployment ARN, pay per token) — but they carry no throughput guarantee and fit variable or lower-volume traffic. For steady high-volume serving, Provisioned Throughput is the appropriate choice and typically the cheaper one at sustained utilization. The older absolute — "custom models cannot be invoked on-demand" — is outdated *(point-in-time)*.

**Q4:** True or False — When a cross-Region inference profile intermittently fails, the right first step is to switch to a different foundation model.

**A:** False. Intermittent failures on a cross-Region profile are most often caused by an SCP or IAM policy that blocks Bedrock inference in one of the profile's destination Regions; a request routed there fails even though the source and other destinations are allowed. The fix is to allow the required inference actions across all destination Regions, not to change the model.

> **Source attribution:** This section aggregates the decision logic and exam-critical distinctions established and MCP-verified across Sections 1-8, organized for rapid pre-exam review against the AIP-C01 domain/task structure.

### Multiple-Response Knowledge Check

The AIP-C01 exam leans heavily on multiple-response items — pick the 2+ correct designs out of five-plus plausible-sounding options. Work each one before reading the answer; the wrong options here are built from this guide's named traps.

**Q1:** A team is deploying a fine-tuned (customized) Bedrock model into a steady, high-volume production service. Which TWO statements about serving and operating this model are correct? (Select TWO)
- A) The custom model can be invoked exactly like the base model, with no additional deployment or provisioning step
- B) For guaranteed throughput on steady high-volume traffic, the custom model must be served through Provisioned Throughput
- C) Provisioned Throughput is purchased in Model Units (MUs), and a committed purchase requires requesting an MU quota increase through AWS Support first
- D) Batch inference is the cheapest way to serve this custom model interactively
- E) Retiring the model later has no billing implication once training is paid for

**A:** B, C — Guaranteed throughput at steady high volume for a custom model means Provisioned Throughput (B), and that capacity is bought in Model Units with a prerequisite Support quota increase for committed purchases (C). A is wrong: a custom model is never invoked like the base model — it needs a serving surface first (Provisioned Throughput, or a custom model deployment for on-demand inference, which carries no throughput guarantee and so fails this workload's requirement). D is wrong twice over: batch is not supported for provisioned/custom serving and is not interactive. E is wrong because Provisioned Throughput bills hourly until you delete the provisioned model, so retirement must include releasing it to stop charges.

**Q2:** An architect must let operations switch the active foundation model at runtime with no code deployment, and the design must absorb unpredictable single-Region traffic bursts without writing custom multi-Region load-balancing logic. Which TWO components directly satisfy these requirements? (Select TWO)
- A) Store the active model identifier in AWS AppConfig, read by a Lambda abstraction layer behind API Gateway
- B) Hardcode the model ID in the Lambda and redeploy on every change
- C) A cross-Region (system-defined) inference profile invoked in place of a bare model ID
- D) Manually purchase Provisioned Throughput in every Region and balance traffic in application code
- E) Raise max tokens so fewer calls are made

**A:** A, C — Externalizing the model choice in AppConfig behind a Lambda/API Gateway abstraction lets you change models by editing configuration rather than redeploying code (A), and the model-agnostic Converse API is what makes that swap a config change. A cross-Region inference profile (C) auto-routes to destination Regions on real-time capacity checks, absorbing bursts with no client-side balancer and no extra routing or data-transfer cost. B is the opposite of the no-deploy requirement. D is the manual, operationally heavy approach the cross-Region profile is meant to replace. E does not address either model switching or capacity bursts.

**Q3:** A high-scale on-demand workload intermittently receives errors from Bedrock. Which TWO error responses should be retried with exponential backoff and jitter, and which handling principle is correct? (Select THREE)
- A) ThrottlingException — retry with exponential backoff and jitter
- B) ValidationException — retry with exponential backoff and jitter
- C) ServiceUnavailableException / ModelTimeoutException — retry with exponential backoff and jitter
- D) AccessDeniedException — retry with exponential backoff and jitter
- E) Configuring the AWS SDK retry mode (standard or adaptive) provides backoff with jitter without custom code; adaptive additionally self-throttles under capacity pressure

**A:** A, C, E — Throttling, ServiceUnavailable, ModelTimeout (and InternalServerException) are transient server-side errors that may succeed on a later attempt, so backoff with jitter is correct (A, C), and the SDK retry modes implement this for you with adaptive mode adding client-side self-throttling (E). B and D are the guide's "retrying client errors" trap: ValidationException (malformed request) and AccessDeniedException (permissions) are deterministic — they fail identically every time, so retrying only wastes time and quota. The fix for those is to correct the request or the IAM policy, not to back off.

**Q4:** A regulated EU customer needs cross-Region resilience but data may not leave the EU, and they also want to attribute Bedrock spend to each consuming application. The team reports the cross-Region setup fails intermittently with AccessDenied-style errors. Which TWO actions correctly address these requirements? (Select TWO)
- A) Use a Global inference profile for the widest possible routing and capacity
- B) Use an EU geography-scoped inference profile, which routes only within the EU on a fixed destination list
- C) Ensure the SCP/IAM policies allow the required Bedrock inference actions in every destination Region of the profile, since a single blocked destination fails the request
- D) Create application inference profiles to attribute cost and usage per application
- E) Switch to a different foundation model to resolve the intermittent failures

**A:** B, C — A geography-scoped (EU) profile keeps routing within the jurisdiction on a fixed destination list, satisfying residency while still giving cross-Region resilience (B); fixing the intermittent failures means permitting Bedrock inference across all destination Regions, because one SCP/IAM-blocked destination fails the request even when others are allowed (C). A violates the residency constraint — a Global profile can route to any commercial Region and its set can grow. E is the guide's trap of changing the model instead of fixing the permissions root cause. D is a real capability but addresses cost attribution, which is not one of the two stated requirements being solved here (resilience-within-residency and fixing the failures) — note the question asks for the two actions that address the residency and intermittent-failure problems.

---

## AWS Documentation References

References are grouped by topic and deduplicated. All URLs were retrieved and verified via the AWS Knowledge MCP server during authoring.

### Foundation Models and Bedrock Overview

[1] What is Amazon Bedrock
https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html

[2] Models at a glance (model catalog)
https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards.html

[3] What are Foundation Models?
https://aws.amazon.com/what-is/foundation-models/

[4] AWS Well-Architected Framework — Generative AI Lens (via Well-Architected Tool)
https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lens.html

### Model Selection and Evaluation

[5] Evaluate the performance of Amazon Bedrock resources (automatic, human, LLM-as-a-judge)
https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html

[6] Foundation Model Evaluation (FMEval) overview
https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-foundation-model-evaluate-whatis.html

### Inference Parameters

[7] Influence response generation with inference parameters
https://docs.aws.amazon.com/bedrock/latest/userguide/inference-parameters.html

### Invocation APIs

[8] Inference using the Converse API
https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html

[9] Converse API reference
https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html

[10] ConverseStream API reference
https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ConverseStream.html

### Inference Modes

[11] Increase model invocation capacity with Provisioned Throughput
https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html

[12] Purchase a Provisioned Throughput for an Amazon Bedrock model
https://docs.aws.amazon.com/bedrock/latest/userguide/prov-thru-purchase.html

[13] Process multiple prompts with batch inference
https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference.html

### Resilience and Cross-Region Inference

[14] Supported Regions and models for inference profiles
https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html

[15] Getting started with cross-region inference in Amazon Bedrock
https://aws.amazon.com/blogs/machine-learning/getting-started-with-cross-region-inference-in-amazon-bedrock/

### Customization and Lifecycle

[16] Customize your model to improve its performance (fine-tuning, RFT, distillation)
https://docs.aws.amazon.com/bedrock/latest/userguide/custom-models.html

[17] Customize a model with fine-tuning in Amazon Bedrock
https://docs.aws.amazon.com/bedrock/latest/userguide/custom-model-fine-tuning.html

### Resilient API Integration and Observability

[18] Implement retry logic and exponential backoff for Amazon Bedrock
https://repost.aws/knowledge-center/bedrock-retry-exponential-backoff-api

[19] Monitor model invocation using CloudWatch Logs and Amazon S3
https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html

[20] CloudWatch generative AI observability — model invocations
https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/model-invocations.html

### Exam Guide

[21] AWS Certified Generative AI Developer - Professional (AIP-C01) Exam Guide
https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.html

---

*Guide 01 of the AIP-C01 study series. Next recommended guide: 02 — RAG, Vector Stores & Knowledge Bases.*
