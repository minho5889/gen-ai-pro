# AIP-C01 Practice Exam 2 — Analysis (Q11-Q15)

## Question 11

### 1. Question Summary
**Scenario:** Users of a RAG assistant ask multi-part comparison questions such as "Did the Phoenix or Denver region have higher Q3 revenue, and which grew faster?" A single semantic retrieval returns chunks about one region or the other but never enough to compare both, so answers are incomplete.

**Ask:** Which managed Bedrock capability addresses this, and where is it configured?

### 2. Domain Mapping
**Domain:** Task 1.5 — Retrieval (query decomposition)
**Task:** Task 1.5

### 3. Option Analysis
- **A** ✅ Query decomposition (QUERY_DECOMPOSITION), set in orchestrationConfiguration.queryTransformationConfiguration on a RetrieveAndGenerate request
- **B** ❌ Hybrid search (overrideSearchType=HYBRID) on a bare Retrieve request
- **C** ❌ Reranking with Cohere Rerank 3.5 on a bare Retrieve request
- **D** ❌ Increasing numberOfResults to 50 on a RetrieveAndGenerate request

### 4. Correct Answer Deep-Dive
**Answer: A**

Query decomposition splits a complex multi-part question into sub-queries, retrieves each independently, and combines the results — exactly the fix when no single chunk answers the whole question. As a managed feature it is set via orchestrationConfiguration.queryTransformationConfiguration.type = QUERY_DECOMPOSITION on RetrieveAndGenerate (not bare Retrieve), because the generation step combines the sub-answers. B addresses exact-token matching, not multi-part decomposition. C reorders candidates but does not split the question. D floods context without ensuring both regions' facts are retrieved together.

### 5. Key Takeaway
Query decomposition splits a complex multi-part question into sub-queries, retrieves each independently, and combines the results — exactly the fix when no single chunk answers the whole question.

---

## Question 12

### 1. Question Summary
**Scenario:** A high-stakes underwriting tool must solve multi-step risk calculations correctly. A single chain-of-thought pass occasionally follows a flawed reasoning path and reaches a wrong conclusion. The team is willing to spend significantly more compute on these decisions to maximize reliability.

**Ask:** Which technique BEST raises reliability here, and what inference setting does it require?

### 2. Domain Mapping
**Domain:** Task 1.6 — Prompt engineering (technique selection)
**Task:** Task 1.6

### 3. Option Analysis
- **A** ✅ Self-consistency — generate multiple independent reasoning paths and take the consensus answer, run at a temperature above zero so the paths diverge
- **B** ❌ Self-consistency run at temperature 0 so every reasoning path is reproducible
- **C** ❌ Zero-shot chain-of-thought run at temperature 0 to make the single answer deterministic
- **D** ❌ Few-shot prompting with three near-identical examples at temperature 0

### 4. Correct Answer Deep-Dive
**Answer: A**

Self-consistency generates many independent reasoning paths (typically 5-20) and takes the majority answer, directly countering a single wrong CoT path — appropriate for high-stakes decisions where the roughly N-fold cost is justified. It requires stochastic decoding (temperature above zero) so the paths genuinely diverge; at temperature 0 every path is identical and voting is pointless, which is why B and C fail. D does not provide a voting mechanism and near-identical examples add little.

### 5. Key Takeaway
Self-consistency generates many independent reasoning paths (typically 5-20) and takes the majority answer, directly countering a single wrong CoT path — appropriate for high-stakes decisions where the roughly N-fold cost is justified.

---

## Question 13

### 1. Question Summary
**Scenario:** A financial-services chatbot must adopt a fixed persona and obey hard constraints — never give investment advice, never reveal account numbers, always respond in formal English — on every turn of a long multi-turn conversation. A developer reports that after about turn 30 the bot starts ignoring these rules.

**Ask:** What is the MOST likely cause and the correct design?

### 2. Domain Mapping
**Domain:** Task 1.6 — Prompt engineering (system vs user prompt)
**Task:** Task 1.6

### 3. Option Analysis
- **A** ✅ The persona and constraints must be placed in the system field and re-sent on every Converse request, because the model has no memory and only honors instructions present in the current request
- **B** ❌ The model forgot the rules permanently; the only fix is to fine-tune it on the constraints
- **C** ❌ Bedrock stores the system prompt server-side after turn one, so the developer must reset the sessionId
- **D** ❌ The constraints belong in the last user message of each turn, not the system prompt

