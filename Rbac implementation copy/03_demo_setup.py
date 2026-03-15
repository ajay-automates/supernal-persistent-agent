"""
DEMO SETUP FOR SUPERNAL'S AI EMPLOYEES
Creates demo data with all 12 Supernal AI employees and realistic company scenarios.
"""

from datetime import datetime

# ============================================================================
# DEMO DATA SETUP
# ============================================================================

def setup_supernal_demo_companies(supabase_client):
    """
    Set up complete demo with:
    - 12 Supernal AI Employees (all actual roles)
    - 6 Demo Companies (realistic scenarios)
    - User assignments
    - Tool permissions
    """
    
    db = supabase_client
    
    print("🚀 Setting up Supernal demo companies...")
    
    # ========================================================================
    # COMPANY 1: AMAZON (B2B SaaS - Sales Focus)
    # ========================================================================
    
    print("\n📌 Setting up Amazon...")
    
    amazon_config = {
        'organization_id': 'amazon',
        'organization_name': 'Amazon',
        'industry': 'SaaS',
        'employees': [
            {
                'ai_employee_id': 'amazon_sales_rep',
                'name': 'Sales SDR - Alex',
                'role': 'Sales Development Rep (SDR)',
                'nickname': 'Alex',
                'job_description': 'Research prospects, write personalized emails, add to Salesforce CRM, schedule discovery calls',
                'documents': [
                    'AWS Product Overview',
                    'Sales Process Documentation',
                    'Customer Success Case Studies'
                ]
            },
            {
                'ai_employee_id': 'amazon_support',
                'name': 'Customer Support - Maya',
                'role': 'Customer Support Agent',
                'nickname': 'Maya',
                'job_description': 'Handle technical support tickets, answer customer questions, escalate to engineers',
                'documents': [
                    'AWS Support Knowledge Base',
                    'Troubleshooting Guide',
                    'API Documentation'
                ]
            },
            {
                'ai_employee_id': 'amazon_content',
                'name': 'Content Creator - David',
                'role': 'Content Creator',
                'nickname': 'David',
                'job_description': 'Write blog posts, create marketing content, manage content calendar',
                'documents': [
                    'Content Style Guide',
                    'Brand Guidelines',
                    'Marketing Calendar Template'
                ]
            },
            {
                'ai_employee_id': 'amazon_ops',
                'name': 'Operations Coordinator - Quinn',
                'role': 'Operations Coordinator',
                'nickname': 'Quinn',
                'job_description': 'Manage schedules, coordinate deliveries, optimize resources',
                'documents': [
                    'Operations Manual',
                    'Delivery Schedule Template',
                    'Resource Allocation Guide'
                ]
            }
        ],
        'users': ['Ajay', 'Naveen', 'Dexter'],
        'user_assignments': {
            'Ajay': ['amazon_sales_rep', 'amazon_ops'],  # Sales team + Ops
            'Naveen': ['amazon_support', 'amazon_ops'],  # Support team + Ops
            'Dexter': ['amazon_sales_rep', 'amazon_support', 'amazon_content', 'amazon_ops']  # Leadership - all access
        }
    }
    
    create_company_demo(db, amazon_config)
    
    # ========================================================================
    # COMPANY 2: STRIPE (FinTech - Payment Processing)
    # ========================================================================
    
    print("\n📌 Setting up Stripe...")
    
    stripe_config = {
        'organization_id': 'stripe',
        'organization_name': 'Stripe',
        'industry': 'FinTech',
        'employees': [
            {
                'ai_employee_id': 'stripe_support',
                'name': 'Support Agent - Jordan',
                'role': 'Customer Support Agent',
                'nickname': 'Jordan',
                'job_description': '24/7 customer support for payment issues, API integration, account setup',
                'documents': [
                    'Stripe API Documentation',
                    'Common Issues & Solutions',
                    'Payment Processing Guide'
                ]
            },
            {
                'ai_employee_id': 'stripe_claims',
                'name': 'Claims Processor - Sam',
                'role': 'Insurance Claims Processor',
                'nickname': 'Sam',
                'job_description': 'Handle fraud claims, chargeback processing, dispute resolution',
                'documents': [
                    'Chargeback Process Guide',
                    'Fraud Detection Rules',
                    'Dispute Resolution Handbook'
                ]
            },
            {
                'ai_employee_id': 'stripe_finance',
                'name': 'Finance Coordinator - Riley',
                'role': 'Finance Coordinator',
                'nickname': 'Riley',
                'job_description': 'Reconcile transactions, generate financial reports, manage invoices',
                'documents': [
                    'Accounting Procedures',
                    'Financial Reporting Standards',
                    'Invoice Template'
                ]
            },
            {
                'ai_employee_id': 'stripe_marketing',
                'name': 'Social Media Manager - Casey',
                'role': 'Social Media Manager',
                'nickname': 'Casey',
                'job_description': 'Create social media content, manage brand presence, engage community',
                'documents': [
                    'Social Media Strategy',
                    'Brand Voice Guidelines',
                    'Content Calendar'
                ]
            }
        ],
        'users': ['Emma', 'James'],
        'user_assignments': {
            'Emma': ['stripe_support', 'stripe_finance'],
            'James': ['stripe_claims', 'stripe_marketing', 'stripe_support']
        }
    }
    
    create_company_demo(db, stripe_config)
    
    # ========================================================================
    # COMPANY 3: TECHVENTUS (HVAC/Plumbing Service Company)
    # ========================================================================
    
    print("\n📌 Setting up TechVentus...")
    
    techventus_config = {
        'organization_id': 'techventus',
        'organization_name': 'TechVentus',
        'industry': 'HVAC/Plumbing Services',
        'employees': [
            {
                'ai_employee_id': 'techventus_dispatch',
                'name': 'Dispatch Manager - Quinn',
                'role': 'Dispatch Manager',
                'nickname': 'Quinn',
                'job_description': 'Dispatch technicians, optimize routes, manage job schedules',
                'documents': [
                    'Dispatch Protocol',
                    'Service Territory Map',
                    'Technician Schedule Template'
                ]
            },
            {
                'ai_employee_id': 'techventus_scheduler',
                'name': 'Customer Scheduler - Riley',
                'role': 'Customer Scheduler',
                'nickname': 'Riley',
                'job_description': 'Answer customer calls, book appointments, manage availability',
                'documents': [
                    'Customer Service Script',
                    'Appointment Booking System',
                    'Service Available Hours'
                ]
            },
            {
                'ai_employee_id': 'techventus_ops',
                'name': 'Operations Coordinator - Jordan',
                'role': 'Operations Coordinator',
                'nickname': 'Jordan',
                'job_description': 'Manage inventory, coordinate with vendors, track parts',
                'documents': [
                    'Inventory Management Guide',
                    'Vendor Contact List',
                    'Parts Catalog'
                ]
            },
            {
                'ai_employee_id': 'techventus_support',
                'name': 'Customer Support - Maya',
                'role': 'Customer Support Agent',
                'nickname': 'Maya',
                'job_description': 'Handle service calls, troubleshoot issues, manage callbacks',
                'documents': [
                    'Troubleshooting Guide',
                    'HVAC Service Standards',
                    'Warranty Information'
                ]
            }
        ],
        'users': ['Michael', 'Sarah'],
        'user_assignments': {
            'Michael': ['techventus_dispatch', 'techventus_ops'],
            'Sarah': ['techventus_scheduler', 'techventus_support']
        }
    }
    
    create_company_demo(db, techventus_config)
    
    # ========================================================================
    # COMPANY 4: INSURANCE COMPANY (Insurance Processing)
    # ========================================================================
    
    print("\n📌 Setting up Insurance Company...")
    
    insurance_config = {
        'organization_id': 'insurance_co',
        'organization_name': 'InsureAll Inc',
        'industry': 'Insurance',
        'employees': [
            {
                'ai_employee_id': 'insurance_claims',
                'name': 'Claims Processor - Sam',
                'role': 'Insurance Claims Processor',
                'nickname': 'Sam',
                'job_description': 'Process claims, verify coverage, detect fraud, generate quotes',
                'documents': [
                    'Claims Processing Manual',
                    'Policy Templates',
                    'Coverage Guidelines'
                ]
            },
            {
                'ai_employee_id': 'insurance_underwriter',
                'name': 'Underwriter Assistant - Alex',
                'role': 'Insurance Underwriter Assistant',
                'nickname': 'Alex',
                'job_description': 'Assess risk, create quotes, analyze coverage, flag edge cases',
                'documents': [
                    'Underwriting Guidelines',
                    'Risk Assessment Matrix',
                    'Quote Templates'
                ]
            },
            {
                'ai_employee_id': 'insurance_support',
                'name': 'Customer Support - Jordan',
                'role': 'Customer Support Agent',
                'nickname': 'Jordan',
                'job_description': 'Handle customer inquiries, policy questions, update info',
                'documents': [
                    'Policy Information Guide',
                    'FAQ Database',
                    'Contact Procedures'
                ]
            },
            {
                'ai_employee_id': 'insurance_finance',
                'name': 'Finance Coordinator - Riley',
                'role': 'Finance Coordinator',
                'nickname': 'Riley',
                'job_description': 'Manage premiums, reconcile payments, generate reports',
                'documents': [
                    'Premium Management Guide',
                    'Payment Processing Procedures',
                    'Financial Reporting Format'
                ]
            }
        ],
        'users': ['Chris', 'Pat'],
        'user_assignments': {
            'Chris': ['insurance_claims', 'insurance_underwriter'],
            'Pat': ['insurance_support', 'insurance_finance']
        }
    }
    
    create_company_demo(db, insurance_config)
    
    # ========================================================================
    # COMPANY 5: MARKETING AGENCY
    # ========================================================================
    
    print("\n📌 Setting up Marketing Agency...")
    
    marketing_config = {
        'organization_id': 'marketing_agency',
        'organization_name': 'CreativeWorks Agency',
        'industry': 'Marketing',
        'employees': [
            {
                'ai_employee_id': 'agency_social',
                'name': 'Social Media Manager - Casey',
                'role': 'Social Media Manager',
                'nickname': 'Casey',
                'job_description': 'Create social posts, manage brand voice, schedule content',
                'documents': [
                    'Social Strategy Guidelines',
                    'Brand Voice Documents',
                    'Posting Schedule'
                ]
            },
            {
                'ai_employee_id': 'agency_content',
                'name': 'Content Creator - David',
                'role': 'Content Creator',
                'nickname': 'David',
                'job_description': 'Write blog posts, create ad copy, manage content calendar',
                'documents': [
                    'Content Style Guide',
                    'SEO Guidelines',
                    'Content Calendar'
                ]
            },
            {
                'ai_employee_id': 'agency_sales',
                'name': 'Sales SDR - Alex',
                'role': 'Sales Development Rep (SDR)',
                'nickname': 'Alex',
                'job_description': 'Prospect new clients, write proposals, schedule pitches',
                'documents': [
                    'Sales Pitch Template',
                    'Client Target List',
                    'Proposal Framework'
                ]
            },
            {
                'ai_employee_id': 'agency_ops',
                'name': 'Operations Coordinator - Quinn',
                'role': 'Operations Coordinator',
                'nickname': 'Quinn',
                'job_description': 'Manage projects, schedule deliverables, track timelines',
                'documents': [
                    'Project Management Guide',
                    'Delivery Checklist',
                    'Timeline Template'
                ]
            }
        ],
        'users': ['Lisa', 'Tom'],
        'user_assignments': {
            'Lisa': ['agency_social', 'agency_content'],
            'Tom': ['agency_sales', 'agency_ops']
        }
    }
    
    create_company_demo(db, marketing_config)
    
    # ========================================================================
    # COMPANY 6: RECRUITING FIRM
    # ========================================================================
    
    print("\n📌 Setting up Recruiting Firm...")
    
    recruiting_config = {
        'organization_id': 'recruiting_firm',
        'organization_name': 'TalentMatch Inc',
        'industry': 'Recruiting',
        'employees': [
            {
                'ai_employee_id': 'recruit_recruiter',
                'name': 'Recruiter - Alex',
                'role': 'Recruiter',
                'nickname': 'Alex',
                'job_description': 'Screen candidates, schedule interviews, source talent',
                'documents': [
                    'Recruiting Process',
                    'Candidate Screening Rubric',
                    'Interview Questions'
                ]
            },
            {
                'ai_employee_id': 'recruit_onboarding',
                'name': 'Onboarding Specialist - Maya',
                'role': 'Onboarding Specialist',
                'nickname': 'Maya',
                'job_description': 'Collect documents, schedule training, setup access',
                'documents': [
                    'Onboarding Checklist',
                    'Training Schedule',
                    'Access Setup Guide'
                ]
            },
            {
                'ai_employee_id': 'recruit_sales',
                'name': 'Sales Development Rep - David',
                'role': 'Sales Development Rep (SDR)',
                'nickname': 'David',
                'job_description': 'Prospect clients, send proposals, book discovery calls',
                'documents': [
                    'Service Overview',
                    'Client Pitch Deck',
                    'Proposal Template'
                ]
            },
            {
                'ai_employee_id': 'recruit_content',
                'name': 'Content Creator - Casey',
                'role': 'Content Creator',
                'nickname': 'Casey',
                'job_description': 'Write job descriptions, create marketing content',
                'documents': [
                    'Job Description Templates',
                    'Marketing Copy Templates',
                    'Content Guidelines'
                ]
            }
        ],
        'users': ['Robert', 'Susan'],
        'user_assignments': {
            'Robert': ['recruit_recruiter', 'recruit_onboarding'],
            'Susan': ['recruit_sales', 'recruit_content']
        }
    }
    
    create_company_demo(db, recruiting_config)
    
    print("\n✅ Demo setup complete!")


