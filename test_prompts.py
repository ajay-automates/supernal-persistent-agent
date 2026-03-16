"""
Test script to validate all prompts work with all agents in all organizations.
This script tests each agent with their generated prompts to ensure they work correctly.
"""

import json
import asyncio
from config import supabase, OPENAI_API_KEY
from agent import answer_question_with_tools
from db import (
    list_organizations,
    get_ai_employees,
    get_org_users,
)

# Test prompts for each role
ROLE_PROMPTS = {
    "sales development rep": [
        "Send a personalized outreach email to a prospect about our solution",
        "Add a new high-value prospect to our CRM",
        "Schedule a discovery call with the prospect for next week",
    ],
    "customer support agent": [
        "Create a high-priority support ticket for this customer issue",
        "Send a response email to the customer with a solution",
    ],
    "operations manager": [
        "Schedule a team standup meeting for tomorrow morning",
        "Order new laptops for our incoming team members",
    ],
}


def normalize_role(role_name: str) -> str:
    """Normalize role name for matching."""
    return role_name.lower() if role_name else ""


def get_prompts_for_role(role_name: str) -> list:
    """Get test prompts for a role."""
    normalized = normalize_role(role_name)
    for key, prompts in ROLE_PROMPTS.items():
        if key in normalized:
            return prompts
    return ["What can you help me with?"]


async def test_agent_with_prompts(org_name: str, agent: dict, user_id: str):
    """Test an agent with their relevant prompts."""
    role_name = agent.get("role_details", {}).get("role_name") or agent.get("role", "")
    agent_name = agent.get("name", "Unknown")
    agent_id = agent.get("id")

    # Get organization ID
    orgs = list_organizations()
    org_id = None
    for org in orgs:
        if org["name"] == org_name:
            org_id = org["id"]
            break

    if not org_id:
        print(f"  ✗ Organization {org_name} not found")
        return False

    prompts = get_prompts_for_role(role_name)
    print(f"\n  {agent_name} ({role_name})")
    print(f"  Tools: {', '.join(agent.get('allowed_tools', []))}")
    print(f"  Prompts to test:")

    all_passed = True
    for i, prompt in enumerate(prompts, 1):
        try:
            print(f"    [{i}] Testing: {prompt[:60]}...")
            result = answer_question_with_tools(
                organization_id=org_id,
                ai_employee_id=agent_id,
                user_id=user_id,
                question=prompt
            )

            if result.get("error"):
                print(f"        ✗ Error: {result['error']}")
                all_passed = False
            elif result.get("answer"):
                # Check if answer is reasonable (not empty, not just error)
                answer_len = len(result.get("answer", ""))
                if answer_len > 0:
                    print(f"        ✓ Success ({answer_len} chars, tool_used={result.get('tool_used')})")
                else:
                    print(f"        ✗ Empty answer")
                    all_passed = False
            else:
                print(f"        ✗ No answer returned")
                all_passed = False
        except Exception as e:
            print(f"        ✗ Exception: {str(e)[:100]}")
            all_passed = False

    return all_passed


async def test_all_organizations():
    """Test all organizations and their agents."""
    print("\n" + "=" * 70)
    print("PROMPT TESTING FOR ALL AGENTS")
    print("=" * 70)

    organizations = list_organizations()
    print(f"\nFound {len(organizations)} organizations")

    summary = {
        "total_orgs": len(organizations),
        "orgs_tested": 0,
        "agents_tested": 0,
        "agents_passed": 0,
        "details": []
    }

    for org in organizations:
        org_name = org.get("name", "Unknown")
        org_id = org.get("id")

        print(f"\n📦 {org_name}")
        print("-" * 70)

        # Get agents for this org
        agents = get_ai_employees(org_id)
        if not agents:
            print("  No agents found")
            continue

        # Get users for this org
        users = get_org_users(org_id)
        if not users:
            print("  No users found")
            continue

        user_id = users[0].get("user_id", "")
        if not user_id:
            print("  No valid user ID found")
            continue

        print(f"  Testing with user: {user_id}")

        org_passed = 0
        org_total = len(agents)

        for agent in agents:
            try:
                passed = await test_agent_with_prompts(org_name, agent, user_id)
                if passed:
                    org_passed += 1
                summary["agents_tested"] += 1
            except Exception as e:
                print(f"  ✗ Error testing agent: {str(e)[:100]}")
                summary["agents_tested"] += 1

        summary["orgs_tested"] += 1
        summary["agents_passed"] += org_passed
        summary["details"].append({
            "org": org_name,
            "agents_tested": org_total,
            "agents_passed": org_passed,
        })

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Organizations tested: {summary['orgs_tested']}/{summary['total_orgs']}")
    print(f"Agents tested: {summary['agents_tested']}")
    print(f"Agents passed: {summary['agents_passed']}")
    print(f"Pass rate: {(summary['agents_passed'] / summary['agents_tested'] * 100 if summary['agents_tested'] > 0 else 0):.0f}%")

    for detail in summary["details"]:
        pass_rate = (detail["agents_passed"] / detail["agents_tested"] * 100
                    if detail["agents_tested"] > 0 else 0)
        print(f"  {detail['org']}: {detail['agents_passed']}/{detail['agents_tested']} ({pass_rate:.0f}%)")

    return summary


if __name__ == "__main__":
    print("\n🧪 Starting comprehensive prompt testing...\n")
    summary = asyncio.run(test_all_organizations())
    print(f"\n✅ Testing complete!\n")
