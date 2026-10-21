import json
from pathlib import Path

from .prompts import get_initial_prompt, get_update_prompt
import ast
from app.services.llm_client import predict

URL_TO_TEXT_FILE = Path(__file__).resolve().parents[2] / "url_to_text.json"

# ----------------------------------------------------------------------------------------------------------------------------

# Build the context-aware prompt and invoke the LLM for CSI classification. 

# This function collates user-inputted details (of country, region, age_group), 
# builds the prompt (via fn "get_initial_prompt"), 
# and calls the model (via fn "get_initial_prompt"),
def get_response_initial_prompt(input_text, country, region, age_group, 
                                political_awareness, education_level, literature_preference, food_cuisine,
                                messages, previous):

    # Here: previous interactions are provided through "messages", and "previous" flag changes the wording of the prompt.

    prompt = get_initial_prompt(input_text, country, region, age_group, 
                                political_awareness, education_level, literature_preference, food_cuisine, 
                                previous)
  
    messages.append({"role": "user", "content": prompt})
    payload = {
        'messages': messages
    }
    
    print(f"Identifying CSIs from the given text...")
    response = predict(payload)
    messages.append({"role":"assistant", "content": str(response)})    
    return response, messages

# ----------------------------------------------------------------------------------------------------------------------------

# Convert model-generated CSI spans into frontend-ready annotations by filtering/removing out familiar terms and adding text offsets.

# This function converts response generated from model into frontend usable format by adding start and end indices to each CSI span based on the input text.
# For example:
# - input => input_text: "I love sushi and ramen" and model identified CSI span: {"CSI": "sushi", "familiarity": "unfamiliar"}, 
# - this function will find start index of "sushi" in the input text (which is 7) and the end index (which is 11), and add these indices to the response.
# - output => [{...}, {"start": 7, "end": 11, "familiarity": "UNFAMILIAR"}, {...}]
def add_start_end_index(input_text, spans):

    input_text = input_text

    output_dict = dict()
    output_dict["classes"] = [
        "UNFAMILIAR",
        "SOMEWHAT FAMILIAR"
    ]
    output_dict["annotations"] = [[input_text, dict()]]

    entities_list = list()
    input_text = input_text.lower()
    for span in spans:
        familiarity = span["familiarity"]
        start_index = input_text.find(span["CSI"].lower())
        
        if start_index == -1:
            entities_list.append([-1,-1, familiarity.upper()])
        else:
            end_index = start_index + len(span["CSI"]) - 1
            entities_list.append([start_index, end_index, familiarity.upper()])

    output_dict['annotations'][0][1]["entities"] = entities_list
    return output_dict


# This function remove FAMILIAR items. 
# Thus only UNFAMILIAR and SOMEWHAT FAMILIAR items continue to the frontend.
def filter_on_familiarity(response):
    spans = response["spans"]
    if(spans != "None"):
        response_filtered_spans = [span for span in spans if span['familiarity'].lower() != 'familiar']
        return response_filtered_spans
    else:
        return []
        

# This function combine filtering of FAMILIAR terms via "filter_on_familiarity" function,
# and offset conversion via "add_start_end_index" function into one for convenience.
def filter_and_add_start_end_indices(input_text, response):
    response_filtered_spans = filter_on_familiarity(response)
    response_add_start_end_index = add_start_end_index(input_text, response_filtered_spans)
    return response_add_start_end_index

# ----------------------------------------------------------------------------------------------------------------------------

# Extract explanations for non-familiar CSIs to accompany highlighted annotations in the frontend.

# This function extracts explanations for non-familiar CSIs from the model response so they can be displayed on frontend alongside the highlighted terms.
def get_explanations(response):
    filtered_spans = filter_on_familiarity(response)
    explanations = []

    for span in filtered_spans:
        explanations.append({"CSI": span['CSI'], "explanation": span['explanation']})

    return explanations

# ----------------------------------------------------------------------------------------------------------------------------

# Process user-edited annotations and update conversation context for subsequent LLM responses.

# This function converts frontend token-block annotations into a simpler dictionary grouped by familiarity.
# For example:
# - input => [{"label": "UNFAMILIAR", "tokens": [{"text": "state"}, {"text": "caucus"}]}, {"label": "FAMILIAR", "tokens": [{"text": "election"}]}]
# - output => {"FAMILIAR": ["election"], "SOMEWHAT FAMILIAR": [], "UNFAMILIAR": ["state caucus"]}
def get_spans(initial_tokens):
    spans = {'FAMILIAR': [], 'SOMEWHAT FAMILIAR': [], 'UNFAMILIAR': []}
    for init_token in initial_tokens:
        label = init_token["label"]
        tokens = []
        for token in init_token["tokens"]:
            tokens.append(token["text"])
        spans[label].append(' '.join(tokens))
    return spans


