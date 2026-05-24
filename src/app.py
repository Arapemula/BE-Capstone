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
    get_dashboard_snapshot,
    get_quiz_questions,
    get_role_profiles,
    score_quiz
)
from src.services.ai_client import (
    enrich_cv_analysis_with_ai,
    enrich_recommendation_with_ai,
    is_ai_service_enabled
)
from src.repositories.store import (
    is_database_enabled,
    save_cv_analysis,
    save_lead,
    save_quiz_result,
    get_latest_activity
)
from src.db import init_database

app = Flask(__name__)
port = int(os.getenv("PORT", 3001))

def get_cors_origin():
    raw = os.getenv("CORS_ORIGIN", "http://localhost:5173")
    if raw.strip() == "*":
        return "*"
    return [origin.strip() for origin in raw.split(",") if origin.strip()]

cors_origins = get_cors_origin()
CORS(app, origins=cors_origins)

# Initialize database
init_database()

def is_pdf_upload(file):
    filename = (file.filename or "").lower()
    mimetype = (file.mimetype or "").lower()
    return filename.endswith(".pdf") or mimetype == "application/pdf"

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "service": "skillmap-api",
        "stack": "flask",
        "database": "postgresql" if is_database_enabled() else "memory"
    })

@app.route('/api/roles', methods=['GET'])
def roles():
    return jsonify({"roles": get_role_profiles()})

@app.route('/api/cv/upload', methods=['POST'])
def cv_upload():
    try:
        domain = request.form.get("domain") or request.args.get("domain") or "technology"
        target_role = request.form.get("targetRole") or request.args.get("targetRole") or "fullstack-web-developer"
        
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
        analysis = enrich_cv_analysis_with_ai(
            extracted_text,
            fallback_analysis,
            {"domain": domain, "targetRole": target_role}
        )

        save_cv_analysis(
            file_name=file_name,
            file_size=file_size,
            analysis=analysis
        )

        return jsonify({
            "fileName": file_name,
            "fileSize": file_size,
            "sourceFormat": "pdf" if file_obj else "text",
            "extractedCvText": extracted_pdf_text,
            "aiReadableText": extracted_text,
            **analysis
        }), 201
    except ValueError as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/quiz/questions', methods=['GET'])
def quiz_questions():
    domain = request.args.get("domain", "technology")
    target_role = request.args.get("targetRole", "fullstack-web-developer")
    
    return jsonify({
        "questions": get_quiz_questions(domain, target_role)
    })

@app.route('/api/quiz/submit', methods=['POST'])
def quiz_submit():
    try:
        payload = request.json or {}
        domain = payload.get("domain") or request.args.get("domain") or "technology"
        target_role = payload.get("targetRole") or request.args.get("targetRole") or "fullstack-web-developer"
        
        result = score_quiz(payload.get("answers", []), {
            "domain": domain,
            "targetRole": target_role
        })

        save_quiz_result(score=result["score"], result=result)
        return jsonify(result), 201
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
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/overview', methods=['GET'])
def dashboard_overview():
    try:
        snapshot = get_dashboard_snapshot()
        activity = get_latest_activity()
        return jsonify({**snapshot, "activity": activity})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

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

@app.route('/api/project/requirements', methods=['GET'])
def project_requirements():
    return jsonify({
        "project": "SkillMap - Navigator Pembelajaran Keterampilan yang Dipersonalisasi",
        "mvpFeatures": [
            "JobStreet-style biodata capture before CV scanning",
            "PDF-only CV upload with text extraction for AI scanning",
            "AI job matching with percentage scores",
            "YES/NO mini quiz branching",
            "Skill gap mapping against target role",
            "Career recommendation or e-course learning option",
            "Result dashboard with persisted activity"
        ],
        "technicalCoverage": {
            "frontend": ["React", "Vite", "Axios networking calls", "responsive mockup and layout"],
            "backend": ["Flask REST API", "RESTful URL convention", "PostgreSQL persistence with memory fallback"],
            "aiMl": [
                "TensorFlow-ready model service contract",
                "skill extraction and recommendation contract",
                "external AI service" if is_ai_service_enabled() else "local fallback AI service"
            ],
            "dataScience": ["dataset/EDA/dashboard integration contract", "business-question driven insights"]
        }
    })

if __name__ == '__main__':
    app.run(port=port)
