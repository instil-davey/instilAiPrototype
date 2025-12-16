# Constituent Briefing Engine - Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Anthropic API key
# Get a key from: https://console.anthropic.com/
nano .env  # or use your preferred editor
```

Your `.env` should contain:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### 3. Initialize Database (if not already done)

```bash
# If you have CSV files with constituent data:
python load_data.py

# Or if you need to create sample data, the database will be created automatically
# when you first run the API
```

### 4. Start the API Server

```bash
python main.py
```

The server will start at `http://localhost:8000`

### 5. Test It Out

**Option A: Interactive Documentation**
- Open your browser: http://localhost:8000/docs
- Click on the `/api/constituents/{constituent_id}/briefing` endpoint
- Click "Try it out"
- Enter a constituent ID (e.g., `CONST003`)
- Click "Execute"

**Option B: Command Line**
```bash
curl "http://localhost:8000/api/constituents/CONST003/briefing?segments=Major%20Donors,Board%20Members"
```

**Option C: Python Test Script**
```bash
python test_briefing.py
```

## 📖 Detailed Usage

### Using the API

#### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "checks": {
    "api": "healthy",
    "anthropic_api_key": "configured",
    "database": "available"
  }
}
```

#### 2. Generate Briefing

```bash
curl "http://localhost:8000/api/constituents/CONST001/briefing?segments=Major%20Donors"
```

**Response:**
```json
{
  "summary": "John Smith is a donor who has contributed...",
  "giving_summary": "Total giving of $15,000 across 4 gifts...",
  "engagement_pattern": "Has 3 recorded interactions...",
  "why_they_matter": "Consistent donor with capacity...",
  "segment_reason": "Classified as Major Donor based on...",
  "suggested_action": "Schedule a cultivation lunch within 30 days...",
  "metadata": {
    "constituent_id": "CONST001",
    "generated_at": "2025-01-20T10:30:00.000Z",
    "data_points": {
      "contributions": 4,
      "interactions": 3,
      "opportunities": 1,
      "transactions": 4,
      "segments": 1
    }
  }
}
```

#### 3. Batch Briefings

```bash
curl -X POST http://localhost:8000/api/constituents/briefings/batch \
  -H "Content-Type: application/json" \
  -d '["CONST001", "CONST002", "CONST003"]'
```

### Using Python SDK

```python
from models import get_session
from src.briefing.engine import BriefingEngine

# Initialize
engine = BriefingEngine()  # Uses ANTHROPIC_API_KEY from environment
session = get_session()

# Generate briefing
briefing = engine.generate_briefing(
    constituent_id="CONST001",
    db_session=session,
    segment_names=["Major Donors", "Monthly Giving"]
)

# Access fields
print(f"Summary: {briefing['summary']}")
print(f"Action: {briefing['suggested_action']}")

