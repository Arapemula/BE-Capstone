import json
import os
import re
import socket
import urllib.error
import urllib.request
from urllib.parse import urlparse

from src.services.analysis import (
    build_recommendation_texts,
    create_career_recommendation,
    create_course_recommendations,
    create_roadmap,
    find_role_profile,
    get_role_profile,
    readiness_label,
)


ROLE_ID_TO_AI_JOB = {
    "fullstack-web-developer": "web developer",
    "full stack developer": "web developer",
    "full-stack developer": "web developer",
    "fullstack developer": "web developer",
    "frontend developer": "web developer",
    "backend developer": "web developer",
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


def get_openrouter_api_key():
    return os.getenv("OPENROUTER_API_KEY", "").strip()


def get_openrouter_model():
    return os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-v4-flash:free").strip() or "deepseek/deepseek-v4-flash:free"


def get_openrouter_site_url():
    return os.getenv("OPENROUTER_SITE_URL", "").strip()


def get_openrouter_app_name():
    return os.getenv("OPENROUTER_APP_NAME", "SkillMap").strip()


def map_role_to_ai_job(target_role=""):
    target_role = str(target_role or "").strip()
    if not target_role:
        return ""

    lookup_key = target_role.lower()
    return ROLE_ID_TO_AI_JOB.get(lookup_key, target_role.replace("-", " "))


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


def format_career_name(career):
    normalized = str(career or "").strip()
    if not normalized:
        return ""

    acronym_words = {"ai", "api", "hr", "it", "ml", "qa", "seo", "sql", "ui", "ux"}
    return " ".join(
        part.upper() if part.lower() in acronym_words else part.capitalize()
        for part in normalized.replace("_", " ").split()
    )


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


def compact_text_list(value, limit=6):
    if not isinstance(value, list):
        return []

    return [
        str(item).strip()
        for item in value
        if str(item).strip()
    ][:limit]


def build_quiz_role_context(fallback_quiz):
    roles = fallback_quiz.get("roles", []) if isinstance(fallback_quiz.get("roles"), list) else []
    role_by_id = {
        role.get("id"): role
        for role in roles
        if isinstance(role, dict) and role.get("id")
    }

    role_context = []
    for option in fallback_quiz.get("options", []):
        if not isinstance(option, dict):
            continue

        role_id = option.get("roleId")
        role = role_by_id.get(role_id, {})
        role_context.append({
            "roleId": role_id,
            "label": option.get("label"),
            "matchScore": clamp_score(option.get("matchScore"), 0),
            "matchedSkills": compact_text_list(role.get("matchedSkills"), 5),
            "missingSkills": compact_text_list(role.get("missingSkills"), 5),
            "requiredSkills": compact_text_list(role.get("requiredSkills"), 8),
            "businessGoal": role.get("businessGoal"),
            "marketSignals": compact_text_list(role.get("marketSignals"), 5),
            "fallbackResponse": option.get("response"),
            "fallbackDescription": option.get("description"),
        })

    return role_context


def get_response_prefix(response, word_count=3):
    words = re.findall(r"[a-z0-9]+", str(response or "").lower())
    return " ".join(words[:word_count])


def has_repeated_option_stems(options):
    responses = [
        str(option.get("response") or "").strip()
        for option in options
        if isinstance(option, dict) and str(option.get("response") or "").strip()
    ]
    if len(responses) < 2:
        return False

    prefixes = [get_response_prefix(response) for response in responses]
    prefix_counts = {
        prefix: prefixes.count(prefix)
        for prefix in set(prefixes)
        if prefix
    }
    return any(count > 1 for count in prefix_counts.values())


def has_unrelated_web_terms(option, role):
    web_terms = [
        "react",
        "vite",
        "express",
        "rest api",
        "api integration",
        "frontend",
        "backend",
        "javascript",
        "postgresql",
    ]
    response_text = str(option.get("response") or "").lower()
    if not any(term in response_text for term in web_terms):
        return False

    role_context = " ".join([
        str(role.get("id") or ""),
        str(role.get("name") or ""),
        " ".join(compact_text_list(role.get("matchedSkills"), 20)),
        " ".join(compact_text_list(role.get("missingSkills"), 20)),
        " ".join(compact_text_list(role.get("requiredSkills"), 20)),
        " ".join(compact_text_list(role.get("marketSignals"), 20)),
    ]).lower()
    return not any(term in role_context for term in web_terms)


def quiz_output_looks_template(questions, roles):
    role_by_id = {
        role.get("id"): role
        for role in roles
        if isinstance(role, dict) and role.get("id")
    }

    for question in questions:
        options = question.get("options", []) if isinstance(question, dict) else []
        if has_repeated_option_stems(options):
            return True

        for option in options:
            if not isinstance(option, dict):
                continue
            role = role_by_id.get(option.get("roleId"), {})
            if has_unrelated_web_terms(option, role):
                return True

    return False


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


def extract_json_object(raw_text=""):
    text = str(raw_text or "").strip()
    if not text:
        return None

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            return None

    return None


def call_openrouter_quiz(payload, fallback_quiz):
    api_key = get_openrouter_api_key()
    if not api_key:
        return None

    role_context = build_quiz_role_context(fallback_quiz)
    if not role_context:
        return None

    prompt_payload = {
        "roles": role_context,
        "extractedSkills": compact_text_list(payload.get("extractedSkills"), 12),
        "skillDimiliki": compact_text_list(payload.get("skillDimiliki"), 12),
        "skillGap": compact_text_list(payload.get("skillGap"), 12),
        "targetRole": payload.get("targetRole"),
        "recommendedCareer": payload.get("recommendedCareer"),
        "aiSource": payload.get("aiSource"),
    }
    messages = [
        {
            "role": "system",
            "content": (
                "Kamu adalah generator mini quiz karier SkillMap. Tugasmu membuat lima pertanyaan "
                "situasional berbahasa Indonesia berdasarkan daftar saran pekerjaan dari hasil scan CV. "
                "Quiz ini bukan tes teknis, melainkan memilih kecenderungan role yang paling diminati user. "
                "Jawab hanya JSON valid dan jangan menambah roleId di luar daftar."
            ),
        },
        {
            "role": "user",
            "content": (
                "Buat 5 pertanyaan. Setiap pertanyaan wajib punya 1 opsi untuk setiap role pada roles. Gunakan matchScore, "
                "matchedSkills, missingSkills, businessGoal, dan marketSignals sebagai referensi. "
                "Aturan output:\n"
                "- JSON valid saja, tanpa markdown.\n"
                "- Format: {\"context\":\"...\",\"questions\":[{\"prompt\":\"...\",\"options\":[{\"roleId\":\"...\",\"response\":\"...\",\"description\":\"...\"}]}]}\n"
                "- Jumlah questions wajib 5.\n"
                "- Jumlah options di setiap question harus sama dengan jumlah roles.\n"
                "- roleId wajib persis dari roles.\n"
                "- Jangan sebut nama jabatan atau role title di response dan description.\n"
                "- Jangan memakai kalimat template/generik yang sama antar pertanyaan.\n"
                "- Setiap response harus spesifik pada matchedSkills, missingSkills, marketSignals, atau konteks CV.\n"
                "- response maksimal 16 kata, berupa pilihan aktivitas/pekerjaan yang natural.\n"
                "- description maksimal 24 kata, sebutkan sinyal CV seperti skill cocok, gap, atau match score.\n\n"
                f"Konteks:\n{json.dumps(prompt_payload, ensure_ascii=False)}"
            ),
        },
    ]
    body = json.dumps({
        "model": get_openrouter_model(),
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 1800,
        "response_format": {"type": "json_object"},
    }).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    site_url = get_openrouter_site_url()
    if site_url:
        headers["HTTP-Referer"] = site_url

    app_name = get_openrouter_app_name()
    if app_name:
        headers["X-Title"] = app_name

    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=get_ai_timeout_seconds()) as response:
            result = json.loads(response.read().decode("utf-8"))
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return extract_json_object(content)
    except (urllib.error.URLError, TimeoutError, socket.timeout, json.JSONDecodeError) as exc:
        print("OpenRouter quiz request failed:", exc)
        return None


