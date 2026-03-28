 Multi-Agent AI Research Platform (AIRA)

> An intelligent backend system that orchestrates three specialized AI agents — Research, Analysis, and Coding — to help founders explore startup ideas, analyze markets, and generate production-ready code from a single natural language prompt.



## What it does

You send one goal. The system figures out what kind of work needs to happen, routes it across the right agents, searches the live web, reasons about the results, and returns structured startup ideas, market insights, or working code — all personalized to your founder profile.

**Example:**
```
POST /api/v1/tasks
{
  "goal": "Find AI startup opportunities in edtech for 2025",
  "industry": "edtech",
  "location": "India",
  "budget": "bootstrap",
  "technical_level": "intermediate"
}
```

Returns 3 personalized startup ideas with problem/solution/market size/competitors/business model, a risk assessment for each, and a concrete first step tailored to your profile.

---

## Architecture

```
Client / n8n / curl
        │
        ▼
  POST /api/v1/tasks
        │
  ┌─────▼──────────────┐
  │   FastAPI router    │  ← Pydantic validation, task_id generation
  │   task_router.py    │  ← tasks_db (in-memory store)
  └─────┬──────────────┘
        │
  ┌─────▼──────────────┐
  │    Orchestrator     │  ← Planner decides which agents run
  │ agent_orchestrator  │
  └──┬──────┬──────┬───┘
     │      │      │
     ▼      ▼      ▼
Research  Analysis  Coding
 Agent    Agent     Agent
  (always) (if analyze/  (if code/
           compare/      build/app
           strategy)     detected)
     │
     ├── Intent detection (past / present / future)
     ├── 2× Tavily web search
     ├── Smart token-budget truncation
     ├── VectorStore memory (read + write)
     └── LLM call → structured startup ideas
```

---

## Features

Research agent
- **Intent detection** — classifies the goal as past, present, or future-oriented and adjusts search queries accordingly
- **Dual web search** — runs two targeted Tavily queries per task, scored by relevance
- **Smart truncation** — scores results and trims to a token budget before building the prompt
- **Token guard** — estimates prompt size before the LLM call; returns a structured error instead of an over-budget API call
- **Vector memory** — persists results to a vector store and injects relevant prior context into new prompts
- **Founder profile personalization** — injects industry, location, budget, team size, and risk appetite into the LLM prompt for tailored output

### Analysis agent
- Accepts research output and extracts patterns, insights, and conclusions
- Keyword-triggered (fires when "analyze", "compare", "strategy", "evaluate" etc. are detected in the goal)

### Coding agent
- Generates full project scaffolds with clearly delimited filenames
- Produces `requirements.txt`, `app.py`, and supporting files ready to run
- Keyword-triggered (fires when "code", "build", "implement", "app", "api" etc. are detected)

### API layer (FastAPI)
- `POST /api/v1/tasks` — submit a goal with optional founder profile fields
- `GET /api/v1/tasks` — list all tasks and their statuses
- `GET /api/v1/tasks/{task_id}` — retrieve a single task result
- Pydantic request validation with sensible defaults for all profile fields
- In-memory task store with status tracking (`running` → `completed` / `failed`)
- Structured error responses with HTTP status codes (400 for token limit, 500 for agent failures)

---

## Tech stack

| Layer                |    Technology                                      |
|----------------------|----------------------------------------------------|
| API framework        | FastAPI                                            |
| Request validation   | Pydantic v2                                        |
| Web search           | Tavily API                                         |
| LLM                  | GPT-4o (via Azure AI Inference using GitHub Token) |
| Memory               | ChromaDB + sentence-transformers                   |                 
| Task orchestration   | Custom planner + agent runner                      |
| Workflow automation  | n8n (HTTP Request node integration)                |

---

## Getting started

