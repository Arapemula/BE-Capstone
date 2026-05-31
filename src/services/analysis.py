import json
import os
from io import BytesIO

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIRS = [
    os.path.join(BASE_DIR, "..", "data"),
    os.path.join(BASE_DIR, "..", "..", "..", "..", "services", "ai", "src", "data"),
]

DEFAULT_TAXONOMIES = {
    "technology": {
        "JavaScript": ["javascript", "js", "ecmascript"],
        "React": ["react", "next", "vite"],
        "Express": ["express", "node", "nodejs"],
        "REST API": ["rest", "api", "endpoint", "http"],
        "PostgreSQL": ["postgres", "postgresql", "sql", "database"],
        "TensorFlow": ["tensorflow", "keras", "deep learning"],
        "NLP": ["nlp", "natural language", "text classification"],
        "Deployment": ["deployment", "deploy", "vercel", "netlify", "render"],
        "Time Management": ["time management", "manajemen waktu", "atur waktu", "deadline", "prioritas"],
        "Leadership": ["leadership", "kepemimpinan", "lead", "koordinasi", "memimpin"],
        "Project Planning": ["project planning", "perencanaan proyek", "timeline", "milestone", "sprint"],
        "Risk Management": ["risk management", "manajemen risiko", "risiko", "mitigasi"]
    }
}

DEFAULT_QUIZ_BANK = {
    "technology": [
        {
            "id": "tq1",
            "prompt": "Seberapa nyaman kamu membangun fitur web interaktif dengan JavaScript?",
            "options": ["Belum pernah", "Paham dasar", "Sering praktik", "Mampu memimpin implementasi"]
        },
        {
            "id": "tq2",
            "prompt": "Seberapa siap kamu membuat REST API dengan validasi dan error handling?",
            "options": ["Belum siap", "Masih belajar", "Cukup siap", "Sangat siap"]
        },
        {
            "id": "tq3",
            "prompt": "Bagaimana pengalamanmu menggunakan database relasional?",
            "options": ["Belum pernah", "Query dasar", "Desain tabel sederhana", "Optimasi dan relasi kompleks"]
        }
    ]
}

ROLE_PROFILES = [
    {
        "id": "fullstack-web-developer",
        "name": "Junior Full-Stack Web Developer",
        "domain": "technology",
        "audience": "Mahasiswa tingkat akhir dan fresh graduates",
        "requiredSkills": ["JavaScript", "React", "Express", "REST API", "PostgreSQL", "Deployment", "Testing"],
        "businessGoal": "Siap melamar role full-stack junior dengan portofolio end-to-end.",
        "marketSignals": ["React + API integration", "RESTful backend", "database persistence", "public deployment"]
    },
    {
        "id": "ai-engineer",
        "name": "Junior AI Engineer",
        "domain": "technology",
        "audience": "Fresh graduates yang ingin masuk ke bidang AI/NLP",
        "requiredSkills": ["Python", "TensorFlow", "NLP", "Model Evaluation", "TensorBoard", "Model Serving"],
        "businessGoal": "Mampu membangun model NLP untuk ekstraksi skill dan rekomendasi learning path.",
        "marketSignals": ["TensorFlow Functional API", "custom training loop", "model export", "inference API"]
    },
    {
        "id": "data-scientist",
        "name": "Junior Data Scientist",
        "domain": "technology",
        "audience": "Mahasiswa/fresh graduates yang fokus pada analisis data",
        "requiredSkills": ["Python", "Data Wrangling", "EDA", "Feature Engineering", "A/B Testing", "Streamlit"],
        "businessGoal": "Mampu mengubah dataset CV, job description, dan quiz menjadi insight siap dashboard.",
        "marketSignals": ["data cleaning", "business questions", "explanatory analysis", "interactive dashboard"]
    },
    {
        "id": "project-manager-digital",
        "name": "Junior Project Manager Digital",
        "domain": "business",
        "audience": "Fresh graduates yang kuat di koordinasi, organisasi, dan komunikasi tim",
        "requiredSkills": ["Time Management", "Leadership", "Communication", "Project Planning", "Problem Solving", "Risk Management"],
        "businessGoal": "Siap masuk role coordinator, management trainee, atau junior project manager.",
        "marketSignals": ["time management", "team coordination", "timeline ownership", "risk tracking"]
    }
]

