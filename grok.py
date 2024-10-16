import os
import json
import requests


def startchat():
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("API key not found in Secrets")
        exit()

    conversation = [{"role": "system", "content": "You are who you are."}]

    print("Enter an empty message to quit.\n")

    while True:
        user_input = input("Hello, please give us some feedback on our product: ")
        user_input += "Please give the output in JSON format with the format {message:}"
        print("")

        if not user_input:
            print("Empty input received. Exiting chat.")
            break

        conversation.append({"role": "user", "content": user_input})

        print("Support Bot: ", end="", flush=True)
        full_response = ""
        for token in create_chat_completion(api_key, conversation):
            full_response += token
        print("\n")

        print(full_response)
        conversation.append({"role": "assistant", "content": full_response})

    print("Thank you for using the customer service bot!")


def send_grok_message(message):

    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("API key not found in Secrets")
        exit()

    conversation = [{"role": "system", "content": "You are who you are."}]

    conversation.append({"role": "user", "content": message})

    full_response = ""
    for token in create_chat_completion(api_key, conversation):
        full_response += token
    
    return full_response


def create_chat_completion(api_key, messages):
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }
    data = {
        "messages": messages,
        "model": "grok-2-public",
        "stream": True,
    }

    with requests.post(url, headers=headers, json=data, stream=True) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    line = line[6:]
                    if line.strip() == "[DONE]":
                        break
                    chunk = json.loads(line)
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        delta = chunk["choices"][0]["delta"]
                        if "content" in delta:
                            yield delta["content"]

    conversation = [{"role": "system", "content": "You are who you are."}]


# Return a boolean if a message is a valid product review or not
def check_review(review):

    message = send_grok_message("Return 1 if this is a valid product review and 0 otherwise. Do not output any text other than 0 or 1. The review:" + review)

    if message == "1":
        return True
    
    return False


