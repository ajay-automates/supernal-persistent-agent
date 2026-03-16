"""
Verify that tool execution data was persisted to the database.
Tests data persistence for all 5 tools across all organizations.
"""

import requests
from db import (
    list_organizations,
    get_emails_sent,
    get_crm_leads,
    get_support_tickets,
    get_calendar_events,
    get_equipment_orders
)

BASE_URL = "http://localhost:8000"

def verify_organization_data():
    """Verify tool execution data for all organizations."""
    orgs = list_organizations()

    print("\n" + "="*80)
    print("🔍 VERIFYING TOOL EXECUTION DATA PERSISTENCE")
    print("="*80)

    for org in orgs:
        org_id = org["id"]
        org_name = org["name"]

        print(f"\n📊 Organization: {org_name} ({org_id})")
        print("-" * 80)

        # Check emails
        emails = get_emails_sent(org_id)
        print(f"   📧 Emails sent: {len(emails)}")
        if emails:
            for email in emails[:3]:  # Show first 3
                to_email = email.get("to_email", email.get("recipient", "unknown"))
                subject = email.get("subject", "No subject")
                sent_at = email.get("sent_at", "unknown")
                print(f"      ✅ {to_email} | {subject} | {sent_at}")
            if len(emails) > 3:
                print(f"      ... and {len(emails) - 3} more")

        # Check CRM leads
        leads = get_crm_leads(org_id)
        print(f"   🏢 CRM leads: {len(leads)}")
        if leads:
            for lead in leads[:3]:  # Show first 3
                company = lead.get("company_name", "Unknown")
                contact = lead.get("contact_name", "Unknown")
                email = lead.get("email", "unknown@email.com")
                print(f"      ✅ {company} | {contact} | {email}")
            if len(leads) > 3:
                print(f"      ... and {len(leads) - 3} more")

        # Check support tickets
        tickets = get_support_tickets(org_id)
        print(f"   🎟️  Support tickets: {len(tickets)}")
        if tickets:
            for ticket in tickets[:3]:  # Show first 3
                ticket_id = ticket.get("ticket_id", "Unknown")
                customer = ticket.get("customer_email", "unknown@email.com")
                priority = ticket.get("priority", "unknown")
                print(f"      ✅ {ticket_id} | {customer} | Priority: {priority}")
            if len(tickets) > 3:
                print(f"      ... and {len(tickets) - 3} more")

        # Check calendar events
        events = get_calendar_events(org_id)
        print(f"   📅 Calendar events: {len(events)}")
        if events:
            for event in events[:3]:  # Show first 3
                title = event.get("title", "Unknown")
                attendee = event.get("attendee_email", "unknown@email.com")
                created = event.get("created_at", "unknown")
                print(f"      ✅ {title} | {attendee} | {created}")
            if len(events) > 3:
                print(f"      ... and {len(events) - 3} more")

        # Check equipment orders
        orders = get_equipment_orders(org_id)
        print(f"   📦 Equipment orders: {len(orders)}")
        if orders:
            for order in orders[:3]:  # Show first 3
                item = order.get("item_name", "Unknown")
                qty = order.get("quantity", 0)
                created = order.get("created_at", "unknown")
                print(f"      ✅ {qty}x {item} | {created}")
            if len(orders) > 3:
                print(f"      ... and {len(orders) - 3} more")

        total_tools = len(emails) + len(leads) + len(tickets) + len(events) + len(orders)
        print(f"   📈 TOTAL PERSISTED RECORDS: {total_tools}")

    print("\n" + "="*80)
    print("✅ DATA VERIFICATION COMPLETE")
    print("="*80)
    print("\nAll tool execution data should be visible at: http://localhost:8000/verification")

if __name__ == "__main__":
    verify_organization_data()
