# Suggested Action Generator for Nonprofit Fundraisers

An AI-powered module that generates personalized, actionable recommendations for nonprofit fundraisers to engage with constituents.

## Overview

The Suggested Action Generator analyzes constituent data including giving history, engagement patterns, and segment characteristics to produce specific, time-bound, stewardship-oriented action recommendations using Claude AI.

## Features

- **AI-Powered Recommendations**: Uses Claude 3.5 Sonnet to generate sophisticated fundraising strategies
- **Segment-Aware**: Tailors recommendations based on 10 different constituent segments
- **Data-Driven**: Analyzes giving history, interaction patterns, and opportunity pipeline
- **Best Practices**: Follows nonprofit fundraising best practices (stewardship over transactions)
- **RESTful API**: FastAPI endpoint for easy integration
- **Flexible Usage**: Use directly in Python or via HTTP API

## Architecture

```
instilAiPrototype/
├── src/
│   └── actions/
│       └── generator.py          # Core generator logic
├── api/
│   └── suggested_action.py       # FastAPI endpoint
├── segments.py                    # Segment definitions and detection
├── models.py                      # SQLAlchemy ORM models
├── examples/
│   ├── usage_example.py          # Python usage examples
│   └── suggested_action_examples.md  # Sample outputs
└── requirements.txt               # Dependencies
```

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up API key:**
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

3. **Configure database (optional):**
```bash
export DATABASE_URL='sqlite:///nonprofit_crm.db'  # Default
# or
export DATABASE_URL='postgresql://user:pass@localhost/nonprofit_crm'
```

## Usage

### Option 1: Direct Python Usage

```python
from models import create_database_engine, get_session
from src.actions.generator import generate_suggested_action

# Set up database
engine = create_database_engine("sqlite:///nonprofit_crm.db")
session = get_session(engine)

# Generate action for constituent
result = generate_suggested_action(
    session=session,
    constituent_id=1,
    segment_id="major_donor"  # Optional
)

print(result['suggested_action'])
session.close()
```

### Option 2: API Endpoint

**Start the server:**
```bash
cd api
python suggested_action.py
# Server runs at http://localhost:8000
```

**Make requests:**
```bash
# List available segments
curl http://localhost:8000/api/segments

# Generate suggested action
curl -X POST http://localhost:8000/api/suggested-action \
  -H "Content-Type: application/json" \
  -d '{
    "constituent_id": 1,
    "segment_id": "major_donor"
  }'
```

**Using Python requests:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/suggested-action",
    json={
        "constituent_id": 1,
        "segment_id": "major_donor"
    }
)

