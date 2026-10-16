import os
import json


def get_initial_prompt(text, country, region, age_group, political_awareness, education_level, literature_preference, food_cuisine, previous=True):

    ai_rules = """
        # AI Rules
        - Output response in JSON format
        - Everything should be inside {}
        - JSON keys and values in double-quotes
        - Do not output any extra text. 
        """

    role = """You are a cultural mediator who understands all cultures across the world."""

    role_desc = """As a mediator, your job is to identify and translate culturally exotic concepts from texts from an unknown source culture to my culture."""

    if(political_awareness == "yes"):
        politically_aware = f"""I am politically aware"""
    else:
        politically_aware = f"""I am not poltically aware"""

    client_desc = f"""I am a/an {age_group}, who grew up in the {region} {country} and only knows about {region} {country} culture. {politically_aware} about {country}, have {education_level.lower()} education level, I prefer reading {literature_preference.lower()} literature, and I prefer {food_cuisine.lower()} cuisine."""

    text_desc = """I came across a piece of text."""

    task1 = """Task 1: Identify all culture-specific items (CSIs) from the review text that I might find hard to understand due to my cultural background. CSIs are textual spans denoting concepts and items uncommon and not prevalent in my culture, making them difficult to understand."""

    task2 = """For each CSI, identify its familiarity from one of the following three levels: 
    1. Familiar: Most people from my culture know and relate to the concept as intended. 
    2. Somewhat familiar: Only some people from my culture know and relate to the concept as intended. 
    3. Unfamiliar: Most people from my culture do not know or relate to the concept."""

    task3 = """Task 3: Within 50 words, detail your reason for highlighting the span as CSI in Task 1 by correlating it with my background."""

    task4 = """Task 4: Reformulate the entire text to make it more understandable to me. Keep the length similar to the original review text."""

    formatting = """Format your response as a valid Python dictionary formatted as: {"spans": [List of Python dictionaries where each dictionary item is formatted as: {"CSI": <task 1: copy the CSI span from text>, "familiarity": <task 2: familiarity level name>, "reason": <task 3: reason within 50 words>}], "reformulation": <task 4: reformulate entire review text>}. Respond with {"spans": "None"} if you think I will not find anything difficult to understand."""

    tasks = f"""{task1}\n\n{task2}\n\n{task3}\n\n{task4}\n\n{formatting}"""

    prompt = f"""{ai_rules}\n{role} {role_desc}\n{client_desc}\n{text_desc}\n\n{tasks}\n\nText: {text}"""

    return prompt


def get_update_prompt(difference_spans):

    text1 = f"On further understanding, I observe the following things."

    text_update = ''
    for key in difference_spans.keys():
        if(len(difference_spans[key])!=0):
            text = f"""I am {key.lower()} with spans of text like {", ".join(difference_spans[key])}."""
            text_update += ' ' + text

    region_update_prompt = "Based on familiarity with these spans, update my background cultural information. Return them as a valid Python dictionary. {\"political_awareness\": <yes/no>, \"education_level\": <primary/secondary>, \"food_cuisine\": <japanese/mexican/american/emirati>, \"literature_preference\": <bengali/english/hindi>}"

    prompt = f"""{text1}\n\n{text_update}\n\n{region_update_prompt}"""

    return prompt