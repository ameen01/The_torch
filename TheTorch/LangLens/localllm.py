import requests
import json
import ast
from django.http import JsonResponse
from openai import OpenAI
import time



# Initialize client for LM Studio
client = OpenAI(
    base_url="http://localhost:1234/v1", 
    api_key="lm-studio" # Placeholder

)

def get_llm_rhyme(word):
    SYSTEM_PROMPT = (
    "You must return ONLY a JSON object this "
    "Example:{'word':'salad','category':'food','description':'Vegetables dressed with oil and herbs'}. "
    "Do not include any conversational text. "
    "The JSON must have keys: 'word', 'category', and 'description'. "
    "Rules: 1. If any field is empty, return absolutely nothing. "
    "2.description should be concise, no more than 15 words. "
    "3. Provide a valid dictionary/JSON only." \
    "4. The category must be from ths list only list: color, food, animals, jobs, sports, clothing, household items, nature, technology, body, numbers, letters, transportation." \
    "5. do not create any new category if it is not in the list. " \
)
    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.5-9b:2",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Provide details for the word: {word}"}
            ],
            temperature=0.4,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def generate_vocabulary_list():
    SYSTEM_PROMPT = (
        "You are a vocabulary generator for newcomer english learners . Generate a list of 10 unique words for each category create the same amount of words for each category . "
        "Return ONLY a JSON array of strings, like ['word1', 'word2', ...]. "
        "Do not include any other text." \
        "Rules: 1. YOU NOT ALLOWED TO INCLUDE ANY OTHER TEXT"
        "2 YOU NOT ALLOWED TO REPEAT WORDS IN THIS LIST. " \
        "3. YOU CAN ONLY USE FROM THIS CATEGORY [color, food, animals,jobs,Sports,clothing,household items, nature, technology,body,numbers,letters, transportation]."
    )
    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.5-9b:2",
            # model="dolphin3.0-llama3.1-8b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "Generate a list of 10 words."}
            ],
            temperature=0.7,
        )
        word_list = json.loads(response.choices[0].message.content)
        return word_list
    except Exception as e:
        return f"Error: {str(e)}"


def get_vocabulary_details(word_list):
    details = []
    for word in word_list:
        result = get_llm_rhyme(word)
        if result.startswith("Error"):
            details.append({"word": word, "category": "Error", "description": result})
        else:
            try:
                data = json.loads(result)
                details.append(data)
            except json.JSONDecodeError:
                details.append({"word": word, "category": "Invalid", "description": "Failed to parse response"})
    return details

# Example usage:
# response = get_llm_rhyme(query)
