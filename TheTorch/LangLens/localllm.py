import requests
import json








def get_llama_rhyme(user_query,):
    url = "http://localhost:1234/v1/chat/completions"
    SYSTEM_PROMPT ="you need give chose one category [animal , food, Occupation ] word and small definition max 20 words to definition the only response just like the exampel as python dict" \
    "for  exampel:" \
    "{category: food","word:apple", "definition: An apple is a type of fruit that grows on trees. It's often red, green, or yellow and can be eaten fresh or used in cooking}"

    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "dolphin3.0-llama3.1-8b",
        "messages": [
            {
                "role": "system", 
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user", 
                "content": user_query
            }
        ],
        "temperature": 0.5,
        "max_tokens": 600,
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_json = response.json()
        # Extracting the text just like the curl output does
        # return response_json['choices'][0]['message']['content']
        return response
    except Exception as e:
        return f"Model is sleeping, I suppose? Error: {e}"

    

user_text = "dog"
the_rhyme = get_llama_rhyme(user_text)

d = the_rhyme.json()

print(d)


