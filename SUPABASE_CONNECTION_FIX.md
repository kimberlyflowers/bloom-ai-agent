# 🔧 SUPABASE CONNECTION - CORRECT FORMAT

## ✅ Use This Connection String in Railway

Update the `SUPABASE_DB_URL` environment variable to:

```
postgresql://postgres:P2NponYbQbgSGQxI@aws-0-us-east-2.pooler.supabase.com:5432/postgres
```

## 🎯 Why This Works

1. **Hostname**: `aws-0-us-east-2.pooler.supabase.com` - The pooler endpoint DOES resolve (we got auth errors, not DNS errors)
2. **Username**: `postgres` - Simple format confirmed by SQL queries (NOT `postgres.wazbpoujdmckkozjqyqs`)
3. **Port**: `5432` - Session mode for persistent Railway server connections
4. **Password**: `P2NponYbQbgSGQxI` - Reset password (no special chars, no encoding needed)
5. **SSL**: Automatically added by our code (`?sslmode=require`)

## 🔍 What We Learned

- The direct connection host `wazbpoujdmckkozjqyqs.db.us-east-2.supabase.co` fails DNS resolution from Railway
- The pooler host `aws-0-us-east-2.pooler.supabase.com` DOES resolve
- We were using the wrong username format with the pooler (dotted instead of simple)
- This combination should work!

## 📋 Steps to Update

1. Go to Railway dashboard → bloom-ai-agent service
2. Navigate to Variables tab
3. Update `SUPABASE_DB_URL` with the connection string above
4. Railway will auto-redeploy
5. Check logs for "✅ Connected to Supabase PostgreSQL database"
