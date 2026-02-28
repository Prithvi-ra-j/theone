"""Opportunity service for managing internships, jobs, and scholarships."""

from typing import Any, Dict, List, Optional
from datetime import datetime
from loguru import logger

class OpportunityService:
    def __init__(self):
        # Mock data representing what a scraper would eventually provide
        self._mock_opportunities = [
            {
                "id": "intern-001",
                "type": "internship",
                "title": "Frontend Development Intern",
                "company": "TechNav AI",
                "location": "Remote / Bengaluru",
                "salary": "₹15,000 - ₹25,000 / month",
                "skills_required": ["React", "JavaScript", "Tailwind"],
                "description": "Work on building modern AI-driven interfaces for Indian startups.",
                "url": "https://example.com/jobs/intern-001",
                "deadline": "2026-04-15"
            },
            {
                "id": "intern-002",
                "type": "internship",
                "title": "Python Backend Intern",
                "company": "DataBharat",
                "location": "Pune",
                "salary": "₹20,000 / month",
                "skills_required": ["Python", "FastAPI", "SQL"],
                "description": "Developing scalable backend services for data analytics.",
                "url": "https://example.com/jobs/intern-002",
                "deadline": "2026-05-01"
            },
            {
                "id": "schol-001",
                "type": "scholarship",
                "title": "National Scholarship for Career Excellence",
                "provider": "Ministry of Education, GOI",
                "benefit": "₹50,000 per year",
                "eligibility": "Minimum 80% in Class 12, Annual family income < ₹6 LPA",
                "description": "Support for meritorious students pursuing professional degrees.",
                "url": "https://scholarships.gov.in/special-schol-001",
                "deadline": "2026-08-30"
            },
            {
                "id": "schol-002",
                "type": "scholarship",
                "title": "Women in Tech India Scholarship",
                "provider": "LeadHER Foundation",
                "benefit": "Full tuition waiver + Laptop",
                "eligibility": "Female students in STEM, 2nd year or higher",
                "description": "Empowering the next generation of women leaders in technology.",
                "url": "https://example.org/scholarship-women-tech",
                "deadline": "2026-06-15"
            }
        ]

    def get_all_opportunities(self, type_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return all opportunities, optionally filtered by type."""
        if type_filter:
            return [o for o in self._mock_opportunities if o["type"] == type_filter.lower()]
        return self._mock_opportunities

    def match_opportunities_to_user(self, user_skills: List[str], user_goals: List[str]) -> List[Dict[str, Any]]:
        """Match opportunities based on user skills and career goals."""
        matches = []
        user_skills_set = {s.lower() for s in user_skills}
        
        for opp in self._mock_opportunities:
            # Simple matching logic: if any required skill matches user's skills
            opp_skills = {s.lower() for s in opp.get("skills_required", [])}
            if opp_skills & user_skills_set:
                matches.append(opp)
            elif opp["type"] == "scholarship":
                # Scholarships are generally recommended to everyone for now
                matches.append(opp)
        
        return matches

    def get_scholarship_radar(self, income_lpa: float, academic_score: float) -> List[Dict[str, Any]]:
        """Filter scholarships based on financial and academic eligibility."""
        eligible = []
        for opp in self._mock_opportunities:
            if opp["type"] == "scholarship":
                # In a real app, we would parse eligibility criteria
                # For now, simple mock logic
                eligible.append(opp)
        return eligible
