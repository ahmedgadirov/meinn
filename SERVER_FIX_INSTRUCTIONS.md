# 🔧 Server Database Path Fix

## The Problem
- Lightning import created database at: `/project/src/menu_data.db`
- API is looking for database at: `/project/menu_data.db`
- **Result**: Products don't show in interface

## Quick Fix (2 commands)

On your server, run these commands:

```bash
# 1. Go to project root
cd ~/project

# 2. Move the database to correct location
mv src/menu_data.db ./menu_data.db
```

## Alternative: Re-run Import from Correct Location

If you prefer to re-run the import:

```bash
# 1. Go to project root  
cd ~/project

# 2. Copy the lightning import script and CSV here (if not already)
cp src/lightning_import.py ./
cp src/real_menu_data.csv ./

# 3. Run the lightning import from project root
python lightning_import.py
```

## Verify the Fix

After either approach, check that the database exists in the right place:

```bash
ls -la ~/project/menu_data.db
```

You should see the database file listed.

## Why This Happened

The MenuManager calculates the database path as 3 directory levels up from `src/services/product/menu_manager.py`:
- `src/services/product/` → `src/services/` → `src/` → `project/` (root)
- So it expects: `/project/menu_data.db`

When you ran the lightning import from `/project/src/`, it created the database in that directory instead of the project root.

## Future Imports

Always run `python lightning_import.py` from the **project root directory** (`~/project/`) to ensure the database is created in the correct location.
