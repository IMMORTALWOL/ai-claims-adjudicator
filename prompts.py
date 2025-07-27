# prompts.py

# This prompt instructs the LLM to act as a data entry specialist.
# It takes a raw, unstructured user query and transforms it into a structured JSON object.
# The JSON schema is defined within the prompt itself, ensuring consistent output.
QUERY_STRUCTURING_PROMPT = """
You are an expert at parsing and structuring insurance claim information.
Your task is to analyze the user's query and extract the key details into a structured JSON format.

The user query is: "{query}"

Extract the following information:
- "age": The age of the person.
- "gender": The gender of the person (male/female/other).
- "procedure": The medical procedure or treatment mentioned.
- "location": The city or location where the procedure took place.
- "policy_duration_months": The age of the insurance policy in months.

If a piece of information is not available in the query, use a null value for that key.
Return ONLY the JSON object. Do not include any explanatory text or markdown formatting.

Example:
Query: "46-year-old male, knee surgery in Pune, 3-month-old insurance policy"
Output:
{{
  "age": 46,
  "gender": "male",
  "procedure": "knee surgery",
  "location": "Pune",
  "policy_duration_months": 3
}}
"""

# This is the core reasoning prompt for the FIRST turn.
# It takes the structured query and the relevant policy clauses found via semantic search.
# It instructs the LLM to act as an insurance claim adjudicator, make a decision,
# and provide a detailed justification by citing the specific clauses.
DECISION_MAKING_PROMPT = """
You are an AI-powered insurance claim adjudicator. Your task is to make a decision on a claim based on the provided policy clauses.

**Claim Details (Structured JSON):**
{structured_query}

**Relevant Policy Clauses Retrieved via Semantic Search:**
---
{clauses}
---

**Your Task:**
1.  **Analyze:** Carefully review the claim details and the provided policy clauses.
2.  **Evaluate:** Determine if the claim is covered based on the rules, waiting periods, exclusions, and conditions mentioned in the clauses.
3.  **Decide:** Make a clear decision: "Approved", "Rejected", or "Needs More Information".
4.  **Justify:** Provide a step-by-step justification for your decision, explicitly citing the relevant clause numbers or text that support your reasoning. If you need more information, clearly state what specific information is missing.
5.  **Format Output:** Return your response as a single, well-formed JSON object.

**Required JSON Output Format:**
{{
  "decision": "...",
  "payout_amount_inr": "...",
  "justification": [
    {{
      "reason": "...",
      "clause_reference": "..."
    }}
  ]
}}

Now, process the claim and return ONLY the JSON response.
"""

# --- NEW PROMPT FOR FOLLOW-UP QUESTIONS ---
FOLLOW_UP_DECISION_PROMPT = """
You are an AI-powered insurance claim adjudicator continuing a conversation about a claim.
You previously determined you needed more information. The user has now provided it.
Your task is to re-evaluate the claim with this new context and make a final decision.

**Original Claim Details (Structured JSON):**
{structured_query}

**Relevant Policy Clauses:**
---
{clauses}
---

**Previous Conversation Turn (Your questions and reasoning):**
{previous_justification}

**New Information Provided by User:**
---
{user_follow_up}
---

**Your Task:**
1.  **Analyze:** Review all the information above: the original claim, the policy clauses, your previous questions, and the user's new answers.
2.  **Re-evaluate:** Based on the new information, make a final decision.
3.  **Decide:** Make a clear decision: "Approved", "Rejected", or "Needs More Information" (if the user's response is insufficient).
4.  **Justify:** Provide a new, complete justification for your final decision based on the combined information.
5.  **Format Output:** Return your response as a single, well-formed JSON object using the same format as before.

**Required JSON Output Format:**
{{
  "decision": "...",
  "payout_amount_inr": "...",
  "justification": [
    {{
      "reason": "...",
      "clause_reference": "..."
    }}
  ]
}}

Now, process the claim with the new information and return ONLY the JSON response.
"""


# This prompt takes the detailed JSON decision and converts it into a simple,
# human-readable, one-sentence summary.
FINAL_SUMMARY_PROMPT = """
You are an AI assistant that summarizes complex information into a simple, clear sentence.
Based on the following JSON decision object, provide a one-sentence, easy-to-understand answer to the user's original insurance claim query.

**Decision JSON:**
{decision_json}

**Task:**
- If the decision is "Approved", the sentence should be positive and confirm coverage.
- If the decision is "Rejected", the sentence should be clear and state that it is not covered, giving the main reason.
- If the decision is "Needs More Information", the sentence should explain what is needed in simple terms.

Do not use jargon. The output must be a single sentence.

Now, provide the single-sentence summary for the provided Decision JSON.
"""