# ============================================================================
# HELPER FUNCTION TO CREATE COMPANY DEMO
# ============================================================================

def create_company_demo(db, config: dict):
    """Create a company with all its AI employees and user assignments"""
    
    org_id = config['organization_id']
    
    print(f"  Setting up {config['organization_name']}...")
    
    # Create organization
    try:
        db.table('organizations').insert({
            'organization_id': org_id,
            'organization_name': config['organization_name'],
            'industry': config.get('industry', ''),
            'created_at': datetime.utcnow().isoformat()
        }).execute()
        print(f"    ✓ Created organization")
    except Exception as e:
        print(f"    ℹ Organization may already exist: {e}")
    
    # Create users
    for user_name in config['users']:
        try:
            db.table('users').insert({
                'organization_id': org_id,
                'user_id': user_name,
                'user_name': user_name,
                'created_at': datetime.utcnow().isoformat()
            }).execute()
            print(f"    ✓ Created user: {user_name}")
        except Exception as e:
            print(f"    ℹ User may already exist: {user_name}")
    
    # Create AI employees with roles
    for employee in config['employees']:
        try:
            # Get role ID
            role_result = db.table('ai_employee_roles').select('id').eq(
                'role_name', employee['role']
            ).single().execute()
            
            role_id = role_result.data['id'] if role_result.data else None
            
            # Create AI employee
            db.table('ai_employees').insert({
                'organization_id': org_id,
                'ai_employee_id': employee['ai_employee_id'],
                'name': employee['name'],
                'nickname': employee.get('nickname', employee['name']),
                'role_id': role_id,
                'job_description': employee['job_description'],
                'created_at': datetime.utcnow().isoformat()
            }).execute()
            
            print(f"    ✓ Created AI employee: {employee['name']}")
            
        except Exception as e:
            print(f"    ⚠ Error creating employee {employee['name']}: {e}")
    
    # Create user-to-agent assignments
    for user_id, assigned_agents in config['user_assignments'].items():
        for agent_id in assigned_agents:
            try:
                db.table('user_ai_employee_assignments').insert({
                    'organization_id': org_id,
                    'user_id': user_id,
                    'ai_employee_id': agent_id,
                    'assigned_at': datetime.utcnow().isoformat()
                }).execute()
                print(f"    ✓ Assigned {agent_id} to {user_id}")
            except Exception as e:
                print(f"    ⚠ Assignment error: {e}")


# ============================================================================
# CALL THIS ON APP STARTUP
# ============================================================================

"""
In your main.py:

from demo_setup import setup_supernal_demo_companies

@app.on_event("startup")
async def startup_event():
    # Setup demo companies on startup
    setup_supernal_demo_companies(supabase)
    print("Demo companies initialized")
"""

