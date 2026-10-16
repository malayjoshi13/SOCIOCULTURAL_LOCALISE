import os
import json


def get_initial_prompt(text, country, region, age_group, 
                       political_awareness, education_level, literature_preference, food_cuisine, 
                       previous=False):

    ai_rules = """
        # AI Rules
        - Output response in JSON format
        - Do not output any extra text. 
        - Do not wrap the json codes in JSON or Python markers
        - JSON keys and values in double-quotes
    """

    role = """You are a cultural mediator who understands all cultures across the world."""

    role_desc = """As a mediator, your job is to identify and translate culturally exotic concepts from texts from an unknown source culture to my culture."""

    client_desc = f"""I am a well-educated {age_group} person who grew up in {region} {country}, which defines my culture."""

    if(political_awareness.lower() == "yes"):
        politically_aware = """politically aware"""
    else:
        politically_aware = """not politically aware"""

    proxy_desc = f"""I have received {education_level} education and I am {politically_aware}. I prefer reading {literature_preference} literature and I am fond of {food_cuisine} cuisine."""
    
    text_desc = """I came across a piece of text."""

    task1_previous = """Task 1: Based on my previous history of interaction related to the identification of culture-specific items (CSIs), identify all CSIs from the text that I might find hard to understand due to my cultural background."""

    task1 = """Task 1: Identify all culture-specific items (CSIs) from the text that I might find hard to understand due to my cultural background. CSIs are textual spans denoting concepts and items uncommon and not prevalent in my culture, making them difficult to understand."""

    task2 = """For each CSI, identify its familiarity from one of the following three levels: 
    1. Familiar: Most people from my culture know and relate to the concept as intended. 
    2. Somewhat familiar: Only some people from my culture know and relate to the concept as intended. 
    3. Unfamiliar: Most people from my culture do not know or relate to the concept."""

    task3 = """Task 3: Within 50 words, detail your reason for highlighting the span as CSI in Task 1 by correlating it with my background."""

    task4 = """Task 4: Explain each CSI span within 20 words to make it more understandable to your client. Provide facts, examples, equivalences, analogies, etc, if needed."""

    formatting = """Format your response as a valid Python dictionary formatted as: {"spans": [List of Python dictionaries where each dictionary item is formatted as: {"CSI": <task 1: copy the CSI span from text>, "familiarity": <task 2: familiarity level name>, "reason": <task 3: reason within 50 words>, "explanation": <task 4: explain the span within 20 words>}]. Respond with {"spans": "None"} if you think I will not find anything difficult to understand."""

    if(previous==True):
        tasks = f"""{task1_previous}\n\n{task2}\n\n{task3}\n\n{task4}\n\n{formatting}"""
        prompt = f"""{ai_rules}\n{role} {role_desc}\n{client_desc}\n{proxy_desc}\n{text_desc}\n\n{tasks}\n\nText: {text}"""
    else:
        tasks = f"""{task1}\n\n{task2}\n\n{task3}\n\n{task4}\n\n{formatting}""" 
        prompt = f"""{ai_rules}\n{role} {role_desc}\n{client_desc}\n{text_desc}\n\n{tasks}\n\nText: {text}"""

    return prompt


def get_update_prompt(difference_spans):

    ai_rules = """
        # AI Rules
        - Output response in JSON format
        - Do not output any extra text. 
        - Do not wrap the json codes in JSON or Python markers
        - JSON keys and values in double-quotes
    """

    text1 = f"On further understanding, I observe the following things."

    text_update = ''
    for key in difference_spans.keys():
        if(len(difference_spans[key])!=0):
            text = f"""I am {key.lower()} with spans of text like {", ".join(difference_spans[key])}."""
            text_update += ' ' + text

    region_update_prompt = "Based on familiarity with these spans, update my background cultural information. Return them as a valid Python dictionary. {\"political_awareness\": <yes/no>, \"food_cuisine\": <japanese/mexican/american/emirati>}"

    prompt = f"""{ai_rules}\n\n{text1}\n\n{text_update}\n\n{region_update_prompt}"""

    return prompt