from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm.attributes import flag_modified
from src.db import ENGINE, session_scope, get_or_create_authenticated_user, get_or_create_skill, Cv, UserSkill, LearningPath, QuizAttempt

memory_store = {
    "cvAnalyses": [],
    "quizAttempts": [],
    "leads": []
}

def is_database_enabled():
    return ENGINE is not None

def get_owner_key(user_context=None):
    return user_context.get("external_id") if user_context else "anonymous"


def save_cv_analysis(file_name, file_size=0, analysis=None, user_context=None):
    if analysis is None:
        analysis = {}

    record = {
        "id": len(memory_store["cvAnalyses"]) + 1,
        "fileName": file_name,
        "fileSize": file_size,
        "analysis": analysis,
        "ownerId": get_owner_key(user_context),
        "createdAt": datetime.utcnow().isoformat() + "Z"
    }

    memory_store["cvAnalyses"].append(record)

    if not is_database_enabled():
        return record

    try:
        with session_scope() as session:
            user = get_or_create_authenticated_user(session, user_context)

            cv_record = Cv(user_id=user.id, file_url=f"/uploads/{file_name}", file_name=file_name, analysis=analysis)
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


def update_latest_cv_analysis(final_result, user_context=None):
    """Merge final career conclusion ke record CV terbaru milik user."""
    if not final_result:
        return

    # Field-field yang dipakai halaman riwayat di frontend
    merged = {"finalResult": final_result}
    if final_result.get("recommendedRoleName"):
        merged["recommendedCareer"] = final_result["recommendedRoleName"]
    if final_result.get("summary"):
        merged["summary"] = final_result["summary"]
    if final_result.get("confidenceScore") is not None:
        merged["careerMatchScore"] = final_result["confidenceScore"]
    if isinstance(final_result.get("nextFocus"), list) and final_result["nextFocus"]:
        merged["roadmap"] = final_result["nextFocus"]

    # Update in-memory store
    owner_id = get_owner_key(user_context)
    user_cvs = [item for item in memory_store["cvAnalyses"] if item.get("ownerId") == owner_id]
    if user_cvs:
        latest = user_cvs[-1]
        latest["analysis"] = {**(latest.get("analysis") or {}), **merged}

    if not is_database_enabled():
        return

    try:
        with session_scope() as session:
            user = get_or_create_authenticated_user(session, user_context)
            latest_cv = (
                session.query(Cv)
                .filter_by(user_id=user.id)
                .order_by(Cv.created_at.desc())
                .first()
            )
            if latest_cv:
                existing = latest_cv.analysis or {}
                latest_cv.analysis = {**existing, **merged}
                flag_modified(latest_cv, "analysis")
    except Exception as e:
        print("Database error in update_latest_cv_analysis:", e)

def save_quiz_result(score, result, user_context=None):
    record = {
        "id": len(memory_store["quizAttempts"]) + 1,
        "score": score,
        "result": result,
        "ownerId": get_owner_key(user_context),
        "createdAt": datetime.utcnow().isoformat() + "Z"
    }

    memory_store["quizAttempts"].append(record)

    if not is_database_enabled():
        return record

    try:
        with session_scope() as session:
            user = get_or_create_authenticated_user(session, user_context)
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

def get_user_profile(user_context):
    if not user_context:
        return None

    if not is_database_enabled():
        owner_id = get_owner_key(user_context)
        return {
            "user": {
                "name": user_context.get("name"),
                "email": user_context.get("email"),
                "externalId": owner_id,
            },
            "stats": {
                "cvScanCount": len([item for item in memory_store["cvAnalyses"] if item.get("ownerId") == owner_id]),
                "quizAttemptCount": len([item for item in memory_store["quizAttempts"] if item.get("ownerId") == owner_id]),
            }
        }

    try:
        with session_scope() as session:
            user = get_or_create_authenticated_user(session, user_context)
            cv_count = session.query(Cv).filter_by(user_id=user.id).count()
            quiz_count = session.query(QuizAttempt).filter_by(user_id=user.id).count()
            return {
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "externalId": user.external_id,
                    "authProvider": user.auth_provider,
                    "createdAt": user.created_at.isoformat() + "Z" if user.created_at else None,
                },
                "stats": {
                    "cvScanCount": cv_count,
                    "quizAttemptCount": quiz_count,
                }
            }
    except Exception as e:
        print("Database error in get_user_profile:", e)
        return None

def get_user_cv_history(user_context, limit=20):
    if not user_context:
        return []

    if not is_database_enabled():
        owner_id = get_owner_key(user_context)
        records = [item for item in memory_store["cvAnalyses"] if item.get("ownerId") == owner_id]
        return list(reversed(records[-limit:]))

    try:
        with session_scope() as session:
            user = get_or_create_authenticated_user(session, user_context)
            rows = (
                session.query(Cv)
                .filter_by(user_id=user.id)
                .order_by(Cv.created_at.desc())
                .limit(limit)
                .all()
            )
            return [
                {
                    "id": row.id,
                    "fileName": row.file_name,
                    "fileUrl": row.file_url,
                    "analysis": row.analysis or {},
                    "createdAt": row.created_at.isoformat() + "Z" if row.created_at else None,
                }
                for row in rows
            ]
    except Exception as e:
        print("Database error in get_user_cv_history:", e)
        return []

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