def enrich_career_fit_quiz_with_openrouter(payload, fallback_quiz):
    ai_quiz = call_openrouter_quiz(payload or {}, fallback_quiz)
    if not ai_quiz:
        return fallback_quiz

    fallback_questions = fallback_quiz.get("questions", [])
    if not isinstance(fallback_questions, list) or not fallback_questions:
        fallback_questions = [{
            "id": "career-fit-question-1",
            "prompt": fallback_quiz.get("prompt"),
            "options": fallback_quiz.get("options", []),
        }]

    ai_questions = ai_quiz.get("questions", []) if isinstance(ai_quiz.get("questions"), list) else []
    if not ai_questions and isinstance(ai_quiz.get("options"), list):
        ai_questions = [{
            "prompt": ai_quiz.get("prompt"),
            "options": ai_quiz.get("options", []),
        }]

    if not ai_questions:
        return fallback_quiz

    normalized_questions = []
    mapped_option_count = 0
    for index, fallback_question in enumerate(fallback_questions[:5]):
        fallback_options = fallback_question.get("options", []) if isinstance(fallback_question, dict) else []
        allowed_role_ids = {option.get("roleId") for option in fallback_options if isinstance(option, dict)}
        ai_question = ai_questions[index] if index < len(ai_questions) and isinstance(ai_questions[index], dict) else {}
        ai_options = ai_question.get("options", []) if isinstance(ai_question.get("options"), list) else []
        ai_option_by_role_id = {
            option.get("roleId"): option
            for option in ai_options
            if isinstance(option, dict) and option.get("roleId") in allowed_role_ids
        }
        mapped_option_count += len(ai_option_by_role_id)

        normalized_options = []
        for fallback_option in fallback_options:
            role_id = fallback_option.get("roleId")
            ai_option = ai_option_by_role_id.get(role_id, {})
            response = str(ai_option.get("response") or fallback_option.get("response") or "").strip()
            description = str(ai_option.get("description") or fallback_option.get("description") or "").strip()
            normalized_options.append({
                **fallback_option,
                "response": response,
                "description": description,
            })

        normalized_questions.append({
            **fallback_question,
            "prompt": str(ai_question.get("prompt") or fallback_question.get("prompt") or "").strip(),
            "options": normalized_options,
        })

    if mapped_option_count == 0:
        return fallback_quiz
    if quiz_output_looks_template(normalized_questions, fallback_quiz.get("roles", [])):
        return fallback_quiz

    first_question = normalized_questions[0]
    context = str(ai_quiz.get("context") or "Pertanyaan ini dibuat AI dari daftar job match hasil scan CV.").strip()
    return {
        **fallback_quiz,
        "source": "openrouter",
        "sourceModel": get_openrouter_model(),
        "prompt": first_question.get("prompt"),
        "context": context,
        "options": first_question.get("options", []),
        "questions": normalized_questions,
    }


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


