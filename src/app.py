"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from threading import Lock

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

signup_lock = Lock()

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Competitive soccer training and matches against other schools",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": []
    },
    "Swimming Club": {
        "description": "Swim training, technique improvement, and inter-school competitions",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": []
    },
    "Basketball Team": {
        "description": "Team practices focused on game strategy, drills, and competitive matches",
        "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": []
    },
    "Track and Field": {
        "description": "Sprint, distance, and field-event training for school athletics meets",
        "schedule": "Tuesdays and Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 24,
        "participants": []
    },
    "Art Studio": {
        "description": "Explore painting, drawing, and mixed media in a creative environment",
        "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": []
    },
    "Drama Club": {
        "description": "Act, direct, and produce theatrical performances for the school community",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 25,
        "participants": []
    },
    "Photography Club": {
        "description": "Learn composition, lighting, and storytelling through digital photography",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 14,
        "participants": []
    },
    "Music Ensemble": {
        "description": "Practice instrumental and vocal performance for school events and concerts",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": []
    },
    "Math Olympiad": {
        "description": "Prepare for and compete in regional and national mathematics competitions",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": []
    },
    "Debate Team": {
        "description": "Develop critical thinking, research, and public speaking through competitive debate",
        "schedule": "Mondays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": []
    },
    "Robotics Club": {
        "description": "Design, build, and program robots for hands-on engineering challenges",
        "schedule": "Wednesdays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": []
    },
    "Science Society": {
        "description": "Explore experiments, scientific inquiry, and STEM fair preparation",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": []
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    normalized_email = email.strip().lower()
    if not normalized_email:
        raise HTTPException(status_code=400, detail="Email is required")

    with signup_lock:
        # Treat emails case-insensitively and ignore surrounding whitespace
        if any(participant.strip().lower() == normalized_email for participant in activity["participants"]):
            raise HTTPException(status_code=400, detail="Student is already signed up for this activity")

        if len(activity["participants"]) >= activity["max_participants"]:
            raise HTTPException(status_code=400, detail="This activity is already full")

        # Add student
        activity["participants"].append(normalized_email)

    return {"message": f"Signed up {normalized_email} for {activity_name}"}


@app.delete("/activities/{activity_name}/signup")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    normalized_email = email.strip().lower()

    match = next(
        (p for p in activity["participants"] if p.strip().lower() == normalized_email),
        None
    )
    if match is None:
        raise HTTPException(status_code=404, detail="Student is not registered for this activity")

    activity["participants"].remove(match)
    return {"message": f"Unregistered {normalized_email} from {activity_name}"}
