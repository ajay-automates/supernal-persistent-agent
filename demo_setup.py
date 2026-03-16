"""
RBAC-aware demo data seeder.

Creates three organizations (Amazon, Stripe, TechVentus) with 3 AI employees each
and 1 user per organization, all tied to the RBAC role catalog.
"""

import logging

from config import OPENAI_API_KEY
from db import (
    create_organization,
    list_organizations,
    create_ai_employee,
    get_ai_employees,
    create_user,
    get_org_users,
    save_organization_document,
    save_organization_chunk,
    get_organization_documents,
    register_tool,
    get_organization_tools,
    assign_ai_employee_to_user,
    get_role_id_by_name,
    get_allowed_tools_for_role,
)
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("demo_setup")

client = OpenAI(api_key=OPENAI_API_KEY)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def _chunk(text: str):
    chunks = []
    for i in range(0, len(text), CHUNK_SIZE - CHUNK_OVERLAP):
        chunk = text[i:i + CHUNK_SIZE]
        if chunk.strip():
            chunks.append(chunk.strip())
    return chunks


def _embed_and_store(org_id: str, filename: str, text: str) -> int:
    count = 0
    for chunk in _chunk(text):
        embedding = client.embeddings.create(
            model="text-embedding-3-small",
            input=chunk,
        )
        save_organization_chunk(org_id, chunk, embedding.data[0].embedding, filename)
        count += 1
    return count


def _get_or_create_org(name: str) -> dict:
    for org in list_organizations():
        if org["name"].lower() == name.lower():
            log.info("Org exists: %s", name)
            return org
    org = create_organization(name)
    log.info("Created org: %s", name)
    return org


def _get_or_create_user(org_id: str, user_id: str, name: str, email: str) -> dict:
    for user in get_org_users(org_id):
        if user["user_id"] == user_id:
            return user
    return create_user(org_id, user_id, name, email)


def _get_or_create_agent(org_id: str, name: str, role: str, job_description: str) -> dict:
    for agent in get_ai_employees(org_id):
        if agent["name"].lower() == name.lower():
            return agent
    return create_ai_employee(org_id, name, role, job_description)


def _upload_doc_if_missing(org_id: str, filename: str, text: str) -> None:
    docs = get_organization_documents(org_id)
    if any(doc["filename"] == filename for doc in docs):
        return
    save_organization_document(org_id, filename, filename)
    chunks = _embed_and_store(org_id, filename, text)
    log.info("Uploaded doc %s (%s chunks)", filename, chunks)


def _register_tool_if_missing(org_id: str, name: str) -> None:
    existing = get_organization_tools(org_id)
    if any(tool["name"] == name for tool in existing):
        return
    register_tool(
        org_id,
        name,
        f"RBAC-enabled tool: {name}",
        {"parameters": {}},
        "",
    )


def _ensure_assignments(user_assignments: dict) -> int:
    count = 0
    for user_id, agent_ids in user_assignments.items():
        for agent_id in agent_ids:
            if assign_ai_employee_to_user(user_id, agent_id):
                count += 1
    return count


def _seed_company(config: dict) -> dict:
    org = _get_or_create_org(config["organization_name"])
    org_id = org["id"]

    for document in config.get("documents", []):
        _upload_doc_if_missing(org_id, document["filename"], document["text"])

    users = {}
    for user in config["users"]:
        users[user["user_id"]] = _get_or_create_user(
            org_id, user["user_id"], user["name"], user["email"]
        )

    agents = {}
    role_tools = set()
    for employee in config["employees"]:
        if not get_role_id_by_name(employee["role"]):
            raise ValueError(f"Unknown RBAC role: {employee['role']}")
        agent = _get_or_create_agent(
            org_id,
            employee["name"],
            employee["role"],
            employee["job_description"],
        )
        agents[employee["key"]] = agent

        role_id = get_role_id_by_name(employee["role"])
        role_tools.update(get_allowed_tools_for_role(role_id))

    for tool_name in sorted(role_tools):
        _register_tool_if_missing(org_id, tool_name)

    assignment_map = {
        user_id: [agents[key]["id"] for key in agent_keys]
        for user_id, agent_keys in config["assignments"].items()
    }
    assignment_count = _ensure_assignments(assignment_map)

    return {
        "organization_id": org_id,
        "organization_name": config["organization_name"],
        "users": len(users),
        "agents": len(agents),
        "assignments": assignment_count,
        "tools": len(role_tools),
    }


