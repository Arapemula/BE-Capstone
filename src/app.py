import os
import traceback
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parents[1]
load_dotenv(APP_DIR / "server.env")
load_dotenv()

from src.services.analysis import (
    analyze_cv_text,
    create_personalized_recommendation,
    extract_pdf_text,
    extract_text_from_upload,
    generate_career_fit_quiz,
    get_dashboard_snapshot,
    get_quiz_questions,
    score_quiz
)
from src.services.ai_client import (
    AIServiceUnavailable,
    create_final_career_conclusion,
    enrich_career_fit_quiz_with_openrouter,
    enrich_cv_analysis_with_ai,
    enrich_recommendation_with_ai,
    is_ai_service_enabled
)
from src.repositories.store import (
    get_user_cv_history,
    get_user_profile,
    is_database_enabled,
    save_cv_analysis,
    save_lead,
    save_quiz_result,
    get_latest_activity
)
from src.db import init_database
from src.auth import get_current_user_context

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
port = int(os.getenv("PORT", 3001))

DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://capstone-odwh.vercel.app",
)


def normalize_origin(origin):
    if not origin:
        return ""
    if origin.strip() == "*":
        return "*"
    return origin.strip().rstrip("/")


def parse_cors_origins(raw):
    return [origin for origin in (normalize_origin(item) for item in raw.split(",")) if origin]


def get_cors_origin():
    cors_origin = os.getenv("CORS_ORIGIN", "")
    configured_origins = parse_cors_origins(cors_origin)
    if "*" in configured_origins:
        return "*"

    origins = list(DEFAULT_CORS_ORIGINS)
    frontend_url = normalize_origin(os.getenv("FRONTEND_URL", ""))
    if frontend_url:
        origins.append(frontend_url)
    origins.extend(configured_origins)
    return list(dict.fromkeys(origins))

cors_origins = get_cors_origin()
CORS(
    app,
    resources={r"/*": {"origins": cors_origins}},
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=86400
)

# Initialize database
init_database()

def is_pdf_upload(file):
    filename = (file.filename or "").lower()
    mimetype = (file.mimetype or "").lower()
    return filename.endswith(".pdf") or mimetype == "application/pdf"

def clamp_quiz_score(value, fallback=0):
    try:
        score = round(float(value))
    except (TypeError, ValueError):
        score = fallback
    return max(0, min(100, score))

def is_career_fit_quiz_payload(payload):
    answers = payload.get("answers")
    return (
        payload.get("track") == "career-fit"
        or bool(payload.get("selectedRoleId"))
        or bool(payload.get("selectedRoleName"))
        or (isinstance(answers, list) and any(isinstance(answer, dict) for answer in answers))
    )

def build_career_fit_quiz_result(payload, domain, target_role):
    answers = payload.get("answers") if isinstance(payload.get("answers"), list) else []
    job_matches = payload.get("jobMatches") if isinstance(payload.get("jobMatches"), list) else []
    score = clamp_quiz_score(payload.get("score"))

    result = {
        "score": score,
        "track": payload.get("track") or "career-fit",
        "domain": domain,
        "targetRole": payload.get("targetRole") or target_role,
        "targetRoleName": payload.get("targetRoleName") or payload.get("selectedRoleName"),
        "selectedRoleId": payload.get("selectedRoleId"),
        "selectedRoleName": payload.get("selectedRoleName"),
        "selectedResponse": payload.get("selectedResponse"),
        "answeredCount": len(answers),
        "answers": answers,
        "recommendation": payload.get("recommendation"),
        "recommendedCareer": payload.get("recommendedCareer"),
        "jobMatches": job_matches[:5],
    }

    return score, {key: value for key, value in result.items() if value is not None}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "service": "skillmap-api",
        "stack": "flask",
        "database": "postgresql" if is_database_enabled() else "memory"
    })

@app.route('/api/profile', methods=['GET'])
def profile():
    user_context = get_current_user_context()
    if not user_context:
        return jsonify({"error": "Sign in is required to access profile data."}), 401

    profile_data = get_user_profile(user_context)
    if profile_data is None:
        return jsonify({"error": "Profile data is unavailable."}), 500

    return jsonify(profile_data)

@app.route('/api/profile/cv-analyses', methods=['GET'])
def profile_cv_analyses():
    user_context = get_current_user_context()
    if not user_context:
        return jsonify({"error": "Sign in is required to access CV scan history."}), 401

    return jsonify({"history": get_user_cv_history(user_context)})

@app.route('/api/cvs', methods=['POST'])
@app.route('/api/cv/upload', methods=['POST'])
def cv_upload():
    try:
        domain = request.form.get("domain") or request.args.get("domain") or "technology"
        target_role = request.form.get("targetRole") or request.args.get("targetRole") or "fullstack-web-developer"
        target_job = request.form.get("targetJob")
        if target_job is None:
            target_job = request.args.get("targetJob")
        
        file = request.files.get("cv")
        if file and not is_pdf_upload(file):
            return jsonify({"error": "CV hanya boleh diupload dalam format PDF (.pdf)."}), 400

        file_obj = None
        if file:
            file_obj = {
                "originalname": file.filename,
                "mimetype": file.mimetype,
                "buffer": file.read()
            }
        file_name = file.filename if file else "profile-text"
        file_size = len(file_obj["buffer"]) if file_obj else 0
        form_body = request.form.to_dict()
        extracted_pdf_text = extract_pdf_text(file_obj) if file_obj else ""
        body_text = str(form_body.get("text", "")).strip()
        extracted_text = "\n\n".join([body_text, extracted_pdf_text]).strip() if extracted_pdf_text else extract_text_from_upload(None, form_body)
        fallback_analysis = analyze_cv_text(extracted_text, {"domain": domain, "targetRole": target_role})
        analysis_options = {"domain": domain, "targetRole": target_role}
        if target_job is not None:
            analysis_options["targetJob"] = target_job
        analysis = enrich_cv_analysis_with_ai(extracted_text, fallback_analysis, analysis_options)

        save_cv_analysis(
            file_name=file_name,
            file_size=file_size,
            analysis=analysis,
            user_context=get_current_user_context()
        )

        return jsonify({
            "fileName": file_name,
            "fileSize": file_size,
            "sourceFormat": "pdf" if file_obj else "text",
            "extractedCvText": extracted_pdf_text,
            "aiReadableText": extracted_text,
            **analysis
        }), 201
    except AIServiceUnavailable as e:
        print("AI service unavailable:", e)
        return jsonify({"error": str(e)}), 503
    except ValueError as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/quiz-questions', methods=['GET'])