ROADMAP_BY_SKILL = {
    "JavaScript": "Practice JavaScript fundamentals through form, state, and validation tasks.",
    "React": "Build the SkillMap frontend flow with reusable React components and responsive states.",
    "Express": "Create Express routes for CV upload, quiz submission, recommendations, and dashboard data.",
    "REST API": "Document RESTful endpoints and test success, empty, and error responses.",
    "PostgreSQL": "Persist users, CV analysis, quiz attempts, and learning paths in PostgreSQL.",
    "Deployment": "Deploy the frontend and API, then connect production environment variables.",
    "Testing": "Run feature checks for upload, quiz, dashboard, and API failure states.",
    "Python": "Prepare Python notebooks/scripts for preprocessing CV and job description datasets.",
    "TensorFlow": "Train a TensorFlow model with a production-ready export format.",
    "NLP": "Build text preprocessing and skill extraction pipelines for CV content.",
    "Model Evaluation": "Measure model quality and compare predictions against labeled job requirements.",
    "TensorBoard": "Log training metrics to TensorBoard for monitoring and final reporting.",
    "Model Serving": "Serve model inference from a Flask or FastAPI service.",
    "Data Wrangling": "Gather, assess, clean, and document dataset quality before modeling.",
    "EDA": "Create visual analysis of skill distributions and role demand patterns.",
    "Feature Engineering": "Create role-skill match, quiz readiness, and gap severity features.",
    "A/B Testing": "Run a Python A/B test for two recommendation presentation variants.",
    "Streamlit": "Deploy an interactive Streamlit dashboard for data insight and conclusions.",
    "Time Management": "Latih pembagian prioritas mingguan, deadline tracking, dan refleksi progres harian.",
    "Leadership": "Ambil peran kecil sebagai koordinator tim dan dokumentasikan cara kamu membagi tugas.",
    "Communication": "Latih update progres singkat, notulen meeting, dan cara menyampaikan risiko ke stakeholder.",
    "Project Planning": "Buat timeline proyek sederhana dengan milestone, owner, status, dan risiko.",
    "Problem Solving": "Dokumentasikan masalah, opsi solusi, keputusan, dan hasil dari satu proyek kecil.",
    "Risk Management": "Buat risk register sederhana untuk proyek tim atau capstone."
}

COURSE_BY_SKILL = {
    "JavaScript": {
        "platform": "Dicoding",
        "title": "Belajar Dasar Pemrograman JavaScript",
        "url": "https://www.dicoding.com/academies/256-belajar-dasar-pemrograman-javascript",
        "reason": "Cocok untuk memperkuat dasar logika, DOM, dan interaksi web sebelum lanjut React."
    },
    "React": {
        "platform": "Dicoding",
        "title": "Belajar Membuat Aplikasi Web dengan React",
        "url": "https://www.dicoding.com/academies/403-belajar-membuat-aplikasi-web-dengan-react",
        "reason": "Relevan untuk menutup gap frontend modern dan membuat portofolio aplikasi."
    },
    "Express": {
        "platform": "Dicoding",
        "title": "Belajar Membuat Aplikasi Back-End untuk Pemula",
        "url": "https://www.dicoding.com/academies/261-belajar-back-end-pemula-dengan-javascript",
        "reason": "Membantu memahami server, routing, API, dan pola backend dasar."
    },
    "REST API": {
        "platform": "Postman Academy",
        "title": "API Fundamentals Student Expert",
        "url": "https://academy.postman.com/",
        "reason": "Langsung relevan untuk membuat endpoint, request-response, validasi, dan error handling."
    },
    "PostgreSQL": {
        "platform": "freeCodeCamp",
        "title": "Relational Database Certification",
        "url": "https://www.freecodecamp.org/learn/relational-database",
        "reason": "Membantu memahami SQL, relasi tabel, dan database relasional untuk aplikasi kerja."
    },
    "Deployment": {
        "platform": "AWS Skill Builder",
        "title": "AWS Cloud Practitioner Essentials",
        "url": "https://explore.skillbuilder.aws/learn/course/external/view/elearning/134/aws-cloud-practitioner-essentials",
        "reason": "Cocok untuk mengenal cloud, deployment, dan istilah produksi sebelum publish project."
    },
    "Testing": {
        "platform": "Dicoding",
        "title": "Belajar Dasar Quality Assurance",
        "url": "https://www.dicoding.com/academies/list",
        "reason": "Membantu membangun kebiasaan testing dan validasi fitur sebelum melamar."
    },
    "Python": {
        "platform": "Dicoding",
        "title": "Memulai Pemrograman dengan Python",
        "url": "https://www.dicoding.com/academies/list",
        "reason": "Cocok untuk dasar scripting, data, dan fondasi AI/Data Science."
    },
    "TensorFlow": {
        "platform": "DeepLearning.AI",
        "title": "TensorFlow Developer Professional Certificate",
        "url": "https://www.deeplearning.ai/courses/tensorflow-developer-professional-certificate/",
        "reason": "Membantu memahami training model, evaluasi, dan deployment model sederhana."
    },
    "NLP": {
        "platform": "Coursera",
        "title": "Natural Language Processing Specialization",
        "url": "https://www.coursera.org/specializations/natural-language-processing",
        "reason": "Relevan untuk ekstraksi skill dari CV dan pemrosesan teks."
    },
    "Model Evaluation": {
        "platform": "Google Cloud Skills Boost",
        "title": "Machine Learning Evaluation Basics",
        "url": "https://www.cloudskillsboost.google/",
        "reason": "Membantu membaca metrik model dan memilih model yang layak dipakai."
    },
    "Data Wrangling": {
        "platform": "DQLab",
        "title": "Data Analyst Career Track",
        "url": "https://dqlab.id/",
        "reason": "Cocok untuk latihan cleaning, transformasi data, dan workflow analisis."
    },
    "EDA": {
        "platform": "DQLab",
        "title": "Exploratory Data Analysis with Python",
        "url": "https://dqlab.id/",
        "reason": "Membantu mengubah dataset menjadi insight yang bisa dijelaskan."
    },
    "Feature Engineering": {
        "platform": "Kaggle Learn",
        "title": "Feature Engineering",
        "url": "https://www.kaggle.com/learn/feature-engineering",
        "reason": "Cocok untuk memahami cara membuat fitur yang meningkatkan kualitas model."
    },
    "A/B Testing": {
        "platform": "Coursera",
        "title": "A/B Testing and Experimentation",
        "url": "https://www.coursera.org/search?query=a%2Fb%20testing",
        "reason": "Membantu memahami eksperimen produk dan pengambilan keputusan berbasis data."
    },
    "Streamlit": {
        "platform": "freeCodeCamp",
        "title": "Streamlit Dashboard Tutorial",
        "url": "https://www.freecodecamp.org/news/tag/streamlit/",
        "reason": "Cocok untuk membuat dashboard data yang bisa langsung didemokan."
    },
    "Time Management": {
        "platform": "Coursera",
        "title": "Manajemen Waktu dan Prioritas Kerja",
        "url": "https://www.coursera.org/search?query=time%20management",
        "reason": "Membantu membangun kebiasaan deadline tracking sebelum masuk role manager."
    },
    "Leadership": {
        "platform": "LinkedIn Learning",
        "title": "Dasar Kepemimpinan dan Koordinasi Tim",
        "url": "https://www.linkedin.com/learning/topics/leadership-and-management",
        "reason": "Cocok untuk melatih cara membagi tugas dan menjaga komunikasi tim."
    },
    "Communication": {
        "platform": "TOEFL Preparation",
        "title": "TOEFL Speaking and Professional Communication",
        "url": "https://www.ets.org/toefl/test-takers/ibt/prepare.html",
        "reason": "Membantu memperkuat bahasa Inggris, presentasi, dan komunikasi profesional."
    },
    "Project Planning": {
        "platform": "Coursera",
        "title": "Google Project Management: Foundations",
        "url": "https://www.coursera.org/learn/project-management-foundations",
        "reason": "Langsung relevan untuk role coordinator atau junior project manager."
    },
    "Problem Solving": {
        "platform": "Dicoding",
        "title": "Memulai Dasar Pemrograman untuk Menjadi Pengembang Software",
        "url": "https://www.dicoding.com/academies/list",
        "reason": "Membantu melatih pola pikir problem solving, breakdown masalah, dan solusi bertahap."
    },
    "Risk Management": {
        "platform": "PMI",
        "title": "Project Risk Management Basics",
        "url": "https://www.pmi.org/learning/training-development",
        "reason": "Membantu membaca hambatan proyek lebih awal."
    }
}

