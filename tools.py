"""
Mock tool implementations for the Supernal Persistent Agent demo.

All tools simulate real integrations with:
- Realistic responses (IDs, timestamps, URLs)
- Simulated latency (0.5–2s)
- Structured logging
- Error handling

Companies:
  Amazon    → Sales / SDR tools
  Stripe    → Customer Support tools
  TechVentus → HR & Ops tools
  Generic   → Shared utilities
"""

import uuid
import time
import random
import logging
from datetime import datetime, timedelta

logger = logging.getLogger("tools")

# Verify logging helper - imported lazily to avoid circular imports
def _get_db_module():
    try:
        from db import (
            log_email_sent, log_crm_lead, log_support_ticket,
            log_calendar_event, log_equipment_order, log_tool_execution
        )
        return {
            "log_email_sent": log_email_sent,
            "log_crm_lead": log_crm_lead,
            "log_support_ticket": log_support_ticket,
            "log_calendar_event": log_calendar_event,
            "log_equipment_order": log_equipment_order,
            "log_tool_execution": log_tool_execution,
        }
    except Exception:
        return {}

# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────

def _fake_latency(min_s: float = 0.3, max_s: float = 1.2):
    time.sleep(random.uniform(min_s, max_s))

def _short_id() -> str:
    return str(uuid.uuid4())[:8].upper()

def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

def _future_iso(days: int = 0, hours: int = 0) -> str:
    dt = datetime.utcnow() + timedelta(days=days, hours=hours)
    return dt.isoformat() + "Z"

def _log(tool: str, params: dict, result: dict):
    logger.info("[TOOL] %s | params=%s | result_keys=%s", tool, list(params.keys()), list(result.keys()))


def _require_verification_log(logged: bool, record_type: str):
    """Fail tool execution if the verification record was not persisted."""
    if not logged:
        raise RuntimeError(
            f"{record_type} could not be saved to the verification store. "
            "The action was not completed."
        )


# ══════════════════════════════════════════════════════════════
# AMAZON — SALES / SDR TOOLS
# ══════════════════════════════════════════════════════════════

def send_email_tool(params: dict, organization_id: str = None, ai_employee_id: str = None, user_id: str = None) -> dict:
    """
    Simulate sending a sales outreach email.
    params: to, subject, body, from_name (optional)
    """
    start_time = time.time()
    _fake_latency(0.4, 1.0)

    to       = params.get("to", "prospect@example.com")
    subject  = params.get("subject", "Following up")
    body     = params.get("body", "")
    from_name = params.get("from_name", "Amazon Sales Bot")
    email_id = f"MSG-{_short_id()}"

    # Log to mock emails table if org provided
    if organization_id:
        db = _get_db_module()
        if db.get("log_email_sent"):
            status = "bounced" if random.random() < 0.05 else "sent"
            logged = db["log_email_sent"](organization_id, to, subject, body, email_id, status)
            _require_verification_log(logged, "Email")

    # Simulate occasional bounce
    if random.random() < 0.05:
        result = {
            "status": "bounced",
            "email_id": email_id,
            "to": to,
            "subject": subject,
            "error": "Mailbox does not exist",
            "timestamp": _now_iso(),
        }
    else:
        result = {
            "status": "sent",
            "email_id": email_id,
            "to": to,
            "from": f"{from_name} <noreply@amazon.com>",
            "subject": subject,
            "preview": body[:120] + ("…" if len(body) > 120 else ""),
            "timestamp": _now_iso(),
            "tracking_url": f"https://mail.amazon.internal/track/{_short_id()}",
        }

    latency_ms = int((time.time() - start_time) * 1000)
    if organization_id and ai_employee_id and user_id:
        db = _get_db_module()
        if db.get("log_tool_execution"):
            db["log_tool_execution"](
                organization_id, ai_employee_id, user_id, "send_email",
                params, result, "success", None, latency_ms
            )

    _log("send_email_tool", params, result)
    return result