def slugify_job_id(value):
    text = str(value or "").lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "recommended-role"


def get_ai_job_matches(ai_result):
    for key in ("jobMatches", "job_matches", "matches", "careerMatches", "career_matches"):
        value = ai_result.get(key)
        if isinstance(value, list):
            return value
    return []


def normalize_ai_job_matches(ai_result, fallback_analysis, role_id, score, skill_gap, recommendation_source):
    ai_matches = get_ai_job_matches(ai_result)
    if not ai_matches:
        return []

    normalized_matches = []
    seen_ids = set()
    for index, match in enumerate(ai_matches):
        if not isinstance(match, dict):
            continue

        name = str(
            match.get("name")
            or match.get("roleName")
            or match.get("role")
            or match.get("career")
            or match.get("recommended_career")
            or f"Rekomendasi {index + 1}"
        ).strip()
        match_role_id = str(match.get("id") or match.get("roleId") or "").strip()
        known_role_id = infer_role_id_from_ai_job(name, "")
        normalized_id = known_role_id or match_role_id or slugify_job_id(name)
        if normalized_id in seen_ids:
            continue
        seen_ids.add(normalized_id)

        required_skills = compact_text_list(match.get("requiredSkills") or match.get("required_skills"), 20)
        matched_skills = compact_text_list(match.get("matchedSkills") or match.get("matched_skills"), 20)
        missing_skills = compact_text_list(match.get("missingSkills") or match.get("missing_skills") or match.get("skill_gap"), 20)
        match_score = clamp_score(
            match.get("matchScore")
            or match.get("match_score")
            or match.get("career_match_score")
            or match.get("score"),
            score if normalized_id == role_id else 0,
        )

        normalized_matches.append({
            **match,
            "id": normalized_id,
            "name": format_career_name(name),
            "matchScore": match_score,
            "matchedSkills": matched_skills,
            "missingSkills": missing_skills or (skill_gap if normalized_id == role_id else []),
            "requiredSkills": required_skills,
            "businessGoal": match.get("businessGoal") or match.get("business_goal"),
            "marketSignals": compact_text_list(match.get("marketSignals") or match.get("market_signals"), 20),
            "recommendationSource": match.get("recommendationSource") or recommendation_source,
        })

    return normalized_matches


