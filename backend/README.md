# Backend

Flask backend service that extracts Culture-Specific Items (CSIs) from text/URLs using an LLM, and serves the `ner-annotator` frontend and Chrome extension.

## API Endpoints

| Endpoint        | Method | Description                                                                                                                    |
| --------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `/gateway`    | POST   | Main analysis endpoint (dispatches to `backend_exp1`/`backend_exp2`/`backend_exp3` via `backend_endpoint` query param) |
| `/chrome-api` | POST   | Fetches + strips HTML from a URL, runs pipeline, returns CSI spans                                                             |
| `/login`      | POST   | User authentication (against `users.json`)                                                                                   |
| `/register`   | POST   | New user registration                                                                                                          |
| `/live`       | GET    | Health check → `{"health_status":"live"}`                                                                                   |

## Running Modes

- **Development**: Quick setup with minimal configuration — omit `env=prod` from `/gateway` requests and no MongoDB is required.
- **Production**: Full features with MongoDB logging and data persistence — append `env=prod` to `/gateway` calls to log request/response traces into `mongodb://localhost:27017/` (`user_data` db).

## TLDR; Quick run

```sh
cd backend
conda activate test1
python -m app.main
```

Server starts on `http://localhost:8081`

Verify server health via:

- Visiting on weblink: `http://localhost:8081/live`
- or Running curl command: ``curl http://localhost:8081/live --> Expected: {"health_status":"live"}``

## Setup

```sh
cd backend
conda create -n test1 python=3.10    # you can keep any environment name of your choice in place of "test1"
conda activate test1
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, then provide your API key:

```env
OPENROUTER_API_KEY=sk-or-v1-<your-key>  
DEPLOYMENT_NAME=openai/gpt-4o   # optional; this is the default
```

Create `app/users.json` (required by `/login` + `/register`):

```json
{}
```

Create `app/url_to_text.json`:
```json
{}
```
This file `app/url_to_text.json`, is used when a request includes a URL instead of raw text; it maps each URL to the article text that should be analyzed:

```json
{"https://example.com/article": "Full article text to use as fallback input for the LLM pipeline."}
```

## Run

```sh
python -m app.main
```

Server starts on `http://localhost:8081`. Verify:

```sh
curl http://localhost:8081/live  
# → {"health_status":"live"}  [header-2](#header-2)
```

## Test `/gateway`

Linux/macOS (bash):

```sh
curl -X POST 'http://localhost:8081/gateway?backend_endpoint=backend_exp1' \  
  -H 'Content-Type: application/json' \  
  -d '{"type":"fresh","text":"Your article text here","country":"USA","age_group":"Adult (18+)","region":"Urban","messages":[],"political_awareness":"No","education_level":"Primary","literature_preference":"English","food_cuisine":"American"}'
```

Windows CMD (single line, escaped quotes):

```cmd
curl -X POST "http://localhost:8081/gateway?backend_endpoint=backend_exp1" -H "Content-Type: application/json" -d "{\"type\":\"fresh\",\"text\":\"Your article text here\",\"country\":\"USA\",\"age_group\":\"Adult (18+)\",\"region\":\"Urban\",\"messages\":[],\"political_awareness\":\"No\",\"education_level\":\"Primary\",\"literature_preference\":\"English\",\"food_cuisine\":\"American\"}"
```

On success you'll see `Using gpt4o in the backend !!!` printed in the server console. The exact `fresh` payload fields are defined in `app/experimentation_pipelines/exp1/backend.py`.

## Experimentation Pipelines

This backend provides following three experimentation pipelines.

These pipelines are not separate servers or models. They are alternative prompt and response-processing strategies exposed through the same `/gateway` API. All use the shared LLM client, configured to use GPT-4o by default.

### 1. Experiment 1 (`exp1`): Free learning

Identifies culture-specific items (CSIs) in the text that the user may find hard to understand. The prompt describes the user only by country, region (rural/urban) and age group. The four semantic proxies in the request (political awareness, education level, literature preference and food/cuisine) are accepted but never used in the prompt.

For each identified CSI, the LLM returns:

- CSI text
- Familiarity: Familiar, Somewhat familiar or Unfamiliar
- Reason for marking it as a CSI, related to the user's background
- Short explanation of the CSI (within 20 words)

CSIs labelled Familiar are dropped. Only Unfamiliar and Somewhat familiar CSIs are highlighted in the UI, each with its explanation.

