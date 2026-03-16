"""
Simplified tool implementations for the Supernal Persistent Agent.

5 Essential Tools:
1. send_email — Send outreach/support emails
2. create_crm_lead — Add prospects to CRM
3. create_support_ticket — Create support tickets
4. schedule_calendar_event — Schedule meetings/calls
5. place_equipment_order — Order equipment/supplies
"""

import uuid
import time
import random
import logging
from datetime import datetime, timedelta

logger = logging.getLogger("tools")


def _get_db_module():
    """Lazy import to avoid circular imports."""
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


def _fake_latency(min_s: float = 0.3, max_s: float = 1.2):
    """Simulate network latency."""
    time.sleep(random.uniform(min_s, max_s))


def _short_id() -> str:
    """Generate a short unique ID."""
    return str(uuid.uuid4())[:8].upper()


def _now_iso() -> str:
    """Get current UTC time in ISO format."""
    return datetime.utcnow().isoformat() + "Z"


def _require_verification_log(logged: bool, record_type: str):
    """Fail if verification record was not persisted."""
    if not logged:
        raise RuntimeError(
            f"{record_type} could not be saved to the verification store. "
            "The action was not completed."
        )


# ══════════════════════════════════════════════════════════════
# 5 ESSENTIAL TOOLS
# ══════════════════════════════════════════════════════════════

def send_email_tool(params: dict, organization_id: str = None, ai_employee_id: str = None, user_id: str = None) -> dict:
    """
    Send an email.
    params: to, subject, body, cc (optional)
    """
    start_time = time.time()
    _fake_latency(0.4, 1.0)

    to = params.get("to", "recipient@example.com")
    subject = params.get("subject", "Message from Agent")
    body = params.get("body", "")
    cc = params.get("cc", "")
    email_id = f"MSG-{_short_id()}"

    # Log to verification table
    if organization_id:
        db = _get_db_module()
        if db.get("log_email_sent"):
            status = "sent"
            logged = db["log_email_sent"](organization_id, to, subject, body, email_id, status)
            _require_verification_log(logged, "Email")

    result = {
        "status": "sent",
        "email_id": email_id,
        "to": to,
        "cc": cc or None,
        "subject": subject,
        "preview": body[:120] + ("…" if len(body) > 120 else ""),
        "timestamp": _now_iso(),
    }

    latency_ms = int((time.time() - start_time) * 1000)
    if organization_id and ai_employee_id and user_id:
        db = _get_db_module()
        if db.get("log_tool_execution"):
            db["log_tool_execution"](
                organization_id, ai_employee_id, user_id, "send_email",
                params, result, "success", None, latency_ms
            )

    logger.info("[TOOL] send_email | to=%s | timestamp=%s", to, result["timestamp"])
    return result


def create_crm_lead_tool(params: dict, organization_id: str = None, ai_employee_id: str = None, user_id: str = None) -> dict:
    """
    Add a lead to CRM.
    params: company_name, contact_name, email, phone (optional), status (optional)
    """
    start_time = time.time()
    _fake_latency(0.5, 1.5)

    company = params.get("company_name", "Unknown Company")
    contact = params.get("contact_name", "")
    email = params.get("email", "")
    phone = params.get("phone", "")
    status = params.get("status", "new")
    lead_id = f"LD-{_short_id()}"

    # Log to verification table
    if organization_id:
        db = _get_db_module()
        if db.get("log_crm_lead"):
            logged = db["log_crm_lead"](organization_id, lead_id, company, contact, email, phone, status)
            _require_verification_log(logged, "CRM lead")

    result = {
        "status": "created",
        "lead_id": lead_id,
        "company": company,
        "contact_name": contact,
        "email": email,
        "phone": phone or None,
        "opportunity_stage": status,
        "created_at": _now_iso(),
    }

    latency_ms = int((time.time() - start_time) * 1000)
    if organization_id and ai_employee_id and user_id:
        db = _get_db_module()
        if db.get("log_tool_execution"):
            db["log_tool_execution"](
                organization_id, ai_employee_id, user_id, "create_crm_lead",
                params, result, "success", None, latency_ms
            )

    logger.info("[TOOL] create_crm_lead | lead_id=%s | company=%s", lead_id, company)
    return result


def create_support_ticket_tool(params: dict, organization_id: str = None, ai_employee_id: str = None, user_id: str = None) -> dict:
    """
    Create a support ticket.
    params: customer_email, subject, description, priority (optional: low|medium|high|critical)
    """
    start_time = time.time()
    _fake_latency(0.4, 1.0)

    customer_email = params.get("customer_email", "customer@example.com")
    subject = params.get("subject", "Support Request")
    description = params.get("description", "")
    priority = params.get("priority", "medium")
    ticket_id = f"TKT-{_short_id()}"

    SLA_MAP = {"critical": "30 min", "high": "2 hrs", "medium": "8 hrs", "low": "24 hrs"}

    # Log to verification table
    if organization_id:
        db = _get_db_module()
        if db.get("log_support_ticket"):
            logged = db["log_support_ticket"](
                organization_id, ticket_id, customer_email, subject, description, priority, "open"
            )
            _require_verification_log(logged, "Support ticket")

    result = {
        "status": "created",
        "ticket_id": ticket_id,
        "customer_email": customer_email,
        "subject": subject,
        "priority": priority,
        "sla_response_time": SLA_MAP.get(priority, "8 hrs"),
        "description_preview": description[:100] + ("…" if len(description) > 100 else ""),
        "created_at": _now_iso(),
    }

    latency_ms = int((time.time() - start_time) * 1000)
    if organization_id and ai_employee_id and user_id:
        db = _get_db_module()
        if db.get("log_tool_execution"):
            db["log_tool_execution"](
                organization_id, ai_employee_id, user_id, "create_support_ticket",
                params, result, "success", None, latency_ms
            )

    logger.info("[TOOL] create_support_ticket | ticket_id=%s | priority=%s", ticket_id, priority)
    return result


