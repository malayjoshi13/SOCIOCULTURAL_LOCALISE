from openai import OpenAI
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_deployment_and_client(model):  
  
    api_key = os.getenv("OPENROUTER_API_KEY")  
  
    client = OpenAI(  
        base_url="https://openrouter.ai/api/v1",  
        api_key=api_key,  
    )  
  
    if model == 'gpt35':  
        deployment = os.getenv("DEPLOYMENT_NAME", "openai/gpt-3.5-turbo")  
    elif model == 'gpt4':  
        deployment = os.getenv("DEPLOYMENT_NAME", "openai/gpt-4-turbo")  
    elif model == 'gpt4o':  
        deployment = os.getenv("DEPLOYMENT_NAME", "openai/gpt-4o")  
  
    return deployment, client


def generate_output(deployment, client, messages):

    response = client.chat.completions.create(
        model=deployment,
        messages=messages,
        temperature=0.0,
        max_tokens=4096
    )

    generated_text = response.choices[0].message.content.strip()
    return json.loads(generated_text)

def predict(payload):

    query_parameters = payload

    model = 'gpt4o'
    print(f'Using {model} in the backend !!!')
    deployment, client = get_deployment_and_client(model)

    messages = query_parameters['messages']
    response = generate_output(deployment, client, messages)
    
    return response
