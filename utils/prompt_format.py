from utils.redis_handler import redis_client as r

async def get_or_prompt(user_input, marks, stm_history, session_id):
    redis_key = f"session_extracted_text:{session_id}"
    print(redis_key)
    extracted_text = await r.get(redis_key)
    print(extracted_text)

    # Format short-term memory (recent chat history)
    stm_text = ""
    if stm_history:
        stm_text += "### Recent Conversation (Short-Term Memory):\n"
        for msg in stm_history[-3:]:  # Only last 3 pairs for relevance
            user_msg = msg.get('user_msg') or (msg['content'] if msg.get('role') == 'user' else '')
            bot_msg = msg.get('bot_response') or (msg['content'] if msg.get('role') == 'bot' else '')
            stm_text += f"- **User**: {user_msg}\n  **Bot**: {bot_msg}\n"

    # Format long-term memory context
    # Instruction formatting based on marks
    instruction_block = f"""
#### Instructions:
- **2 marks**: Write only **3–4 concise lines**. Be direct, avoid extra detail, and highlight only the **core concept**. No headings required.
- **5 marks**:  
  - Use markdown structure.  
  - Start with **### Definition:** in 1–2 lines.  
  - Then write **### Explanation:** in **120–150 words**, expanding on the topic with clarity.  
  - End with **### Examples:** giving 1–2 simple examples.  
- **10 marks**:  
  - Use markdown structure.  
  - Start with **### Definition:** in 3 lines.  
  - Add **### Example:** (1 strong, relevant example).  
  - Then write **### Detailed Answer:** in **180–250 words** (up to 300 if needed), elaborating the main question with structured points, analysis, and higher-level exam detail.  
""".strip()

    # Final prompt
    if extracted_text:
        await r.delete(redis_key)
        return f"""
{stm_text}

### New Question:
**Extracted content from file**:\n{extracted_text}\n\n
**User**:{user_input}

### Bot (Answer for approximately {marks} marks):

{instruction_block}

### Answer (Markdown formatted):
""".strip()
    else:
        return f"""
{stm_text}

### New Question:
**User**:{user_input}

### Bot (Answer for approximately {marks} marks):

{instruction_block}

### Answer (Markdown formatted):
""".strip()
        



def get_flash_prompt(user_input, marks):
    format = f"""
Q:...\nA:...
"""

    instruction_block = f"""
#### Instructions:
- **2 marks**: Write only **3–4 concise lines**. Be direct, avoid extra detail, and highlight only the **core concept**. No headings required.
- **5 marks**:  
  - Use markdown structure.  
  - Start with **### Definition:** in 1–2 lines.  
  - Then write **### Explanation:** in **120–150 words**, expanding on the topic with clarity.  
  - End with **### Examples:** giving 1–2 simple examples.  
- **10 marks**:  
  - Use markdown structure.  
  - Start with **### Definition:** in 3 lines.  
  - Add **### Example:** (1 strong, relevant example).  
  - Then write **### Detailed Answer:** in **180–250 words** (up to 300 if needed), elaborating the main question with structured points, analysis, and higher-level exam detail.  
""".strip()
    
    return f"""
### Generate 5 flashcard in the following format {format},
for this content **User**:{user_input}, for {marks} marks.
{instruction_block}

""".strip()


def get_note_prompt(user_input, marks):

    instruction_block = f"""
#### Instructions:
You are a Study Assistant. Convert the given content or user query into clear, structured notes. Follow these rules:

1. Use **headings and subheadings** to organize topics.
2. Use **bullet points** or numbered lists for key ideas.
3. Highlight **important terms** in **bold**.
4. Include **examples or formulas** where relevant.
5. Avoid unnecessary repetition; keep it concise but informative.
6. If a concept has multiple steps, explain each step clearly.
7. Add a summary of the notes at the end.
8. Format everything in **Markdown**, so it can be directly displayed on the frontend.
""".strip()
    return f"""
Generate concise study notes from the following:
for this content{user_input}
{instruction_block}

""".strip()


def get_quiz_prompt(user_input: str, marks: int = 5, mode: str = "short") -> str:

    if mode == "mcq":
        return f"""
You are an quiz generator for students, You create quizzez that can make rivision easy, fun and memorizable.
Stictly based on the "text to generate from", create a quiz with around {marks}marks multiple-choice questions.
Each question must follow this format:
Q: [question]
Options:
A. [Option A]
B. [Option B]
C. [Option C]
D. [Option D]
Answer: [Correct Option Letter]
Rules:
- Options should be plausible and clearly distinct.
- Only ONE correct answer per question.
- Do not include explanations or context.
- Avoid repeating questions.
Text to generate from:
\"\"\"
{user_input}
\"\"\"
"""
    else:
        return f"""
You are an quiz generator for students, You create quizzez that can make rivision easy, fun and memorizable.
Stictly based on the "text to generate from", generate {marks}{["MARKS" if marks <=10 else "WORDS"]} short/long answer type questions.
Rules:
- Keep questions fact-based and clear.
- Answers should be accurate, strictly based on the "text to generate from".
- Do not include explanations.
- Avoid duplicating ideas.
- For 2 marks: Expect 1–2 line factual answers.
- For 5 marks: Expect 1–2 paragraph concept-based answers.
- For 10 marks: Expect detailed explanations with examples.

text to generate from:
{user_input}

Format strictly:
Q: [question]
A: [answer]

Only include {marks}{["MARKS" if marks <=10 else "WORDS"]} such Q&A pairs.
""".strip()

# def get_flan_prompt(user_input, marks, last_msg):
#     return f"""
# ### Previous Interaction:
# **User:** {last_msg['user_msg']}
# **Bot:** {last_msg['bot_response']}

# ### New Question:
# **User:** {user_input}

# ### Bot (Answer for approximately {marks} marks):

# #### Instructions:
# - **2 marks**: 2–3 bullet points. Highlight keywords using `**bold**`.
# - **5 marks**: Short paragraph with key concepts. Emphasize important terms using `**bold**`.
# - **10 marks**: Detailed explanation with `**bold**` for definitions, `code` for technical terms, and examples/diagrams where needed.

# ### Answer (Markdown formatted):
# """.strip()

