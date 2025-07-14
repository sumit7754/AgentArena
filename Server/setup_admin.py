import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import get_db, init_db
from app.models.user import User
from app.models.task import Task
from app.models.enums import UserRole, TaskDifficulty
from app.services.auth_service import AuthService
from sqlalchemy.orm import Session
import json

def create_admin_account():
    """Create the admin account for sumit@gmail.com"""
    init_db(force_recreate=False)
    db = next(get_db())
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == "sumit@gmail.com").first()
        if existing_admin:
            print("Admin account already exists!")
            return existing_admin
        
        # Create admin account
        auth_service = AuthService(db)
        admin_data = {
            "email": "sumit@gmail.com",
            "password": "sumit@12345",
            "firstName": "Sumit",
            "lastName": "Admin",
            "role": UserRole.ADMIN
        }
        
        # Create the admin user directly
        admin_user = User(
            email=admin_data["email"],
            password=auth_service._get_hashed_password(admin_data["password"]),
            firstName=admin_data["firstName"],
            lastName=admin_data["lastName"],
            role=UserRole.ADMIN,
            isActive=True,
            isEmailVerified=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"✅ Admin account created successfully!")
        print(f"Email: {admin_user.email}")
        print(f"Role: {admin_user.role}")
        return admin_user
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin account: {str(e)}")
        return None
    finally:
        db.close()