def add_lead_to_crm_tool(params: dict, organization_id: str = None, ai_employee_id: str = None, user_id: str = None) -> dict:
    """
    Add a prospect to Salesforce CRM.
    params: company, contact_name, email, phone (optional), industry, company_size, opportunity_stage
    """
    start_time = time.time()
    _fake_latency(0.5, 1.5)

    company   = params.get("company", "Unknown Co")
    contact   = params.get("contact_name", "")
    email     = params.get("email", "")
    phone     = params.get("phone", "")
    stage     = params.get("opportunity_stage", "New Lead")
    lead_id   = f"LD-{_short_id()}"

    # Log to mock CRM table if org provided
    if organization_id:
        db = _get_db_module()
        if db.get("log_crm_lead"):
            logged = db["log_crm_lead"](organization_id, lead_id, company, contact, email, phone, stage)
            _require_verification_log(logged, "CRM lead")

    result = {
        "status": "created",
        "lead_id": lead_id,
        "salesforce_id": f"003{_short_id()}",
        "company": company,
        "contact_name": contact,
        "email": email,
        "opportunity_stage": stage,
        "crm_url": f"https://amazon.salesforce.com/leads/{lead_id}",
        "created_at": _now_iso(),
        "owner": "Sales Bot (SDR)",
    }

    latency_ms = int((time.time() - start_time) * 1000)
    if organization_id and ai_employee_id and user_id:
        db = _get_db_module()
        if db.get("log_tool_execution"):
            db["log_tool_execution"](
                organization_id, ai_employee_id, user_id, "add_lead_to_crm",
                params, result, "success", None, latency_ms
            )

    _log("add_lead_to_crm_tool", params, result)
    return result


def schedule_meeting_tool(params: dict, organization_id: str = None, ai_employee_id: str = None, user_id: str = None) -> dict:
    """
    Book a discovery call with a prospect.
    params: attendee_email, attendee_name, date (YYYY-MM-DD), time (HH:MM), duration_min
    """
    start_time = time.time()
    _fake_latency(0.6, 1.8)

    attendee  = params.get("attendee_email", "prospect@example.com")
    name      = params.get("attendee_name", "Prospect")
    date      = params.get("date", _future_iso(days=3)[:10])
    time_str  = params.get("time", "14:00")
    duration  = params.get("duration_min", 30)
    event_id  = f"EVT-{_short_id()}"
    zoom_id   = _short_id()

    # Log to mock calendar table if org provided
    if organization_id:
        db = _get_db_module()
        if db.get("log_calendar_event"):
            logged = db["log_calendar_event"](
                organization_id, event_id, attendee, f"Discovery Call with {name}",
                f"{date}T{time_str}", duration, f"https://zoom.us/j/{zoom_id}"
            )
            _require_verification_log(logged, "Calendar event")

    result = {
        "status": "scheduled",
        "event_id": event_id,
        "calendar_event_id": f"CAL-{_short_id()}",
        "attendee_email": attendee,
        "attendee_name": name,
        "date": date,
        "time": time_str,
        "duration_min": duration,
        "timezone": "America/Los_Angeles",
        "zoom_link": f"https://zoom.us/j/{zoom_id}",
        "zoom_id": zoom_id,
        "calendar_url": f"https://calendar.amazon.com/events/{event_id}",
        "confirmation_sent": True,
        "created_at": _now_iso(),
    }

    latency_ms = int((time.time() - start_time) * 1000)
    if organization_id and ai_employee_id and user_id:
        db = _get_db_module()
        if db.get("log_tool_execution"):
            db["log_tool_execution"](
                organization_id, ai_employee_id, user_id, "schedule_meeting",
                params, result, "success", None, latency_ms
            )

    _log("schedule_meeting_tool", params, result)
    return result


