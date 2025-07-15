import fitz
import docx2txt
import re
from collections import Counter

# Define role-specific criteria and their weights
ROLE_CRITERIA = {
    "Data Scientist": {
        "skills": {
            "python": 50, "machine learning": 50, "data analysis": 45, "statistics": 45,
            "pandas": 50, "scikit-learn": 40, "deep learning": 50, "big data": 45,
            "data visualization": 45, "sql": 50, "numpy": 40, "jupyter": 35,
            "tensorflow": 40, "pytorch": 40, "r": 35, "power bi": 35, "tableau": 35,
            "data mining": 40, "feature engineering": 40, "a/b testing": 35
        },
        "leadership": {
            "team lead": 5, "project manager": 5, "mentor": 5, "leadership": 5,
            "managed": 5, "led team": 5, "research": 5
        },
        "experience_multiplier": 1.5
    },
    "Web Developer": {
        "skills": {
            "html5": 45, "css3": 45, "javascript": 50, "react.js": 50, "node.js": 50,
            "rest api": 40, "git": 35, "responsive design": 40, "web security": 35,
            "database": 40, "typescript": 40, "next.js": 40, "vue.js": 35, 
            "angular": 35, "webpack": 35, "sass": 35, "bootstrap": 35, "jquery": 30,
            "graphql": 35, "docker": 35, "ci/cd": 35
        },
        "leadership": {
            "team lead": 5, "project lead": 5, "mentor": 5, "leadership": 5,
            "managed": 5, "led development": 5, "agile": 5
        },
        "experience_multiplier": 1.5
    },
    "Machine Learning Engineer": {
        "skills": {
            "machine learning": 50, "python": 50, "deep learning": 50, "tensorflow": 45,
            "pytorch": 45, "neural networks": 45, "algorithms": 40, "data modeling": 40,
            "computer vision": 45, "nlp": 50, "keras": 40, "scikit-learn": 45,
            "mlops": 40, "docker": 35, "kubernetes": 35, "aws": 35, "azure": 35,
            "data pipeline": 40, "spark": 35, "hadoop": 35, "feature engineering": 40
        },
        "leadership": {
            "team lead": 5, "project lead": 5, "mentor": 5, "leadership": 5,
            "managed": 5, "led research": 5, "publications": 5
        },
        "experience_multiplier": 1.5
    },
    "Frontend Developer": {
        "skills": {
            "html5": 45, "css3": 45, "javascript": 50, "react.js": 50, "typescript": 45,
            "responsive design": 40, "ui/ux": 40, "web accessibility": 35, "sass": 35,
            "testing": 35, "redux": 40, "vue.js": 35, "angular": 35, "webpack": 35,
            "jest": 35, "cypress": 35, "bootstrap": 35, "tailwind": 35, "next.js": 40,
            "material ui": 35, "styled components": 35
        },
        "leadership": {
            "team lead": 5, "project lead": 5, "mentor": 5, "leadership": 5,
            "managed": 5, "led frontend": 5, "ui/ux lead": 5
        },
        "experience_multiplier": 1.5
    },
    "Backend Developer": {
        "skills": {
            "python": 50, "java": 50, "node.js": 45, "sql": 45, "rest api": 45,
            "database design": 40, "system architecture": 40, "microservices": 40,
            "docker": 40, "aws": 45, "data structures": 60, "algorithms": 45,
            "mongodb": 40, "postgresql": 40, "redis": 35, "kafka": 35, "rabbitmq": 35,
            "kubernetes": 35, "ci/cd": 35, "spring boot": 40, "express.js": 40,
            "security": 40
        },
        "leadership": {
            "team lead": 5, "project lead": 5, "mentor": 5, "leadership": 5,
            "managed": 5, "led backend": 5, "architecture": 5
        },
        "experience_multiplier": 1.5
    },
    "Cyber Security": {
        "skills": {
            "security": 50, "penetration testing": 50, "network security": 45, "cryptography": 45,
            "incident response": 45, "firewall": 40, "security tools": 40, "vulnerability assessment": 45,
            "ethical hacking": 45, "malware analysis": 45, "siem": 40, "forensics": 40,
            "security+": 35, "cissp": 40, "ceh": 40, "python": 35, "linux": 40,
            "risk assessment": 40, "compliance": 35, "security architecture": 40
        },
        "leadership": {
            "team lead": 5, "security lead": 5, "mentor": 5, "leadership": 5,
            "managed": 5, "incident management": 5, "security planning": 5
        },
        "experience_multiplier": 1.5
    },
    "Full Stack Developer": {
        "skills": {
            "javascript": 50, "python": 45, "react.js": 50, "node.js": 50, "html5": 45,
            "css3": 45, "sql": 45, "mongodb": 40, "rest api": 45, "git": 40,
            "docker": 40, "aws": 40, "typescript": 45, "redux": 40, "express.js": 40,
            "database": 40, "system design": 40, "testing": 35, "ci/cd": 35,
            "microservices": 35, "web security": 40
        },
        "leadership": {
            "team lead": 5, "tech lead": 5, "mentor": 5, "leadership": 5,
            "managed": 5, "project lead": 5, "architecture": 5
        },
        "experience_multiplier": 1.5
    },
    "Cloud Engineer": {
        "skills": {
            "aws": 50, "azure": 50, "gcp": 45, "kubernetes": 50, "docker": 50,
            "terraform": 45, "ci/cd": 45, "python": 40, "linux": 45, "networking": 40,
            "cloud security": 45, "microservices": 40, "devops": 45, "jenkins": 35,
            "ansible": 35, "cloud architecture": 45, "monitoring": 35, "serverless": 40,
            "infrastructure as code": 45, "load balancing": 35
        },
        "leadership": {
            "team lead": 5, "cloud architect": 5, "mentor": 5, "leadership": 5,
            "managed": 5, "infrastructure lead": 5, "devops lead": 5
        },
        "experience_multiplier": 1.5
    },
    "Database Developer": {
        "skills": {
            "sql": 50, "postgresql": 45, "mongodb": 45, "oracle": 45, "mysql": 45,
            "database design": 50, "data modeling": 45, "stored procedures": 40,
            "database security": 40, "performance tuning": 45, "etl": 40, "nosql": 40,
            "data warehousing": 40, "database administration": 40, "indexing": 35,
            "transactions": 35, "backup recovery": 35, "normalization": 40, "plsql": 40
        },
        "leadership": {
            "team lead": 5, "database architect": 5, "mentor": 5, "leadership": 5,
            "managed": 5, "data lead": 5, "technical planning": 5
        },
        "experience_multiplier": 1.5
    },
    "Android App Developer": {
        "skills": {
            "kotlin": 50, "java": 50, "android sdk": 50, "android studio": 45,
            "material design": 45, "sqlite": 40, "rest api": 40, "mvvm": 45,
            "jetpack compose": 45, "firebase": 45, "git": 35, "room": 40,
            "retrofit": 40, "coroutines": 40, "unit testing": 35, "gradle": 35,
            "rx java": 35, "android architecture": 40, "ui/ux": 35, "app security": 35
        },
        "leadership": {
            "team lead": 5, "mobile lead": 5, "mentor": 5, "leadership": 5,
            "managed": 5, "android lead": 5, "app architecture": 5
        },
        "experience_multiplier": 1.5
    }
}