result = response.json()
print(result['suggested_action'])
```

## Segments

The generator recognizes 10 constituent segments:

| Segment ID | Description | Priority |
|------------|-------------|----------|
| `major_donor` | $5,000+ lifetime giving | High |
| `lapsed_donor` | No gift in 18+ months | Medium |
| `first_time_donor` | First gift in last 90 days | High |
| `recurring_donor` | 3+ gifts in last 12 months | High |
| `high_engagement` | 5+ interactions in 6 months | Medium |
| `low_engagement` | No interactions in 12+ months | Medium |
| `planned_giving_prospect` | 60+ years, $10,000+ giving | High |
| `board_member` | Current board member | High |
| `volunteer` | Active volunteer | Medium |
| `event_attendee` | Event in last 3 months | Medium |

Get full segment list via API:
```bash
curl http://localhost:8000/api/segments
```

## API Reference

### POST /api/suggested-action

Generate a personalized action recommendation.

**Request Body:**
```json
{
  "constituent_id": 1,
  "segment_id": "major_donor"  // optional
}
```

**Response:**
```json
{
  "success": true,
  "constituent_id": 1,
  "constituent_name": "John Smith",
  "segments": ["major_donor", "recurring_donor"],
  "target_segment": "major_donor",
  "suggested_action": "Action: Schedule a 45-minute lunch...\n\nTiming: Within 10 business days...\n\nWhy: ...\n\nKey Points:\n• ...",
  "generated_at": "2025-01-15T10:30:00"
}
```

### GET /api/segments

List all available segments with descriptions.

**Response:**
```json
{
  "segments": [
    {
      "id": "major_donor",
      "name": "Major Donor",
      "description": "Constituents who have given $5,000+ in lifetime contributions",
      "priority": "high"
    },
    ...
  ],
  "total": 10
}
```

### GET /health

Health check endpoint.

## Action Format

All generated actions follow this structure:

```
Action: [Specific action to take]
Timing: [Exact timeframe]
Why: [Data-driven rationale]
Key Points:
• [Specific detail 1]
• [Specific detail 2]
• [Specific detail 3]
```

### Quality Guidelines

Generated actions are:
- ✅ **Specific**: Clear, actionable steps (not "reach out" or "touch base")
- ✅ **Time-bound**: Include specific deadlines ("within 2 weeks", "by Friday")
- ✅ **Stewardship-oriented**: Focus on relationships, not just transactions
- ✅ **Donor-centric**: Prioritize donor experience and interests
- ✅ **Non-generic**: Tailored to individual constituent context

## Examples

See [examples/suggested_action_examples.md](examples/suggested_action_examples.md) for detailed examples of generated actions for each segment type.

Run the example script:
```bash
python examples/usage_example.py
```

## How It Works

1. **Data Collection**: Gathers constituent data from CRM database
   - Basic profile (name, type, location, lifetime giving)
   - Giving history (recency, frequency, monetary value)
   - Engagement history (interactions, types, recency)
   - Pipeline opportunities (stages, amounts)

2. **Segment Detection**: Identifies which segments the constituent belongs to
   - Analyzes giving patterns
   - Reviews engagement frequency
   - Evaluates constituent characteristics
   - Returns prioritized segment list

3. **Context Building**: Constructs detailed context for AI
   - Formats constituent data
   - Summarizes giving patterns
   - Highlights engagement trends
   - Includes segment information

4. **AI Generation**: Sends context to Claude API
   - Uses structured prompt with requirements
   - Enforces quality guidelines
   - Returns formatted action recommendation

5. **Response Delivery**: Returns structured result
   - Includes metadata (segments, timestamp)
   - Provides actionable recommendation
   - Formats for easy consumption

## Configuration

### Environment Variables

- `ANTHROPIC_API_KEY`: Your Anthropic API key (required)
- `DATABASE_URL`: Database connection string (default: `sqlite:///nonprofit_crm.db`)

### Create .env file:
```bash
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=sqlite:///nonprofit_crm.db
```

## Error Handling

The generator handles common errors gracefully:

```python
result = generate_suggested_action(session, constituent_id=999)

if not result["success"]:
    print(f"Error: {result['error']}")
    # Error: Constituent 999 not found
```

API errors return appropriate HTTP status codes:
- `404`: Constituent not found
- `400`: Invalid segment_id
- `500`: Server error or API failure

## Performance

- **Average response time**: 2-5 seconds (depends on Claude API)
- **Database queries**: 4-6 queries per constituent
- **Token usage**: ~1,000-1,500 tokens per request
- **Cost**: ~$0.01-0.02 per action generated (Claude 3.5 Sonnet pricing)

## Best Practices

1. **Batch Processing**: For multiple constituents, implement rate limiting
2. **Caching**: Consider caching results for frequently accessed constituents
3. **Error Handling**: Always check `success` field in response
4. **API Key Security**: Never commit API keys to version control
5. **Database Connections**: Always close sessions after use

## Troubleshooting

### "ANTHROPIC_API_KEY must be provided"
Set your API key in environment:
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

### "Constituent not found"
Verify the constituent_id exists in your database:
```python
from models import Constituent
constituent = session.query(Constituent).filter_by(constituent_id=1).first()
```

### API connection errors
Check that the API server is running:
```bash
curl http://localhost:8000/health
```

## Future Enhancements

Potential improvements:
- [ ] Support for multiple languages
- [ ] Custom segment definitions
- [ ] Action history tracking
- [ ] A/B testing of recommendations
- [ ] Integration with email/CRM systems
- [ ] Batch processing API endpoint
- [ ] Action effectiveness metrics

## Contributing

This is a proof-of-concept module. To extend:

1. **Add new segments**: Update `segments.py` with new segment definitions
2. **Customize prompts**: Modify `_generate_action_with_ai()` in `generator.py`
3. **Add endpoints**: Extend `api/suggested_action.py` with new routes
4. **Improve detection**: Enhance segment detection logic in `get_constituent_segment()`

## License

This is a proof-of-concept for educational purposes.

## Support

For questions or issues:
1. Check the [examples](examples/) directory
2. Review [sample outputs](examples/suggested_action_examples.md)
3. Test with [usage_example.py](examples/usage_example.py)

---

**Built with:**
- [Anthropic Claude API](https://www.anthropic.com/api)
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- Python 3.8+