def query_crm_tool(params: dict) -> dict:
    """
    Query CRM for existing leads / opportunities.
    params: query (free text), stage (optional), limit (optional)
    """
    _fake_latency(0.3, 0.9)

    query  = params.get("query", "")
    stage  = params.get("stage", "")
    limit  = min(params.get("limit", 5), 20)

    SAMPLE_LEADS = [
        {"lead_id": f"LD-{_short_id()}", "company": "TechCorp Inc",         "contact": "John Smith",    "email": "john@techcorp.com",   "stage": "Contacted",  "deal_size": "$85K"},
        {"lead_id": f"LD-{_short_id()}", "company": "CloudBase Solutions",   "contact": "Emma Davis",    "email": "emma@cloudbase.io",   "stage": "Qualified",  "deal_size": "$120K"},
        {"lead_id": f"LD-{_short_id()}", "company": "DataFlow Analytics",    "contact": "Mike Johnson",  "email": "mike@dataflow.com",   "stage": "Proposal",   "deal_size": "$200K"},
        {"lead_id": f"LD-{_short_id()}", "company": "Nexus Digital",         "contact": "Sarah Lee",     "email": "sarah@nexus.io",      "stage": "New Lead",   "deal_size": "$55K"},
        {"lead_id": f"LD-{_short_id()}", "company": "Pinnacle Retail",       "contact": "Chris Wang",    "email": "chris@pinnacle.com",  "stage": "Contacted",  "deal_size": "$70K"},
    ]

    leads = [l for l in SAMPLE_LEADS if not stage or l["stage"] == stage][:limit]

    result = {
        "status": "success",
        "query": query,
        "total_results": len(leads),
        "leads": leads,
        "queried_at": _now_iso(),
    }

    _log("query_crm_tool", params, result)
    return result


def search_web_tool(params: dict) -> dict:
    """
    Simulate a web search for prospect research.
    params: query, num_results (optional)
    """
    _fake_latency(0.5, 1.2)

    query  = params.get("query", "")
    n      = min(params.get("num_results", 3), 5)
    slug   = query.lower().replace(" ", "-")[:30]

    results = [
        {
            "rank": i + 1,
            "title": f"{query} — {['Overview', 'News', 'LinkedIn', 'Crunchbase', 'Website'][i % 5]}",
            "url":   f"https://example.com/{slug}-{i+1}",
            "snippet": (
                f"Recent information about {query}. "
                f"Key insight #{i+1}: The company has been expanding rapidly, "
                "focusing on enterprise B2B segments with strong growth indicators."
            ),
            "published": _future_iso(days=-(i * 7))[:10],
        }
        for i in range(n)
    ]

    result = {
        "status": "success",
        "query": query,
        "results": results,
        "searched_at": _now_iso(),
    }

    _log("search_web_tool", params, result)
    return result


# ══════════════════════════════════════════════════════════════
# STRIPE — CUSTOMER SUPPORT TOOLS
# ══════════════════════════════════════════════════════════════

def search_knowledge_base_tool(params: dict) -> dict:
    """
    Search Stripe's internal knowledge base.
    params: query, category (optional: billing|technical|account|fraud)
    """
    _fake_latency(0.3, 0.8)

    query    = params.get("query", "")
    category = params.get("category", "general")

    KB_ARTICLES = {
        "billing": [
            {"id": "KB-1001", "title": "How to handle duplicate charges",               "relevance": 0.97},
            {"id": "KB-1002", "title": "Subscription upgrade/downgrade billing cycles",  "relevance": 0.88},
            {"id": "KB-1003", "title": "Invoice PDF generation and delivery",            "relevance": 0.75},
        ],
        "technical": [
            {"id": "KB-2001", "title": "Resolving Invalid API Key errors",               "relevance": 0.98},
            {"id": "KB-2002", "title": "Webhook signature verification guide",           "relevance": 0.92},
            {"id": "KB-2003", "title": "Rate limiting — retries and exponential backoff","relevance": 0.85},
        ],
        "account": [
            {"id": "KB-3001", "title": "MFA setup and recovery codes",                  "relevance": 0.96},
            {"id": "KB-3002", "title": "User permission tiers in Stripe Dashboard",     "relevance": 0.87},
            {"id": "KB-3003", "title": "Account recovery for lost access",              "relevance": 0.90},
        ],
        "fraud": [
            {"id": "KB-4001", "title": "Account lock — fraud detection triggers",       "relevance": 0.99},
            {"id": "KB-4002", "title": "Dispute handling and chargeback process",       "relevance": 0.93},
            {"id": "KB-4003", "title": "Radar rules — blocking high-risk transactions", "relevance": 0.88},
        ],
    }

    articles_raw = KB_ARTICLES.get(category, KB_ARTICLES["technical"])
    articles = [
        {
            **a,
            "url": f"https://support.stripe.com/articles/{a['id'].lower()}",
            "snippet": f"This article covers {a['title'].lower()} in detail with step-by-step resolution guides.",
        }
        for a in articles_raw[:3]
    ]

    result = {
        "status": "success",
        "query": query,
        "category": category,
        "articles_found": len(articles),
        "top_article": articles[0] if articles else None,
        "all_articles": articles,
        "searched_at": _now_iso(),
    }

    _log("search_knowledge_base_tool", params, result)
    return result


