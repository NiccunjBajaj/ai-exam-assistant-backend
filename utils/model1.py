import asyncio

from .prompt_format import get_flash_prompt, get_note_prompt, get_quiz_prompt

TIMEOUT = 20

def init_sarvam_openai(gpt,svaram):
    global client, sarvam_client
    client = gpt
    sarvam_client = svaram

async def _run_llm(prompt: str, type:str) -> str | None:

    if type == "notes":
        try:
            response_raw = await asyncio.wait_for(
                asyncio.to_thread(
                    lambda: client.chat.completions.create(
                        messages=[{"role": "system", "content": prompt}],
                        model="openai/gpt-4.1"
                        )
                ),timeout=TIMEOUT
            )
            response = response_raw.choices[0].message.content
            return response
        except asyncio.TimeoutError:
            print(f"❌ GPT Timeout😴")
        except Exception as e:
            print(f"GPT error: {str(e)}")
    else:
        try:
            response_raw = await asyncio.wait_for(
                asyncio.to_thread(
                    lambda: sarvam_client.chat.completions(
                        messages=[
                            {
                            "content": prompt,
                            "role": "system", 
                            },
                            {
                            "content": "create quiz",
                            "role": "user", 
                            }
                        ],
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
    return await _run_llm(get_flash_prompt(user_input, marks),"flashcard")

async def note(user_input: str, marks: int) -> str | None:
    return await _run_llm(get_note_prompt(user_input, marks),"notes")

async def quiz(user_input: str, marks: int, mode: str) -> str | None:
    return await _run_llm(get_quiz_prompt(user_input, marks, mode),"quiz")