COMPANIES = [
    {
        "organization_name": "Amazon",
        "documents": [
            {
                "filename": "amazon_playbook.txt",
                "text": (
                    "Amazon runs outbound sales with emphasis on research, CRM hygiene, and fast meeting booking. "
                    "Agents should personalize outreach, log leads, handle support tickets, and schedule calls."
                ),
            },
        ],
        "employees": [
            {
                "key": "sales",
                "name": "Alex",
                "role": "Sales Development Rep (SDR)",
                "job_description": "Research prospects, send personalized outreach, update CRM, and schedule discovery calls.",
            },
            {
                "key": "support",
                "name": "Maya",
                "role": "Customer Support Agent",
                "job_description": "Resolve customer issues, create support tickets, and escalate when needed.",
            },
            {
                "key": "ops",
                "name": "Quinn",
                "role": "Operations Manager",
                "job_description": "Coordinate schedules, place equipment orders, and schedule operational meetings.",
            },
        ],
        "users": [
            {"user_id": "ajay", "name": "Ajay", "email": "ajay@amazon.com"},
        ],
        "assignments": {
            "ajay": ["sales", "support", "ops"],
        },
    },
    {
        "organization_name": "Stripe",
        "documents": [
            {
                "filename": "stripe_playbook.txt",
                "text": (
                    "Stripe support handles billing, account, and API issues. Agents should search the knowledge base, "
                    "verify customer details, and escalate through support tickets."
                ),
            },
        ],
        "employees": [
            {
                "key": "support",
                "name": "Jordan",
                "role": "Customer Support Agent",
                "job_description": "Handle customer support issues across billing, technical, and account topics.",
            },
            {
                "key": "sales",
                "name": "Sam",
                "role": "Sales Development Rep (SDR)",
                "job_description": "Prospect new customers, send outreach emails, and add leads to CRM.",
            },
            {
                "key": "ops",
                "name": "Riley",
                "role": "Operations Manager",
                "job_description": "Manage operations, schedule meetings, and place equipment orders.",
            },
        ],
        "users": [
            {"user_id": "emma", "name": "Emma", "email": "emma@stripe.com"},
        ],
        "assignments": {
            "emma": ["support", "sales", "ops"],
        },
    },
    {
        "organization_name": "TechVentus",
        "documents": [
            {
                "filename": "techventus_guide.txt",
                "text": (
                    "TechVentus runs field operations for tech startups. Agents coordinate customer support, "
                    "sales outreach, and operational scheduling."
                ),
            },
        ],
        "employees": [
            {
                "key": "support",
                "name": "Maya",
                "role": "Customer Support Agent",
                "job_description": "Handle customer service issues and create support tickets for escalations.",
            },
            {
                "key": "sales",
                "name": "Alex",
                "role": "Sales Development Rep (SDR)",
                "job_description": "Prospect and outreach, manage leads, and schedule customer calls.",
            },
            {
                "key": "ops",
                "name": "Quinn",
                "role": "Operations Manager",
                "job_description": "Schedule meetings, coordinate operations, and manage equipment.",
            },
        ],
        "users": [
            {"user_id": "sarah", "name": "Sarah", "email": "sarah@techventus.com"},
        ],
        "assignments": {
            "sarah": ["support", "sales", "ops"],
        },
    },
]


def run():
    """Seed the RBAC demo organizations."""
    log.info("Starting RBAC demo setup")
    summary = {"organizations": [], "count": 0}

    for company in COMPANIES:
        company_summary = _seed_company(company)
        summary["organizations"].append(company_summary)

    summary["count"] = len(summary["organizations"])
    log.info("RBAC demo setup complete")
    return summary


if __name__ == "__main__":
    run()
