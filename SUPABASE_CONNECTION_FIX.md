# 🔧 SUPABASE CONNECTION - CORRECT FORMAT (FINAL!)

## ✅ Use This Connection String in Railway

Update the `SUPABASE_DB_URL` environment variable to:

```
postgresql://postgres.wazbpoujdmckkozjqyqs:P2NponYbQbgSGQxI@aws-1-us-east-2.pooler.supabase.com:5432/postgres
```

## 🎯 Why This FINALLY Works

1. **Method**: Session Pooler (IPv4 compatible - required for Railway!)
2. **Hostname**: `aws-1-us-east-2.pooler.supabase.com` (It's aws-1, not aws-0!)
3. **Username**: `postgres.wazbpoujdmckkozjqyqs` (Dotted format for Session Pooler!)
4. **Port**: `5432` (Session mode for persistent connections)
5. **Password**: `P2NponYbQbgSGQxI` (Reset password)
6. **SSL**: Automatically added by our code (`?sslmode=require`)

## 🔍 What We Learned (The Hard Way!)

- Direct connection uses **IPv6** - Railway doesn't support IPv6
- Must use **Session Pooler** for IPv4 compatibility
- Session Pooler uses **dotted username** format: `postgres.projectref`
- Session Pooler hostname is **`aws-1`** not `aws-0`
- This is the EXACT format from Supabase Connect UI!

## 📋 Steps to Update

1. Go to Railway dashboard → bloom-ai-agent service
2. Navigate to Variables tab
3. Update `SUPABASE_DB_URL` with the connection string above
4. Railway will auto-redeploy
5. Check logs for "✅ Connected to Supabase PostgreSQL database"
