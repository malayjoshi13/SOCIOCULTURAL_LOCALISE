# SOCIOCULTURAL_LOCALISE

**Exploring context-aware localisation of educational content**

## Overview

SOCIOCULTURAL_LOCALISE explores methods for adapting educational content to learners' sociocultural contexts, with the aim of improving comprehension, relevance, and accessibility while preserving pedagogical intent.

The project investigates how contextual information—including language, dialect, cultural references, local environments, lived experiences, and prior knowledge—can inform the interpretation and adaptation of educational material for diverse learning contexts.

## Technical Direction & Status

This project investigates the extension of existing cross-cultural content understanding approaches to educational localisation. Initial work focuses on analysing the upstream implementation, identifying reusable components, and evaluating potential extensions through narrowly scoped educational use cases.

Areas of investigation include:

- **Contextual reference identification:** Detecting content elements that may be unfamiliar or inaccessible to a target learner.
- **Context-aware adaptation:** Generating explanations and locally relevant alternatives informed by the learner's context.
- **Pedagogical preservation:** Maintaining conceptual accuracy, curriculum alignment, and intended learning outcomes during adaptation.
- **Context representation and integration:** Investigating how learner and environmental context can be collected, structured, validated, and incorporated into the adaptation pipeline.
- **Human-in-the-loop validation:** Incorporating teacher and community input to evaluate contextual appropriateness and educational quality.

The implementation scope, system architecture, and evaluation methodology will evolve based on these investigations.


## Acknowledgements

This project builds on [CULTURALLY YOURS: A Reading Assistant for Cross-Cultural Content](https://aclanthology.org/2025.coling-demos.21/) by Saurabh Kumar Pandey, Harshit Budhiraja, Sougata Saha, and Monojit Choudhury (COLING 2025), which identifies culture-specific items in general text and personalises their explanations using readers' cultural backgrounds and interaction feedback.

This repository explores extending these approaches to educational content, accounting for learner context and pedagogical objectives.

The original authors retain credit for their work. Refer to the [upstream repository](https://github.com/skp1999/CULTURALLY_YOURS) for implementation details and licensing terms. Additional attribution will follow the applicable licence and contribution requirements.