def create_support_ticket_tool(params: dict, organization_id: str = None, ai_employee_id: str = None, user_id: str = None) -> dict:
    """
    Create a support ticket in Stripe's ticketing system.
    params: customer_id, issue_type (billing|technical|account|fraud), description, priority (low|medium|high|critical)
    """
    start_time = time.time()
    _fake_latency(0.4, 1.0)

    customer  = params.get("customer_id", "cus_unknown")
    customer_email = params.get("customer_email", f"{customer}@example.com")
    issue     = params.get("issue_type", "general")
    desc      = params.get("description", "")
    priority  = params.get("priority", "medium")
    ticket_id = f"TKT-{_short_id()}"

    SLA_MAP = {"critical": "30 minutes", "high": "2 hours", "medium": "8 hours", "low": "24 hours"}

    # Log to mock tickets table if org provided
    if organization_id:
        db = _get_db_module()
        if db.get("log_support_ticket"):
            logged = db["log_support_ticket"](
                organization_id, ticket_id, customer_email, issue, desc, priority, "open"
            )
            _require_verification_log(logged, "Support ticket")

    result = {
        "status": "created",
        "ticket_id": ticket_id,
        "customer_id": customer,
        "issue_type": issue,
        "priority": priority,
        "sla_response_time": SLA_MAP.get(priority, "8 hours"),
        "assigned_team": "Support Bot" if priority in ("low", "medium") else "Human Support",
        "ticket_url": f"https://support.stripe.com/tickets/{ticket_id}",
        "description_preview": desc[:100] + ("…" if len(desc) > 100 else ""),
        "created_at": _now_iso(),
        "auto_response_sent": priority in ("low", "medium"),
    }

    latency_ms = int((time.time() - start_time) * 1000)
    if organization_id and ai_employee_id and user_id:
        db = _get_db_module()
        if db.get("log_tool_execution"):
            db["log_tool_execution"](
                organization_id, ai_employee_id, user_id, "create_support_ticket",
                params, result, "success", None, latency_ms
            )

    _log("create_support_ticket_tool", params, result)
    return result


def check_account_status_tool(params: dict) -> dict:
    """
    Retrieve Stripe account status and health.
    params: account_id (or customer_id)
    """
    _fake_latency(0.4, 1.1)

    account_id = params.get("account_id") or params.get("customer_id", "cus_unknown")

    # Simulate various account states
    states = ["active", "active", "active", "restricted", "under_review"]
    status = random.choice(states)

    result = {
        "status": "success",
        "account_id": account_id,
        "account_status": status,
        "email": f"customer+{account_id[-4:]}@business.com",
        "business_name": "Sample Business LLC",
        "payment_volume_30d": f"${random.randint(5, 500) * 1000:,}",
        "successful_payments_30d": random.randint(50, 5000),
        "failed_payments_30d": random.randint(0, 20),
        "open_disputes": random.randint(0, 3),
        "current_balance": f"${random.randint(1, 50) * 1000:,}",
        "last_activity": _future_iso(hours=-random.randint(1, 48)),
        "risk_level": "normal" if status == "active" else "elevated",
        "retrieved_at": _now_iso(),
    }

    _log("check_account_status_tool", params, result)
    return result


