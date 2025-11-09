# def init_model(gemini):
#     global model
#     model = gemini

# def summarize_with_gemini(full_text: str) -> str:
#     prompt = f"""INSTRUCTION:
# You are an AI assistant tasked with summarizing a conversation between a user and an AI.
# The conversation will be stored in long-term memory for future reference, so preserve essential context, intentions, and key knowledge shared.

# Summarize the following conversation in a detailed yet concise manner:
# 1. Clearly mention what the user is trying to achieve or understand.
# 2. Capture helpful responses, insights, or factual data shared by the assistant.
# 3. Avoid repetition or generic filler phrases.
# 4. Format the output in paragraphs or numbered points.
# 5. Keep it under 800 characters if possible, otherwise split it logically.

# CONVERSATION:
# {full_text}
# """
#     try:
#         response = model.generate_content(prompt)
#         return response.text.strip()
#     except Exception as e:
#         print(f"❌ Gemini summarization failed: {e}")
#         return ""
