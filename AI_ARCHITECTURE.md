# TripShield AI — AI Architecture

## Principles

### AI Does What AI Does Best

TripShield AI uses AI (LLMs) **only where natural language processing adds genuine value**. Deterministic calculations use algorithms.

| Task | Implementation | Rationale |
|------|---------------|-----------|
| Graph traversal | Algorithm (BFS) | Deterministic, exact |
| Time conflict detection | Algorithm | Mathematical comparison |
| Cost calculation | Algorithm | Arithmetic, no ambiguity |
| Impact scoring | Algorithm (weighted sum) | Configurable, reproducible |
| Recovery scoring | Algorithm (weighted sum) | Must be explainable |
| Preference weighting | Algorithm (normalization) | Mathematical |
| **Disruption explanation** | **LLM** | Natural language generation |
| **Recovery explanation** | **LLM** | Narrative from data |
| **Travel Q&A** | **LLM** | Conversational understanding |
| **Risk summarization** | **LLM** | Human-readable summary |

## Architecture

```
┌─────────────────────────────────────┐
│           AI Service Layer           │
│  ┌────────────┐  ┌────────────────┐ │
│  │ Guardian   │  │ Explainer      │ │
│  │ (Chat)     │  │ (Explanations) │ │
│  └─────┬──────┘  └────────┬───────┘ │
│        │                  │          │
│  ┌─────┴──────────────────┴───────┐ │
│  │     LLM Abstraction Layer      │ │
│  │  interface LLMProvider:        │ │
│  │    generate(prompt, context)   │ │
│  │    chat(message, context)      │ │
│  │    explain(data)               │ │
│  └─────────────┬─────────────────┘ │
└────────────────┼──────────────────┘
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
   ┌────────┐ ┌──────┐ ┌──────┐
   │MockLLM │ │Gemini│ │OpenAI│
   │Provider│ │Prov. │ │Prov. │
   └────────┘ └──────┘ └──────┘
```

## MockLLMProvider

The default provider uses **template-based response generation** with actual data injection. This means:

1. **No API key required** — demo works out of the box
2. **Deterministic responses** — reproducible for presentations
3. **Data-grounded** — responses always reference actual calculated values
4. **No hallucination** — templates prevent fabrication of information

### Template Examples

**Disruption Explanation:**
```
"Your {node_type} {provider} ({booking_ref}) from {origin} to {destination} 
has been {disruption_type}. This {delay_text}. Based on the Ripple Impact 
Analysis, {affected_count} downstream bookings are affected with an impact 
score of {impact_score}/100 ({severity_class}). The estimated financial 
exposure is {currency} {financial_exposure}."
```

**Recovery Recommendation:**
```
"I recommend '{strategy_title}' (Score: {score}/100) because it {reason_parts}. 
This option {preserves_text} and {cost_text}. The recovery confidence is 
{confidence}% with {num_changes} itinerary change(s)."
```

## TripShield Guardian

The Guardian is a conversational AI assistant that:

1. **Answers questions about the traveler's actual journey** using Digital Twin data
2. **Explains disruptions** using actual Impact Analysis results  
3. **Compares recovery options** using actual Recovery Strategy scores
4. **Simulates what-if scenarios** by triggering the simulation engine
5. **Summarizes risks** using actual Risk Assessment data

### Context Injection

```python
context = {
    "journey": journey_data,      # Actual nodes, dependencies, status
    "disruptions": disruptions,    # Actual disruption records
    "recoveries": strategies,      # Actual recovery options
    "preferences": preferences,    # User's actual preferences
    "resilience": score           # Calculated resilience score
}

# The LLM receives this context and generates responses grounded in real data
response = llm_provider.chat(user_message, context)
```

### Critical Rule: No Fabrication

The Guardian MUST NOT:
- Invent flight numbers or prices
- Fabricate hotel availability
- Create fake booking confirmations
- Present simulated data as real-world live data

If information is simulated, the response includes: **"[Demo/Simulated Data]"**

## Responsible AI Practices

1. **Transparency**: AI recommendations are clearly labeled as recommendations
2. **Explainability**: Every recommendation includes a data-backed explanation
3. **Human oversight**: Default mode requires user approval before execution
4. **No deception**: Simulated data is always clearly labeled
5. **Audit trail**: All AI decisions are logged for review
6. **Separation**: AI reasoning is separate from deterministic business logic
7. **Failsafe**: If AI fails, system falls back to "Human Assistance Required"

## Adding a Real LLM Provider

To add Gemini or OpenAI support:

1. Create a new class implementing `LLMProvider`
2. Set `AI_PROVIDER` environment variable to `gemini` or `openai`
3. Set the appropriate API key environment variable
4. The system automatically selects the provider at startup

```python
class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = genai.configure(api_key=api_key)
    
    def generate(self, prompt: str, context: dict) -> str:
        # Build prompt with context
        # Call Gemini API
        # Return response
        pass
```