def send_notification_tool(params: dict) -> dict:
    """
    Send a notification (email / Slack / SMS).
    params: channel (email|slack|sms), recipient, message, subject (optional)
    """
    _fake_latency(0.2, 0.7)

    channel   = params.get("channel", "email")
    recipient = params.get("recipient", "")
    message   = params.get("message", "")
    subject   = params.get("subject", "Notification from Stripe Support")
    notif_id  = f"NOTIF-{_short_id()}"

    result = {
        "status": "sent",
        "notification_id": notif_id,
        "channel": channel,
        "recipient": recipient,
        "subject": subject,
        "message_preview": message[:100] + ("…" if len(message) > 100 else ""),
        "delivered_at": _now_iso(),
    }

    _log("send_notification_tool", params, result)
    return result


# ══════════════════════════════════════════════════════════════
# TECHVENTUS — HR & OPERATIONS TOOLS
# ══════════════════════════════════════════════════════════════

def schedule_interview_tool(params: dict) -> dict:
    """
    Schedule a candidate interview (HR Bot).
    params: candidate_name, candidate_email, position, interviewer, date, time, interview_type (video|phone|onsite)
    """
    _fake_latency(0.5, 1.5)

    candidate  = params.get("candidate_name", "Candidate")
    email      = params.get("candidate_email", "")
    position   = params.get("position", "Software Engineer")
    interviewer = params.get("interviewer", "Hiring Manager")
    date       = params.get("date", _future_iso(days=5)[:10])
    time_str   = params.get("time", "10:00")
    itype      = params.get("interview_type", "video")
    int_id     = f"INT-{_short_id()}"
    zoom_id    = _short_id()

    result = {
        "status": "scheduled",
        "interview_id": int_id,
        "candidate_name": candidate,
        "candidate_email": email,
        "position": position,
        "interviewer": interviewer,
        "date": date,
        "time": time_str,
        "duration_min": 45,
        "interview_type": itype,
        "zoom_link": f"https://zoom.us/j/{zoom_id}" if itype == "video" else None,
        "lever_url": f"https://hire.lever.co/interviews/{int_id}",
        "confirmation_sent_to_candidate": True,
        "calendar_invite_sent": True,
        "created_at": _now_iso(),
    }

    _log("schedule_interview_tool", params, result)
    return result


def process_leave_request_tool(params: dict) -> dict:
    """
    Process an employee leave request.
    params: employee_name, employee_id, leave_type (PTO|sick|parental|unpaid), start_date, end_date, reason (optional)
    """
    _fake_latency(0.4, 1.2)

    employee   = params.get("employee_name", "Employee")
    emp_id     = params.get("employee_id", f"EMP-{_short_id()}")
    leave_type = params.get("leave_type", "PTO")
    start_date = params.get("start_date", _future_iso(days=7)[:10])
    end_date   = params.get("end_date", _future_iso(days=12)[:10])
    reason     = params.get("reason", "")
    leave_id   = f"LV-{_short_id()}"

    # Parse days
    try:
        from datetime import date
        s = date.fromisoformat(start_date)
        e = date.fromisoformat(end_date)
        days_requested = max((e - s).days + 1, 1)
    except Exception:
        days_requested = 5

    # Simulate leave balance check
    balance_remaining = random.randint(3, 18)
    approved = leave_type == "sick" or balance_remaining >= days_requested

    result = {
        "status": "approved" if approved else "denied",
        "leave_id": leave_id,
        "employee_name": employee,
        "employee_id": emp_id,
        "leave_type": leave_type,
        "start_date": start_date,
        "end_date": end_date,
        "days_requested": days_requested,
        "balance_before": balance_remaining + (days_requested if approved else 0),
        "balance_after": balance_remaining if approved else balance_remaining,
        "denial_reason": None if approved else f"Insufficient leave balance ({balance_remaining} days remaining, {days_requested} requested)",
        "bamboohr_url": f"https://techventus.bamboohr.com/leaves/{leave_id}",
        "calendar_blocked": approved,
        "manager_notified": True,
        "processed_at": _now_iso(),
    }

    _log("process_leave_request_tool", params, result)
    return result