def load_json(filename, fallback):
    for data_dir in DATA_DIRS:
        try:
            with open(os.path.abspath(os.path.join(data_dir, filename)), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            continue
    return fallback

taxonomies = load_json("taxonomies.json", DEFAULT_TAXONOMIES)
quiz_bank = load_json("quizBank.json", DEFAULT_QUIZ_BANK)

def normalize_text(value=""):
    return str(value).lower() if value else ""

def get_role_profile(target_role="fullstack-web-developer"):
    role = find_role_profile(target_role)
    return role or ROLE_PROFILES[0]

def find_role_profile(target_role="fullstack-web-developer"):
    for role in ROLE_PROFILES:
        if role["id"] == target_role:
            return role
    return None

def format_role_label(value=""):
    text = str(value or "").strip().replace("-", " ")
    return " ".join(part.upper() if part.lower() in {"ai", "api", "it", "ml", "qa", "sql", "ui", "ux"} else part.capitalize() for part in text.split())

def get_domain_taxonomy(domain="technology"):
    base = taxonomies.get(domain) or taxonomies.get("technology") or DEFAULT_TAXONOMIES["technology"]
    expanded = dict(base)

    for role in ROLE_PROFILES:
        if role.get("domain") != domain:
            continue

        for skill in role.get("requiredSkills", []):
            if skill not in expanded:
                expanded[skill] = [skill.lower()]

    return expanded

def extract_skills(input_text="", domain="technology"):
    text = normalize_text(input_text)
    detected_skills = []
    taxonomy = get_domain_taxonomy(domain)

    for skill, keywords in taxonomy.items():
        normalized_keywords = keywords if isinstance(keywords, list) else [skill]
        for keyword in normalized_keywords:
            if normalize_text(keyword) in text:
                detected_skills.append(skill)
                break

    return list(dict.fromkeys(detected_skills)) # return unique

def create_roadmap(skill_gaps, role_profile):
    has_gaps = len(skill_gaps) > 0
    focus_gaps = skill_gaps if has_gaps else role_profile.get("requiredSkills", [])[:3]

    roadmap = []
    for index, skill in enumerate(focus_gaps[:5]):
        roadmap.append({
            "id": f"step-{index + 1}",
            "title": f"Close {skill} gap" if has_gaps else f"Polish {skill} proof",
            "focus": skill,
            "duration": "1-2 weeks" if index < 2 else "2-3 weeks",
            "action": ROADMAP_BY_SKILL.get(skill) or f"Build one practical project artifact that proves {skill}."
        })
    return roadmap

def build_recommendation_texts(roadmap, role_profile):
    roadmap_texts = [step["action"] for step in roadmap]
    return [
        f"Focus on {role_profile['name']} requirements before applying.",
    ] + roadmap_texts[:3] + [
        "Publish progress as portfolio evidence for recruiters."
    ]

def create_career_recommendation(role_profile, readiness_score):
    entry_label = "langsung mulai melamar role junior" if readiness_score >= 75 else "mulai dari magang, trainee, atau project assistant"
    return {
        "title": role_profile["name"],
        "summary": f"Kamu paling dekat dengan jalur {role_profile['name']}; {entry_label} sambil memperkuat bukti portofolio.",
        "nextSteps": [
            f"Siapkan CV yang menonjolkan skill inti: {', '.join(role_profile.get('requiredSkills', [])[:3])}.",
            "Buat satu studi kasus singkat dari proyek, organisasi, magang, atau capstone.",
            "Latih cerita interview dengan format masalah, aksi, hasil, dan pelajaran."
        ]
    }

def create_course_recommendations(skill_gaps, role_profile):
    focus_skills = skill_gaps[:4] if skill_gaps else role_profile.get("requiredSkills", [])[:3]
    courses = []

    for skill in focus_skills:
        default_course = {
            "platform": "Dicoding / Coursera",
            "title": f"Dasar {skill} untuk Karier Entry-Level",
            "url": "https://www.coursera.org/search?query=career%20skills",
            "reason": f"Menutup gap {skill} dengan materi terstruktur sebelum mengambil rekomendasi karier utama."
        }
        course = COURSE_BY_SKILL.get(skill, default_course)
        courses.append({
            "skill": skill,
            **course
        })

    return courses

def calculate_readiness_score(extracted_skills, required_skills, quiz_score=None):
    required_set = {skill.lower() for skill in required_skills}
    matched_count = sum(1 for skill in extracted_skills if skill.lower() in required_set)
    cv_score = round((matched_count / max(len(required_skills), 1)) * 100)

    if isinstance(quiz_score, (int, float)):
        return round(cv_score * 0.6 + quiz_score * 0.4)

    return max(0, min(100, cv_score))

def has_actionable_match(match):
    return (
        clamp_number(match.get("matchScore"), 0, 100) > 0
        or bool(compact_skill_items(match.get("matchedSkills"), 1))
    )

def readiness_label(score):
    if score >= 85:
        return "job-ready"
    if score >= 65:
        return "nearly ready"
    return "foundation"

def get_role_profiles():
    return ROLE_PROFILES

def extract_pdf_text(file_obj):
    if PdfReader is None:
        raise ValueError("PDF parser belum terpasang. Jalankan `pip install pypdf` atau install requirements backend.")

    file_data = file_obj.get("buffer", b"")
    try:
        reader = PdfReader(BytesIO(file_data))
        page_texts = []
        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                page_texts.append(text.strip())
        extracted_text = "\n\n".join(page_texts).strip()
    except Exception as exc:
        raise ValueError("File PDF gagal dibaca. Pastikan PDF tidak rusak atau bukan hasil scan gambar.") from exc

    if not extracted_text:
        raise ValueError("Teks tidak ditemukan di PDF. Gunakan PDF berbasis teks, bukan scan gambar.")

    return extracted_text

def extract_text_from_upload(file_obj=None, body=None):
    if body is None:
        body = {}

    body_text = str(body.get("text", "")).strip()

    if file_obj:
        mimetype = file_obj.get("mimetype", "")
        originalname = file_obj.get("originalname", "")

        if mimetype == "application/pdf" or originalname.lower().endswith(".pdf"):
            pdf_text = extract_pdf_text(file_obj)
            return "\n\n".join([body_text, pdf_text]).strip() if body_text else pdf_text

        raise ValueError("CV hanya boleh diupload dalam format PDF (.pdf).")

    if body_text:
        return body_text

    raise ValueError("CV PDF atau teks profil wajib dikirim sebelum analisis dijalankan.")

def analyze_cv_text(input_text="", options=None):
    if options is None:
        options = {}
        
    domain = options.get("domain", "technology")
    extracted_skills = extract_skills(input_text, domain)
    normalized_extracted = {skill.lower() for skill in extracted_skills}

    job_matches = []
    for role in ROLE_PROFILES:
        required_skills = role.get("requiredSkills", [])
        matched_skills = [skill for skill in required_skills if skill.lower() in normalized_extracted]
        match_score = calculate_readiness_score(extracted_skills, required_skills)
        
        job_matches.append({
            "id": role["id"],
            "name": role["name"],
            "domain": role["domain"],
            "matchScore": match_score,
            "matchedSkills": matched_skills,
            "requiredSkills": required_skills,
            "businessGoal": role.get("businessGoal"),
            "marketSignals": role.get("marketSignals")
        })
        
    job_matches.sort(key=lambda x: x["matchScore"], reverse=True)

    best_match = job_matches[0]
    best_role_profile = get_role_profile(best_match["id"])
    skill_gap = [skill for skill in best_role_profile.get("requiredSkills", []) if skill.lower() not in normalized_extracted]
    roadmap = create_roadmap(skill_gap, best_role_profile)
    
    confidence = max(0.45, min(0.94, 0.48 + (len(extracted_skills) / max(len(best_role_profile.get("requiredSkills", [])), 1)) * 0.42))

    return {
        "extractedSkills": extracted_skills,
        "jobMatches": [match for match in job_matches if has_actionable_match(match)],
        "suggestedRoleId": best_match["id"],
        "skillGap": skill_gap,
        "recommendation": build_recommendation_texts(roadmap, best_role_profile),
        "careerRecommendation": create_career_recommendation(best_role_profile, best_match["matchScore"]),
        "courseRecommendations": create_course_recommendations(skill_gap, best_role_profile),
        "roadmap": roadmap,
        "readinessScore": best_match["matchScore"],
        "readinessLabel": readiness_label(best_match["matchScore"]),
        "confidence": confidence,
        "domain": domain,
        "targetRole": best_match["name"],
        "targetRoleId": best_match["id"],
        "marketSignals": best_match.get("marketSignals"),
        "businessGoal": best_match.get("businessGoal")
    }

def get_quiz_questions(domain="technology", target_role="fullstack-web-developer"):
    base_questions = quiz_bank.get(domain) or quiz_bank.get("technology") or DEFAULT_QUIZ_BANK["technology"]
    role_profile = get_role_profile(target_role)
    
    role_question = {
        "id": f"{role_profile['id']}-focus",
        "prompt": f"Seberapa siap kamu membuktikan skill utama untuk {role_profile['name']}?",
        "options": ["Belum punya bukti", "Ada latihan kecil", "Ada proyek sederhana", "Ada portofolio siap demo"]
    }

    return (base_questions + [role_question])[:5]

def normalize_job_matches_for_quiz(job_matches=None):
    source_matches = job_matches if isinstance(job_matches, list) else []
    normalized_matches = []
    seen_role_ids = set()

    for match in source_matches:
        if not isinstance(match, dict):
            continue

        role_id = match.get("id") or match.get("roleId")
        if not role_id or role_id in seen_role_ids:
            continue

        role_profile = find_role_profile(role_id)
        normalized_role_id = role_profile["id"] if role_profile else role_id
        matched_skills = compact_skill_items(match.get("matchedSkills") or match.get("matched_skills"), 20)
        missing_skills = compact_skill_items(
            match.get("missingSkills")
            or match.get("missing_skills")
            or match.get("skillGap")
            or match.get("skill_gap"),
            20,
        )
        required_skills = compact_skill_items(
            match.get("requiredSkills")
            or match.get("required_skills")
            or (role_profile.get("requiredSkills", []) if role_profile else []),
            20,
        )
        normalized_matches.append({
            **match,
            "id": normalized_role_id,
            "name": match.get("name") or (role_profile["name"] if role_profile else format_role_label(role_id)),
            "domain": match.get("domain") or (role_profile.get("domain") if role_profile else None),
            "matchScore": clamp_number(match.get("matchScore"), 0, 100),
            "matchedSkills": matched_skills,
            "missingSkills": missing_skills,
            "requiredSkills": required_skills,
            "businessGoal": match.get("businessGoal") or (role_profile.get("businessGoal") if role_profile else None),
            "marketSignals": compact_skill_items(
                match.get("marketSignals")
                or match.get("market_signals")
                or (role_profile.get("marketSignals", []) if role_profile else []),
                20,
            ),
        })
        seen_role_ids.add(normalized_role_id)

    normalized_matches.sort(key=lambda item: item.get("matchScore", 0), reverse=True)
    return [match for match in normalized_matches if has_actionable_match(match)]

def clamp_number(value, min_value=0, max_value=100):
    try:
        number = round(float(value))
    except (TypeError, ValueError):
        number = min_value

    return max(min_value, min(max_value, number))

def get_missing_skills_for_match(match):
    explicit_missing = compact_skill_items(
        match.get("missingSkills")
        or match.get("missing_skills")
        or match.get("skillGap")
        or match.get("skill_gap"),
        20,
    )
    if explicit_missing:
        return explicit_missing

    required_skills = compact_skill_items(match.get("requiredSkills"), 20)
    matched_skills = compact_skill_items(match.get("matchedSkills"), 20)
    matched_lookup = {str(skill).lower() for skill in matched_skills}

    return [
        skill
        for skill in required_skills
        if str(skill).lower() not in matched_lookup
    ]

def compact_skill_items(value, limit=3):
    if not isinstance(value, list):
        return []

    return [
        str(item).strip()
        for item in value
        if str(item).strip()
    ][:limit]

def join_natural(items, fallback):
    clean_items = compact_skill_items(items, 3)
    if not clean_items:
        return fallback
    if len(clean_items) == 1:
        return clean_items[0]
    return ", ".join(clean_items[:-1]) + f", dan {clean_items[-1]}"

def text_has_any(text, keywords):
    padded_text = f" {text} "
    for keyword in keywords:
        if len(keyword) <= 2:
            if f" {keyword} " in padded_text:
                return True
            continue
        if keyword in text:
            return True
    return False

def get_role_work_context(match, signal):
    searchable_text = " ".join([
        str(match.get("id") or ""),
        str(match.get("name") or ""),
        " ".join(compact_skill_items(match.get("matchedSkills"), 20)),
        " ".join(compact_skill_items(match.get("requiredSkills"), 20)),
        " ".join(compact_skill_items(get_missing_skills_for_match(match), 20)),
        " ".join(compact_skill_items(match.get("marketSignals"), 20)),
    ]).lower()

    if text_has_any(searchable_text, ["secretary", "administrative", "administrator", "office", "assistant", "confidentiality", "attention to detail"]):
        return {
            "workContext": "agenda, dokumen, dan komunikasi kantor",
            "proofArtifact": "log agenda, notulen, dan arsip dokumen",
            "routineWork": "mengelola jadwal, email, dan dokumen penting",
            "teamContribution": "menjaga follow-up rapat dan informasi sensitif",
        }

    if text_has_any(searchable_text, ["project", "manager", "coordinator", "leadership", "timeline", "risk management"]):
        return {
            "workContext": "prioritas, timeline, dan koordinasi tim",
            "proofArtifact": "timeline proyek, risk log, dan catatan keputusan",
            "routineWork": "memantau progres, blocker, dan pembagian tugas",
            "teamContribution": "menyelaraskan update tim dan risiko proyek",
        }

    if text_has_any(searchable_text, ["data", "scientist", "analyst", "eda", "wrangling", "dashboard"]):
        return {
            "workContext": "dataset, insight, dan laporan analisis",
            "proofArtifact": "notebook analisis, visualisasi, dan ringkasan insight",
            "routineWork": "membersihkan data dan mengecek pola utama",
            "teamContribution": "menerjemahkan data menjadi keputusan yang mudah dibaca",
        }

    if text_has_any(searchable_text, ["ai-engineer", "ai engineer", "machine learning", "tensorflow", "nlp", "model evaluation", "model serving"]):
        return {
            "workContext": "dataset, eksperimen model, dan evaluasi",
            "proofArtifact": "laporan eksperimen, metrik model, dan demo inference",
            "routineWork": "menguji data, model, dan hasil prediksi",
            "teamContribution": "menjelaskan performa model dan batasannya",
        }

    if text_has_any(searchable_text, ["web", "developer", "react", "api", "frontend", "backend", "javascript"]):
        return {
            "workContext": "fitur web, API, dan perbaikan bug",
            "proofArtifact": "fitur end-to-end dengan dokumentasi singkat",
            "routineWork": "membangun UI, menghubungkan API, dan mengetes alur",
            "teamContribution": "mengirim update teknis dan hasil testing",
        }

    return {
        "workContext": f"aktivitas yang mengasah {signal['primarySkill']}",
        "proofArtifact": f"contoh kerja seputar {signal['primarySkill']}",
        "routineWork": f"latihan rutin pada {signal['marketSignal']}",
        "teamContribution": f"kontribusi yang memperkuat {signal['primarySkill']}",
    }

def get_match_signal(match):
    matched_skills = compact_skill_items(match.get("matchedSkills"), 3)
    missing_skills = compact_skill_items(get_missing_skills_for_match(match), 3)
    market_signals = compact_skill_items(match.get("marketSignals"), 3)
    required_skills = compact_skill_items(match.get("requiredSkills"), 3)

    primary_skill = (matched_skills or required_skills or ["skill utama"])[0]
    priority_gap = (missing_skills or required_skills or [primary_skill])[0]
    if str(priority_gap).lower() == str(primary_skill).lower() and len(missing_skills) > 1:
        priority_gap = missing_skills[1]
    market_signal = (market_signals or [primary_skill])[0]

    signal = {
        "primarySkill": primary_skill,
        "priorityGap": priority_gap,
        "marketSignal": market_signal,
        "matchedText": join_natural(matched_skills, primary_skill),
        "gapText": join_natural(missing_skills, priority_gap),
        "marketText": join_natural(market_signals, market_signal),
    }

    return {
        **signal,
        **get_role_work_context(match, signal),
    }

def build_career_fit_response(match, question_index=0, option_index=0):
    signal = get_match_signal(match)
    response_variants = [
        [
            f"Menyusun {signal['proofArtifact']} yang membuktikan {signal['primarySkill']}.",
            f"Membuat contoh kerja kecil untuk memperbaiki {signal['priorityGap']}.",
            f"Menyiapkan bukti praktik seputar {signal['workContext']}.",
            f"Merapikan hasil latihan {signal['primarySkill']} agar siap ditunjukkan.",
        ],
        [
            f"Menjaga ritme harian lewat {signal['routineWork']}.",
            f"Mengurus pekerjaan rutin seputar {signal['workContext']}.",
            f"Mencatat progres harian untuk {signal['marketSignal']}.",
            f"Memilih tugas operasional yang mengasah {signal['primarySkill']}.",
        ],
        [
            f"Melatih {signal['priorityGap']} lewat target mingguan yang jelas.",
            f"Mengulang praktik {signal['priorityGap']} sampai hasilnya konsisten.",
            f"Mencari mentor atau feedback khusus untuk {signal['priorityGap']}.",
            f"Membuat latihan kecil yang menutup gap {signal['priorityGap']}.",
        ],
        [
            f"Menampilkan {signal['proofArtifact']} sebagai bukti portofolio.",
            f"Membuat studi kasus dari pekerjaan seputar {signal['workContext']}.",
            f"Mengemas hasil praktik {signal['primarySkill']} menjadi cerita portofolio.",
            f"Menulis ringkasan masalah, aksi, dan hasil dari {signal['marketSignal']}.",
        ],
        [
            f"Mengambil peran untuk {signal['teamContribution']}.",
            f"Membantu tim dengan kontribusi seputar {signal['workContext']}.",
            f"Menjadi penghubung saat pekerjaan butuh {signal['primarySkill']}.",
            f"Menjaga kualitas kerja tim pada area {signal['marketSignal']}.",
        ],
    ]
    variants_for_question = response_variants[question_index % len(response_variants)]
    return variants_for_question[option_index % len(variants_for_question)]

def build_career_fit_prompt(job_matches, question_index=0):
    top_match = job_matches[0] if job_matches else {}
    signal = get_match_signal(top_match)
    role_names = [
        match.get("name")
        for match in job_matches[:3]
        if isinstance(match, dict) and match.get("name")
    ]
    role_text = join_natural(role_names, "saran pekerjaan")
    prompt_variants = [
        f"Dari scan CV, arah yang muncul adalah {role_text}. Bukti kerja mana yang ingin kamu mulai dulu?",
        f"Kalau aktivitas hariannya dekat dengan {signal['workContext']}, pola kerja mana yang paling kamu pilih?",
        f"Gap utama seperti {signal['gapText']} masih perlu dikejar. Latihan mana yang terasa paling realistis?",
        f"Untuk portofolio awal, bukti yang menunjukkan {signal['primarySkill']} seperti apa yang ingin kamu tampilkan?",
        f"Dalam kerja tim, kontribusi seputar {signal['marketText']} mana yang terasa paling natural?"
    ]
    return prompt_variants[question_index % len(prompt_variants)]

def build_career_fit_option(match, index=0, question_index=0):
    role_id = match.get("id")
    role_profile = find_role_profile(role_id)
    normalized_role_id = role_profile["id"] if role_profile else role_id
    role_name = match.get("name") or (role_profile["name"] if role_profile else format_role_label(role_id))
    matched_skills = match.get("matchedSkills", []) if isinstance(match.get("matchedSkills"), list) else []
    missing_skills = get_missing_skills_for_match(match)
    match_score = clamp_number(match.get("matchScore"), 0, 100)
    response = build_career_fit_response(match, question_index, index)
    description_parts = [f"{match_score}% match dari hasil scan CV"]
    if matched_skills:
        description_parts.append(f"skill cocok: {', '.join(matched_skills[:2])}")
    if missing_skills:
        description_parts.append(f"gap utama: {', '.join(missing_skills[:2])}")

    return {
        "id": f"career-fit-q{question_index + 1}-{index + 1}-{normalized_role_id}",
        "roleId": normalized_role_id,
        "label": role_name,
        "response": response,
        "description": "; ".join(description_parts),
        "matchScore": match_score,
    }

def build_career_fit_question(job_matches, question_index=0, prompt=None):
    options = [
        build_career_fit_option(match, index, question_index)
        for index, match in enumerate(job_matches)
    ]

    return {
        "id": f"career-fit-question-{question_index + 1}",
        "prompt": prompt or build_career_fit_prompt(job_matches, question_index),
        "options": options,
    }

def generate_career_fit_quiz(payload=None):
    if payload is None:
        payload = {}

    job_matches = normalize_job_matches_for_quiz(payload.get("jobMatches"))
    if not job_matches:
        return {
            "id": "career-fit-disambiguation",
            "source": "local_rules",
            "prompt": "",
            "context": "Mini quiz belum tersedia karena belum ada saran pekerjaan dengan sinyal kecocokan.",
            "options": [],
            "questions": [],
            "roles": [],
        }

    questions = [
        build_career_fit_question(job_matches, index)
        for index in range(5)
    ]
    first_question = questions[0]

    return {
        "id": "career-fit-disambiguation",
        "source": "local_rules",
        "prompt": first_question["prompt"],
        "context": "Pertanyaan ini dibuat dari semua rekomendasi karier hasil scan CV.",
        "options": first_question["options"],
        "questions": questions,
        "roles": [
            {
                "id": match.get("id"),
                "name": match.get("name"),
                "matchScore": clamp_number(match.get("matchScore"), 0, 100),
                "matchedSkills": match.get("matchedSkills", []),
                "requiredSkills": match.get("requiredSkills", []),
                "missingSkills": get_missing_skills_for_match(match),
                "businessGoal": match.get("businessGoal"),
                "marketSignals": match.get("marketSignals", []),
            }
            for match in job_matches
        ],
    }

def score_quiz(answers=None, options=None):
    if answers is None:
        answers = []
    if options is None:
        options = {}
        
    role_profile = get_role_profile(options.get("targetRole"))
    domain = options.get("domain") or role_profile.get("domain", "technology")
    questions = get_quiz_questions(domain, role_profile["id"])
    
    normalized_answers = answers if isinstance(answers, list) else []
    max_score = len(questions) * 3
    
    raw_score = 0
    for i, _ in enumerate(questions):
        try:
            val = float(normalized_answers[i])
            raw_score += max(0, min(3, val))
        except (IndexError, TypeError, ValueError):
            pass
            
    score = round((raw_score / max(max_score, 1)) * 100)
    
    weak_signals = []
    for i, question in enumerate(questions):
        try:
            if float(normalized_answers[i]) <= 1:
                weak_signals.append(question["prompt"])
        except (IndexError, TypeError, ValueError):
            weak_signals.append(question["prompt"])

    roadmap = create_roadmap(role_profile.get("requiredSkills", [])[:4], role_profile)

    return {
        "score": score,
        "track": readiness_label(score),
        "answeredCount": len([a for a in normalized_answers if a is not None]),
        "totalQuestions": len(questions),
        "weakSignals": weak_signals,
        "roadmap": [step["action"] for step in roadmap],
        "targetRole": role_profile["name"],
        "recommendation": "Prioritize portfolio polish, deployment, and interview storytelling." if score >= 80 else "Strengthen fundamentals first, then convert each skill gap into one portfolio artifact."
    }

def create_personalized_recommendation(payload=None):
    if payload is None:
        payload = {}
        
    role_profile = get_role_profile(payload.get("targetRole"))
    extracted_skills = payload.get("extractedSkills", [])
    if not isinstance(extracted_skills, list):
        extracted_skills = []
        
    quiz_score = payload.get("quizScore")
    if not isinstance(quiz_score, (int, float)):
        quiz_score = None
        
    normalized_extracted = {str(skill).lower() for skill in extracted_skills}
    skill_gap = [skill for skill in role_profile.get("requiredSkills", []) if skill.lower() not in normalized_extracted]
    readiness_score = calculate_readiness_score(extracted_skills, role_profile.get("requiredSkills", []), quiz_score)
    roadmap = create_roadmap(skill_gap, role_profile)

    return {
        "targetRole": role_profile["name"],
        "readinessScore": readiness_score,
        "readinessLabel": readiness_label(readiness_score),
        "skillGap": skill_gap,
        "roadmap": roadmap,
        "recommendation": build_recommendation_texts(roadmap, role_profile),
        "careerRecommendation": create_career_recommendation(role_profile, readiness_score),
        "courseRecommendations": create_course_recommendations(skill_gap, role_profile),
        "marketSignals": role_profile.get("marketSignals")
    }

def get_dashboard_snapshot():
    return {
        "user": None,
        "skillScore": None,
        "targetRole": None,
        "strengths": [],
        "gaps": [],
        "roadmap": [],
        "featureModules": [
            "CV skill extraction",
            "Adaptive quiz",
            "Skill gap mapping",
            "Personalized learning path",
            "Dashboard insight"
        ],
        "researchQuestions": [
            "How accurately can NLP detect CV skill gaps against industry requirements?",
            "How does a personalized learning path affect confidence and job readiness?"
        ],
        "compliance": {
            "frontend": ["React", "Vite module bundler", "Axios networking calls", "responsive UI"],
            "backend": ["Flask REST API", "RESTful URL convention", "PostgreSQL-ready persistence"],
            "aiMl": ["CV NLP extraction contract", "model-service integration contract", "recommendation engine"],
            "dataScience": ["skill mapping dataset", "EDA/dashboard insight contract", "ready for Streamlit reporting"]
        }
    }
