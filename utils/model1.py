import asyncio

from .prompt_format import get_flash_prompt, get_note_prompt, get_quiz_prompt

TIMEOUT = 20

def init_sarvam(sarvam):
    global client
    client = sarvam

async def _run_llm(prompt: str) -> str | None:
    try:
        response_raw = await asyncio.wait_for(
            asyncio.to_thread(
                lambda: client.chat.completions(
                messages=[{"role": "system", "content": prompt}],
                )
            ),timeout=TIMEOUT
        )
        response = response_raw.choices[0].message.content
        return response
    except asyncio.TimeoutError:
        print(f"❌ Sarvam Timeout😴")
    except Exception as e:
        print(f"Sarvam error: {str(e)}")

async def flashcard(user_input: str, marks: int) -> str | None:
    return await _run_llm(get_flash_prompt(user_input, marks))

async def note(user_input: str, marks: int) -> str | None:
    return await _run_llm(get_note_prompt(user_input, marks))

async def quiz(user_input: str, marks: int, mode: str) -> str | None:
    return await _run_llm(get_quiz_prompt(user_input, marks, mode))



