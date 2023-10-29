from googlesearch import search

# Define the search query
query = "dubai"

# Perform the Google search and print the results
for result in search(query, num_results=5, lang='en', advanced=True):
    print(result)


# # Function for performing a Google search
# def google_search(query, num_rslts=2, lang='en'):
#     search_results = []
#     for result in search(query, num_results=num_rslts, lang=lang, advanced=True):
#         downloaded = fetch_url(result)
#         if downloaded is not None:
#             description = extract(downloaded)
#             description = ' '.join(description.split()[:200])
#             item = {"title": result, "link": result, "description": description}
#             search_results.append(item)
#     return search_results

# def process_input(user_input):
#     response = {}
    
#     # Try to evaluate the user input as a mathematical expression first
#     calculation_result = calculate_expression(user_input)
#     if calculation_result is not None:
#         response['calculation'] = calculation_result
#         return json.dumps(response, separators=(',', ':'))
        
#     words = word_tokenize(user_input)

#     for word in words:
#         if word in ['search', 'find', 'query', 'google']:
#             query = ' '.join(words[words.index(word)+1:])
#             response['web_result'] = google_search(query)
#         elif word == 'calculate':
#             expression = ' '.join(words[words.index(word)+1:])
#             response['calculation'] = calculate_expression(expression)

#     return json.dumps(response, separators=(',', ':'))

# def read_llm_output(llm_process, ready_for_input):
#     previous_char = ''
#     first_prompt_found = False
    
#     while True:
#         current_char = llm_process.stdout.read(1)
#         print(current_char, end='', flush=True)

#         if first_prompt_found:
#             # After the first prompt is found, just check for '>'
#             if current_char == '>':
#                 with ready_for_input:
#                     ready_for_input.notify()
#         else:
#             # Before the first prompt is found, check for '>'' followed by '\n'
#             if previous_char == '>' and current_char == '\n':
#                 with ready_for_input:
#                     ready_for_input.notify()
#                 first_prompt_found = True

#         previous_char = current_char