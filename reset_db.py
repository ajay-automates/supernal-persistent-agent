"""Reset Supabase data (keep schema, clear data)."""
from config import supabase

# Delete in reverse dependency order
tables_to_clear = [
    "tool_access_attempts",
    "user_ai_employee_assignments",
    "ai_employees",
    "users",
    "tools",
    "organization_chunks",
    "organization_documents",
    "organizations",
]

for table in tables_to_clear:
    try:
        # Delete all records - use a filter that matches everything
        supabase.table(table).delete().filter("id", "is.not", None).execute()
        print(f"✓ Cleared {table}")
    except Exception as e:
        print(f"⚠ {table}: {e}")

print("\n✅ Database reset complete")