# This function compares the AI’s original classifications (sp1) with the user’s edited classifications (sp2).
# It then treats every removed phrase as FAMILIAR, as the assumption is: if the user removes an AI-generated highlight, the user must already understand it.
def get_added_removed_spans(sp1, sp2):
    added = {}
    removed = {}

    for familiarity in sp1.keys():
        set1 = set(sp1[familiarity])
        set2 = set(sp2[familiarity])
        added[familiarity] = list(set2 - set1)
        removed[familiarity] = list(set1 - set2)
    
    for key, values in removed.items():
        if(values != []):
            for value in values:
                added['FAMILIAR'].append(value)

    return added


# This function builds the prompt for the model to generate an updated response based on the user’s edits to the AI’s original classifications.
def get_response_update_prompt(annotations_initial, annotations_updated, messages):
    initial_spans = get_spans(annotations_initial)
    updated_spans = get_spans(annotations_updated)
    difference_spans = get_added_removed_spans(initial_spans, updated_spans)
    
    prompt = get_update_prompt(difference_spans)
    messages.append({"role": "user", "content": prompt})
    return messages

# ----------------------------------------------------------------------------------------------------------------------------

# Main function orchestrating this "base_localization" experiment pipeline.

# Retrieve the input text either from a URL-to-text mapping or directly from user-provided text.
# Extract the user's attributes and conversation history.
# Based on the request type (fresh, old, or save_info), following action takes place: 
# - For fresh and old requests, generate an LLM response via "get_response_initial_prompt" function using the appropriate previous-context setting.
# - For fresh and old requests, filter the LLM-response annotations and assign their start and end indices via "filter_and_add_start_end_indices" function.
# - For fresh and old requests, extract explanations from the LLM response via "get_explanations" function.
# - For save_info requests, update the message history based on initial AI's classifications and user-edited annotations (to this AI's initial classifications).
# Update the query parameters with generated annotations, explanations, and/or updated conversation history, as applicable.
# Then return these updated query parameters.
def get_response_from_backend_exp1(query_parameters):

    type_ = query_parameters['type']

    if('text' not in query_parameters.keys()):
        with URL_TO_TEXT_FILE.open('r') as file:
            url_to_text = json.load(file)
        text = url_to_text[query_parameters['url']]
    else:
        text = query_parameters['text']

    country = query_parameters['country']
    age_group = query_parameters['age_group']
    region = query_parameters['region']
    messages = query_parameters['messages']

    political_awareness = query_parameters['political_awareness']
    education_level = query_parameters['education_level']
    literature_preference = query_parameters['literature_preference']
    food_cuisine = query_parameters['food_cuisine']

    if(isinstance(messages, list) == False):
        messages = list(ast.literal_eval(messages))

    # Here: "type_" comes from the JSON request body sent by ner-annotator =>
    # - type_ = 'fresh': Sent when the user submits the first text or URL and no previous interaction history exists.
    # - type_ = 'save_info': Sent when the user saves their edits to the initial AI-generated annotations.
    # - type_ = 'old': Sent when the user submits another text or URL after feedback has been saved and conversation history exists.

    if(type_ == 'fresh'):
        # Upon receiving a 'type_ = fresh' request from ner-annotator, the backend builds the initial prompt with previous=False. 
        # Then the LLM identifies CSIs and returns familiarity labels and explanations.
        # Then frontend displays the resulting highlights.
        response, messages = get_response_initial_prompt(text, country, region, age_group, 
                                                         political_awareness, education_level, literature_preference, food_cuisine,
                                                         messages, previous=False)
        query_parameters['annotations_response'] = filter_and_add_start_end_indices(text, response)
        query_parameters['explanations'] = get_explanations(response)
        query_parameters['messages'] = messages

    elif(type_ == 'save_info'):
        # Upon receiving a 'type_ = save_info' request from ner-annotator, the backend converts those differences into a feedback prompt and appends it to the conversation messages.
        # The LLM is not called during this step, and the feedback is not persistently stored in a database.
        annotations_initial = query_parameters['annotations_updated']['token_block_initial']
        annotations_updated = query_parameters['annotations_updated']['token_block_body']
        messages = get_response_update_prompt(annotations_initial, annotations_updated, messages)
        query_parameters['messages'] = messages

    elif(type_ == 'old'):
        # Upon receiving an 'type_ = old' request from ner-annotator, the backend uses the same inference flow as "fresh", 
        # but passes previous=True to select the history-aware prompting (uaing the earlier conversation and user corrections), 
        # allowing it to personalize its next CSI classifications.
        response, messages = get_response_initial_prompt(text, country, region, age_group, 
                                                         political_awareness, education_level, literature_preference, food_cuisine,
                                                         messages, previous=True)
        query_parameters['annotations_response'] = filter_and_add_start_end_indices(text, response)
        query_parameters['explanations'] = get_explanations(response)
        query_parameters['messages'] = messages

    return query_parameters