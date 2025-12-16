# Nonprofit CRM Platform

A comprehensive, production-ready CRM system for nonprofit organizations with REST API, multiple web interfaces, and advanced data management capabilities.

## 🎯 Overview

This platform provides a complete full-stack CRM solution for nonprofits to manage constituents, track donations, log interactions, and manage fundraising opportunities. It features a FastAPI backend with two frontend options: a React SPA and a modern Next.js dashboard.

## ✨ Features

### Backend API
- **RESTful API** with FastAPI and automatic OpenAPI documentation
- **JWT Authentication** for secure access
- **CRUD Operations** for all entities (constituents, contributions, interactions, opportunities)
- **Advanced Filtering** and search capabilities
- **Dashboard Statistics** and reporting endpoints
- **Database Agnostic** - Works with SQLite and PostgreSQL

### Frontend Options

#### React Frontend
- **Modern React Application** with routing and state management
- **Responsive Design** that works on desktop and mobile
- **Dashboard** with key metrics and recent activity
- **Constituent Management** with detailed profiles and giving history
- **Contribution Tracking** with campaign analytics
- **Search and Filtering** across all data

#### Next.js Dashboard
- **Modern UI**: Built with Next.js 15, Tailwind CSS, and shadcn/ui
- **AI Insights**: Real-time metrics and performance indicators
- **Segment Analysis**: Constituent segmentation with detailed analytics
- **Responsive Design**: Mobile-friendly interface with smooth animations
- **Type-Safe**: Full TypeScript support
- **Optimized Performance**: React Query for efficient data fetching

### Data Layer
- **Normalized SQL Schema** with proper relationships and constraints
- **SQLAlchemy ORM** for database abstraction
- **Sample Data Generator** using Faker for realistic test data
- **Pre-built Views** for reporting and analytics
- **Comprehensive Indexing** for optimal query performance
- **Data Quality Handling**: Graceful handling of missing/null values
- **🆕 AI-Driven Insights**: Intelligent donor analysis using Claude 3.5 Sonnet (see [INSIGHTS_README.md](INSIGHTS_README.md))
- **🆕 Donor Segmentation**: RFM (Recency, Frequency, Monetary) analysis and engagement scoring
- **🆕 REST API**: Flask-based API for insights and segmentation

## 🚀 Quick Start

### Option 1: Easy Start Script (Recommended)

```bash
# Make the script executable (first time only)
chmod +x start.sh

# Run the startup script
./start.sh
```

The script will:
1. Create a virtual environment
2. Install all dependencies
3. Generate sample data (if needed)
4. Start both backend and frontend servers

**Access the application:**
- React Frontend: http://localhost:5173 (set `FRONTEND_PORT` to override)
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Default Login:**
- Username: `admin`
- Password: `secret`

### Option 2: Next.js Dashboard

```bash
# Install dependencies
pip install -r requirements.txt
npm install

# Load sample data
python3 generate_sample_data.py

# Start Next.js dashboard (development)
npm run dev
```

Dashboard will be available at: http://localhost:3000

### Option 3: Docker Compose

```bash
# Generate sample data first
python3 generate_sample_data.py

# Start with Docker
docker-compose up
```

### Option 4: Manual Setup

#### Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate sample data
python3 generate_sample_data.py