### Prerequisites
- Python 3.11+
- A Tavily API key ([get one here](https://tavily.com))
- A personalized github token

### Installation

```bash
git clone https://github.com/Subhra-Nandi/aira-platform.git
cd aira-platform

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Environment variables

Create a `.env` file in the project root:

```env
TAVILY_API_KEY=your_tavily_key_here
GITHUB_TOKEN=your_github_token_here   
```

### Run the server

```bash
uvicorn app.main:app --reload --port
```

The API will be live at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

---

## API usage

### Submit a task
### using cURL (Linux / macOS)

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Find AI startup ideas in healthcare for India",
    "industry": "healthcare",
    "location": "India",
    "budget": "bootstrap",
    "risk_appetite": "medium",
    "technical_level": "intermediate",
    "team_size": "solo"
  }'
```

**Response:**
```json
{
  "task_id": "3f2a1b4c-...",
  "status": "completed",
  "result": {
    "version": "v1",
    "status": "success",
    "goal": "...",
    "plan": { "research": true, "analysis": false, "coding": false },
    "results": [
      {
        "agent": "research",
        "type": "text",
        "content": "## Insights\n...\n## Idea 1: ..."
      }
    ]
  }
}
```

### Check task status

```bash
curl http://localhost:8000/api/v1/tasks/{task_id}
```

### n8n integration

Add an **HTTP Request** node in your n8n workflow:
- Method: `POST`
- URL: `http://localhost:8000/api/v1/tasks`
- Body: JSON with `goal` and any profile fields

Add a **Code** node after it to validate:
```javascript
const body = $input.first().json;
if (!body.results || !Array.isArray(body.results)) {
  throw new Error("Unexpected response: " + JSON.stringify(body));
}
return body.results.map(r => ({ json: r }));
```

Verify the server health before running:
```bash
curl http://localhost:8000/docs         # FastAPI auto-docs
curl http://localhost:5678/healthz      # n8n health endpoint
n8n --version                           # verify n8n install
```

---

## Project structure

```
aira-platform/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── routers/
│   │   └── task_routes.py         # POST/GET /api/v1/tasks
│   ├── agents/
│   │   ├── research_agent.py      # Intent detection, web search, LLM
│   │   ├── analysis_agent.py      # Pattern extraction
│   │   └── coding_agent.py        # Code generation
│   ├── services/
│   │   ├── agent_orchestrator.py  # Planner + agent runner
│   │   ├── llm_service.py         # LLM API wrapper
│   │   └── intent_detector.py     # Past / present / future classifier
│   ├── tools/
│   │   └── web_search.py          # Tavily client wrapper
│   └── memory/
│       └── vector_store.py        # In-memory vector store
├── .env.example
├── requirements.txt
└── README.md
```

---

## Roadmap

### High priority
- [ ] **Structured error propagation** — agent-level errors should bubble up cleanly rather than silently producing empty strings in downstream agents
- [ ] **LLM-based planner** — replace keyword substring matching with a fast classifier call for more reliable routing
- [ ] **Typed agent handoffs** — pass structured dicts between agents instead of sliced raw strings to prevent silent data loss

### Medium priority
- [ ] **Async agent execution** — run independent agents concurrently with `asyncio.gather()` to reduce total latency
- [ ] **Accurate token counting** — replace the `len // 4` heuristic with `tiktoken` for the exact model being called
- [ ] **Profile injection in all agents** — analysis and coding agents accept `user_profile` but currently ignore it; wire it into their prompts
- [ ] **Per-session VectorStore** — replace the global singleton with scoped instances to prevent cross-request memory contamination

### Low priority
- [ ] **Streaming LLM responses** — stream tokens back to the client for a faster perceived response
- [ ] **API key authentication** — add `X-API-Key` header validation and rate limiting
- [ ] **Prompt injection sanitization** — sanitize user-supplied `goal` strings before interpolating into prompts
- [ ] **React frontend dashboard** — visual interface to set founder profile, submit goals, and browse agent outputs
- [ ] **Docker + docker-compose** — containerize the app for one-command deployment

---

## Limitations (current)

- `tasks_db` is in-memory only — tasks are lost on server restart. A future version will add Redis or SQLite persistence.
- The planner always runs the Research agent regardless of goal type. Tasks like "build a login API" still trigger a web search unnecessarily.
- Agents run synchronously and sequentially, so a full research + analysis + coding run can take 20–40 seconds depending on LLM latency.
- No authentication on the API endpoints.

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/async-agents`)
3. Commit your changes (`git commit -m 'Add async agent execution'`)
4. Push and open a pull request

---

## License

MIT
