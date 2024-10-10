import json
import subprocess
from nltk.tokenize import word_tokenize
from googlesearch import search

# Function for calculating mathematical expressions
def calculate_expression(expression):
    try:
        result = eval(expression, {'__builtins__': None}, {})
    except Exception as e:
        result = None
    return result

def google_search(query, num_rslts=3, lang='en'):
    print('Performing Google search...')
    try:
        search_results = []
        for result in search(query, num_results=num_rslts, lang=lang, advanced=True):
            item = {"title": result.title, "link": result.url, "description": result.description}

            # Limit the description to 200 words
            item["description"] = ' '.join(item["description"].split()[:200])

            search_results.append(item)

            # Print the search result for confirmation
            print("Search Result:", item)

        return search_results
    except Exception as e:
        print("Error in google_search:", e)
        return []  # Return an empty list in case of an error

def process_input(user_input):
    response = {}
    
    # Try to evaluate the user input as a mathematical expression first
    calculation_result = calculate_expression(user_input)
    if calculation_result is not None:
        response['calculation'] = calculation_result
        return json.dumps(response, separators=(',', ':'))
        
    words = word_tokenize(user_input)

    for word in words:
        if word in ['search', 'find', 'query', 'google']:
            query = ' '.join(words[words.index(word)+1:])
            response['web_result'] = google_search(query)
        elif word == 'calculate':
            expression = ' '.join(words[words.index(word)+1:])
            response['calculation'] = calculate_expression(expression)

    return json.dumps(response, separators=(',', ':'))

def run_daisy(input_text):
    print(input_text)
    if 'google' in input_text or 'search' in input_text:
        response = 'Googling...'
    else:
        response = 'Thinking...'

    try:
        llm_process = subprocess.Popen(
            ["./main", "-t", "4", "-m", "/Users/rick/Desktop/DaisyChat-3/llama.cpp/models/llama-2-7b-chat.ggmlv3.q2_K.bin",
            "--color", "-c", "2048", "--temp", "0.7", "--repeat_penalty", "1.1", "-ins",
            "-p", '<<SYS>> You are a helpful, respectful and honest female assistant called Daisy. Always answer as helpfully as possible. The user’s name is Friend.',
            "-p", response + " " + input_text],  # Combine response with input_text
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        for line in llm_process.stdout:
            print(line.strip())  # Print the output to the console

    except Exception as e:
        return str(e)

# Example usage:
if __name__ == "__main__":
    while True:
        user_input = input("Enter your query: ")
        if user_input.lower() == 'exit':
            break
        run_daisy(user_input)
