# This function constructs the prompt for the initial and subsequent 
# content-analysis interactions with the user.
#
# This prompt:
# - Assigns the model the role of a cultural mediator responsible for
#   identifying culture-specific items (CSIs), classifying their familiarity,
#   justifying their identification, and providing concise explanations.
#
# - During the initial interaction (previous=False), to identify CSIs via `get_initial_prompt` function,
#   it instructs the model to use only the user's basic demographic information (like country, region, and age group.
# - Other user profile attributes (namely, political_awareness, education_level, 
#   literature_preference, and food_cuisine, with respective default values of "No", "Primary", "English" 
#   and "American") are intentionally ignored to be used during this initial interaction.
#   Therefore, during current initial interaction, this pipeline's generated prompt is essentially 
#   same as exp1 prompt.
#
# - During subsequent interactions (previous=True), to identify CSIs via `get_initial_prompt` function, 
#   it: 1) uses basic demographic description (like age, country and region), 
#   2) uses `proxy_desc` which uses four additional user attributes (of political awareness, 
#   education level, literature preference, and food/cuisine preference),
#   and 3) instructs model to consider accumulated interaction history (aka 
#   appended selected or deselected spans). 
#   Therefore, during subsequent interactions, this pipeline's generated prompt is different 
#   from exp1 prompt.
# - During this subsequent interaction, it update values of only two semantic proxies (namely, political-awareness 
#   and food/cuisine) using user’s previous annotation feedback interaction, while other two proxies (namely, education level and 
#   literature preference) carrying forward their default/initial values, i.e. in subsequent interactions, 
#   the values of attributes within `proxy_desc' are as follows:
#   1) political_awareness = updated as per inferred from user feedback, 
#   2) food_cuisine = updated as per inferred from user feedback, 
#   3) education_level = "Primary"; carried forward from default value, 
#   and 4) literature_preference = "English"; carried forward from default value.
# - Defines the required JSON response structure.
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


# This function constructs a profile-update prompt when the user 
# saves selected or deselected spans in NER Annotator UI.
#
# This profile-update prompt is developed via:
# - Incorporating the selected and deselected spans supplied in `difference_spans`.
# - Asking a LLM model to infer updated values for two semantic profile attributes, 
#   namely, `political_awareness` and `food_cuisine`, based on the user's familiarity with these spans.
# - Does not infer/update other two attributes of `education_level` or `literature_preference`; 
#   thus their existing values are carried forward unchanged.
#
# This function then sends this prompt to the conversation history, and during
# the next content-analysis interaction, the code flow of function `get_initial_prompt` corresponding `previous=True`,
# instructs model to consider this accumulated history of updated user profile prompt/description.
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