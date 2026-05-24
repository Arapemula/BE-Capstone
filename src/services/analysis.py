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
dashboard_snapshot_data = load_json("dashboardSnapshot.json", {
    "user": {"name": "Demo User", "role": "SkillMap Explorer"},
    "skillScore": 76,
    "targetRole": "Junior Full-Stack Web Developer",
    "strengths": ["JavaScript", "React"],
    "gaps": ["Express", "PostgreSQL", "Deployment"],
    "roadmap": []
})

def normalize_text(value=""):
    return str(value).lower() if value else ""

def get_role_profile(target_role="fullstack-web-developer"):
    for role in ROLE_PROFILES:
        if role["id"] == target_role:
            return role
    return ROLE_PROFILES[0]

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

    return max(35, min(95, cv_score))

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

    return " ".join([
        (file_obj.get("originalname") if file_obj else "uploaded-cv"),
        body.get("targetRole", ""),
        body.get("domain", "technology"),
        "portfolio project communication problem solving"
    ])

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
        "extractedSkills": extracted_skills if extracted_skills else ["Communication", "Problem Solving"],
        "jobMatches": job_matches,
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
    snapshot = dict(dashboard_snapshot_data)
    snapshot.update({
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
            "aiMl": ["CV NLP extraction placeholder", "model-service integration contract", "recommendation engine"],
            "dataScience": ["skill mapping dataset", "EDA/dashboard insight contract", "ready for Streamlit reporting"]
        }
    })
    return snapshot
