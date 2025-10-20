import asyncio

from .prompt_format import get_flash_prompt, get_note_prompt, get_quiz_prompt

TIMEOUT = 20

GPT_MODEL = "openai/gpt-4.1"

def init_gpt(gpt):
    global client
    client = gpt

def init_gemini(gemini):
    global model
    model = gemini


async def _run_llm(prompt: str) -> str | None:
    try:
        response_raw = await asyncio.wait_for(asyncio.to_thread(model.generate_content,prompt),timeout=TIMEOUT)
        gemini_response = response_raw.text
        return gemini_response
    except asyncio.TimeoutError:
        print(f"❌ Gemini Timeout😴")
    except Exception as e:
        print(f"Gemini error: {str(e)}")

    try:
        print(f"🔍 Generating response with GPT-4.1")
        response_raw = await asyncio.wait_for(
            asyncio.to_thread(
                lambda: client.chat.completions.create(
                model=GPT_MODEL,
                messages=[{"role": "system", "content": prompt}],
                max_tokens=4096,
                temperature=1,
                )
            ),timeout=TIMEOUT
        )
        gpt_response = response_raw.choices[0].message.content
        return gpt_response
    except asyncio.TimeoutError:
        print(f"❌ GPT Timeout😴")
    except Exception as e:
        print(f"GPT error: {str(e)}")



# async def _run_quiz(prompt: str) -> str | None:
#     try:
#         response_raw = await asyncio.wait_for(
#             asyncio.to_thread(
#                 lambda: client.chat.completions.create(
#                 model=GPT_MODEL,
#                 messages=[{"role": "system", "content": prompt}],
#                 max_tokens=4096,
#                 temperature=1,
#                 )
#             ),timeout=TIMEOUT
#         )
#         response = response_raw.choices[0].message.content
#         return response
#     except asyncio.TimeoutError:
#         print("❌ Gemini timeout")
#     except Exception as e:
#         print("Gemini error:", e)

async def flashcard(user_input: str, marks: int) -> str | None:
    return await _run_llm(get_flash_prompt(user_input, marks))

async def note(user_input: str, marks: int) -> str | None:
    return await _run_llm(get_note_prompt(user_input, marks))

async def quiz(user_input: str, marks: int, mode: str) -> str | None:
    return await _run_llm(get_quiz_prompt(user_input, marks, mode))