def schedule_meeting_room_tool(params: dict) -> dict:
    """
    Book a meeting room at TechVentus office.
    params: room_name (optional), date, start_time, end_time, attendees (int), purpose
    """
    _fake_latency(0.3, 0.9)

    date       = params.get("date", _future_iso(days=1)[:10])
    start      = params.get("start_time", "10:00")
    end        = params.get("end_time", "11:00")
    attendees  = params.get("attendees", 4)
    purpose    = params.get("purpose", "Team meeting")
    room_id    = f"ROOM-{_short_id()}"

    ROOMS = [
        {"name": "Sequoia",   "capacity": 8,  "amenities": ["Zoom Room", "Whiteboard", "4K Display"]},
        {"name": "Redwood",   "capacity": 4,  "amenities": ["Webcam", "Whiteboard"]},
        {"name": "Yosemite",  "capacity": 12, "amenities": ["Zoom Room", "Whiteboard", "4K Display", "Conference Phone"]},
        {"name": "Tahoe",     "capacity": 2,  "amenities": ["Webcam", "Monitor"]},
    ]
    available_rooms = [r for r in ROOMS if r["capacity"] >= attendees]
    chosen = random.choice(available_rooms) if available_rooms else ROOMS[0]

    result = {
        "status": "booked",
        "booking_id": room_id,
        "room_name": chosen["name"],
        "capacity": chosen["capacity"],
        "amenities": chosen["amenities"],
        "date": date,
        "start_time": start,
        "end_time": end,
        "attendees": attendees,
        "purpose": purpose,
        "zoom_link": f"https://zoom.us/j/{_short_id()}" if "Zoom Room" in chosen["amenities"] else None,
        "calendar_event_created": True,
        "booked_at": _now_iso(),
    }

    _log("schedule_meeting_room_tool", params, result)
    return result


def order_equipment_tool(params: dict, organization_id: str = None, ai_employee_id: str = None, user_id: str = None) -> dict:
    """
    Order equipment for an employee.
    params: employee_name, employee_id, items (list of dicts with name/quantity), shipping_address (optional)
    """
    start_time = time.time()
    _fake_latency(0.5, 1.5)

    employee  = params.get("employee_name", "Employee")
    emp_id    = params.get("employee_id", f"EMP-{_short_id()}")
    items     = params.get("items", [{"name": "MacBook Pro 14\"", "quantity": 1}])
    order_id  = f"ORD-{_short_id()}"

    # Mock pricing
    PRICES = {
        "macbook": 2000, "laptop": 1500, "monitor": 400,
        "keyboard": 150, "mouse": 80, "headset": 200,
        "webcam": 120, "dock": 250, "chair": 450,
    }

    order_items = []
    total = 0
    equipment_str = ""
    for item in (items if isinstance(items, list) else [items]):
        name = item.get("name", "Item") if isinstance(item, dict) else str(item)
        qty  = item.get("quantity", 1) if isinstance(item, dict) else 1
        price_key = next((k for k in PRICES if k in name.lower()), "laptop")
        unit_price = PRICES[price_key]
        subtotal = unit_price * qty
        total += subtotal
        equipment_str = name  # Use first item for logging
        order_items.append({"item": name, "quantity": qty, "unit_price": f"${unit_price:,}", "subtotal": f"${subtotal:,}"})

    estimated_delivery = _future_iso(days=random.randint(3, 7))[:10]

    # Log to mock equipment table if org provided
    if organization_id and order_items:
        db = _get_db_module()
        if db.get("log_equipment_order"):
            first_item = order_items[0]
            # Extract unit price as float
            unit_price_str = first_item.get("unit_price", "0").replace("$", "").replace(",", "")
            try:
                unit_price_float = float(unit_price_str)
            except:
                unit_price_float = 0.0

            logged = db["log_equipment_order"](
                organization_id, order_id, equipment_str,
                len(order_items), unit_price_float, float(total),
                employee, estimated_delivery, "ordered"
            )
            _require_verification_log(logged, "Equipment order")

    result = {
        "status": "ordered",
        "order_id": order_id,
        "employee_name": employee,
        "employee_id": emp_id,
        "items": order_items,
        "total_cost": f"${total:,}",
        "vendor": "Coupa Procurement",
        "estimated_delivery": estimated_delivery,
        "coupa_url": f"https://techventus.coupahost.com/orders/{order_id}",
        "tracking_number": f"1Z{_short_id()}",
        "it_setup_scheduled": True,
        "ordered_at": _now_iso(),
    }

    latency_ms = int((time.time() - start_time) * 1000)
    if organization_id and ai_employee_id and user_id:
        db = _get_db_module()
        if db.get("log_tool_execution"):
            db["log_tool_execution"](
                organization_id, ai_employee_id, user_id, "order_equipment",
                params, result, "success", None, latency_ms
            )

    _log("order_equipment_tool", params, result)
    return result