def has_actionable_match(match):
    return (
        clamp_score(match.get("matchScore"), 0) > 0
        or bool(compact_text_list(match.get("matchedSkills"), 1))
    )


def normalize_ai_analysis(ai_result, fallback_analysis, target_role_id="fullstack-web-developer", domain="technology"):
    if not ai_result:
        return {**fallback_analysis, "aiSource": "local_rules"}

    recommended_job = ai_result.get("recommended_career") or ai_result.get("target_job")
    recommended_job_display = format_career_name(recommended_job)
    recommendation_source = ai_result.get("recommendation_source")
    score = clamp_score(ai_result.get("career_match_score"), fallback_analysis.get("readinessScore", 0))
    gap_score = clamp_score(ai_result.get("gap_score"), 100 - score)
    detected_skills = [humanize_skill(skill) for skill in ai_result.get("detected_skills_from_cv", [])]
    skill_gap = [humanize_skill(skill) for skill in ai_result.get("skill_gap", [])]
    skill_dimiliki = [humanize_skill(skill) for skill in ai_result.get("skill_dimiliki", [])]
    matched_recommendation_skills = skill_dimiliki
    role_id = infer_role_id_from_ai_job(recommended_job, None) or slugify_job_id(recommended_job_display or target_role_id)
    role_profile = find_role_profile(role_id) or {
        "id": role_id,
        "name": recommended_job_display or format_career_name(role_id),
        "domain": domain,
        "requiredSkills": matched_recommendation_skills + skill_gap,
        "businessGoal": None,
        "marketSignals": [],
    }
    owned_skills = {str(skill).lower() for skill in skill_dimiliki}
    extracted_lookup = {str(skill).lower() for skill in detected_skills}

    job_matches = normalize_ai_job_matches(ai_result, fallback_analysis, role_id, score, skill_gap, recommendation_source)
    if not job_matches:
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
                    "name": recommended_job_display or match.get("name"),
                    "matchScore": score,
                    "matchedSkills": matched_skills,
                    "missingSkills": skill_gap,
                    "recommendationSource": recommendation_source,
                })
            else:
                job_matches.append(match)

    has_recommended_match = any(
        match.get("id") == role_id
        or str(match.get("name") or "").strip().lower() == recommended_job_display.lower()
        for match in job_matches
    )
    if recommended_job_display and score > 0 and not has_recommended_match:
        job_matches.insert(0, {
            "id": role_id,
            "name": recommended_job_display,
            "domain": domain,
            "matchScore": score,
            "matchedSkills": matched_recommendation_skills,
            "missingSkills": skill_gap,
            "requiredSkills": matched_recommendation_skills + skill_gap,
            "recommendationSource": recommendation_source,
        })

    job_matches.sort(
        key=lambda item: (
            item.get("matchScore", 0),
            len(compact_text_list(item.get("matchedSkills"), 20)),
        ),
        reverse=True,
    )
    job_matches = [match for match in job_matches if has_actionable_match(match)]

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

    display_role_profile = {
        **role_profile,
        "name": recommended_job_display or role_profile["name"],
    }
    career_recommendation = create_career_recommendation(display_role_profile, score)
    if ai_result.get("summary"):
        career_recommendation["summary"] = ai_result["summary"]

    return {
        **fallback_analysis,
        "extractedSkills": detected_skills or fallback_analysis.get("extractedSkills", []),
        "skillDimiliki": skill_dimiliki,
        "jobMatches": job_matches,
        "suggestedRoleId": role_id,
        "skillGap": skill_gap,
        "recommendation": build_recommendation_texts(roadmap, display_role_profile),
        "careerRecommendation": career_recommendation,
        "courseRecommendations": course_recommendations,
        "roadmap": roadmap,
        "readinessScore": score,
        "readinessLabel": readiness_label(score),
        "confidence": clamp_score(ai_result.get("model_career_score"), 0) / 100,
        "domain": domain,
        "targetRole": recommended_job_display or role_profile["name"],
        "targetRoleId": role_id,
        "recommendedCareer": recommended_job_display,
        "recommended_career": recommended_job,
        "recommendationSource": recommendation_source,
        "recommendation_source": recommendation_source,
        "careerMatchScore": score,
        "career_match_score": score,
        "gapScore": gap_score,
        "gap_score": gap_score,
        "skill_dimiliki": skill_dimiliki,
        "learningPath": learning_path,
        "learning_path": learning_path,
        "summary": ai_result.get("summary"),
        "marketSignals": role_profile.get("marketSignals"),
        "businessGoal": role_profile.get("businessGoal"),
        "aiSource": "external",
        "aiRaw": ai_result,
    }


