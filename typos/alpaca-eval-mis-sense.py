import requests
import json
import time
from tqdm import tqdm  # For a progress bar

# Your API key - store this securely in practice
API_KEY=""

# The API endpoint
API_URL = "https://api.anthropic.com/v1/messages"

# Headers for the request
headers = {
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

# List of queries to send
queries = []

with open("/Users/jacobm/Documents/repos/llm-ambiguity/typos/alpaca-eval-prompts.json") as f_in:
    data = json.loads(f_in.read())
    for elem in data:
        queries.append(elem["instruction"])

# Function to send a single query
def query_claude(alpaca_prompt):
    prompt = f"Can you change one word in this prompt as if I had misspelled it and it was autocorrected to another word? Ideally the word should be \"reasonable\" if I were to read the sentence after the change. Please give me 3 different options.\n\nAfter you explain your rationale, please list all 3 on separate lines at the bottom after the word \"Options:\" like this:\n\nOptions:\n<option 1>\n<option 2>\n<option 3>\n\nPrompt: \"{alpaca_prompt}\""

    data = {
        "model": "claude-3-7-sonnet-20250219",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None

# Process all queries with rate limiting
results = []
failed_results = []
for query in tqdm(queries, desc="Processing queries"):
    result = query_claude(query)
    if result:
        results.append(
            {
                "original_query": query,
                "claude_response": result
            })
    else:
        failed_results.append(query)
    
    # Rate limiting - adjust as needed based on your API tier
    # time.sleep(0.1)

# Save results to a file
with open("claude_responses.json", "w") as f_out:
    json.dump(results, f_out, indent=2)

if len(failed_results > 0):
    with open("failed_queries.json", "w") as f_out:
        json.dump(failed_results, f_out, indent=2)

print(f"Completed {len(results)} queries successfully.")