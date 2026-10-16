import requests
import json
import ast
import datetime
import os
import sys
from pathlib import Path

from .prompts import get_initial_prompt, get_update_prompt
from app.services.llm_client import predict

URL_TO_TEXT_FILE = Path(__file__).resolve().parents[2] / "url_to_text.json"
GPT_URL = "127.0.0.1"
GPT_PORT = 7777

def add_start_end_index(input_text, spans):

    input_text = input_text

    output_dict = dict()
    output_dict["classes"] = [
        "FAMILIAR",
        "SOMEWHAT FAMILIAR",
        "UNFAMILIAR"
    ]
    output_dict["annotations"] = [[input_text, dict()]]

    entities_list = list()
    input_text = input_text.lower()
    for span in spans:
        familiarity = span["familiarity"]
        start_index = input_text.find(span["CSI"].lower())
        
        if start_index == -1:
            pass
            #entities_list.append([-1,-1, familiarity.upper()])
        else:
            end_index = start_index + len(span["CSI"]) - 1
            entities_list.append([start_index, end_index, familiarity.upper()])

    output_dict['annotations'][0][1]["entities"] = entities_list
    return output_dict

def filter_on_familiarity(response):
    spans = response["spans"]
    response_filtered_spans = [span for span in spans if span['familiarity'].lower() != 'familiar']

    return response_filtered_spans

def filter_and_add_start_end_indices(input_text, response):
    response_filtered_spans = filter_on_familiarity(response)
    response_add_start_end_index = add_start_end_index(input_text, response_filtered_spans)
    return response_add_start_end_index

def get_response_initial_prompt(input_text, country, region, age_group, 
                                political_awareness, education_level, literature_preference, food_cuisine,
                                messages, previous):
    
    prompt = get_initial_prompt(input_text, country, region, age_group, political_awareness, education_level, literature_preference, food_cuisine, previous)
    
    messages.append({"role": "user", "content": prompt})
    payload = {
        'messages': messages
    }

    print(f"Identifying CSIs from the given text...")
    response = predict(payload)
    messages.append({"role":"assistant", "content": str(response)})    
    return response, messages

def get_spans(initial_tokens):
    spans = {'FAMILIAR': [], 'SOMEWHAT FAMILIAR': [], 'UNFAMILIAR': []}
    for init_token in initial_tokens:
        label = init_token["label"]
        tokens = []
        for token in init_token["tokens"]:
            tokens.append(token["text"])
        spans[label].append(' '.join(tokens))
    return spans

def dict2_minus_dict1(d1, d2):
    difference = {}
    for key in d2:
        difference[key] = list(set(d2[key]) - set(d1[key]))
    return difference

def get_response_update_prompt(query_parameters):

    annotations_initial = query_parameters['annotations_updated']['token_block_initial']
    annotations_updated = query_parameters['annotations_updated']['token_block_body']

    initial_spans = get_spans(annotations_initial)
    updated_spans = get_spans(annotations_updated)
    difference_spans = dict2_minus_dict1(initial_spans, updated_spans)
    
    prompt = get_update_prompt(difference_spans)

    messages = query_parameters['messages']
    messages.append({"role": "user", "content": prompt})

    payload = {
        'messages': messages
    }

    print(f"Identifying CSIs from the given text...")
    response = predict(payload)
    messages.append({"role":"assistant", "content": str(response)}) 

    response_json_format = response
    for key in response_json_format.keys():
        query_parameters[key] = response_json_format[key]

    return query_parameters


def get_response_from_backend_exp3(query_parameters):

    type_ = query_parameters['type']
    with URL_TO_TEXT_FILE.open('r') as file:
        url_to_text = json.load(file)

    text = url_to_text[query_parameters['url']]

    country = query_parameters['country']
    age_group = query_parameters['age_group']
    region = query_parameters['region']

    political_awareness = query_parameters['political_awareness']
    education_level = query_parameters['education_level']
    literature_preference = query_parameters['literature_preference']
    food_cuisine = query_parameters['food_cuisine']

    messages = query_parameters['messages']
    if(isinstance(messages, list) == False):
        messages = ast.literal_eval(query_parameters['messages'])

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    if(type_ == 'fresh'):
        response, messages = get_response_initial_prompt(text, country, region, age_group, 
                                                         political_awareness, education_level, literature_preference, food_cuisine,
                                                         messages, previous=False)
        query_parameters['annotations_response'] = filter_and_add_start_end_indices(text, response)
        query_parameters['messages'] = messages
        # json.dump(query_parameters, open(f'outputs/{type_}_{country}_{age_group}_{region}_{timestamp}.json','w'), indent=4)
    elif(type_ == 'old'):
        response, messages = get_response_initial_prompt(text, country, region, age_group, 
                                                         political_awareness, education_level, literature_preference, food_cuisine,
                                                         messages, previous=True)
        query_parameters['annotations_response'] = filter_and_add_start_end_indices(text, response)
        query_parameters['messages'] = messages
        # json.dump(query_parameters, open(f'outputs/{type_}_{country}_{age_group}_{region}_{timestamp}.json','w'), indent=4)
    elif(type_ == 'save_info'):    
        query_parameters = get_response_update_prompt(query_parameters)
        # json.dump(query_parameters, open(f'outputs/{type_}_{country}_{age_group}_{region}_{timestamp}.json','w'), indent=4)

    return query_parameters