@app.route('/api/quiz/questions', methods=['GET'])
def quiz_questions():
    domain = request.args.get("domain", "technology")
    target_role = request.args.get("targetRole", "fullstack-web-developer")
    
    return jsonify({
        "questions": get_quiz_questions(domain, target_role)
    })

@app.route('/api/career-fit-quizzes', methods=['POST'])
@app.route('/api/quiz/career-fit', methods=['POST'])
def career_fit_quiz():
    try:
        payload = request.json or {}
        fallback_quiz = generate_career_fit_quiz(payload)
        quiz = enrich_career_fit_quiz_with_openrouter(payload, fallback_quiz)
        return jsonify({"question": quiz}), 201
    except AIServiceUnavailable as e:
        print("AI service unavailable:", e)
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/quiz-attempts', methods=['POST'])
@app.route('/api/quiz/submit', methods=['POST'])
def quiz_submit():
    try:
        payload = request.json or {}
        domain = payload.get("domain") or request.args.get("domain") or "technology"
        target_role = payload.get("targetRole") or request.args.get("targetRole") or "fullstack-web-developer"

        if is_career_fit_quiz_payload(payload):
            score, result = build_career_fit_quiz_result(payload, domain, target_role)
        else:
            result = score_quiz(payload.get("answers", []), {
                "domain": domain,
                "targetRole": target_role
            })
            score = result["score"]

        saved_attempt = save_quiz_result(score=score, result=result, user_context=get_current_user_context())
        return jsonify({**result, "saved": True, "attemptId": saved_attempt.get("id")}), 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/career-results', methods=['POST'])
@app.route('/api/quiz/final-result', methods=['POST'])
def quiz_final_result():
    try:
        payload = request.json or {}
        result = create_final_career_conclusion(payload)
        return jsonify(result), 201
    except AIServiceUnavailable as e:
        print("AI service unavailable:", e)
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/recommendations', methods=['POST'])
def recommendations():
    try:
        payload = request.json or {}
        fallback_recommendation = create_personalized_recommendation(payload)
        recommendation = enrich_recommendation_with_ai(payload, fallback_recommendation)
        return jsonify(recommendation), 201
    except AIServiceUnavailable as e:
        print("AI service unavailable:", e)
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard-snapshots/overview', methods=['GET'])
@app.route('/api/dashboard/overview', methods=['GET'])
def dashboard_overview():
    try:
        snapshot = get_dashboard_snapshot()
        activity = get_latest_activity()
        return jsonify({**snapshot, "activity": activity})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<user_id>/dashboard-snapshot', methods=['GET'])
@app.route('/api/dashboard/<user_id>', methods=['GET'])
def dashboard_user(user_id):
    try:
        snapshot = get_dashboard_snapshot()
        activity = get_latest_activity()
        
        snapshot["user"]["id"] = user_id
        return jsonify({**snapshot, "activity": activity})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/leads', methods=['POST'])
def leads():
    try:
        payload = request.json or {}
        email = str(payload.get("email", "")).strip().lower()

        if not email or "@" not in email:
            return jsonify({"error": "A valid email address is required."}), 400

        lead = save_lead(
            email=email,
            target_role=payload.get("targetRole")
        )

        return jsonify({
            "message": "Journey request received.",
            "lead": lead
        }), 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/project-requirements', methods=['GET'])
@app.route('/api/project/requirements', methods=['GET'])
def project_requirements():
    return jsonify({
        "project": "SkillMap - Navigator Pembelajaran Keterampilan yang Dipersonalisasi",
        "mvpFeatures": [
            "JobStreet-style biodata capture before CV scanning",
            "PDF-only CV upload with text extraction for AI scanning",
            "AI job matching with percentage scores",
            "Career-fit mini quiz based on top job matches",
            "Skill gap mapping against target role",
            "Career recommendation or e-course learning option",
            "Result dashboard with persisted activity"
        ],
        "technicalCoverage": {
            "frontend": ["React", "Vite", "Axios networking calls", "responsive workflow UI"],
            "backend": ["Flask REST API", "RESTful URL convention", "PostgreSQL persistence with memory fallback"],
            "aiMl": [
                "TensorFlow-ready model service contract",
                "skill extraction and recommendation contract",
                "external AI service" if is_ai_service_enabled() else "local deterministic analysis service"
            ],
            "dataScience": ["dataset/EDA/dashboard integration contract", "business-question driven insights"]
        }
    })

if __name__ == '__main__':
    app.run(port=port)
