import requests

# Chat Completions (POST /v1/chat/completions)
response = requests.post(
  "https://api.sarvam.ai/v1/chat/completions",
  headers={
    "api-subscription-key": "sk_kpp6wrwv_LmDZSqQSZJOKyzRiVrh3Ahhb"
  },
  json={
    "messages": [
      {
        "content": "you are a desgin prompter",
        "role": "system"
      },
      {
        "content": "what is the best color pallete for edu",
        "role": "user"
      }
    ],
    "model": "sarvam-m"
  },
)

data = response.json()

assistant_reply = data["choices"][0]["message"]["content"]
print("Assistant:", assistant_reply)