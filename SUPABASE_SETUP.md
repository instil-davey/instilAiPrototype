# Supabase Setup Guide

This guide will help you complete the Supabase setup for your Nonprofit CRM application.

## ✅ What's Already Done

The following has been configured automatically:

1. ✅ **Backend Configuration**
   - Added Supabase PostgreSQL connection to `.env`
   - Installed `psycopg2-binary` for PostgreSQL support
   - Updated `requirements.txt`

2. ✅ **Frontend Configuration**
   - Installed `@supabase/supabase-js` client library
   - Created Supabase client configuration (`frontend/src/supabaseClient.js`)
   - Added environment variables (`frontend/.env`)

3. ✅ **Database Schema**
   - Created SQL migration file (`supabase_schema.sql`)

## 🚀 Next Steps (Manual Action Required)

### Step 1: Create Database Schema in Supabase

Since the sandbox environment can't directly connect to external databases, you need to run the SQL migration manually:

1. Go to your Supabase project dashboard: https://app.supabase.com/project/yzkmlvnwllxrybywafrh
2. Navigate to **SQL Editor** in the left sidebar
3. Create a new query
4. Copy the contents of `supabase_schema.sql` and paste it into the SQL editor
5. Click **Run** to execute the SQL

This will create all necessary tables:
- `constituents` - Donors, volunteers, board members
- `contributions` - Donations and gifts
- `interactions` - Meetings, calls, emails
- `opportunities` - Fundraising pipeline

### Step 2: Verify Database Connection

After creating the schema, you can verify the connection:

```bash
# Activate virtual environment
source venv/bin/activate

# Run the verification script
python init_supabase.py
```

If successful, you should see:
```
✅ Database connection successful
✅ Database schema created successfully!
```

### Step 3: Start Your Application

**Backend (API):**
```bash
# Make sure you're in the project root
source venv/bin/activate
uvicorn main:app --reload
```

The API will be available at: http://localhost:8000

**Frontend:**
```bash
cd frontend
npm run dev
```

The frontend will be available at: http://localhost:5173

## 📁 Configuration Files

### Backend Environment (`.env`)
```env
# Supabase PostgreSQL
DATABASE_URL=postgresql://postgres:QrnEZ5HPT%2AW%40%24.j@db.yzkmlvnwllxrybywafrh.supabase.co:5432/postgres

# Supabase Frontend Configuration
NEXT_PUBLIC_SUPABASE_URL=https://yzkmlvnwllxrybywafrh.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=sb_publishable_vsqohPH_vhHEuowhZa2tHQ_H1LcelWg
```

### Frontend Environment (`frontend/.env`)
```env
# Supabase Configuration
VITE_SUPABASE_URL=https://yzkmlvnwllxrybywafrh.supabase.co
VITE_SUPABASE_ANON_KEY=sb_publishable_vsqohPH_vhHEuowhZa2tHQ_H1LcelWg

# API Configuration
VITE_API_URL=http://localhost:8000
```

## 🔧 Using Supabase in Your Frontend

The Supabase client is already configured and ready to use. Import it in your React components:

```javascript
import { supabase, db } from './supabaseClient'

// Example: Fetch all constituents
const constituents = await db.getConstituents()

// Example: Get a single constituent with relationships
const constituent = await db.getConstituent(123)

// Example: Create a new contribution
const contribution = await db.createContribution({
  constituent_id: 123,
  contribution_date: '2024-01-15',
  amount: 100.00,
  contribution_type: 'credit_card',
  campaign: 'Annual Fund 2024'
})
```

## 🔐 Security Notes

1. **Row Level Security (RLS)** is enabled on all tables with basic policies
2. The policies currently allow all authenticated users full access
3. **For Production:** Customize the RLS policies in `supabase_schema.sql` based on your needs

## 📊 Optional: Load Sample Data

If you have a data loading script:

```bash
python load_data.py
```

This will populate your Supabase database with sample data for testing.

## 🐛 Troubleshooting

### Connection Issues

If you get connection errors:
1. Verify your DATABASE_URL is correct in `.env`
2. Check that your Supabase project is active
3. Ensure your IP is not blocked by Supabase (check project settings)

### Authentication Issues

If you need to set up Supabase Auth:
1. Go to Authentication → Providers in Supabase dashboard
2. Enable Email/Password or other providers
3. Update your frontend to use `supabase.auth.signUp()` and `supabase.auth.signIn()`

## 📚 Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase JS Client Reference](https://supabase.com/docs/reference/javascript/introduction)
- [SQLAlchemy + PostgreSQL Guide](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html)

## ✅ Migration Complete!

Your application is now configured to use Supabase PostgreSQL instead of SQLite. All your data will be stored in Supabase's cloud database with automatic backups, scaling, and real-time capabilities.
