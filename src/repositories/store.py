from datetime import datetime
from sqlalchemy import text
from src.db import ENGINE, session_scope, get_or_create_demo_user, get_or_create_skill, Cv, UserSkill, LearningPath, QuizAttempt

memory_store = {
    "cvAnalyses": [],
    "quizAttempts": [],
    "leads": []
}

def is_database_enabled():
    return ENGINE is not None

def save_cv_analysis(file_name, file_size=0, analysis=None):
    if analysis is None:
        analysis = {}

    record = {
        "id": len(memory_store["cvAnalyses"]) + 1,
        "fileName": file_name,
        "fileSize": file_size,
        "analysis": analysis,
        "createdAt": datetime.utcnow().isoformat() + "Z"
    }

    memory_store["cvAnalyses"].append(record)

    if not is_database_enabled():
        return record

    try:
        with session_scope() as session:
            user = get_or_create_demo_user(session)

            cv_record = Cv(user_id=user.id, file_url=f"/uploads/{file_name}", file_name=file_name)
            session.add(cv_record)
            session.flush()

            for skill_name in analysis.get("extractedSkills", []):
                skill = get_or_create_skill(session, skill_name)
                # handle upsert or ignore, simplified here:
                existing_skill = session.query(UserSkill).filter_by(user_id=user.id, skill_id=skill.id).first()
                if existing_skill:
                    existing_skill.proficiency = 2
                    existing_skill.source = "cv"
                else:
                    session.add(UserSkill(user_id=user.id, skill_id=skill.id, proficiency=2, source="cv"))

            session.add(
                LearningPath(
                    user_id=user.id,
                    recommendation=analysis,
                )
            )

            return {**record, "userId": user.id, "cvId": cv_record.id}
    except Exception as e:
        print("Database error in save_cv_analysis:", e)
        return record

def save_quiz_result(score, result):
    record = {
        "id": len(memory_store["quizAttempts"]) + 1,
        "score": score,
        "result": result,
        "createdAt": datetime.utcnow().isoformat() + "Z"
    }

    memory_store["quizAttempts"].append(record)

    if not is_database_enabled():
        return record

    try:
        with session_scope() as session:
            user = get_or_create_demo_user(session)
            session.add(QuizAttempt(user_id=user.id, score=score, result=result))
            return {**record, "userId": user.id}
    except Exception as e:
        print("Database error in save_quiz_result:", e)
        return record

def save_lead(email, target_role=None):
    record = {
        "id": len(memory_store["leads"]) + 1,
        "email": email,
        "targetRole": target_role,
        "createdAt": datetime.utcnow().isoformat() + "Z"
    }

    memory_store["leads"].append(record)

    if not is_database_enabled():
        return record

    try:
        with ENGINE.connect() as conn:
            conn.execute(
                text("INSERT INTO leads (email, target_role) VALUES (:email, :target_role)"),
                {"email": email, "target_role": target_role}
            )
            conn.commit()
    except Exception as e:
        print("Database error in save_lead:", e)
    
    return record

def get_latest_activity():
    if not is_database_enabled():
        return {
            "cvAnalyses": list(reversed(memory_store["cvAnalyses"][-5:])),
            "quizAttempts": list(reversed(memory_store["quizAttempts"][-5:])),
            "leads": list(reversed(memory_store["leads"][-5:]))
        }

    try:
        with ENGINE.connect() as conn:
            cvs = conn.execute(text('SELECT id, file_name AS "fileName", created_at AS "createdAt" FROM cvs ORDER BY created_at DESC LIMIT 5')).mappings().all()
            quizzes = conn.execute(text('SELECT id, score, result, created_at AS "createdAt" FROM quiz_attempts ORDER BY created_at DESC LIMIT 5')).mappings().all()
            try:
                leads = conn.execute(text('SELECT id, email, target_role AS "targetRole", created_at AS "createdAt" FROM leads ORDER BY created_at DESC LIMIT 5')).mappings().all()
            except Exception:
                leads = []

            # Format datetime objects for JSON serialization
            def format_rows(rows):
                res = []
                for row in rows:
                    r = dict(row)
                    if "createdAt" in r and r["createdAt"]:
                        r["createdAt"] = r["createdAt"].isoformat() + "Z"
                    res.append(r)
                return res

            return {
                "cvAnalyses": format_rows(cvs),
                "quizAttempts": format_rows(quizzes),
                "leads": format_rows(leads)
            }
    except Exception as e:
        print("Database error in get_latest_activity:", e)
        return {
            "cvAnalyses": list(reversed(memory_store["cvAnalyses"][-5:])),
            "quizAttempts": list(reversed(memory_store["quizAttempts"][-5:])),
            "leads": list(reversed(memory_store["leads"][-5:]))
        }