def enrich_cv_analysis_with_ai(input_text, fallback_analysis, options=None):
    if options is None:
        options = {}

    target_role = options.get("targetRole", "fullstack-web-developer")
    target_job = options.get("targetJob") if "targetJob" in options else target_role
    domain = options.get("domain", "technology")
    ai_result = call_ai_predict(
        cv_text=input_text,
        target_role=target_job,
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
        "recommendedCareer": normalized.get("recommendedCareer"),
        "recommendationSource": normalized.get("recommendationSource"),
        "careerMatchScore": normalized.get("careerMatchScore"),
        "gapScore": normalized.get("gapScore"),
        "skillDimiliki": normalized.get("skillDimiliki", []),
        "learningPath": normalized.get("learningPath", []),
        "summary": normalized.get("summary"),
        "aiSource": normalized.get("aiSource", "local_rules"),
        "aiRaw": normalized.get("aiRaw"),
    }


def get_known_role_ids(job_matches=None):
    role_ids = []
    for match in job_matches if isinstance(job_matches, list) else []:
        if not isinstance(match, dict):
            continue
        role_id = match.get("id") or match.get("roleId")
        if role_id and role_id not in role_ids:
            role_ids.append(role_id)

    return role_ids or [role["id"] for role in [
        get_role_profile("fullstack-web-developer"),
        get_role_profile("ai-engineer"),
        get_role_profile("data-scientist"),
        get_role_profile("project-manager-digital"),
    ]]


def get_quiz_vote_summary(quiz_answers=None):
    counts = {}
    answers = quiz_answers if isinstance(quiz_answers, list) else []

    for answer in answers:
        if not isinstance(answer, dict):
            continue
        role_id = answer.get("selectedRoleId")
        if role_id:
            counts[role_id] = counts.get(role_id, 0) + 1

    return counts


def choose_fallback_final_role(payload):
    job_matches = payload.get("jobMatches", []) if isinstance(payload, dict) else []
    quiz = payload.get("quiz", {}) if isinstance(payload.get("quiz"), dict) else {}
    vote_counts = get_quiz_vote_summary(quiz.get("answers"))
    selected_role_id = quiz.get("selectedRoleId")

    if vote_counts:
        score_by_role = {
            (match.get("id") or match.get("roleId")): clamp_score(match.get("matchScore"), 0)
            for match in job_matches
            if isinstance(match, dict)
        }
        return sorted(
            vote_counts.keys(),
            key=lambda role_id: (vote_counts.get(role_id, 0), score_by_role.get(role_id, 0)),
            reverse=True,
        )[0]

    if selected_role_id:
        return selected_role_id

    if isinstance(job_matches, list) and job_matches:
        return job_matches[0].get("id") or job_matches[0].get("roleId") or "fullstack-web-developer"

    return "fullstack-web-developer"


