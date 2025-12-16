# AI-Driven Donor Insights Engine

An intelligent system that analyzes your nonprofit's donor database and generates actionable fundraising insights using Claude 3.5 Sonnet.

## Overview

The Insights Engine combines donor segmentation (RFM analysis) with AI-powered analysis to provide strategic recommendations for:
- **Giving Trends**: Patterns in contribution behavior
- **Engagement Risks**: Donors at risk of lapsing
- **Upgrade Opportunities**: Potential for increased giving
- **Portfolio Suggestions**: Strategic donor management recommendations

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    REST API Layer                        │
│                  (api/insights.py)                       │
│  GET /api/insights • GET /api/segmentation • etc.       │
└─────────────────────────────────────────────────────────┘
                          │
         ┌────────────────┴─────────────────┐
         │                                  │
┌────────▼─────────┐              ┌────────▼──────────┐
│ Segmentation     │              │ AI Insights       │
│ Engine           │──────────────▶│ Engine            │
│ (RFM Analysis)   │              │ (Claude 3.5)      │
└──────────────────┘              └───────────────────┘
         │                                  │
         └────────────────┬─────────────────┘
                          │
                ┌─────────▼──────────┐
                │ Data Summary       │
                │ Functions          │
                └─────────┬──────────┘
                          │
                ┌─────────▼──────────┐
                │ Database           │
                │ (SQLAlchemy ORM)   │
                └────────────────────┘
```

## Components

### 1. Segmentation Engine (`src/segmentation/engine.py`)

Performs RFM (Recency, Frequency, Monetary) analysis to segment donors into categories:

- **Champions**: High RFM scores, most engaged donors
- **Loyal**: Regular givers with consistent engagement
- **Potential Loyalists**: Recent donors with growth potential
- **Major Gift Prospects**: High capacity donors
- **At Risk**: Previously engaged, declining activity
- **Lost**: No recent engagement
- **Need Attention**: Donors requiring follow-up
- **New/Promising**: Recent but limited history
- **Hibernating**: Long-dormant donors
- **Casual**: Occasional supporters

#### Key Functions:
- `calculate_rfm_scores()`: Calculate RFM scores for all donors
- `get_engagement_metrics()`: Analyze interaction patterns
- `get_opportunity_pipeline()`: Evaluate fundraising opportunities
- `generate_complete_segments()`: Comprehensive segmentation analysis

### 2. AI Insights Engine (`src/insights/engine.py`)

Uses Claude 3.5 Sonnet to generate strategic insights from segmentation data.

#### Key Functions:
- `generate_insights()`: Generate 4-6 strategic insights
- `generate_focused_insight()`: Deep dive on a specific area

Each insight includes:
- **title**: Compelling headline (max 10 words)
- **description**: 2-3 sentences with supporting data
- **impact**: Quantified potential impact
- **recommended_action**: Specific next steps

### 3. Data Summary Functions (`src/insights/data_summary.py`)

Aggregates database statistics for AI analysis:

- `get_database_summary()`: Overall statistics
- `get_giving_trends()`: Contribution patterns over time
- `get_engagement_analysis()`: Interaction analysis
- `get_opportunity_analysis()`: Pipeline metrics

### 4. AI Prompt Templates (`src/insights/prompts.py`)

Structured prompts that guide Claude to generate high-quality insights:

- `SYSTEM_PROMPT`: Expert fundraising strategist persona
- `generate_insights_prompt()`: Main analysis prompt
- `generate_followup_prompt()`: Focused deep-dive prompt

### 5. REST API (`api/insights.py`)

Flask-based REST API with CORS support:

#### Endpoints:

**`GET /api/insights`**
Generate AI-powered insights

Query Parameters:
- `full_data` (bool): Include segmentation and database data (default: false)
- `max_retries` (int): Retry attempts for AI generation (default: 2)

Response:
```json
{
  "insights": [
    {
      "title": "High-Value Donors at Risk",
      "description": "3 major donors haven't engaged in 90+ days...",
      "impact": "At risk of losing $15,000 in annual giving",
      "recommended_action": "Schedule personalized outreach calls this week"
    }
  ],
  "metadata": {
    "model": "claude-3-5-sonnet-20241022",
    "insights_count": 6,
    "analysis_date": "2025-11-20T...",
    "total_constituents": 10
  }
}
```

**`POST /api/insights/focused`**
Generate focused analysis on a specific area

Request:
```json
{
  "focus_area": "engagement risks",
  "previous_insights": [...]
}
```

**`GET /api/segmentation`**
Get full segmentation analysis without AI

**`GET /api/segmentation/rfm`**
Get RFM scores for all donors

**`GET /api/segmentation/engagement`**
Get engagement metrics

**`GET /health`**
Health check endpoint

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Dependencies:
- `anthropic>=0.39.0` - Claude API client
- `sqlalchemy>=2.0.0` - Database ORM
- `flask>=3.0.0` - Web framework
- `flask-cors>=4.0.0` - CORS support
- `python-dotenv>=1.0.0` - Environment configuration

### 2. Set Up Environment

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=your_api_key_here
```

