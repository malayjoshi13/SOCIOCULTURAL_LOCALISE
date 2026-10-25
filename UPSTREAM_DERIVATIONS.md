# Derivation from CULTURALLY_YOURS

SOCIOCULTURAL_LOCALISE is derived from CULTURALLY_YOURS. The following records the verified structural, functional, configuration, and documentation changes introduced in the derived repository.

> PR tags identify the merged pull request responsible for each change. Multiple tags indicate changes introduced incrementally across PRs.

## Repository and Backend Architecture

- Reorganized the backend from `cy_demo/demo/` into the clearer `backend/app/` application hierarchy. [PR5]
- Separated gateway orchestration, LLM-provider integration, experimentation pipelines, and shared utilities into dedicated modules. [PR5] [PR10]
- Consolidated the three experimental implementations under `app/experimentation_pipelines/exp1|exp2|exp3/`. [PR5] [PR11]
- Renamed `server_gateway.py` to `app/main.py` and `server_gpt.py` to `app/services/llm_client.py`. [PR5]
- Removed obsolete pipeline constants, path-bootstrap logic, unused imports, timestamp calculations, and commented-out output statements. [PR7] [PR11] [PR12]

## Configuration and Deployment Portability

- Removed the deployment-specific absolute path previously used for `users.json`. [PR1]
- Resolved user storage relative to `app/main.py`, making authentication storage independent of both the deployment host and process working directory. [PR1] [PR5]
- Added `.env` loading through `python-dotenv`. [PR1]
- Added `backend/.env.example` documenting the required OpenRouter key, model identifier, and default experimentation pipeline. [PR1] [PR5] [PR10]
- Added `BACKEND_ENDPOINT` configuration with `backend_exp1` as the fallback pipeline. [PR10]
- Preserved request-level pipeline selection while giving the `backend_endpoint` query parameter precedence over environment configuration. [PR10]
- Replaced the Azure OpenAI-specific client with OpenRouter’s OpenAI-compatible API. While retaining configurable model selection through `DEPLOYMENT_NAME`, using OpenRouter model identifiers. [PR1]

## Dependency Corrections

- Added `pymongo`, which was imported by the gateway but absent from the original requirements. [PR1]
- Added `beautifulsoup4`, which was required by URL extraction but previously undeclared. [PR1]
- Added `python-dotenv` to support environment-driven runtime configuration; the initial dependency-name typo was subsequently corrected. [PR1] [PR13]
- Relocated backend dependencies to `backend/requirements.txt` alongside the reorganized service. [PR5]

## Pipeline Reliability Fixes

- Corrected Experiment 1 span handling so LLM-generated CSIs absent from the source text are discarded instead of emitting invalid `[-1, -1]` annotation offsets. [PR11]
- Added explicit handling for the model’s `"spans": "None"` response in Experiments 2 and 3. [PR11] [PR12]
- Added direct-text input support to Experiments 2 and 3; both now accept either raw text or fixture-backed URLs. [PR11] [PR12]
- Reworked Experiments 2 and 3 to explicitly return and reattach updated message histories instead of relying on incidental in-place mutation. [PR11] [PR12]

## Experiment 3 Response Alignment

- Replaced whole-document reformulation with concise per-CSI explanations. [PR13]
- Added explanation extraction to both fresh and subsequent Experiment 3 responses. [PR12]
- Added a safe fallback for model spans that omit the optional `explanation` field. [PR13]
- Aligned Experiment 3 output with the annotator interface, which consumes explanations alongside highlighted spans. [PR12] [PR13]
- Retained four-proxy profile inference during feedback updates while integrating the resulting values into subsequent interactions. [PR12]

## Frontend–Backend Integration

- Added `src/config/api.js` as the single source of truth for the backend base URL. [PR8]
- Replaced separate hard-coded loading and saving endpoints with a shared `API_BASE_URL`. [PR8]
- Added development and production environment files using `VUE_APP_API_BASE_URL`. [PR8]
- Ensured annotation retrieval and feedback submission target the same backend deployment. [PR8]

## Debugging and Runtime Inspection

- Added timestamped JSON snapshots for model responses, request state, and conversation history across all three pipelines. [PR10] [PR11] [PR12]
- Added ignore rules for generated debugging output, local environments, bytecode, user records, and backend secrets. [PR5] [PR10]

## Code Documentation and Maintainability

- Added detailed inline documentation across all experimentation pipelines and prompt modules. [PR7] [PR11] [PR12]
- Documented prompt construction, demographic and semantic-proxy usage, annotation-offset conversion, familiarity filtering, feedback comparison, and message-history updates. [PR7] [PR11] [PR12]
- Clarified the behavioral distinction between free, semi-constrained, and constrained feedback pipelines. [PR9] [PR11]
- Grouped pipeline responsibilities into clearly delimited processing stages. [PR7] [PR11] [PR12]
- Improved naming and module placement to make the request lifecycle easier to trace. [PR5] [PR11]

## Project Documentation

- Expanded the backend README with installation steps, environment configuration, endpoint documentation, request examples, pipeline semantics, health checks, and pipeline-selection instructions. [PR2] [PR5] [PR7] [PR9] [PR11] [PR13]
- Added Node/Yarn setup, backend startup ordering, sample inputs, public-path guidance, and troubleshooting information. [PR3] [PR5]
- Added explicit acknowledgement of the CULTURALLY YOURS paper, authors, repository, and upstream intellectual contribution. [PR4]
- Updated the MIT licence notice to distinguish upstream authorship from original contributions in the derived repository. [PR4]