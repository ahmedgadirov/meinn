# Database Schema Update Deployment Guide

## Problem Summary

The production server is experiencing SQLite errors:
```
sqlite3.OperationalError: no such column: c.name_en
```

This occurs because the code expects multilingual database columns that don't exist in the production database.

## Solution Overview

We've implemented a **two-phase solution**:

### Phase 1: Immediate Fix (✅ COMPLETED)
- Modified `menu_manager.py` to be backward compatible
- Code now detects available columns and adapts queries automatically
- **Result**: No more crashes, immediate stability

### Phase 2: Complete Fix (Schema Update)
- Deploy database schema update to add multilingual columns
- **Result**: Full multilingual functionality enabled

## Deployment Instructions

### Option A: Emergency Deployment (Immediate)

**Current code changes are already backward compatible!**

Simply deploy the updated `src/services/product/menu_manager.py` file to production. The errors will stop immediately.

```bash
# Deploy the updated menu_manager.py
# The code will automatically detect missing columns and work around them
```

### Option B: Complete Deployment (Recommended)

**Step 1: Deploy Code Changes**
```bash
# Deploy updated menu_manager.py (backward compatible)
git pull origin main
# Restart application
```

**Step 2: Run Schema Update**
```bash
# Navigate to project root directory
cd /path/to/your/project

# Run the schema update script
python3 deploy_schema_update.py
```

**Step 3: Restart Application**
```bash
# Restart your application server
# The code will now detect multilingual support and use full functionality
```

## What the Schema Update Does

1. **Safety First**:
   - Creates automatic database backup with timestamp
   - Checks current schema before making changes
   - Logs all operations for audit trail

2. **Schema Updates**:
   - Adds multilingual columns to `categories` table
   - Adds multilingual columns to `menu_items` table
   - Supports 8 languages: az, en, ru, tr, ar, hi, fr, it

3. **Data Migration**:
   - Migrates existing data to English columns
   - Preserves all existing functionality
   - No data loss

## Verification

After deployment, check logs for:
```
INFO - Multilingual support detected: True
```

If you see `False`, the schema update needs to be run.

## Rollback Plan

If anything goes wrong:

1. **For Code Issues**:
   ```bash
   git revert <commit-hash>
   ```

2. **For Database Issues**:
   ```bash
   # Restore from automatic backup
   cp menu_data.db.backup_YYYYMMDD_HHMMSS menu_data.db
   ```

## Files Modified

- `src/services/product/menu_manager.py` - Made backward compatible
- `deploy_schema_update.py` - Schema update script (new)
- `DEPLOYMENT_GUIDE.md` - This guide (new)

## Languages Supported

The schema update adds support for:
- **az** - Azerbaijani (primary)
- **en** - English
- **ru** - Russian  
- **tr** - Turkish
- **ar** - Arabic
- **hi** - Hindi
- **fr** - French
- **it** - Italian

## Support

If you encounter any issues:

1. Check application logs for error details
2. Check schema update logs: `schema_update_YYYYMMDD_HHMMSS.log`
3. Verify database backup exists before making changes
4. Contact development team if manual intervention needed

## Success Indicators

✅ **Immediate Success** (Phase 1):
- No more "no such column" errors in logs
- API endpoints return data successfully
- Application runs without crashes

✅ **Complete Success** (Phase 2):
- Logs show "Multilingual support detected: True"
- Full multilingual functionality available
- Schema update completed without errors