# Start the backend server
uvicorn api.main:app --reload
```

Backend will be available at: http://localhost:8000

#### Frontend Setup (React)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:5173 (or your configured port).
Set a custom port by exporting `FRONTEND_PORT` (for example `FRONTEND_PORT=4000 npm run dev`) or by adding it to `frontend/.env`.

## 📁 Project Structure

```
.
├── api/                        # Backend API
│   ├── main.py                # FastAPI application
│   ├── auth.py                # Authentication & JWT
│   ├── deps.py                # Database dependencies
│   ├── schemas.py             # Pydantic models
│   └── routers/               # API endpoints
│       ├── auth.py            # Login endpoints
│       ├── constituents.py    # Constituent CRUD
│       ├── contributions.py   # Contribution CRUD
│       ├── interactions.py    # Interaction CRUD
│       ├── opportunities.py   # Opportunity CRUD
│       └── dashboard.py       # Dashboard stats
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API client
│   │   └── context/          # Auth context
│   ├── package.json
│   └── vite.config.js
├── app/                       # Next.js dashboard
│   ├── api/                   # API routes
│   ├── dashboard/            # Dashboard pages
│   └── layout.tsx
├── components/                # Next.js components
├── lib/                       # Next.js utilities
├── models.py                  # SQLAlchemy ORM models
├── schema.sql                 # Database schema
├── config.py                  # Application configuration
├── generate_sample_data.py    # Sample data generator
├── requirements.txt           # Python dependencies
├── package.json              # Next.js dependencies
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose setup
└── start.sh                   # Quick start script
```

## 🔌 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info

### Constituents
- `GET /api/v1/constituents` - List constituents (with filtering)
- `POST /api/v1/constituents` - Create constituent
- `GET /api/v1/constituents/{id}` - Get constituent details
- `PUT /api/v1/constituents/{id}` - Update constituent
- `DELETE /api/v1/constituents/{id}` - Delete constituent
- `GET /api/v1/constituents/{id}/summary` - Get giving summary

### Contributions
- `GET /api/v1/contributions` - List contributions (with filtering)
- `POST /api/v1/contributions` - Create contribution
- `GET /api/v1/contributions/{id}` - Get contribution details
- `PUT /api/v1/contributions/{id}` - Update contribution
- `DELETE /api/v1/contributions/{id}` - Delete contribution
- `GET /api/v1/contributions/stats/by-campaign` - Campaign statistics

### Interactions
- `GET /api/v1/interactions` - List interactions
- `POST /api/v1/interactions` - Create interaction
- `GET /api/v1/interactions/{id}` - Get interaction details
- `PUT /api/v1/interactions/{id}` - Update interaction
- `DELETE /api/v1/interactions/{id}` - Delete interaction

### Opportunities
- `GET /api/v1/opportunities` - List opportunities
- `POST /api/v1/opportunities` - Create opportunity
- `GET /api/v1/opportunities/{id}` - Get opportunity details
- `PUT /api/v1/opportunities/{id}` - Update opportunity
- `DELETE /api/v1/opportunities/{id}` - Delete opportunity
- `GET /api/v1/opportunities/stats/pipeline` - Pipeline statistics

### Dashboard
- `GET /api/v1/dashboard/stats` - Comprehensive dashboard statistics
- `GET /api/v1/dashboard/recent-activity` - Recent contributions and interactions

**Full API Documentation:** Visit http://localhost:8000/docs after starting the backend

## 📊 Database Schema

### Tables

1. **constituents** - Core table for all constituent types
   - constituent_id (PK), first_name, last_name, email, phone, address
   - constituent_type: donor, volunteer, board_member, staff, other
   - status: active, inactive, deceased

2. **contributions** - Monetary and in-kind donations
   - contribution_id (PK), constituent_id (FK), amount, contribution_date
   - contribution_type: cash, check, credit_card, stock, in_kind, other
   - campaign, appeal, notes

3. **interactions** - Communications and meetings
   - interaction_id (PK), constituent_id (FK), interaction_date
   - interaction_type: email, phone, meeting, event, letter, other
   - subject, notes, outcome

4. **opportunities** - Fundraising pipeline
   - opportunity_id (PK), constituent_id (FK), opportunity_name
   - amount, probability, expected_close_date
   - stage: prospecting, qualification, proposal, negotiation, closed_won, closed_lost
   - campaign, notes

### Relationships
```
constituents (1) ──→ (N) contributions
constituents (1) ──→ (N) interactions
constituents (1) ──→ (N) opportunities
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Application
APP_NAME=Nonprofit CRM
DEBUG=True

