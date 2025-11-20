# 🚀 How to Connect Supabase PostgreSQL to Railway

**Date**: 2025-11-20
**Status**: ✅ WORKING - Tested and Verified

This guide documents the correct way to connect a Railway-deployed application to Supabase PostgreSQL for persistent database storage.

---

## 📋 Prerequisites

- Active Supabase project
- Railway project deployed
- Python application with `psycopg2-binary>=2.9.9` installed

---

## 🎯 The Critical Issue

**Railway is IPv4-only**, but **Supabase Direct Connection uses IPv6**. This causes connection failures with errors like:
- `could not translate host name to address`
- `Network is unreachable`

**Solution**: Use Supabase **Session Pooler** which provides IPv4 compatibility.

---

## ✅ Step-by-Step Setup

### 1. Get the Correct Connection String from Supabase

1. Go to your Supabase project dashboard
2. Click **"Connect"** button in the top navigation
3. Select **"Connection String"** tab
4. **IMPORTANT**: Change the "Method" dropdown from **"Direct connection"** to **"Session pooler"**
5. You'll see a connection string like:

```
postgresql://postgres.YOUR_PROJECT_REF:[YOUR-PASSWORD]@aws-1-REGION.pooler.supabase.com:5432/postgres
```

### 2. Key Format Details

The Session Pooler connection string has this specific format:

```
postgresql://postgres.PROJECT_REF:PASSWORD@aws-1-REGION.pooler.supabase.com:5432/postgres
```

**Important notes:**
- ✅ Username: `postgres.YOUR_PROJECT_REF` (includes project reference with dot)
- ✅ Hostname: `aws-1-REGION.pooler.supabase.com` (note: `aws-1`, not `aws-0`)
- ✅ Port: `5432` (Session mode - for persistent server connections)
- ✅ Database: `postgres`

**DO NOT use:**
- ❌ Direct connection hostname: `db.PROJECT_REF.supabase.co` (IPv6 only)
- ❌ Simple username: `postgres` (without project reference)
- ❌ Wrong pooler number: `aws-0` instead of `aws-1`

### 3. Insert Your Password

Replace `[YOUR-PASSWORD]` with your actual database password from Supabase Database Settings.

For BLOOM AI Agent project:
```
postgresql://postgres.wazbpoujdmckkozjqyqs:P2NponYbQbgSGQxI@aws-1-us-east-2.pooler.supabase.com:5432/postgres
```

### 4. Set Railway Environment Variable

1. Go to your Railway project
2. Navigate to your service → **Variables** tab
3. Add environment variable:
   - **Name**: `SUPABASE_DB_URL` (or your app's database URL variable name)
   - **Value**: The complete connection string from step 3

4. Railway will automatically redeploy with the new variable

### 5. Verify Connection in Logs

After deployment, check Railway logs for:

```
✅ Connection string has postgres. format (CORRECT)
🔒 Added SSL mode to connection string
🔌 PostgreSQL connection established
✅ Database tables created/verified
✅ Connected to Supabase PostgreSQL database
```

If you see these messages, **SUCCESS!** Your app is now connected to Supabase.

---

## 🔒 SSL Configuration

Your application code should automatically add `?sslmode=require` to the connection string:

```python
def connect(self):
    conn_string = self.connection_string
    if 'sslmode=' not in conn_string:
        separator = '&' if '?' in conn_string else '?'
        conn_string = f"{conn_string}{separator}sslmode=require"
        logger.info("🔒 Added SSL mode to connection string")

    self.conn = psycopg2.connect(conn_string, cursor_factory=RealDictCursor)
```

Note: Supabase does not enforce SSL by default, but it's recommended for security.

---

## 🐛 Common Errors and Solutions

### Error: "could not translate host name to address"

**Cause**: Using Direct Connection hostname (IPv6) instead of Session Pooler (IPv4)

**Solution**: Switch to Session Pooler connection string in Supabase Connect UI

---

### Error: "FATAL: Tenant or user not found"

**Cause**: Wrong username format

**Solution**: Ensure username includes project reference: `postgres.PROJECT_REF`

---

### Error: "Network is unreachable" with IPv6 address

**Cause**: Railway doesn't support IPv6

**Solution**: Use Session Pooler, not Direct Connection

---

### Error: "Connection refused" or timeout

**Cause**: Wrong pooler hostname or port

**Solution**:
- Verify hostname is `aws-1-REGION.pooler.supabase.com` (note `aws-1`)
- Verify port is `5432` for Session mode
- Check your Supabase region matches the hostname

---

## 📊 Why Session Pooler vs Direct Connection?

| Feature | Direct Connection | Session Pooler |
|---------|------------------|----------------|
| **IP Protocol** | IPv6 | IPv4 (proxied) |
| **Railway Compatible** | ❌ No | ✅ Yes |
| **Username Format** | `postgres` | `postgres.PROJECT_REF` |
| **Hostname** | `db.PROJECT_REF.supabase.co` | `aws-1-REGION.pooler.supabase.com` |
| **Port** | 5432 or 6543 | 5432 (session) or 6543 (transaction) |
| **Best For** | IPv6 networks, long-lived connections | IPv4 networks (Railway, Vercel, etc.) |

---

## 🔍 Monitoring Connections

Once connected, you can monitor live connections in Supabase SQL Editor:

```sql
SELECT
  pg_stat_activity.pid as connection_id,
  ssl,
  datname as database,
  usename as connected_role,
  application_name,
  client_addr as IP,
  query,
  state,
  backend_start
FROM pg_stat_ssl
JOIN pg_stat_activity
ON pg_stat_ssl.pid = pg_stat_activity.pid
WHERE usename LIKE 'postgres%';
```

Look for connections from your Railway app with username `postgres.YOUR_PROJECT_REF`.

---

## ✅ Success Checklist

- [ ] Using Session Pooler connection string (not Direct Connection)
- [ ] Username includes project reference: `postgres.PROJECT_REF`
- [ ] Hostname is `aws-1-REGION.pooler.supabase.com`
- [ ] Port is `5432` for session mode
- [ ] Password is correct (reset in Supabase if needed)
- [ ] Environment variable set in Railway
- [ ] Deployment logs show successful connection
- [ ] Application can read/write to database

---

## 🎓 Lessons Learned

This setup took hours of troubleshooting because:

1. **IPv6 incompatibility** - Railway doesn't support IPv6, but Supabase Direct Connection uses it
2. **Hidden setting** - The "Session pooler" option is in a dropdown that's easy to miss
3. **Username confusion** - Different connection methods use different username formats
4. **Pooler numbering** - It's `aws-1` not `aws-0` (easy to guess wrong)
5. **Documentation gaps** - Neither Railway nor Supabase explicitly mentions this IPv4/IPv6 issue in their Railway integration guides

**Key Insight**: When deploying to IPv4-only platforms (Railway, some Vercel configurations, etc.), **always use Session Pooler, never Direct Connection**.

---

## 📚 References

- [Supabase Connection Pooling Docs](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler)
- [Railway Documentation](https://docs.railway.app/)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)

---

## 🆘 Still Having Issues?

1. Verify your Railway logs for the exact error message
2. Check Supabase Dashboard → Database → Connection Info
3. Test connection locally using Railway CLI: `railway run python test_db.py`
4. Verify your database password is correct (reset if needed)
5. Check Supabase service status: https://status.supabase.com/

---

**Last Updated**: 2025-11-20
**Verified Working**: ✅ Yes
**Project**: BLOOM AI Agent
**Railway Service**: bloom-ai-agent
**Supabase Project**: wazbpoujdmckkozjqyqs