# Cleanup
session.close()
```

### Integration with Your Application

#### JavaScript/React Example

```javascript
async function getConstituentBriefing(constituentId, segments = []) {
  const segmentParam = segments.length
    ? `?segments=${segments.join(',')}`
    : '';

  const response = await fetch(
    `http://localhost:8000/api/constituents/${constituentId}/briefing${segmentParam}`
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

// Usage
getConstituentBriefing('CONST001', ['Major Donors'])
  .then(briefing => {
    console.log('Summary:', briefing.summary);
    console.log('Suggested Action:', briefing.suggested_action);
  })
  .catch(error => console.error('Error:', error));
```

#### Python Requests Example

```python
import requests

def get_briefing(constituent_id, segments=None):
    url = f"http://localhost:8000/api/constituents/{constituent_id}/briefing"

    params = {}
    if segments:
        params['segments'] = ','.join(segments)

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()

# Usage
briefing = get_briefing('CONST001', segments=['Major Donors'])
print(briefing['summary'])
print(briefing['suggested_action'])
```

## 🎯 Common Use Cases

### 1. Pre-Meeting Briefing

**Scenario:** You have a meeting with a donor in 30 minutes and need a quick briefing.

```python
briefing = engine.generate_briefing("CONST001", session)

# Print key points
print("📋 MEETING PREP")
print(f"\nWho they are: {briefing['summary']}")
print(f"\nWhy they matter: {briefing['why_they_matter']}")
print(f"\nSuggested approach: {briefing['suggested_action']}")
```

### 2. Batch Reporting

**Scenario:** Generate briefings for your top 10 donors for a board report.

```python
top_donors = session.query(Constituent)\
    .order_by(Constituent.total_lifetime_giving.desc())\
    .limit(10)\
    .all()

for donor in top_donors:
    briefing = engine.generate_briefing(donor.constituent_id, session)
    # Generate PDF or send email with briefing
```

### 3. Segment Analysis

**Scenario:** Understand why constituents are in a particular segment.

```python
# Get all major donors
major_donors = session.query(Constituent)\
    .filter(Constituent.constituent_type == 'Major Donor')\
    .all()

for donor in major_donors:
    briefing = engine.generate_briefing(
        donor.constituent_id,
        session,
        segment_names=['Major Donors']
    )
    print(f"{donor.full_name}: {briefing['segment_reason']}")
```

### 4. Automated Email Campaigns

**Scenario:** Send personalized briefings to development team about their assigned constituents.

```python
import smtplib
from email.mime.text import MIMEText

def send_briefing_email(staff_email, briefings):
    """Send email with constituent briefings."""
    html_content = "<h1>Your Constituent Briefings</h1>"

    for briefing in briefings:
        html_content += f"""
        <div style="border: 1px solid #ccc; padding: 20px; margin: 10px 0;">
            <h2>{briefing['metadata']['constituent_id']}</h2>
            <p><strong>Summary:</strong> {briefing['summary']}</p>
            <p><strong>Suggested Action:</strong> {briefing['suggested_action']}</p>
        </div>
        """

    # Send email (configure SMTP settings)
    msg = MIMEText(html_content, 'html')
    msg['Subject'] = 'Daily Constituent Briefings'
    msg['To'] = staff_email
    # ... SMTP sending code
```

## 🔧 Configuration Options

### Environment Variables

Create a `.env` file with these variables:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-api03-...

# Optional
DATABASE_URL=sqlite:///nonprofit_crm.db
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info
CORS_ORIGINS=http://localhost:5173

# For production PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost:5432/nonprofit_crm
```

### Customizing the AI Model

You can modify the model in `src/briefing/engine.py`:

```python
class BriefingEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.model = "claude-sonnet-4-5-20250929"  # Change this
        # Options:
        # - claude-sonnet-4-5-20250929 (latest, balanced)
        # - claude-opus-4-5-20250229 (most capable, slower)
        # - claude-3-5-sonnet-20240620 (previous version)
```

### Customizing Prompts

Edit the `_create_briefing_prompt()` method in `src/briefing/engine.py` to customize how the AI generates briefings.

## 🐛 Troubleshooting

### "ANTHROPIC_API_KEY not configured"

```bash
# Check if key is set
echo $ANTHROPIC_API_KEY

# Set it temporarily
export ANTHROPIC_API_KEY="your_key_here"

# Or add to .env file
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
```

### "Constituent not found"

```bash
# Check available constituents
python verify_database.py

# Or query directly
python -c "from models import get_session, Constituent; \
s = get_session(); \
[print(f'{c.constituent_id}: {c.full_name}') for c in s.query(Constituent).all()]"
```

### Port 8000 already in use

```bash
# Use a different port
uvicorn main:app --host 0.0.0.0 --port 8001

# Or find and kill the process
lsof -ti:8000 | xargs kill -9
```

### Import errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

## 📊 Performance Tips

1. **Cache briefings**: Briefings don't change frequently for most constituents
   ```python
   # Add caching with Redis or simple dict
   briefing_cache = {}

   def get_cached_briefing(constituent_id):
       if constituent_id not in briefing_cache:
           briefing_cache[constituent_id] = engine.generate_briefing(...)
       return briefing_cache[constituent_id]
   ```

2. **Use batch endpoint**: For multiple constituents, use the batch endpoint instead of individual calls

3. **Implement rate limiting**: Add rate limiting to prevent API quota exhaustion

4. **Background jobs**: For large batches, use Celery or similar for async processing

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Anthropic Documentation**: https://docs.anthropic.com/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/

## 🤝 Getting Help

If you encounter issues:

1. Check the logs (API will print detailed error messages)
2. Verify your environment variables are set correctly
3. Ensure database is initialized with data
4. Check API key permissions and quota
5. Review the BRIEFING_ENGINE.md documentation

For bugs or feature requests, please open an issue on GitHub.