# ══════════════════════════════════════════════════════════════
# GENERIC TOOLS  (available to all orgs)
# ══════════════════════════════════════════════════════════════

def update_database_tool(params: dict) -> dict:
    """
    Generic database record update.
    params: table, record_id, data (dict of fields to update)
    """
    _fake_latency(0.3, 0.8)

    table     = params.get("table", "records")
    record_id = params.get("record_id", f"REC-{_short_id()}")
    data      = params.get("data", {})

    result = {
        "status": "updated",
        "table": table,
        "record_id": record_id,
        "fields_updated": list(data.keys()),
        "rows_affected": 1,
        "updated_at": _now_iso(),
    }

    _log("update_database_tool", params, result)
    return result


# ══════════════════════════════════════════════════════════════
# ROUTER — used by agent.py
# ══════════════════════════════════════════════════════════════

TOOL_REGISTRY = {
    # Amazon Sales
    "send_email":           send_email_tool,
    "send_email_tool":      send_email_tool,
    "add_lead_to_crm":      add_lead_to_crm_tool,
    "add_lead_to_crm_tool": add_lead_to_crm_tool,
    "schedule_meeting":     schedule_meeting_tool,
    "schedule_meeting_tool": schedule_meeting_tool,
    "query_crm":            query_crm_tool,
    "query_crm_tool":       query_crm_tool,
    "search_web":           search_web_tool,
    "search_web_tool":      search_web_tool,

    # Stripe Support
    "search_knowledge_base":      search_knowledge_base_tool,
    "search_knowledge_base_tool": search_knowledge_base_tool,
    "create_support_ticket":      create_support_ticket_tool,
    "create_support_ticket_tool": create_support_ticket_tool,
    "create_ticket":              create_support_ticket_tool,
    "check_account_status":       check_account_status_tool,
    "check_account_status_tool":  check_account_status_tool,
    "send_notification":          send_notification_tool,
    "send_notification_tool":     send_notification_tool,

    # TechVentus HR/Ops
    "schedule_interview":        schedule_interview_tool,
    "schedule_interview_tool":   schedule_interview_tool,
    "process_leave_request":     process_leave_request_tool,
    "process_leave_request_tool": process_leave_request_tool,
    "schedule_meeting_room":     schedule_meeting_room_tool,
    "schedule_meeting_room_tool": schedule_meeting_room_tool,
    "order_equipment":           order_equipment_tool,
    "order_equipment_tool":      order_equipment_tool,

    # Generic
    "update_database":      update_database_tool,
    "update_database_tool": update_database_tool,
    "add_calendar_event":   schedule_meeting_tool,   # alias
}


def route_tool_call(tool_name: str, params: dict, organization_id: str = None, ai_employee_id: str = None, user_id: str = None) -> dict:
    """
    Route a tool call by name.  Falls back to a descriptive stub for unknowns.
    This is the drop-in replacement for the route_tool_call in agent.py.
    """
    fn = TOOL_REGISTRY.get(tool_name)
    if fn:
        # Check if function accepts the logging parameters
        import inspect
        sig = inspect.signature(fn)
        if len(sig.parameters) > 1:  # More than just 'params'
            return fn(params, organization_id, ai_employee_id, user_id)
        else:
            return fn(params)

    # Unknown tool stub
    _fake_latency(0.2, 0.5)
    return {
        "status": "executed",
        "tool": tool_name,
        "params": params,
        "note": f"Mock result for tool '{tool_name}' — replace with real integration.",
        "timestamp": _now_iso(),
    }