# Database
DATABASE_URL=sqlite:///./nonprofit_crm.db

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
CORS_ORIGINS=["http://localhost:5173"]
```

## AI-Driven Insights Engine

The project now includes an AI-powered insights engine that analyzes your donor data and generates strategic fundraising recommendations.

### Quick Start

1. **Install dependencies** (if not already installed):
```bash
pip install -r requirements.txt
```

2. **Set up your Anthropic API key**:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

3. **Test the segmentation engine** (no API key needed):
```bash
python test_insights.py
```

4. **Start the API server**:
```bash
python api/insights.py
```

5. **Generate insights**:
```bash
curl http://localhost:5000/api/insights
```

### What You Get

The insights engine provides 4-6 strategic recommendations covering:

- **Giving Trends**: Patterns in contribution behavior and seasonality
- **Engagement Risks**: Donors at risk of lapsing or declining engagement
- **Upgrade Opportunities**: Potential for increased giving and major gifts
- **Portfolio Suggestions**: Strategic recommendations for donor management

Each insight includes:
- **Title**: Clear, compelling headline
- **Description**: Analysis with supporting data
- **Impact**: Quantified potential impact
- **Recommended Action**: Specific next steps

### Example Insight

```json
{
  "title": "Champions Segment Shows Strong Momentum",
  "description": "Your 2 Champion donors have contributed $27,500 (35.9% of total giving) with perfect engagement scores...",
  "impact": "Maintaining these relationships could secure $30,000+ in annual recurring revenue.",
  "recommended_action": "Schedule quarterly stewardship meetings with each Champion..."
}
```

### API Endpoints

- `GET /api/insights` - Generate AI-powered insights
- `GET /api/segmentation` - Get donor segmentation (RFM analysis)
- `GET /api/segmentation/rfm` - Get RFM scores
- `GET /api/segmentation/engagement` - Get engagement metrics
- `POST /api/insights/focused` - Get focused analysis on specific area

See [INSIGHTS_README.md](INSIGHTS_README.md) for complete documentation.

### Database Configuration

**SQLite (Default):**
```python
DATABASE_URL = "sqlite:///./nonprofit_crm.db"
```

**PostgreSQL:**
```python
DATABASE_URL = "postgresql://username:password@localhost/nonprofit_crm"
```

## 🎨 Frontend Features

### Dashboard
- Total constituents and active count
- Total contributions with year/month breakdowns
- Average gift amount
- Open opportunities with weighted pipeline value
- Recent interactions (last 30 days)
- Recent contributions and interactions lists

### Constituents Page
- Searchable list of all constituents
- Filter by type (donor, volunteer, board member, etc.)
- Filter by status (active, inactive)
- Click to view detailed profiles

### Constituent Detail Page
- Contact information
- Giving summary (total, count, average, last gift)
- List of all contributions
- Recent interactions history
- Notes

### Contributions Page
- List of all contributions
- Campaign performance statistics
- Total and average calculations

## 🧪 Sample Data

The `generate_sample_data.py` script creates realistic test data:

- **50 constituents** with varied types and statuses
- **100 contributions** with realistic amounts and campaigns
- **150 interactions** across different types
- **30 opportunities** in various pipeline stages

Run it anytime to reset/generate data:
```bash
python3 generate_sample_data.py
```

## 🔐 Security

- **JWT Authentication** for all API endpoints
- **Password hashing** with bcrypt
- **CORS protection** for frontend requests
- **SQL injection protection** via SQLAlchemy ORM
- **Input validation** with Pydantic models

**⚠️ Production Deployment:**
- Change the SECRET_KEY in `.env`
- Use HTTPS in production
- Implement rate limiting
- Add proper logging and monitoring
- Use PostgreSQL instead of SQLite
- Set DEBUG=False

## 📦 Dependencies

### Backend
- FastAPI - Web framework
- SQLAlchemy - ORM
- Pydantic - Data validation
- python-jose - JWT tokens
- passlib - Password hashing
- uvicorn - ASGI server
- Faker - Sample data generation

### React Frontend
- React - UI framework
- React Router - Routing
- Axios - HTTP client
- Vite - Build tool

### Next.js Dashboard
- Next.js 15 - React framework
- Tailwind CSS - Styling
- shadcn/ui - UI components
- TypeScript - Type safety
- React Query - Data fetching

## 🚢 Deployment

### Production Checklist
- [ ] Change SECRET_KEY to a secure random value
- [ ] Set DEBUG=False
- [ ] Switch to PostgreSQL database
- [ ] Configure proper CORS origins
- [ ] Set up HTTPS/SSL
- [ ] Implement rate limiting
- [ ] Add logging and monitoring
- [ ] Set up automated backups
- [ ] Configure proper error handling
- [ ] Add user management system

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🧰 Development

### Run Tests
```bash
# Backend tests (when implemented)
pytest

# Frontend tests (when implemented)
cd frontend && npm test
```

### Code Quality
```bash
# Format Python code
black .

# Lint Python code
flake8 .

# Type checking
mypy .
```

## 📈 Roadmap

### Completed ✅
- [x] Database schema and ORM models
- [x] REST API with authentication
- [x] React frontend with routing
- [x] Next.js dashboard with modern UI
- [x] Dashboard with statistics
- [x] Constituent management
- [x] Contribution tracking
- [x] Sample data generation
- [x] Docker configuration

### Future Enhancements
- [ ] User management and roles
- [ ] Email integration
- [ ] Report generation (PDF/Excel)
- [ ] Advanced analytics and charts
- [ ] Email templates and campaigns
- [ ] Event management
- [ ] Volunteer scheduling
- [ ] Mobile responsive improvements
- [ ] Automated testing suite
- [ ] Data import/export tools

## 🤝 Contributing

This is an MVP/proof-of-concept. To extend:

1. **Add new features** by creating new API endpoints and frontend pages
2. **Improve UI/UX** by enhancing the React components
3. **Add tests** for backend and frontend
4. **Optimize performance** with caching and query optimization
5. **Enhance security** with additional authentication methods

## 📄 License

This is a proof-of-concept for educational and demonstration purposes.

## 🆘 Troubleshooting

### Backend won't start
- Check Python version (3.11+ required)
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify database file permissions

### Frontend won't start
- Check Node version (18+ required)
- Delete `node_modules` and run `npm install` again
- Check if your configured Vite port (default 5173) is already in use

### Database errors
- Delete `nonprofit_crm.db` and run `generate_sample_data.py` again
- Check file permissions on the database file

### Login fails
- Default credentials: username=`admin`, password=`secret`
- Check that backend is running on port 8000
- Clear browser localStorage and try again

## 📞 Support

For issues or questions:
1. Check the API documentation at http://localhost:8000/docs
2. Review the inline code documentation
3. Check application logs for error messages

---

**Built with ❤️ for nonprofit organizations**
