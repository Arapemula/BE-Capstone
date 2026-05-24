import json
import os
import socket
import urllib.error
import urllib.request
from urllib.parse import urlparse

from src.services.analysis import (
    build_recommendation_texts,
    create_career_recommendation,
    create_course_recommendations,
    create_roadmap,
    get_role_profile,
    readiness_label,
)


ROLE_ID_TO_AI_JOB = {
    "fullstack-web-developer": "full stack developer",
    "ai-engineer": "product engineer (ai/ml)",
    "data-scientist": "data scientist",
    "project-manager-digital": "project manager",
}

AI_JOB_TO_ROLE_ID = {
    "full stack developer": "fullstack-web-developer",
    "java full stack developer": "fullstack-web-developer",
    "web developer": "fullstack-web-developer",
    "pengembang web": "fullstack-web-developer",
    "software developer": "fullstack-web-developer",
    "software engineer": "fullstack-web-developer",
    "junior software engineer": "fullstack-web-developer",
    "data scientist": "data-scientist",
    "associate data scientist": "data-scientist",
    "data analyst": "data-scientist",
    "data engineer": "data-scientist",
    "product engineer (ai/ml)": "ai-engineer",
    "computer software engineer": "ai-engineer",
    "project manager": "project-manager-digital",
    "project coordinator": "project-manager-digital",
    "manager": "project-manager-digital",
}

SKILL_DISPLAY_NAMES = {
    "api": "API",
    "css": "CSS",
    "eda": "EDA",
    "html": "HTML",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "nlp": "NLP",
    "postgresql": "PostgreSQL",
    "rest api": "REST API",
    "sql": "SQL",
    "tensorflow": "TensorFlow",
    "ui": "UI",
    "ux": "UX",
}


def get_ai_service_url():
    return os.getenv("AI_SERVICE_URL", "").strip().rstrip("/")


def get_ai_timeout_seconds():
    try:
        return float(os.getenv("AI_TIMEOUT_SECONDS", "20"))
    except ValueError:
        return 20.0


def is_ai_service_enabled():
    return bool(get_ai_service_url())


def map_role_to_ai_job(target_role=""):
    target_role = str(target_role or "").strip()
    if not target_role:
        return ""

    return ROLE_ID_TO_AI_JOB.get(target_role, target_role.replace("-", " "))


def infer_role_id_from_ai_job(ai_job="", fallback_role_id="fullstack-web-developer"):
    normalized_job = str(ai_job or "").lower().strip()
    if not normalized_job:
        return fallback_role_id

    if normalized_job in AI_JOB_TO_ROLE_ID:
        return AI_JOB_TO_ROLE_ID[normalized_job]

    if "project" in normalized_job or "manager" in normalized_job or "coordinator" in normalized_job:
        return "project-manager-digital"
    if "data" in normalized_job or "analyst" in normalized_job:
        return "data-scientist"
    if "ai" in normalized_job or "machine learning" in normalized_job:
        return "ai-engineer"
    if "web" in normalized_job or "developer" in normalized_job or "software" in normalized_job:
        return "fullstack-web-developer"

    return fallback_role_id


def humanize_skill(skill):
    normalized = str(skill or "").strip()
    lookup_key = normalized.lower()
    if lookup_key in SKILL_DISPLAY_NAMES:
        return SKILL_DISPLAY_NAMES[lookup_key]

    return " ".join(part.capitalize() for part in normalized.split())


def clamp_score(value, fallback=0):
    try:
        score = round(float(value))
    except (TypeError, ValueError):
        try:
            score = round(float(fallback))
        except (TypeError, ValueError):
            score = 0

    return max(0, min(100, score))


def guess_platform_from_url(url):
    hostname = urlparse(str(url or "")).hostname or ""
    hostname = hostname.replace("www.", "")
    if not hostname:
        return "Online Course"

    return hostname.split(".")[0].capitalize()