def extract_text_from_resume(path):
    try:
        if path.endswith('.pdf'):
            doc = fitz.open(path)
            text = " ".join([page.get_text() for page in doc])
        elif path.endswith('.docx'):
            text = docx2txt.process(path)
        else:
            return ""
        return text.lower()
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

def extract_years_experience(text):
    # Look for patterns like "X years of experience" or "X+ years"
    experience_patterns = [
        r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
        r'(\d+)\+?\s*years?\s+in\s+(?:the\s+)?industry',
        r'worked\s+(?:for\s+)?(\d+)\+?\s*years?'
    ]
    
    max_years = 0
    for pattern in experience_patterns:
        matches = re.findall(pattern, text.lower())
        if matches:
            max_years = max(max_years, max(int(year) for year in matches))
    return max_years

def evaluate_resume(file_path, role):
    try:
        text = extract_text_from_resume(file_path)  # Changed 'path' to 'file_path'
        if not text or role not in ROLE_CRITERIA:
            return 0

        criteria = ROLE_CRITERIA[role]
        
        # Calculate skills score (60% of total) - Modified multiplier
        skills_score = 0
        max_skills_score = sum(criteria['skills'].values()) * 2  # Reduced from 3 to 2
        for skill, weight in criteria['skills'].items():
            occurrences = min(text.lower().count(skill), 3)
            skills_score += weight * occurrences

        # Calculate leadership score (15% of total) - Modified multiplier
        leadership_score = 0
        max_leadership_score = sum(criteria['leadership'].values()) * 0.7  # Added multiplier
        for trait, weight in criteria['leadership'].items():
            if trait in text.lower():
                leadership_score += weight

        # Calculate experience score (25% of total) - Modified multiplier
        years = extract_years_experience(text)
        experience_score = min(years * criteria['experience_multiplier'] * 1.5, 15)  # Increased multiplier

        # Adjusted weightage calculations with boosted factors
        normalized_skills = (skills_score / max_skills_score) * 60 * 1.3  # Added boost factor
        normalized_leadership = (leadership_score / max_leadership_score) * 15 * 1.2  # Added boost factor
        normalized_experience = (experience_score / 15) * 25 * 1.2  # Added boost factor

        final_score = normalized_skills + normalized_leadership + normalized_experience
        return round(min(final_score, 100), 2)

    except Exception as e:
        print(f"Error evaluating resume: {e}")
        return 0