Get your API key from: https://console.anthropic.com/

### 3. Ensure Database Exists

Make sure you've created and populated the database:

```bash
python load_data.py
```

## Usage

### Command Line Testing

Test the segmentation engine and data summary functions:

```bash
python test_insights.py
```

This will:
- Verify database connectivity
- Test RFM calculation
- Test engagement metrics
- Test data aggregation
- Generate sample prompts

### Starting the API Server

```bash
python api/insights.py
```

The API will start on `http://localhost:5000`

Options:
- Set `PORT` environment variable to change port
- Set `FLASK_DEBUG=true` for debug mode

### API Examples

**Generate insights:**
```bash
curl http://localhost:5000/api/insights
```

**Generate insights with full data:**
```bash
curl "http://localhost:5000/api/insights?full_data=true"
```

**Get segmentation only:**
```bash
curl http://localhost:5000/api/segmentation
```

**Get RFM scores:**
```bash
curl http://localhost:5000/api/segmentation/rfm
```

**Generate focused insight:**
```bash
curl -X POST http://localhost:5000/api/insights/focused \
  -H "Content-Type: application/json" \
  -d '{
    "focus_area": "engagement risks"
  }'
```

### Python Usage

**Direct engine usage:**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.insights.engine import create_insights_engine

# Create database session
engine = create_engine('sqlite:///nonprofit_crm.db')
Session = sessionmaker(bind=engine)
session = Session()

# Create insights engine
insights_engine = create_insights_engine(session)

# Generate insights
result = insights_engine.generate_insights()

# Access insights
for insight in result['insights']:
    print(f"\n{insight['title']}")
    print(f"  Description: {insight['description']}")
    print(f"  Impact: {insight['impact']}")
    print(f"  Action: {insight['recommended_action']}")

session.close()
```

**Segmentation only:**

```python
from src.segmentation.engine import create_segmentation_engine

segmentation_engine = create_segmentation_engine(session)
segments = segmentation_engine.generate_complete_segments()

# View segment summary
for segment, metrics in segments['segment_summary'].items():
    print(f"{segment}: {metrics['count']} donors, ${metrics['total_monetary']:,.2f}")
```

## Sample Output

### Insight Example

```json
{
  "title": "Champions Segment Shows Strong Momentum",
  "description": "Your 2 Champion donors have contributed $27,500 (35.9% of total giving) with perfect engagement scores of 100/100. They represent your most valuable relationships with consistent giving patterns and high interaction rates.",
  "impact": "Maintaining these relationships could secure $30,000+ in annual recurring revenue. Risk of losing even one Champion could cost $13,000+ annually.",
  "recommended_action": "Schedule quarterly stewardship meetings with each Champion. Create personalized impact reports showing their contribution's direct effect. Consider inviting them to serve on advisory committees to deepen engagement."
}
```

### Segment Summary Example

```
Champions: 2 constituents ($27,500.00 lifetime giving)
Loyal: 1 constituents ($12,000.00 lifetime giving)
Major Gift Prospects: 1 constituents ($15,000.00 lifetime giving)
At Risk: 2 constituents ($8,100.00 lifetime giving)
Casual: 3 constituents ($4,500.00 lifetime giving)
Lost: 1 constituents ($500.00 lifetime giving)
```

## Configuration

### Environment Variables

- `ANTHROPIC_API_KEY` (required): Your Anthropic API key
- `DATABASE_URL` (optional): Database connection string (default: `sqlite:///nonprofit_crm.db`)
- `PORT` (optional): API server port (default: 5000)
- `FLASK_DEBUG` (optional): Enable debug mode (default: false)
- `CLAUDE_MODEL` (optional): Claude model to use (default: `claude-3-5-sonnet-20241022`)