def get_result_role_profile(role_id, match=None, fallback_name=""):
    role_profile = find_role_profile(role_id)
    if role_profile:
        return role_profile

    match = match if isinstance(match, dict) else {}
    name = str(match.get("name") or fallback_name or format_career_name(role_id)).strip()
    normalized_role_id = role_id or slugify_job_id(name)

    return {
        "id": normalized_role_id,
        "name": name or format_career_name(normalized_role_id),
        "requiredSkills": compact_text_list(match.get("requiredSkills"), 12),
        "businessGoal": match.get("businessGoal"),
        "marketSignals": compact_text_list(match.get("marketSignals"), 8),
    }


def build_final_conclusion_fallback(payload):
    role_id = choose_fallback_final_role(payload or {})
    job_matches = payload.get("jobMatches", []) if isinstance(payload, dict) else []
    quiz = payload.get("quiz", {}) if isinstance(payload.get("quiz"), dict) else {}
    extracted_skills = compact_text_list(payload.get("skillDimiliki"), 8) or compact_text_list(payload.get("extractedSkills"), 8)
    skill_gap = compact_text_list(payload.get("skillGap"), 8)
    top_match = next(
        (match for match in job_matches if isinstance(match, dict) and (match.get("id") or match.get("roleId")) == role_id),
        job_matches[0] if isinstance(job_matches, list) and job_matches else {},
    )
    role_profile = get_result_role_profile(role_id, top_match, payload.get("recommendedCareer"))
    match_score = clamp_score(top_match.get("matchScore"), quiz.get("score", 0))
    votes = get_quiz_vote_summary(quiz.get("answers")).get(role_id, 0)
    recommended_name = str(
        top_match.get("name") or role_profile["name"]
    ).strip()

    return {
        "recommendedRoleId": role_profile["id"],
        "recommendedRoleName": recommended_name,
        "confidenceScore": match_score,
        "summary": (
            f"Kesimpulan akhir mengarah ke {recommended_name} karena sinyal CV, job match, "
            "dan jawaban mini quiz paling konsisten ke jalur ini."
        ),
        "cvSummary": (
            f"Skill yang paling terlihat dari CV: {', '.join(extracted_skills[:5])}."
            if extracted_skills
            else "CV belum menunjukkan skill spesifik yang kuat, jadi rekomendasi memakai job match dan mini quiz."
        ),
        "jobMatchSummary": (
            f"Role ini memiliki kecocokan sekitar {match_score}% dari hasil scan dan dibandingkan dengan saran job lain."
        ),
        "quizSummary": (
            f"Mini quiz memberi {votes} dari 5 sinyal ke role ini."
            if votes
            else "Mini quiz dipakai sebagai validasi minat terhadap saran job dari hasil scan."
        ),
        "nextFocus": skill_gap[:3] or role_profile.get("requiredSkills", [])[:3],
        "reasoning": [
            "Sinyal skill CV dibandingkan dengan kebutuhan role.",
            "Persentase job match dipakai sebagai baseline kesiapan.",
            "Jawaban mini quiz dipakai untuk memilih arah yang paling diminati."
        ],
        "source": "local_rules",
    }


