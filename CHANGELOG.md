# Changelog

## Homepage Vendor Visibility Fixes & DB Schema Resilience

**Root Causes:**
1. The homepage query filtered strictly by `status='active'`, preventing vendors whose profiles were stuck in `pending` (the default) from being displayed, often confusing users.
2. The initial implementations sometimes ran against older DB schemas lacking the `vendor_profile.status` column, causing SQLAlchemy to hard-crash with an `OperationalError` when rendering the index route.
3. If a vendor profile successfully registered but `description` was `NULL`, the slice operation `business.description[:120]` in `templates/index.html` threw a `TypeError`.

**Fixes Applied:**
1. **Schema Check & Migration**: Added a lightweight startup schema check in `app.py` context that automatically alters the `vendor_profile` table to append a default `status='active'` column and backfill existing entries. This restores older environments safely.
2. **Resilient Queries**: Safely caught the `OperationalError` around the `active` vendor query on the index page. Instead of a 500 server crash, the query falls back to mapping standard raw SQL results (ignoring the missing `status` column mapping constraint) and lists all profiles.
3. **Null-safe Templating**: Modified `templates/index.html` to inject a default empty string summary: `(business.description or 'No description available')[:120]` effectively preventing `NoneType` attribute string crashes.
4. **Visibility & Expectations**: Added clear helper text in `templates/vendor/setup.html` asserting that newly submitted profiles will stay hidden pending admin moderation, setting immediate actionable expectations for vendors.
5. **Testing Added**: Added `test_app.py` covering tests for mock active/pending combinations, explicit missing `status` schema simulation, and `Null` description strings. Tests successfully passing.