def create_realevals_tasks():
    """Create comprehensive tasks similar to realevals.xyz"""
    db = next(get_db())
    
    try:
        # Get admin user
        admin_user = db.query(User).filter(User.email == "sumit@gmail.com").first()
        if not admin_user:
            print("❌ Admin user not found. Please create admin account first.")
            return
        
        # REAL-style tasks similar to realevals.xyz
        realevals_tasks = [
            {
                "title": "E-Commerce Product Search & Purchase",
                "description": "Navigate to an e-commerce site, search for a specific product, apply filters, read reviews, and complete a purchase workflow.",
                "difficulty": TaskDifficulty.EASY,
                "webArenaEnvironment": "omnizon",
                "webArenaTaskId": 1,
                "expectedCompletionTime": 180,
                "maxAllowedTime": 300,
                "environmentConfig": {
                    "instruction": "Find a wireless bluetooth headphone under $100, read at least 3 reviews, add to cart, and proceed to checkout",
                    "success_criteria": [
                        "Product search completed with correct filters",
                        "Reviews read and considered",
                        "Item added to cart with correct specifications",
                        "Checkout process initiated"
                    ],
                    "evaluation_points": {
                        "task_completion": 40,
                        "accuracy": 30,
                        "efficiency": 20,
                        "user_experience": 10
                    },
                    "website_type": "e_commerce",
                    "complexity": "multi_step"
                }
            },
            {
                "title": "Flight Booking with Complex Constraints",
                "description": "Book a flight with specific preferences including dates, times, seat selection, and special requirements.",
                "difficulty": TaskDifficulty.MEDIUM,
                "webArenaEnvironment": "fly_united",
                "webArenaTaskId": 2,
                "expectedCompletionTime": 240,
                "maxAllowedTime": 400,
                "environmentConfig": {
                    "instruction": "Book a round-trip flight from NYC to LAX, departing Dec 15th, returning Dec 22nd, prefer morning flights, select aisle seat",
                    "success_criteria": [
                        "Correct origin and destination selected",
                        "Accurate dates selected",
                        "Morning flight preferences applied",
                        "Seat selection completed",
                        "Booking confirmation received"
                    ],
                    "evaluation_points": {
                        "task_completion": 35,
                        "accuracy": 35,
                        "constraint_satisfaction": 20,
                        "efficiency": 10
                    },
                    "website_type": "travel_booking",
                    "complexity": "constraint_based"
                }
            },
            {
                "title": "Professional Email Campaign Management",
                "description": "Manage a complex email workflow including inbox organization, priority responses, and meeting scheduling.",
                "difficulty": TaskDifficulty.MEDIUM,
                "webArenaEnvironment": "gomail",
                "webArenaTaskId": 3,
                "expectedCompletionTime": 200,
                "maxAllowedTime": 350,
                "environmentConfig": {
                    "instruction": "Organize inbox by priority, respond to urgent emails from client 'TechCorp', schedule a follow-up meeting for next week, and create a project status email",
                    "success_criteria": [
                        "Inbox properly prioritized and organized",
                        "Urgent emails identified and responded to",
                        "Meeting scheduled with correct details",
                        "Professional communication maintained",
                        "Follow-up actions documented"
                    ],
                    "evaluation_points": {
                        "organization": 25,
                        "communication_quality": 25,
                        "task_completion": 25,
                        "professional_etiquette": 25
                    },
                    "website_type": "email_management",
                    "complexity": "workflow_based"
                }
            },
            {
                "title": "Accommodation Booking with Multiple Criteria",
                "description": "Find and book accommodation using complex search criteria including location, amenities, and reviews.",
                "difficulty": TaskDifficulty.MEDIUM,
                "webArenaEnvironment": "staynb",
                "webArenaTaskId": 4,
                "expectedCompletionTime": 220,
                "maxAllowedTime": 380,
                "environmentConfig": {
                    "instruction": "Find a pet-friendly accommodation in downtown San Francisco for 3 nights, check-in Jan 10th, with WiFi, kitchen, and rating above 4.5 stars",
                    "success_criteria": [
                        "Location criteria met (downtown SF)",
                        "Pet-friendly option selected",
                        "Correct dates and duration",
                        "All amenities verified (WiFi, kitchen)",
                        "Rating requirement satisfied",
                        "Booking process completed"
                    ],
                    "evaluation_points": {
                        "criteria_matching": 30,
                        "amenity_verification": 25,
                        "booking_accuracy": 25,
                        "efficiency": 20
                    },
                    "website_type": "accommodation_booking",
                    "complexity": "multi_criteria"
                }
            },
            {
                "title": "Food Delivery Multi-Restaurant Order",
                "description": "Navigate food delivery platform to create a complex order from multiple restaurants for a group.",
                "difficulty": TaskDifficulty.EASY,
                "webArenaEnvironment": "dashdish",
                "webArenaTaskId": 5,
                "expectedCompletionTime": 150,
                "maxAllowedTime": 250,
                "environmentConfig": {
                    "instruction": "Order dinner for 4 people: 2 pizzas from Mario's Pizza, 1 Thai curry from Bangkok Garden, and dessert from Sweet Treats. Deliver to office address.",
                    "success_criteria": [
                        "Items from correct restaurants",
                        "Accurate quantities ordered",
                        "Delivery address correctly specified",
                        "Order timing coordinated",
                        "Payment process completed"
                    ],
                    "evaluation_points": {
                        "order_accuracy": 40,
                        "restaurant_navigation": 25,
                        "logistics_management": 20,
                        "efficiency": 15
                    },
                    "website_type": "food_delivery",
                    "complexity": "multi_vendor"
                }
            },
            {
                "title": "Calendar Scheduling with Conflict Resolution",
                "description": "Manage complex calendar scheduling with multiple participants and conflict resolution.",
                "difficulty": TaskDifficulty.HARD,
                "webArenaEnvironment": "gocalendar",
                "webArenaTaskId": 6,
                "expectedCompletionTime": 300,
                "maxAllowedTime": 480,
                "environmentConfig": {
                    "instruction": "Schedule a 2-hour team meeting for next week, find time that works for all 5 participants, book conference room, send calendar invites with agenda",
                    "success_criteria": [
                        "All participant availability checked",
                        "Optimal time slot identified",
                        "Conference room successfully booked",
                        "Calendar invites sent to all participants",
                        "Meeting agenda included",
                        "No scheduling conflicts created"
                    ],
                    "evaluation_points": {
                        "conflict_resolution": 30,
                        "logistics_coordination": 25,
                        "communication": 25,
                        "efficiency": 20
                    },
                    "website_type": "calendar_management",
                    "complexity": "constraint_optimization"
                }
            },
            {
                "title": "Professional Network Expansion",
                "description": "Navigate professional networking platform to expand connections and engage with content strategically.",
                "difficulty": TaskDifficulty.MEDIUM,
                "webArenaEnvironment": "networkin",
                "webArenaTaskId": 7,
                "expectedCompletionTime": 180,
                "maxAllowedTime": 300,
                "environmentConfig": {
                    "instruction": "Connect with 3 AI researchers, like and comment on relevant posts, update profile with recent project, and post an industry insight",
                    "success_criteria": [
                        "Relevant connections identified and invited",
                        "Meaningful engagement with posts",
                        "Profile updated professionally",
                        "Quality industry insight shared",
                        "Network growth strategy demonstrated"
                    ],
                    "evaluation_points": {
                        "networking_strategy": 30,
                        "content_quality": 25,
                        "professional_presence": 25,
                        "engagement_effectiveness": 20
                    },
                    "website_type": "professional_networking",
                    "complexity": "social_strategy"
                }
            },
            {
                "title": "Ride-sharing with Multiple Stops",
                "description": "Book complex ride-sharing with multiple stops and specific requirements.",
                "difficulty": TaskDifficulty.EASY,
                "webArenaEnvironment": "udriver",
                "webArenaTaskId": 8,
                "expectedCompletionTime": 120,
                "maxAllowedTime": 200,
                "environmentConfig": {
                    "instruction": "Book a ride from airport to hotel with a stop at grocery store, specify car type for 3 passengers with luggage",
                    "success_criteria": [
                        "Pickup location correctly set (airport)",
                        "Multiple stops added (grocery store, hotel)",
                        "Appropriate car type selected",
                        "Passenger and luggage requirements specified",
                        "Booking confirmed with correct details"
                    ],
                    "evaluation_points": {
                        "route_planning": 35,
                        "requirements_specification": 30,
                        "booking_accuracy": 25,
                        "efficiency": 10
                    },
                    "website_type": "transportation",
                    "complexity": "multi_stop"
                }
            },
            {
                "title": "Freelance Project Bidding Strategy",
                "description": "Navigate freelance platform to find, analyze, and bid on projects strategically.",
                "difficulty": TaskDifficulty.HARD,
                "webArenaEnvironment": "topwork",
                "webArenaTaskId": 9,
                "expectedCompletionTime": 280,
                "maxAllowedTime": 450,
                "environmentConfig": {
                    "instruction": "Find 3 AI/ML projects within budget range $1000-$5000, analyze client requirements, write compelling proposals, and submit competitive bids",
                    "success_criteria": [
                        "Relevant projects identified within budget",
                        "Client requirements thoroughly analyzed",
                        "Compelling proposals written",
                        "Competitive pricing strategy applied",
                        "Professional communication maintained",
                        "Bids submitted successfully"
                    ],
                    "evaluation_points": {
                        "project_analysis": 25,
                        "proposal_quality": 25,
                        "competitive_strategy": 25,
                        "communication_skills": 25
                    },
                    "website_type": "freelance_marketplace",
                    "complexity": "strategic_bidding"
                }
            },
            {
                "title": "Restaurant Reservation with Special Requirements",
                "description": "Make restaurant reservations considering dietary restrictions, group size, and special occasions.",
                "difficulty": TaskDifficulty.MEDIUM,
                "webArenaEnvironment": "opendining",
                "webArenaTaskId": 10,
                "expectedCompletionTime": 160,
                "maxAllowedTime": 280,
                "environmentConfig": {
                    "instruction": "Book dinner for 6 people at a high-rated Italian restaurant for anniversary celebration, mention dietary restrictions (vegetarian, gluten-free), request window table",
                    "success_criteria": [
                        "Appropriate restaurant type selected (Italian)",
                        "Correct party size specified (6 people)",
                        "Special occasion noted (anniversary)",
                        "Dietary restrictions communicated",
                        "Special seating request made",
                        "Reservation confirmed"
                    ],
                    "evaluation_points": {
                        "requirement_specification": 30,
                        "restaurant_selection": 25,
                        "special_requests_handling": 25,
                        "booking_completion": 20
                    },
                    "website_type": "restaurant_booking",
                    "complexity": "requirement_based"
                }
            },
            {
                "title": "Real Estate Market Analysis",
                "description": "Conduct comprehensive real estate analysis with specific criteria and market research.",
                "difficulty": TaskDifficulty.HARD,
                "webArenaEnvironment": "zilloft",
                "webArenaTaskId": 11,
                "expectedCompletionTime": 320,
                "maxAllowedTime": 500,
                "environmentConfig": {
                    "instruction": "Find 5 properties in Austin TX under $800K, analyze market trends, compare school ratings, calculate commute times to tech district, create comparison report",
                    "success_criteria": [
                        "Properties found within location and budget",
                        "Market trend analysis completed",
                        "School ratings researched and compared",
                        "Commute times calculated accurately",
                        "Comprehensive comparison report created",
                        "Investment potential assessed"
                    ],
                    "evaluation_points": {
                        "market_research": 25,
                        "criteria_analysis": 25,
                        "data_comparison": 25,
                        "report_quality": 25
                    },
                    "website_type": "real_estate",
                    "complexity": "analytical_research"
                }
            },
            {
                "title": "Complex Web Data Extraction",
                "description": "Extract and analyze data from multiple web sources with structured output requirements.",
                "difficulty": TaskDifficulty.HARD,
                "webArenaEnvironment": "web_browsing",
                "webArenaTaskId": 12,
                "expectedCompletionTime": 280,
                "maxAllowedTime": 420,
                "environmentConfig": {
                    "instruction": "Research the top 10 AI companies by funding in 2024, extract their funding amounts, founding years, and primary focus areas. Create a structured comparison table.",
                    "success_criteria": [
                        "Top 10 AI companies identified accurately",
                        "Funding data extracted and verified",
                        "Company details researched thoroughly",
                        "Data structured in comparison format",
                        "Information accuracy verified",
                        "Professional presentation format"
                    ],
                    "evaluation_points": {
                        "research_accuracy": 30,
                        "data_extraction": 25,
                        "information_verification": 25,
                        "presentation_quality": 20
                    },
                    "website_type": "research_analysis",
                    "complexity": "data_intensive"
                }
            }
        ]
        
        created_tasks = []
        for task_data in realevals_tasks:
            # Check if task already exists
            existing_task = db.query(Task).filter(Task.title == task_data["title"]).first()
            if existing_task:
                print(f"⚠️ Task '{task_data['title']}' already exists, skipping...")
                continue
            
            # Create new task
            new_task = Task(
                title=task_data["title"],
                description=task_data["description"],
                difficulty=task_data["difficulty"],
                webArenaEnvironment=task_data["webArenaEnvironment"],
                webArenaTaskId=task_data["webArenaTaskId"],
                expectedCompletionTime=task_data["expectedCompletionTime"],
                maxAllowedTime=task_data["maxAllowedTime"],
                environmentConfig=task_data["environmentConfig"],
                createdBy=admin_user.id
            )
            
            db.add(new_task)
            created_tasks.append(new_task)
        
        db.commit()
        
        print(f"✅ Created {len(created_tasks)} new REAL-style tasks!")
        for task in created_tasks:
            print(f"  - {task.title} ({task.difficulty})")
        
        return created_tasks
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating tasks: {str(e)}")
        return []
    finally:
        db.close()

def setup_platform():
    """Complete platform setup with admin account and tasks"""
    print("🚀 Setting up AgentArena Platform...")
    print("=" * 50)
    
    # Step 1: Create admin account
    print("\n1. Creating Admin Account...")
    admin_user = create_admin_account()
    
    if admin_user:
        print(f"✅ Admin account ready: {admin_user.email}")
    else:
        print("❌ Failed to create admin account")
        return False
    
    # Step 2: Create REAL-style tasks
    print("\n2. Creating REAL-style Evaluation Tasks...")
    tasks = create_realevals_tasks()
    
    if tasks:
        print(f"✅ Platform setup complete with {len(tasks)} tasks!")
    else:
        print("⚠️ Platform setup complete but no new tasks were created")
    
    print("\n" + "=" * 50)
    print("🎉 AgentArena Platform Ready!")
    print(f"📧 Admin Login: sumit@gmail.com")
    print(f"🔑 Admin Password: sumit@12345")
    print(f"🌐 Frontend: http://localhost:5173")
    print(f"🔧 Backend API: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    setup_platform()