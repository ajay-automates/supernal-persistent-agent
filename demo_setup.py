"""
RBAC-aware demo data seeder.

Creates six organizations with AI employees tied to the RBAC role catalog,
shared knowledge-base documents, organization tool registrations, and
user-to-agent assignments.
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
                "filename": "amazon_sales_playbook.txt",
                "text": (
                    "Amazon runs outbound sales with a strong emphasis on research, CRM hygiene, "
                    "and fast meeting booking. SDRs should personalize outreach, log every lead, "
                    "and schedule discovery calls with decision-makers."
                ),
            },
            {
                "filename": "amazon_ops_notes.txt",
                "text": (
                    "Operations teams coordinate schedules, deliveries, and vendor updates. "
                    "When work changes, update the internal systems and send concise team notifications."
                ),
            },
        ],
        "employees": [
            {
                "key": "sales",
                "name": "Alex (Sales Bot)",
                "role": "Sales Development Rep (SDR)",
                "job_description": "Research prospects, send personalized outreach, update CRM, and schedule discovery calls.",
            },
            {
                "key": "support",
                "name": "Maya (Support Bot)",
                "role": "Customer Support Agent",
                "job_description": "Resolve customer issues, search help content, verify account status, and create support tickets.",
            },
            {
                "key": "content",
                "name": "David (Content Bot)",
                "role": "Content Creator",
                "job_description": "Write blog posts, create campaign content, and manage the content calendar.",
            },
            {
                "key": "ops",
                "name": "Quinn (Ops Bot)",
                "role": "Operations Coordinator",
                "job_description": "Coordinate deliveries, update operational records, and notify vendors.",
            },
        ],
        "users": [
            {"user_id": "ajay", "name": "Ajay", "email": "ajay@amazon.com"},
            {"user_id": "naveen", "name": "Naveen", "email": "naveen@amazon.com"},
            {"user_id": "dexter", "name": "Dexter", "email": "dexter@amazon.com"},
        ],
        "assignments": {
            "ajay": ["sales", "ops"],
            "naveen": ["support", "ops"],
            "dexter": ["sales", "support", "content", "ops"],
        },
    },
    {
        "organization_name": "Stripe",
        "documents": [
            {
                "filename": "stripe_support_playbook.txt",
                "text": (
                    "Stripe support handles billing, account, fraud, and API issues. Agents should "
                    "search the knowledge base first, verify customer details, and escalate through support tickets."
                ),
            },
        ],
        "employees": [
            {
                "key": "support",
                "name": "Jordan (Support Bot)",
                "role": "Customer Support Agent",
                "job_description": "Handle customer support issues across billing, technical, and account topics.",
            },
            {
                "key": "claims",
                "name": "Sam (Claims Bot)",
                "role": "Insurance Claims Processor",
                "job_description": "Process fraud and dispute-related claims, verify coverage, and route cases.",
            },
            {
                "key": "finance",
                "name": "Riley (Finance Bot)",
                "role": "Finance Coordinator",
                "job_description": "Reconcile transactions, generate reports, and manage invoices.",
            },
            {
                "key": "social",
                "name": "Casey (Social Bot)",
                "role": "Social Media Manager",
                "job_description": "Create social media content, maintain brand voice, and analyze engagement.",
            },
        ],
        "users": [
            {"user_id": "emma", "name": "Emma", "email": "emma@stripe.com"},
            {"user_id": "james", "name": "James", "email": "james@stripe.com"},
        ],
        "assignments": {
            "emma": ["support", "finance"],
            "james": ["claims", "social", "support"],
        },
    },
    {
        "organization_name": "TechVentus",
        "documents": [
            {
                "filename": "techventus_dispatch_guide.txt",
                "text": (
                    "TechVentus runs field operations for HVAC and plumbing jobs. Dispatchers coordinate technicians, "
                    "schedulers manage appointment changes, and operations tracks inventory and vendor updates."
                ),
            },
        ],
        "employees": [
            {
                "key": "dispatch",
                "name": "Quinn (Dispatch Bot)",
                "role": "Dispatch Manager",
                "job_description": "Dispatch technicians, optimize routes, and manage job schedules.",
            },
            {
                "key": "scheduler",
                "name": "Riley (Scheduler Bot)",
                "role": "Customer Scheduler",
                "job_description": "Answer scheduling questions, book appointments, and handle reschedules.",
            },
            {
                "key": "ops",
                "name": "Jordan (Ops Bot)",
                "role": "Operations Coordinator",
                "job_description": "Manage inventory, coordinate vendors, and update operational records.",
            },
            {
                "key": "support",
                "name": "Maya (Support Bot)",
                "role": "Customer Support Agent",
                "job_description": "Handle service issues and create support tickets for escalations.",
            },
        ],
        "users": [
            {"user_id": "michael", "name": "Michael", "email": "michael@techventus.com"},
            {"user_id": "sarah", "name": "Sarah", "email": "sarah@techventus.com"},
        ],
        "assignments": {
            "michael": ["dispatch", "ops"],
            "sarah": ["scheduler", "support"],
        },
    },
    {
        "organization_name": "InsureAll Inc",
        "documents": [
            {
                "filename": "insurance_claims_handbook.txt",
                "text": (
                    "Insurance claims should be verified against policy coverage, checked for fraud indicators, "
                    "and routed quickly to adjusters when human review is required."
                ),
            },
        ],
        "employees": [
            {
                "key": "claims",
                "name": "Sam (Claims Bot)",
                "role": "Insurance Claims Processor",
                "job_description": "Process claims, verify coverage, detect fraud, and route cases.",
            },
            {
                "key": "underwriter",
                "name": "Alex (Underwriting Bot)",
                "role": "Insurance Underwriter Assistant",
                "job_description": "Assess risk, analyze coverage, create quotes, and flag edge cases.",
            },
            {
                "key": "support",
                "name": "Jordan (Support Bot)",
                "role": "Customer Support Agent",
                "job_description": "Handle policy questions, account updates, and support escalations.",
            },
            {
                "key": "finance",
                "name": "Riley (Finance Bot)",
                "role": "Finance Coordinator",
                "job_description": "Manage premium records, reconcile payments, and generate reports.",
            },
        ],
        "users": [
            {"user_id": "chris", "name": "Chris", "email": "chris@insureall.com"},
            {"user_id": "pat", "name": "Pat", "email": "pat@insureall.com"},
        ],
        "assignments": {
            "chris": ["claims", "underwriter"],
            "pat": ["support", "finance"],
        },
    },
    {
        "organization_name": "CreativeWorks Agency",
        "documents": [
            {
                "filename": "agency_content_guide.txt",
                "text": (
                    "CreativeWorks produces branded content, ad copy, and social campaigns. "
                    "Social managers publish and analyze posts while content creators build the written assets."
                ),
            },
        ],
        "employees": [
            {
                "key": "social",
                "name": "Casey (Social Bot)",
                "role": "Social Media Manager",
                "job_description": "Create, schedule, and analyze social posts in the agency's brand voice.",
            },
            {
                "key": "content",
                "name": "David (Content Bot)",
                "role": "Content Creator",
                "job_description": "Write blog posts, create ad copy, and manage the content calendar.",
            },
            {
                "key": "sales",
                "name": "Alex (Sales Bot)",
                "role": "Sales Development Rep (SDR)",
                "job_description": "Prospect new clients, send outreach, and schedule intro calls.",
            },
            {
                "key": "ops",
                "name": "Quinn (Ops Bot)",
                "role": "Operations Coordinator",
                "job_description": "Manage project schedules, deliverables, and vendor communication.",
            },
        ],
        "users": [
            {"user_id": "lisa", "name": "Lisa", "email": "lisa@creativeworks.com"},
            {"user_id": "tom", "name": "Tom", "email": "tom@creativeworks.com"},
        ],
        "assignments": {
            "lisa": ["social", "content"],
            "tom": ["sales", "ops"],
        },
    },
    {
        "organization_name": "TalentMatch Inc",
        "documents": [
            {
                "filename": "recruiting_workflow.txt",
                "text": (
                    "Recruiters screen applicants, source candidates, and schedule interviews. "
                    "Onboarding specialists collect documents, schedule training, and provision access for new hires."
                ),
            },
        ],
        "employees": [
            {
                "key": "recruiter",
                "name": "Alex (Recruiter Bot)",
                "role": "Recruiter",
                "job_description": "Screen candidates, schedule interviews, source talent, and track the pipeline.",
            },
            {
                "key": "onboarding",
                "name": "Maya (Onboarding Bot)",
                "role": "Onboarding Specialist",
                "job_description": "Collect documents, schedule training, provision access, and manage onboarding plans.",
            },
            {
                "key": "sales",
                "name": "David (Sales Bot)",
                "role": "Sales Development Rep (SDR)",
                "job_description": "Prospect clients, send outreach, and book discovery calls.",
            },
            {
                "key": "content",
                "name": "Casey (Content Bot)",
                "role": "Content Creator",
                "job_description": "Write job descriptions, recruiting copy, and employer-brand content.",
            },
        ],
        "users": [
            {"user_id": "robert", "name": "Robert", "email": "robert@talentmatch.com"},
            {"user_id": "susan", "name": "Susan", "email": "susan@talentmatch.com"},
        ],
        "assignments": {
            "robert": ["recruiter", "onboarding"],
            "susan": ["sales", "content"],
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