def call_openrouter_final_conclusion(payload, fallback_result):
    api_key = get_openrouter_api_key()
    if not api_key:
        return None

    job_matches = payload.get("jobMatches", []) if isinstance(payload.get("jobMatches"), list) else []
    role_context = [
        {
            "roleId": match.get("id") or match.get("roleId"),
            "name": match.get("name"),
            "matchScore": clamp_score(match.get("matchScore"), 0),
            "matchedSkills": compact_text_list(match.get("matchedSkills"), 6),
            "requiredSkills": compact_text_list(match.get("requiredSkills"), 8),
            "businessGoal": match.get("businessGoal"),
            "marketSignals": compact_text_list(match.get("marketSignals"), 5),
        }
        for match in job_matches
        if isinstance(match, dict)
    ]
    quiz = payload.get("quiz", {}) if isinstance(payload.get("quiz"), dict) else {}
    prompt_payload = {
        "allowedRoleIds": get_known_role_ids(job_matches),
        "cvTextExcerpt": str(payload.get("cvText") or "")[:2200],
        "profile": payload.get("profile", {}),
        "extractedSkills": compact_text_list(payload.get("extractedSkills"), 12),
        "skillDimiliki": compact_text_list(payload.get("skillDimiliki"), 12),
        "skillGap": compact_text_list(payload.get("skillGap"), 12),
        "jobMatches": role_context,
        "miniQuiz": {
            "score": quiz.get("score"),
            "selectedRoleId": quiz.get("selectedRoleId"),
            "answers": quiz.get("answers", [])[:5] if isinstance(quiz.get("answers"), list) else [],
        },
        "fallback": fallback_result,
    }
    messages = [
        {
            "role": "system",
            "content": (
                "Kamu adalah analis karier SkillMap. Berikan kesimpulan akhir pekerjaan paling cocok "
                "berdasarkan ringkasan CV, daftar job match dari scan CV, dan jawaban mini quiz. "
                "Jawab hanya JSON valid. recommendedRoleId wajib dari allowedRoleIds."
            ),
        },
        {
            "role": "user",
            "content": (
                "Tentukan satu final job dan buat ringkasan berbahasa Indonesia. Format JSON: "
                "{\"recommendedRoleId\":\"...\",\"recommendedRoleName\":\"...\",\"confidenceScore\":0,"
                "\"summary\":\"...\",\"cvSummary\":\"...\",\"jobMatchSummary\":\"...\","
                "\"quizSummary\":\"...\",\"nextFocus\":[\"...\"],\"reasoning\":[\"...\"]}\n\n"
                f"Konteks:\n{json.dumps(prompt_payload, ensure_ascii=False)}"
            ),
        },
    ]
    body = json.dumps({
        "model": get_openrouter_model(),
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 1200,
        "response_format": {"type": "json_object"},
    }).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    site_url = get_openrouter_site_url()
    if site_url:
        headers["HTTP-Referer"] = site_url

    app_name = get_openrouter_app_name()
    if app_name:
        headers["X-Title"] = app_name

    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=get_ai_timeout_seconds()) as response:
            result = json.loads(response.read().decode("utf-8"))
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return extract_json_object(content)
    except (urllib.error.URLError, TimeoutError, socket.timeout, json.JSONDecodeError) as exc:
        print("OpenRouter final conclusion request failed:", exc)
        return None


def normalize_final_conclusion(ai_result, fallback_result, payload):
    if not ai_result:
        return fallback_result

    allowed_role_ids = set(get_known_role_ids(payload.get("jobMatches", [])))
    role_id = ai_result.get("recommendedRoleId")
    if role_id not in allowed_role_ids:
        role_id = fallback_result["recommendedRoleId"]

    job_matches = payload.get("jobMatches", []) if isinstance(payload.get("jobMatches"), list) else []
    top_match = next(
        (match for match in job_matches if isinstance(match, dict) and (match.get("id") or match.get("roleId")) == role_id),
        {},
    )
    role_profile = get_result_role_profile(role_id, top_match, ai_result.get("recommendedRoleName"))
    next_focus = ai_result.get("nextFocus", fallback_result.get("nextFocus", []))
    if not isinstance(next_focus, list):
        next_focus = fallback_result.get("nextFocus", [])

    reasoning = ai_result.get("reasoning", fallback_result.get("reasoning", []))
    if not isinstance(reasoning, list):
        reasoning = fallback_result.get("reasoning", [])

    return {
        **fallback_result,
        "recommendedRoleId": role_profile["id"],
        "recommendedRoleName": ai_result.get("recommendedRoleName") or top_match.get("name") or role_profile["name"],
        "confidenceScore": clamp_score(ai_result.get("confidenceScore"), fallback_result.get("confidenceScore", 0)),
        "summary": ai_result.get("summary") or fallback_result.get("summary"),
        "cvSummary": ai_result.get("cvSummary") or fallback_result.get("cvSummary"),
        "jobMatchSummary": ai_result.get("jobMatchSummary") or fallback_result.get("jobMatchSummary"),
        "quizSummary": ai_result.get("quizSummary") or fallback_result.get("quizSummary"),
        "nextFocus": compact_text_list(next_focus, 5),
        "reasoning": compact_text_list(reasoning, 5),
        "source": "openrouter",
        "sourceModel": get_openrouter_model(),
    }


def create_final_career_conclusion(payload=None):
    if payload is None:
        payload = {}

    fallback_result = build_final_conclusion_fallback(payload)
    ai_result = call_openrouter_final_conclusion(payload, fallback_result)
    return normalize_final_conclusion(ai_result, fallback_result, payload)