Example:

```text
CSI: Iowa caucus
Familiarity: Unfamiliar
Reason: This political process may be uncommon in the user's country.
Explanation: A local political meeting used to select a party candidate.
```

**How it learns from feedback:** when the user saves their edits in the annotator, the backend compares the original highlights with the edited ones. It appends the differences to the conversation history as a plain-language note, for example "I am unfamiliar with spans of text like state caucus." A highlight the user removed is recorded as familiar. The LLM is not called at this step, and the feedback is not turned into profile attributes. For the next text in the session, the prompt asks the model to identify CSIs based on this interaction history.

### 2. Experiment 2 (`exp2`): Semi-constrained learning

Identifies, classifies and explains CSIs the same way as exp1, and returns the same output. For the first text in a session, the prompt is identical to exp1's.

**How it learns from feedback:** when the user saves their edits, the backend appends the same span note as exp1. It also asks the LLM to infer two semantic proxies from that feedback:

- Political awareness: yes or no
- Food/cuisine preference: Japanese, Mexican, American or Emirati

The inferred values are returned to the annotator, which sends them with the next request. Education level and literature preference are not inferred, so they keep their current values (by default Primary and English).

For later texts in the session, the prompt adds a profile sentence built from all four proxies and still asks the model to use the interaction history. Two proxies are updated explicitly, as in constrained learning. The other two are left to the appended spans, as in free learning. That mix is what makes this approach semi-constrained.

### 3. Experiment 3 (`exp3`): Constrained learning

Describes the user with all four semantic proxies from the very first request. The proxies are political awareness, education level, literature preference and food/cuisine preference.

For each CSI, the LLM returns the CSI text, its familiarity and a reason, but no per-CSI explanation. Also, the prompt in this pipeline also asks the LLM to rewrite the entire text; even though this reformulation is not yet returned to the UI.

**How it learns from feedback:** when the user saves their edits, the LLM infers updated values for all four proxies from the spans the user added:

- Political awareness: yes or no
- Education level: primary or secondary
- Literature preference: Bengali, English or Hindi
- Food/cuisine preference: Japanese, Mexican, American or Emirati

## Select an Experimentation Pipeline

There are two ways to select and test the above mentioned 3 experimentation pipelines:

### Option 1: Use curl

For example, to test `exp2 pipeline (aka Semi Constrained Learning-based Localisation pipleine)`, send a `POST` request with `backend_endpoint=backend_exp2`:

```sh
curl -X POST "http://127.0.0.1:8081/gateway?backend_endpoint=backend_exp2" \
  -H "Content-Type: application/json" \
  -d '{"type":"fresh","url":"https://www.bbc.com/news/world-us-canada-67285325","country":"India","age_group":"Adult (18+)","region":"Urban","messages":[],"political_awareness":"No","education_level":"Primary","literature_preference":"English","food_cuisine":"Indian"}'
```

Change the query parameter to test another pipeline:

```text
backend_endpoint=backend_exp1
backend_endpoint=backend_exp2
backend_endpoint=backend_exp3
```

The `/gateway` endpoint cannot be tested by opening it in a browser address bar because the browser sends a `GET` request, while `/gateway` requires `POST`.

### Option 2: Use the NER Annotator UI

The NER Annotator UI does not send the `backend_endpoint` query parameter or offer a pipeline selector. Its requests use the pipeline set by `BACKEND_ENDPOINT` in `backend/.env`, or `backend_exp1` if that isn't set.

To test a different pipeline through the UI, set `BACKEND_ENDPOINT` in `backend/.env`. For example:

```env
BACKEND_ENDPOINT=backend_exp2
```

Valid values are `backend_exp1`, `backend_exp2` and `backend_exp3`.

`.env` is only read when the server starts, so restart the backend after changing it:

```sh
cd backend
python -m app.main
```

A `backend_endpoint` query parameter on a request, as in Option 1, takes priority over this setting.

## Notes

- **MongoDB**: only used when you pass `env=prod` to `/gateway` — it logs request/response traces to `mongodb://localhost:27017/` (`user_data` db). Connection failures are caught and printed, not fatal.
- **Model selection**: `DEPLOYMENT_NAME` accepts any OpenRouter model ID (e.g. `openai/gpt-4o`, `anthropic/claude-3.5-sonnet`). Pick a model that reliably returns valid JSON — the response body is parsed with `json.loads`.