### Database Support

The engine supports both SQLite and PostgreSQL:

**SQLite (default):**
```
DATABASE_URL=sqlite:///nonprofit_crm.db
```

**PostgreSQL:**
```
DATABASE_URL=postgresql://user:password@localhost/nonprofit_crm
```

## RFM Scoring System

### Recency Score (1-5)
- 5: Last gift within 90 days
- 4: Last gift within 180 days
- 3: Last gift within 365 days
- 2: Last gift within 730 days
- 1: Last gift over 730 days ago

### Frequency Score (0-5)
- 5: 10+ gifts
- 4: 5-9 gifts
- 3: 3-4 gifts
- 2: 2 gifts
- 1: 1 gift
- 0: No gifts

### Monetary Score (0-5)
- 5: $10,000+
- 4: $5,000-$9,999
- 3: $1,000-$4,999
- 2: $500-$999
- 1: $1-$499
- 0: $0

### Engagement Score (0-100)

Calculated from:
- Recency of interactions (40% weight)
- Frequency of interactions (30% weight)
- Weighted interaction types (30% weight)
  - In-person meetings: 3x weight
  - Phone calls: 2x weight
  - Emails: 1x weight

## Error Handling

The engine includes robust error handling:

- **InsightGenerationError**: Raised when AI generation fails
- **Automatic retries**: Configurable retry logic for API calls
- **JSON validation**: Ensures insights have required fields
- **Database session management**: Proper cleanup on errors

## Testing

### Unit Testing

Test individual components:

```bash
# Test segmentation
python -c "
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.segmentation.engine import create_segmentation_engine

engine = create_engine('sqlite:///nonprofit_crm.db')
Session = sessionmaker(bind=engine)
session = Session()

seg_engine = create_segmentation_engine(session)
rfm = seg_engine.calculate_rfm_scores()
print(f'✓ RFM scores calculated for {len(rfm)} donors')
session.close()
"
```

### Integration Testing

Run the full test suite:

```bash
python test_insights.py
```

### API Testing

Test API endpoints:

```bash
# Health check
curl http://localhost:5000/health

# Generate insights (requires API key)
curl http://localhost:5000/api/insights

# Get segmentation
curl http://localhost:5000/api/segmentation
```

## Performance

- **Segmentation Analysis**: ~100-500ms for typical datasets
- **Database Queries**: Optimized with indexes and aggregations
- **AI Generation**: ~3-10 seconds depending on data volume
- **API Response**: Includes full segmentation data if requested

## Limitations

- Requires Anthropic API key (paid service)
- AI generation costs depend on data volume
- Minimum 4 insights required for valid response
- Database must contain contribution and constituent data

## Troubleshooting

### "ANTHROPIC_API_KEY not set" error

Set your API key in `.env` or as an environment variable:

```bash
export ANTHROPIC_API_KEY=your_key_here
```

### "Database not found" error

Create the database first:

```bash
python load_data.py
```

### API returns 500 error

Check the server logs for detailed error messages. Common issues:
- Invalid API key
- Database connection issues
- Missing required data in database

### Import errors

Install all dependencies:

```bash
pip install -r requirements.txt
```

## Future Enhancements

Potential improvements:
- Caching of segmentation results
- Scheduled insight generation
- Email/Slack notifications for critical insights
- Custom segment definitions
- Predictive modeling for churn risk
- Integration with fundraising CRMs
- Dashboard UI for insight visualization
- Historical trend analysis
- A/B testing recommendations

## Support

For issues or questions:
1. Check this documentation
2. Review error logs
3. Verify all dependencies are installed
4. Ensure database is properly populated
5. Confirm API key is valid

## License

This code is part of the nonprofit CRM prototype and follows the same license as the parent project.
