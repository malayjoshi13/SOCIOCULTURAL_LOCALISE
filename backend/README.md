# Backend  
  
Flask backend service that extracts Culture-Specific Items (CSIs) from text/URLs using an LLM, and serves the `ner-annotator` frontend and Chrome extension.  
  
## API Endpoints  
  
| Endpoint | Method | Description |  
|----------|--------|-------------|  
| `/gateway` | POST | Main analysis endpoint (dispatches to `backend_exp1`/`backend_exp2`/`backend_exp3` via `backend_endpoint` query param) |  
| `/chrome-api` | POST | Fetches + strips HTML from a URL, runs pipeline, returns CSI spans |  
| `/login` | POST | User authentication (against `users.json`) |  
| `/register` | POST | New user registration |  
| `/live` | GET | Health check → `{"health_status":"live"}` |  

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
- or Running curl command: ```curl http://localhost:8081/live --> Expected: {"health_status":"live"}```


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
  
On success you'll see `Using gpt4o in the backend !!!` printed in the server console. The exact `fresh` payload fields are defined in `app/experimentation_pipelines/base_localization/backend.py`.


## Select an Experimentation Pipeline

This backend provides three experimentation pipelines:
- `backend_exp1` → `base_localization`
- `backend_exp2` → `adaptive_profile`
- `backend_exp3` → `text_reformulation`

There are two ways to test a pipeline.

### Option 1: Use curl

For example, to test `adaptive_profile`, send a `POST` request with `backend_endpoint=backend_exp2`:

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

The NER Annotator UI currently does not send the `backend_endpoint` parameter or provide a pipeline selector. Requests therefore use the default configured in `app/main.py`:

```python
backend_endpoint = request.args.get("backend_endpoint") or "backend_exp1"
```

To test `adaptive_profile` through the UI, change the default to:

```python
backend_endpoint = request.args.get("backend_endpoint") or "backend_exp2"
```

Restart the backend after changing it:

```sh
cd backend
python -m app.main
```

Requests that omit `backend_endpoint` will now use `adaptive_profile`.


## Notes  
  
- **MongoDB**: only used when you pass `env=prod` to `/gateway` — it logs request/response traces to `mongodb://localhost:27017/` (`user_data` db). Connection failures are caught and printed, not fatal.  
- **Model selection**: `DEPLOYMENT_NAME` accepts any OpenRouter model ID (e.g. `openai/gpt-4o`, `anthropic/claude-3.5-sonnet`). Pick a model that reliably returns valid JSON — the response body is parsed with `json.loads`.  