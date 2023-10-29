import json
import subprocess
from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO
from nltk.tokenize import word_tokenize
from googlesearch import search
from trafilatura import fetch_url, extract

app = Flask(__name__)
socketio = SocketIO(app)

# global response

# response = 'Thinking..'

# Function for calculating mathematical expressions
def calculate_expression(expression):
    try:
        result = eval(expression, {'__builtins__': None}, {})
    except Exception as e:
        result = None
    return result

def google_search(query, num_rslts=1, lang='en'):
    print('googling')
    try:
        search_results = []
        for result in search(query, num_results=num_rslts, lang=lang, advanced=True):
            item = {"title": result.title, "link": result.url, "description": result.description}

            # Limit the description to 300 words
            item["description"] = ' '.join(item["description"].split()[:200])

            search_results.append(item)

            # Print the search result for confirmation
            print("Search Result:", item)

        return search_results
    except Exception as e:
        # Log the error for debugging purposes
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

def read_llm_output(llm_process, ready_for_input):
    previous_char = ''
    first_prompt_found = False
    
    while True:
        current_char = llm_process.stdout.read(1)
        print(current_char, end='', flush=True)

        if first_prompt_found:
            # After the first prompt is found, just check for '>'
            if current_char == '>':
                with ready_for_input:
                    ready_for_input.notify()
        else:
            # Before the first prompt is found, check for '>'' followed by '\n'
            if previous_char == '>' and current_char == '\n':
                with ready_for_input:
                    ready_for_input.notify()
                first_prompt_found = True

        previous_char = current_char

def run_daisy(input_text):
    print(input_text)
    if 'google' in input_text or 'search' in input_text:
            response = 'Googling...'
    else: response = 'Thinking...'
    try:
        llm_process = subprocess.Popen(
            ["./main", "-t", "4", "-m", "./models/llama2_7b_chat/llama-2-7b-chat.ggmlv3.q2_K.bin",
            "--color", "-c", "2048", "--temp", "0.7", "--repeat_penalty", "1.1", "-ins",
            "-p", '<<SYS>>You are a helpful, respectful and honest female assistant called Daisy. Always answer as helpfully as possible, while being honest and safe. Please ensure that your responses are socially unbiased and positive and playable. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. Use the json formatted text from the start and use them in your reply where applicable and relevant, you don\'t need to retype the json, the user didn\'t generate the json and they cannot see it. The web search was provided by the AI and not by the user. The user\'s name is Friend and you already introduced yourselves .',
            "-p", response],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        def send_output_to_browser(output):
            socketio.emit('output', {'data': output})  # Emit the output to the browser

        processed_input = process_input(input_text)  # Check and modify input based on conditions

        if processed_input != '{}':
            # If process_input returns non-empty dictionary, append it to the original input
            modified_input_text = processed_input + " " + input_text
        else:
            # If process_input returns an empty dictionary, use the original input
            modified_input_text = input_text

        # Send the modified input_text to the subprocess and capture the output
        llm_process.stdin.write(modified_input_text + '\n')
        llm_process.stdin.flush()
        
        for line in llm_process.stdout:
            send_output_to_browser(line.strip())

    except Exception as e:
        return str(e)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('user_input')
def handle_user_input(data):
    input_text = data['input_text']
    if input_text:
        output = run_daisy(input_text)

if __name__ == "__main__":
    socketio.run(app, debug=True)