### 4. Correct Answer Deep-Dive
**Answer: A**

Bedrock is stateless and the model has no memory of prior turns; a conversation only feels continuous because the application re-sends the accumulated history and the system prompt each turn. Persistent persona and hard constraints belong in the system field and must be re-transmitted on every request — if they are dropped on later turns, the rules stop governing behavior. B is overkill for a steering problem prompting solves. C is wrong: Bedrock does not store system prompts server-side. D would still work only if re-sent, but the system field is the correct home for behavior that must persist across the whole session.

### 5. Key Takeaway
Bedrock is stateless and the model has no memory of prior turns; a conversation only feels continuous because the application re-sends the accumulated history and the system prompt each turn.

---

## Question 14

### 1. Question Summary
**Scenario:** A team uses Amazon Bedrock Structured outputs with a JSON Schema to force an extraction response into a fixed object. The schema pins a rating field to integer type. In production they still see ratings outside the allowed 1-to-5 range and product codes that are the wrong length, even though every response is valid JSON conforming to the schema.

**Ask:** Why does this happen, and what closes the gap?

### 2. Domain Mapping
**Domain:** Task 1.6 — Prompt engineering (structured output limits)
**Task:** Task 1.6

### 3. Option Analysis
- **A** ✅ The JSON Schema subset Bedrock supports excludes numeric range (minimum/maximum) and string-length constraints, so those business rules must be enforced by application-side validation after parsing
- **B** ❌ The schema was not compiled correctly; re-submitting it will enforce the 1-to-5 range
- **C** ❌ Amazon Bedrock Guardrails should be configured to reject out-of-range ratings
- **D** ❌ Lowering temperature to 0 will guarantee the values fall within the allowed range

### 4. Correct Answer Deep-Dive
**Answer: A**

Bedrock Structured outputs implements a documented subset of JSON Schema Draft 2020-12 that does NOT support numeric constraints (minimum/maximum/multipleOf) or string-length constraints (minLength/maxLength). A schema can guarantee a field's type but not that an integer is between 1 and 5 or that a string is a certain length — those semantic rules must be checked in application-side validation. B is wrong: a valid schema cannot express the excluded constraints regardless of recompilation. C is wrong: Guardrails is a safety/content control, not a structure/semantics validator. D reduces drift but cannot enforce a numeric range.

### 5. Key Takeaway
Bedrock Structured outputs implements a documented subset of JSON Schema Draft 2020-12 that does NOT support numeric constraints (minimum/maximum/multipleOf) or string-length constraints (minLength/maxLength).

---

## Question 15

### 1. Question Summary
**Scenario:** A SaaS provider's assistant must answer from internal product documentation that changes several times a week and must cite the specific document each answer came from. An engineer proposes fine-tuning the base model nightly on the latest documentation to bake the knowledge in.

**Ask:** What is the stronger approach and why?

### 2. Domain Mapping
**Domain:** Task 1.2 — Select and configure FMs (RAG vs fine-tuning)
**Task:** Task 1.2

### 3. Option Analysis
- **A** ✅ Use RAG with a vector store and source citations, because freshness and source attribution are RAG's domain — update the store and answers reflect current docs immediately, with citations for free
- **B** ❌ Fine-tune hourly instead of nightly so the model stays closer to current
- **C** ❌ Increase the model's context window so all documentation fits in every prompt
- **D** ❌ Raise the temperature so the model adapts to changing documentation

### 4. Correct Answer Deep-Dive
**Answer: A**

Frequently-changing private knowledge plus a citation requirement is the textbook RAG case: retrieve relevant passages at query time, keep the store current with no retraining lag, and return source citations from the vector-to-source mapping. Nightly or hourly fine-tuning (A's distractor B) is expensive, lags changes, and provides no citations. C wastes tokens, breaks once docs exceed the window, and still has no freshness mechanism beyond manual pasting. D affects randomness, not knowledge or freshness. This is the recurring fine-tuning-for-freshness trap.

### 5. Key Takeaway
Frequently-changing private knowledge plus a citation requirement is the textbook RAG case: retrieve relevant passages at query time, keep the store current with no retraining lag, and return source citations from the vector-to-source mapping.

---

