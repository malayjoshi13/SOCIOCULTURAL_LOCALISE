# This function constructs the prompt for the initial and subsequent 
# content-analysis interactions with the user.
#
# This prompt:
# - Assigns the model the role of a cultural mediator responsible for
#   identifying culture-specific items (CSIs), classifying their familiarity,
#   justifying their identification, and providing concise explanations.
#
# - During the initial interaction (previous=False), to identify CSIs via `get_initial_prompt` function,
#   it instructs the model to use only the user's basic demographic information (like country, region, and age group).
# - Other user profile attributes (namely, political_awareness, education_level, literature_preference, 
#   and food_cuisine, with respective default values of "No", "Primary", "English" and "American")
#   are intentionally ignored to be used during this first interaction (when previous=False) AS WELL AS during 
#   subsequent interactions (when previous=True) also.
# 
# - During subsequent interactions (previous=True), to identify CSIs via `get_initial_prompt` function,
#   it still: 1) uses only basic demographic description (like age, country and region),
#   and 2) other user profile attributes (like political_awareness, education_level, literature_preference, and food_cuisine)
#   are accepted but intentionally ignored to be used, 3) while also instructing the model 
#   to consider user's prior interaction history (aka appended selected or deselected spans).
#   This last instruction is the only new thing within subsequent interactions in comparison to first interaction.
# - Defines the required JSON response structure.
def get_initial_prompt(text, country, region, age_group, 
                       political_awareness, education_level, literature_preference, food_cuisine, 
                       previous=False):

    ai_rules = """
        # AI Rules
        - Output response in JSON format only
        - Do not output any extra text
        - Do not wrap the json codes in JSON or Python markers
        - JSON keys and values in double-quotes
    """

    role = """You are a cultural mediator who understands all cultures across the world."""

    role_desc = """As a mediator, your job is to identify and translate culturally exotic concepts from texts from an unknown source culture to my culture."""

    client_desc = f"""I am a well-educated {age_group} person who grew up in {region} {country}, which defines my culture."""
    
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
    else:
        tasks = f"""{task1}\n\n{task2}\n\n{task3}\n\n{task4}\n\n{formatting}""" 

    prompt = f"""{ai_rules}\n{role} {role_desc}\n{client_desc}\n{text_desc}\n\n{tasks}\n\nText: {text}"""

    return prompt


# This function constructs a profile-update prompt when user 
# saves selected or deselected spans in NER Annotator UI (frontend).
#
# This prompt is directly appended to the conversation history (aka selected or deselected spans)
# in `messages`, without inferring broader profile attributes or explicitly interpreting why user 
# selected or deselected each span.
#
# For subsequent content-analysis interactions, the instruction `task1_previous` present in
# `get_initial_prompt()` function uses this prompt to tell the model to consider this accumulated 
# interaction history when identifying and explaining CSIs.
def get_update_prompt(difference_spans):

    text1 = f"On further understanding, I observe the following things."

    text_update = ''
    for key in difference_spans.keys():
        if(len(difference_spans[key])!=0):
            text = f"""I am {key.lower()} with spans of text like {", ".join(difference_spans[key])}."""
            text_update += ' ' + text

    prompt = f"""{text1}\n\n{text_update}"""

    return prompt