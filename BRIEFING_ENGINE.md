# AI-Powered Constituent Briefing Engine

## Overview

The Constituent Briefing Engine uses Claude AI to generate comprehensive, personalized briefings for nonprofit constituents. It analyzes contribution history, interactions, opportunities, and segment membership to provide actionable insights for development officers.

## Features

- **AI-Powered Analysis**: Uses Claude Sonnet 4.5 to generate intelligent insights
- **Comprehensive Data Integration**: Analyzes contributions, interactions, opportunities, transactions, and segments
- **Personalized Recommendations**: Provides specific, actionable next steps
- **REST API**: Easy integration with existing systems
- **Batch Processing**: Generate briefings for multiple constituents
- **Fallback Mode**: Generates basic briefings if AI service is unavailable

## Architecture

```
├── src/briefing/
│   ├── __init__.py
│   └── engine.py          # Core briefing engine with AI integration
├── api/constituents/
│   ├── __init__.py
│   └── briefing.py        # REST API endpoints
└── main.py                # FastAPI application entry point
```

## Installation

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

2. **Configure environment variables:**

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

3. **Ensure database is initialized:**

```bash
python load_data.py
```

## Usage

### Starting the API Server

```bash
# Development mode (auto-reload)
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### API Endpoints

#### Get Constituent Briefing

```http
GET /api/constituents/{constituent_id}/briefing?segments=Major%20Donors,Board%20Members
```

**Response:**

```json
{
  "summary": "Michael Brown is a Board Member and major donor who has demonstrated exceptional commitment with $50,000 in lifetime giving...",
  "giving_summary": "Total giving of $50,000 across 1 major gift to the Capital Campaign (CAMP003)...",
  "engagement_pattern": "Highly engaged through board governance with 2 recorded interactions...",
  "why_they_matter": "As a Board Member with major donor capacity, Michael provides both strategic leadership...",
  "segment_reason": "Classified as Major Donor and Board Member based on $50,000+ giving level...",
  "suggested_action": "Schedule a one-on-one meeting within the next 30 days to discuss campaign progress...",
  "metadata": {
    "constituent_id": "CONST003",
    "generated_at": "2025-01-20T10:30:00.000Z",
    "data_points": {
      "contributions": 1,
      "interactions": 2,
      "opportunities": 0,
      "transactions": 1,
      "segments": 2
    }
  }
}
```

#### Batch Briefings

```http
POST /api/constituents/briefings/batch
Content-Type: application/json

["CONST001", "CONST002", "CONST003"]
```

**Response:** Array of briefing objects

### Python Integration

```python
from models import get_session
from src.briefing.engine import BriefingEngine

# Initialize engine
engine = BriefingEngine(api_key="your_anthropic_api_key")

# Get database session
session = get_session()

# Generate briefing
briefing = engine.generate_briefing(
    constituent_id="CONST001",
    db_session=session,
    segment_names=["Major Donors", "Monthly Giving"]
)

print(briefing['summary'])
print(briefing['suggested_action'])
```

## Output Fields

Each briefing includes:

| Field | Description | Example |
|-------|-------------|---------|
| `summary` | 2-3 sentence overview of the constituent | "John Smith is a donor who has contributed $15,000..." |
| `giving_summary` | Analysis of giving history and patterns | "Total giving of $15,000 across 4 gifts averaging $3,750..." |
| `engagement_pattern` | Analysis of interaction patterns | "Has 3 recorded interactions, primarily through email..." |
| `why_they_matter` | Strategic importance to organization | "Consistent donor with demonstrated capacity for major gifts..." |
| `segment_reason` | Explanation of segment classification | "Classified as Major Donor based on $10,000+ giving..." |
| `suggested_action` | Personalized recommended next step | "Schedule a cultivation lunch within 30 days to discuss..." |
| `metadata` | Generation timestamp and data point counts | `{"constituent_id": "CONST001", "generated_at": "..."}` |

## Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude AI | - |
| `DATABASE_URL` | No | Database connection string | `sqlite:///nonprofit_crm.db` |
| `API_HOST` | No | API server host | `0.0.0.0` |
| `API_PORT` | No | API server port | `8000` |
| `LOG_LEVEL` | No | Logging level | `info` |

### Getting an Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key
5. Add to your `.env` file

## Testing

Test the engine with sample data:

```bash
python test_briefing.py
```

Or test via API:

```bash
# Health check
curl http://localhost:8000/health

# Generate briefing
curl http://localhost:8000/api/constituents/CONST001/briefing?segments=Major%20Donors
```

## Error Handling

The engine includes comprehensive error handling:

- **404**: Constituent not found
- **500**: API key not configured
- **500**: AI service error (falls back to basic briefing)
- **400**: Invalid request (batch too large, etc.)

## Performance Considerations

- **API Calls**: Each briefing makes one Claude API call (~1-2 seconds)
- **Batch Limits**: Maximum 10 constituents per batch request
- **Rate Limiting**: Consider implementing rate limits for production
- **Caching**: Consider caching briefings with TTL for frequently accessed constituents
- **Background Jobs**: For large batch operations, use task queues (Celery, RQ, etc.)

## Production Deployment

### Recommended Setup

1. **Use PostgreSQL** instead of SQLite
2. **Configure CORS** properly (remove wildcard)
3. **Add Authentication** (JWT, API keys, OAuth)
4. **Implement Rate Limiting** (SlowAPI, etc.)
5. **Add Caching** (Redis for briefing results)
6. **Background Jobs** (Celery for batch processing)
7. **Monitoring** (Sentry, DataDog, etc.)
8. **Load Balancing** (Nginx, Docker, Kubernetes)

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t constituent-briefing-api .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=your_key constituent-briefing-api
```

## Troubleshooting

### "ANTHROPIC_API_KEY not configured"

**Solution:** Set the environment variable:
```bash
export ANTHROPIC_API_KEY="your_api_key_here"
```

### "Constituent not found"

**Solution:** Ensure the constituent exists in the database:
```bash
python verify_database.py
```

### "Failed to generate briefing"

**Possible causes:**
- API key invalid or expired
- Network connectivity issues
- AI service temporarily unavailable

**Solution:** Check logs and API key. The engine will fall back to basic briefings.

### Import errors

**Solution:** Ensure all __init__.py files exist and packages are installed:
```bash
pip install -r requirements.txt
```

## Future Enhancements

- [ ] Caching layer with Redis
- [ ] Background job processing for batches
- [ ] Webhook support for async briefing generation
- [ ] Multi-language support
- [ ] Custom prompt templates per organization
- [ ] Historical briefing comparison
- [ ] Predictive analytics integration
- [ ] Email delivery of briefings
- [ ] PDF export functionality
- [ ] Integration with popular CRM systems (Salesforce, Raiser's Edge, etc.)

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- GitHub Issues: [Your repo URL]
- Email: dev@example.org
- Documentation: http://localhost:8000/docs