def schedule_calendar_event_tool(params: dict, organization_id: str = None, ai_employee_id: str = None, user_id: str = None) -> dict:
    """
    Schedule a calendar event/meeting.
    params: title, attendee_email, start_time (ISO format), end_time (ISO format), description (optional)
    """
    start_time = time.time()
    _fake_latency(0.6, 1.8)

    title = params.get("title", "Meeting")
    attendee_email = params.get("attendee_email", "attendee@example.com")
    start = params.get("start_time", datetime.utcnow().isoformat())
    end = params.get("end_time", (datetime.utcnow() + timedelta(hours=1)).isoformat())
    description = params.get("description", "")
    event_id = f"EVT-{_short_id()}"
    zoom_id = _short_id()

    # Log to verification table
    if organization_id:
        db = _get_db_module()
        if db.get("log_calendar_event"):
            logged = db["log_calendar_event"](
                organization_id, event_id, attendee_email, title, start, 60, f"https://zoom.us/j/{zoom_id}"
            )
            _require_verification_log(logged, "Calendar event")

    result = {
        "status": "scheduled",
        "event_id": event_id,
        "title": title,
        "attendee_email": attendee_email,
        "start_time": start,
        "end_time": end,
        "zoom_link": f"https://zoom.us/j/{zoom_id}",
        "description": description or None,
        "created_at": _now_iso(),
    }

    latency_ms = int((time.time() - start_time) * 1000)
    if organization_id and ai_employee_id and user_id:
        db = _get_db_module()
        if db.get("log_tool_execution"):
            db["log_tool_execution"](
                organization_id, ai_employee_id, user_id, "schedule_calendar_event",
                params, result, "success", None, latency_ms
            )

    logger.info("[TOOL] schedule_calendar_event | event_id=%s | title=%s", event_id, title)
    return result


def place_equipment_order_tool(params: dict, organization_id: str = None, ai_employee_id: str = None, user_id: str = None) -> dict:
    """
    Place an equipment order.
    params: item_name, quantity, cost_usd (optional), delivery_date (optional)
    """
    start_time = time.time()
    _fake_latency(0.5, 1.5)

    item_name = params.get("item_name", "Equipment")
    quantity = params.get("quantity", 1)
    cost_usd = params.get("cost_usd", 100.0)
    delivery_date = params.get("delivery_date", (datetime.utcnow() + timedelta(days=5)).isoformat()[:10])
    order_id = f"ORD-{_short_id()}"

    total_cost = float(cost_usd) * int(quantity)

    # Log to verification table
    if organization_id:
        db = _get_db_module()
        if db.get("log_equipment_order"):
            logged = db["log_equipment_order"](
                organization_id, order_id, item_name, quantity, cost_usd, total_cost,
                "Agent", delivery_date, "ordered"
            )
            _require_verification_log(logged, "Equipment order")

    result = {
        "status": "ordered",
        "order_id": order_id,
        "item_name": item_name,
        "quantity": quantity,
        "unit_cost": f"${cost_usd:,.2f}",
        "total_cost": f"${total_cost:,.2f}",
        "estimated_delivery": delivery_date,
        "tracking_number": f"1Z{_short_id()}",
        "ordered_at": _now_iso(),
    }

    latency_ms = int((time.time() - start_time) * 1000)
    if organization_id and ai_employee_id and user_id:
        db = _get_db_module()
        if db.get("log_tool_execution"):
            db["log_tool_execution"](
                organization_id, ai_employee_id, user_id, "place_equipment_order",
                params, result, "success", None, latency_ms
            )

    logger.info("[TOOL] place_equipment_order | order_id=%s | item=%s | qty=%d", order_id, item_name, quantity)
    return result


# ══════════════════════════════════════════════════════════════
# TOOL REGISTRY & ROUTER
# ══════════════════════════════════════════════════════════════

TOOL_REGISTRY = {
    "send_email": send_email_tool,
    "create_crm_lead": create_crm_lead_tool,
    "create_support_ticket": create_support_ticket_tool,
    "schedule_calendar_event": schedule_calendar_event_tool,
    "place_equipment_order": place_equipment_order_tool,
}


def route_tool_call(tool_name: str, params: dict, organization_id: str = None, ai_employee_id: str = None, user_id: str = None) -> dict:
    """
    Route a tool call by name. Falls back to a stub for unknowns.
    """
    fn = TOOL_REGISTRY.get(tool_name)
    if fn:
        import inspect
        sig = inspect.signature(fn)
        if len(sig.parameters) > 1:
            return fn(params, organization_id, ai_employee_id, user_id)
        else:
            return fn(params)

    # Unknown tool stub
    _fake_latency(0.2, 0.5)
    return {
        "status": "executed",
        "tool": tool_name,
        "params": params,
        "note": f"Tool '{tool_name}' not found. Available tools: {', '.join(TOOL_REGISTRY.keys())}",
        "timestamp": _now_iso(),
    }