def call_ai_predict(cv_text="", target_role="", quiz_score=80):
    ai_service_url = get_ai_service_url()
    if not ai_service_url:
        return None

    payload = {
        "cv_text": cv_text or " ",
        "target_job": map_role_to_ai_job(target_role),
        "quiz_score": clamp_score(quiz_score, 80),
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{ai_service_url}/predict",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=get_ai_timeout_seconds()) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, socket.timeout, json.JSONDecodeError) as exc:
        print("AI service request failed:", exc)
        return None


def normalize_learning_path(ai_learning_path, skill_gap, role_profile):
    normalized_courses = []
    source_items = ai_learning_path if isinstance(ai_learning_path, list) else []

    for item in source_items:
        if not isinstance(item, dict):
            continue

        skill = humanize_skill(item.get("skill"))
        url = item.get("course_link") or item.get("url") or ""
        normalized_courses.append({
            "skill": skill,
            "platform": guess_platform_from_url(url),
            "title": f"Belajar {skill}",
            "url": url,
            "reason": f"Direkomendasikan AI untuk menutup gap {skill}.",
        })

    if normalized_courses:
        return normalized_courses

    return create_course_recommendations([humanize_skill(skill) for skill in skill_gap], role_profile)


def normalize_ai_analysis(ai_result, fallback_analysis, target_role_id="fullstack-web-developer", domain="technology"):
    if not ai_result:
        return {**fallback_analysis, "aiSource": "fallback"}

    recommended_job = ai_result.get("recommended_career") or ai_result.get("target_job")
    role_id = infer_role_id_from_ai_job(recommended_job, target_role_id)
    role_profile = get_role_profile(role_id)
    score = clamp_score(ai_result.get("career_match_score"), fallback_analysis.get("readinessScore", 0))
    detected_skills = [humanize_skill(skill) for skill in ai_result.get("detected_skills_from_cv", [])]
    skill_gap = [humanize_skill(skill) for skill in ai_result.get("skill_gap", [])]
    owned_skills = {str(skill).lower() for skill in ai_result.get("skill_dimiliki", [])}
    extracted_lookup = {str(skill).lower() for skill in detected_skills}

    job_matches = []
    for match in fallback_analysis.get("jobMatches", []):
        match_role_id = match.get("id")
        required_skills = match.get("requiredSkills", [])
        matched_skills = [
            skill for skill in required_skills
            if skill.lower() in owned_skills or skill.lower() in extracted_lookup
        ]

        if match_role_id == role_id:
            job_matches.append({
                **match,
                "matchScore": score,
                "matchedSkills": matched_skills,
            })
        else:
            job_matches.append(match)

    job_matches.sort(key=lambda item: item.get("matchScore", 0), reverse=True)

    learning_path = ai_result.get("learning_path", [])
    course_recommendations = normalize_learning_path(learning_path, skill_gap, role_profile)
    roadmap = []
    for index, course in enumerate(course_recommendations[:5]):
        roadmap.append({
            "id": f"step-{index + 1}",
            "title": f"Close {course['skill']} gap",
            "focus": course["skill"],
            "duration": "1-2 weeks" if index < 2 else "2-3 weeks",
            "action": f"Pelajari {course['skill']} lewat {course['title']}, lalu buat bukti praktik kecil.",
        })

    if not roadmap:
        roadmap = create_roadmap(skill_gap, role_profile)

    career_recommendation = create_career_recommendation(role_profile, score)
    if ai_result.get("summary"):
        career_recommendation["summary"] = ai_result["summary"]

    return {
        **fallback_analysis,
        "extractedSkills": detected_skills or fallback_analysis.get("extractedSkills", []),
        "jobMatches": job_matches,
        "suggestedRoleId": role_id,
        "skillGap": skill_gap,
        "recommendation": build_recommendation_texts(roadmap, role_profile),
        "careerRecommendation": career_recommendation,
        "courseRecommendations": course_recommendations,
        "roadmap": roadmap,
        "readinessScore": score,
        "readinessLabel": readiness_label(score),
        "confidence": clamp_score(ai_result.get("model_career_score"), 0) / 100,
        "domain": domain,
        "targetRole": role_profile["name"],
        "targetRoleId": role_id,
        "marketSignals": role_profile.get("marketSignals"),
        "businessGoal": role_profile.get("businessGoal"),
        "aiSource": "external",
        "aiRaw": ai_result,
    }


def enrich_cv_analysis_with_ai(input_text, fallback_analysis, options=None):
    if options is None:
        options = {}

    target_role = options.get("targetRole", "fullstack-web-developer")
    domain = options.get("domain", "technology")
    ai_result = call_ai_predict(
        cv_text=input_text,
        target_role=target_role,
        quiz_score=options.get("quizScore", 80),
    )
    return normalize_ai_analysis(ai_result, fallback_analysis, target_role, domain)


def enrich_recommendation_with_ai(payload, fallback_recommendation):
    if payload is None:
        payload = {}

    extracted_skills = payload.get("extractedSkills", [])
    if not isinstance(extracted_skills, list):
        extracted_skills = []

    target_role = payload.get("targetRole", "fullstack-web-developer")
    quiz_score = payload.get("quizScore", 80)
    ai_result = call_ai_predict(
        cv_text=" ".join(str(skill) for skill in extracted_skills) or " ",
        target_role=target_role,
        quiz_score=quiz_score,
    )
    normalized = normalize_ai_analysis(
        ai_result,
        fallback_recommendation,
        target_role,
        fallback_recommendation.get("domain", "technology"),
    )

    return {
        **fallback_recommendation,
        "targetRole": normalized.get("targetRole", fallback_recommendation.get("targetRole")),
        "readinessScore": normalized.get("readinessScore", fallback_recommendation.get("readinessScore")),
        "readinessLabel": normalized.get("readinessLabel", fallback_recommendation.get("readinessLabel")),
        "skillGap": normalized.get("skillGap", fallback_recommendation.get("skillGap", [])),
        "roadmap": normalized.get("roadmap", fallback_recommendation.get("roadmap", [])),
        "recommendation": normalized.get("recommendation", fallback_recommendation.get("recommendation", [])),
        "careerRecommendation": normalized.get("careerRecommendation", fallback_recommendation.get("careerRecommendation")),
        "courseRecommendations": normalized.get("courseRecommendations", fallback_recommendation.get("courseRecommendations", [])),
        "marketSignals": normalized.get("marketSignals", fallback_recommendation.get("marketSignals")),
        "aiSource": normalized.get("aiSource", "fallback"),
        "aiRaw": normalized.get("aiRaw"),
    }
