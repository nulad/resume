#!/usr/bin/env python3
"""
Resume Tailoring Engine

Reads a job description and master_data.yml, then generates a tailored
LaTeX resume by selecting the most relevant bullet variants and reordering
skills to match the JD keywords.

Usage:
    python tailor.py --jd jobs/company_role.txt [--profile backend|devops|fullstack|default]
    python tailor.py --jd jobs/company_role.txt --profile auto
"""

import argparse
import os
import re
import sys
from collections import Counter
from pathlib import Path

import yaml


# ── LaTeX escaping ────────────────────────────────────────
LATEX_SPECIAL = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}

# Characters to preserve (not escape) when they appear in LaTeX commands
LATEX_COMMAND_PATTERN = re.compile(r"\\[a-zA-Z]+\{[^}]*\}")


def escape_latex(text):
    """Escape special LaTeX characters, preserving existing LaTeX commands."""
    if not text:
        return ""
    # Replace HTML entities
    text = text.replace("&mdash;", "--")
    text = text.replace("&amp;", r"\&")
    # Escape special chars
    for char, replacement in LATEX_SPECIAL.items():
        text = text.replace(char, replacement)
    return text


# ── Keyword extraction ───────────────────────────────────
# Common words to ignore when extracting keywords from JD
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "need", "must",
    "we", "you", "they", "it", "our", "your", "their", "its", "this",
    "that", "these", "those", "as", "if", "not", "no", "so", "up",
    "about", "into", "through", "during", "before", "after", "above",
    "below", "between", "out", "off", "over", "under", "again", "further",
    "then", "once", "here", "there", "when", "where", "why", "how", "all",
    "each", "every", "both", "few", "more", "most", "other", "some",
    "such", "than", "too", "very", "just", "also", "only", "own", "same",
    "what", "which", "who", "whom", "while", "work", "working", "role",
    "experience", "team", "ability", "etc", "including", "using", "used",
    "well", "across", "within", "strong", "new", "join", "help", "re",
    "looking", "ideal", "candidate", "required", "preferred", "plus",
    "years", "year", "minimum", "responsibilities", "requirements",
    "qualifications", "benefits", "salary", "company", "position",
    "based", "ensure", "ensuring", "best", "development", "practices",
    "building", "build", "built", "technical", "software", "product",
    "tools", "systems", "system", "code", "features", "data",
    "design", "support", "process", "processes", "implement",
    "maintain", "improve", "create", "make", "like", "take",
    "day", "don", "time", "high", "key", "real", "set",
    "job", "my", "us", "one", "get", "two", "may", "let",
}

# Technology and skill keywords to boost when found in JD
TECH_KEYWORDS = {
    "java", "spring", "node", "nodejs", "node.js", "golang", "go",
    "python", "php", "dotnet", ".net", "c#", "csharp", "typescript",
    "javascript", "react", "angular", "vue", "docker", "kubernetes",
    "k8s", "aws", "azure", "gcp", "lambda", "ecs", "ec2", "sqs", "sns",
    "s3", "rds", "aurora", "cloudformation", "cloudwatch", "terraform",
    "express", "express.js", "expressjs", "stripe", "payment",
    "microservices", "microservice", "api", "rest", "restful", "graphql",
    "postgresql", "postgres", "mysql", "mongodb", "redis", "sql",
    "nosql", "dynamodb", "elasticsearch", "kafka", "rabbitmq", "kinesis",
    "elk", "logstash", "kibana", "grafana", "prometheus", "datadog",
    "newrelic", "splunk", "fluentd",
    "ci/cd", "cicd", "jenkins", "github", "bitbucket", "bamboo",
    "serverless", "event-driven", "pub-sub", "pubsub", "messaging",
    "agile", "scrum", "kanban", "devops", "sre", "infrastructure",
    "cloud", "migration", "security", "authentication", "oauth",
    "scalability", "reliability", "performance", "monitoring",
    "observability", "distributed", "architecture",
    "saas", "b2b-saas", "multi-tenant", "multitenant", "tenant",
    "telephony", "telephony-saas",
}


def extract_jd_keywords(jd_text):
    """Extract and rank keywords from a job description."""
    # Normalize text
    text = jd_text.lower()
    # Extract words (including hyphenated and dotted terms)
    words = re.findall(r"[a-z][a-z0-9./#+-]*(?:-[a-z0-9./#+-]+)*", text)

    # Count frequencies, excluding stop words
    keyword_counts = Counter()
    for word in words:
        if word not in STOP_WORDS and len(word) > 1:
            keyword_counts[word] += 1

    # Boost tech keywords
    boosted = Counter()
    for word, count in keyword_counts.items():
        if word in TECH_KEYWORDS:
            boosted[word] = count * 3  # Triple weight for tech terms
        else:
            boosted[word] = count

    return boosted


def detect_profile(jd_keywords, jd_text):
    """Auto-detect the best profile type based on JD content and keywords."""
    jd_lower = jd_text.lower()

    # Phase 1: Scan full JD for strong role phrases (order matters — check
    # fullstack first since it's more specific than backend)
    role_phrases = {
        "fullstack": [
            "full-stack", "fullstack", "full stack",
            "react and node", "node and react",
            "frontend and backend", "backend and frontend",
        ],
        "devops": [
            "devops", "dev ops", "site reliability", "sre ",
            "platform engineer", "cloud engineer",
            "infrastructure engineer",
        ],
        "backend": [
            "backend engineer", "back-end engineer",
            "backend developer", "back-end developer",
            "server-side", "api engineer",
        ],
    }

    # Count phrase matches across the full JD text
    phrase_scores = {profile: 0 for profile in role_phrases}
    for profile, phrases in role_phrases.items():
        for phrase in phrases:
            count = jd_lower.count(phrase)
            if count > 0:
                phrase_scores[profile] += count * 10  # Strong signal

    # If any profile has clear phrase matches, use it
    # Priority order for tie-breaking: backend > fullstack > devops
    # (more specific role phrases should win over generic mentions)
    priority = ["backend", "fullstack", "devops"]
    best_score = max(phrase_scores.values())
    if best_score > 0:
        for profile in priority:
            if phrase_scores.get(profile, 0) == best_score:
                return profile

    # Phase 2: Fallback to keyword scoring from full JD
    profile_signals = {
        "backend": ["api", "backend", "back-end", "server", "database", "sql",
                     "rest", "restful", "microservices", "data", "scalability"],
        "devops": ["devops", "infrastructure", "ci/cd", "cicd", "terraform",
                   "docker", "kubernetes", "k8s", "sre", "deployment",
                   "monitoring", "pipeline", "iac"],
        "fullstack": ["frontend", "fullstack", "full-stack", "react", "angular",
                      "vue", "ui", "ux", "end-to-end"],
    }

    scores = {profile: 0 for profile in profile_signals}
    for profile, signals in profile_signals.items():
        for signal in signals:
            if signal in jd_keywords:
                scores[profile] += jd_keywords[signal]

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "default"
    return best


# ── Bullet scoring and selection ─────────────────────────

def score_bullet(bullet, jd_keywords):
    """Score a bullet based on keyword overlap with JD."""
    score = 0
    text_lower = bullet["text"].lower()
    tags = [t.lower() for t in bullet.get("tags", [])]

    for keyword, weight in jd_keywords.items():
        # Check if keyword appears in bullet text
        if keyword in text_lower:
            score += weight * 2
        # Check if keyword matches a tag
        if keyword in tags:
            score += weight

    return score


def select_bullet_text(bullet, profile, jd_keywords):
    """Select the best bullet text variant for the given profile and JD."""
    alts = bullet.get("alt", {})

    # If the profile has an alt variant, score it against the original
    if profile in alts:
        alt_text = alts[profile]
        alt_score = sum(
            weight for kw, weight in jd_keywords.items()
            if kw in alt_text.lower()
        )
        orig_score = sum(
            weight for kw, weight in jd_keywords.items()
            if kw in bullet["text"].lower()
        )
        if alt_score >= orig_score:
            return alt_text

    return bullet["text"]


def select_experience_bullets(experience, jd_keywords, profile, max_bullets=4):
    """Select and order the most relevant bullets for a job entry."""
    bullets = experience.get("bullets", [])
    if not bullets:
        return []

    # Score each bullet
    scored = []
    for bullet in bullets:
        score = score_bullet(bullet, jd_keywords)
        text = select_bullet_text(bullet, profile, jd_keywords)
        scored.append((score, text))

    # Sort by score descending, take top N
    scored.sort(key=lambda x: x[0], reverse=True)
    return [text for _, text in scored[:max_bullets]]


# ── LaTeX rendering ──────────────────────────────────────

def score_experience(exp, jd_keywords):
    """Score an entire experience entry by its bullets and tech stack relevance."""
    score = 0
    for bullet in exp.get("bullets", []):
        score += score_bullet(bullet, jd_keywords)
    # Also score the tech stack
    tech = exp.get("tech_stack", "").lower()
    for kw, weight in jd_keywords.items():
        if kw in tech:
            score += weight
    return score


def render_experience_entries(experiences, jd_keywords, profile, max_roles=5, max_bullets=4):
    """Render the most relevant experience entries as LaTeX."""
    # Score and rank roles, but preserve chronological order among selected ones
    scored = [(i, score_experience(exp, jd_keywords)) for i, exp in enumerate(experiences)]
    scored.sort(key=lambda x: x[1], reverse=True)
    selected_indices = sorted([i for i, _ in scored[:max_roles]])

    entries = []
    for i in selected_indices:
        exp = experiences[i]
        company = escape_latex(exp["company"])
        position = escape_latex(exp["position"])
        duration = exp["duration"].replace("&mdash;", "--")
        location = escape_latex(exp.get("location", ""))
        tech_stack = escape_latex(exp.get("tech_stack", ""))

        bullets = select_experience_bullets(exp, jd_keywords, profile, max_bullets=max_bullets)
        bullet_lines = "\n".join(
            f"  \\item {escape_latex(b)}" for b in bullets
        )

        entry = (
            f"\\entry{{{company}}}{{{duration}}}{{{position}}}{{{location}}}\n"
            f"\\begin{{itemize}}\n"
            f"{bullet_lines}\n"
            f"\\end{{itemize}}\n"
            f"\\textbf{{Tech:}} {tech_stack}"
        )
        entries.append(entry)

    return "\n\n\\vspace{6pt}\n\n".join(entries)


def render_skills_entries(skills, languages_sorted=""):
    """Render skills section as LaTeX."""
    items = []
    for skill in skills:
        name = escape_latex(skill["skill"])
        desc = skill["description"].replace("<<LANGUAGES>>", languages_sorted)
        desc = escape_latex(desc)
        items.append(f"  \\item \\textbf{{{name}:}} {desc}")

    return "\\begin{itemize}\n" + "\n".join(items) + "\n\\end{itemize}"


def render_education_entries(education):
    """Render education section as LaTeX."""
    entries = []
    for edu in education:
        degree = escape_latex(edu["degree"])
        uni = escape_latex(edu["uni"])
        year = edu["year"].replace("&mdash;", "--")
        summary = escape_latex(edu.get("summary", ""))

        entry = f"\\entry{{{uni}}}{{{year}}}{{{degree}}}{{}}\n{summary}"
        entries.append(entry)

    return "\n\n\\vspace{6pt}\n\n".join(entries)


def render_spoken_languages(spoken_languages):
    """Render spoken languages section as LaTeX."""
    if not spoken_languages:
        return ""
    items = ", ".join(
        f"{escape_latex(lang['language'])} ({escape_latex(lang['proficiency'])})"
        for lang in spoken_languages
    )
    return f"\\section{{Languages}}\n{items}"


# ── Synonym mapping ──────────────────────────────────────
# Maps equivalent tech terms. If the resume contains any term in a group,
# it covers all terms in that group for gap analysis purposes.
SYNONYM_GROUPS = [
    {"javascript", "node.js", "nodejs", "node", "js"},
    {"express", "express.js", "expressjs"},
    {"typescript"},
    {"golang", "go"},
    {"postgresql", "postgres"},
    {"c#", "csharp", ".net", "dotnet"},
    {"vb.net", "vbnet"},
    {"kubernetes", "k8s"},
    {"ci/cd", "cicd"},
    {"react", "reactjs", "react.js"},
    {"angular", "angularjs"},
    {"vue", "vuejs", "vue.js"},
    {"mongodb", "mongo", "nosql", "redis", "dynamodb"},
    {"elasticsearch", "elastic", "elk", "logstash", "kibana",
     "cloudwatch", "grafana", "prometheus", "datadog", "splunk"},
    {"sqs", "kafka", "rabbitmq", "rabbit", "kinesis", "message queue", "message broker"},
    {"amazon web services", "aws"},
    {"google cloud platform", "gcp"},
    {"devops", "dev ops"},
    {"oauth", "oauth2", "authentication"},
    {"pub-sub", "pubsub"},
    {"microservices", "microservice"},
]


def _find_synonym_group(keyword):
    """Find the synonym group a keyword belongs to, or None."""
    for group in SYNONYM_GROUPS:
        if keyword in group:
            return group
    return None


# ── Skills gap analysis ───────────────────────────────────

def _collect_resume_text(data):
    """Collect all searchable text from resume master data."""
    parts = []
    for exp in data.get("experience", []):
        parts.append(exp.get("tech_stack", ""))
        for bullet in exp.get("bullets", []):
            parts.append(bullet.get("text", ""))
            for alt_text in bullet.get("alt", {}).values():
                parts.append(alt_text)
    for skill in data.get("skills", []):
        parts.append(skill.get("description", ""))
    for summary in data.get("profile", {}).get("summaries", {}).values():
        parts.append(summary)
    return " ".join(parts).lower()


def _word_in_text(word, text):
    """Check if word appears as a whole word (not substring) in text."""
    # Use word boundary matching to avoid 'ts' matching 'struts'
    pattern = r'(?<![a-z0-9.])' + re.escape(word) + r'(?![a-z0-9])'
    return bool(re.search(pattern, text))


def _has_synonym_in_text(keyword, resume_text):
    """Check if keyword or any of its synonyms appear in the resume text."""
    if _word_in_text(keyword, resume_text):
        return True
    group = _find_synonym_group(keyword)
    if group:
        return any(_word_in_text(syn, resume_text) for syn in group)
    return False


def _report_skills_gap(jd_keywords, data):
    """Print warnings for JD tech keywords not found in resume data."""
    resume_text = _collect_resume_text(data)

    # Only check tech keywords that appear in the JD
    jd_tech = {kw for kw in jd_keywords if kw in TECH_KEYWORDS}

    gaps = []
    covered = []
    for kw in sorted(jd_tech, key=lambda k: jd_keywords[k], reverse=True):
        if _has_synonym_in_text(kw, resume_text):
            # Check if covered by synonym (not direct match)
            if not _word_in_text(kw, resume_text):
                group = _find_synonym_group(kw)
                match = next((s for s in group if _word_in_text(s, resume_text)), None)
                covered.append((kw, match))
        else:
            gaps.append((kw, jd_keywords[kw]))

    if covered:
        print("\n~  Covered by synonym (resume has equivalent):")
        for kw, match in covered:
            print(f"   {kw} ← covered by '{match}' in resume")

    if gaps:
        print("\n⚠  Skills gap (JD requires, resume lacks):")
        for kw, score in gaps:
            print(f"   MISSING: {kw} (JD weight: {score})")
        print("   → Consider adding these to master_data.yml or writing bullet variants")
    elif len(jd_tech) < 3:
        print(f"\n⚠  Low tech signal — only {len(jd_tech)} tech keywords found in JD")
        print("   This JD is light on specific technologies. Tailoring will be less effective.")
        print("   → Consider using --profile to manually set the best angle")
    else:
        print("\n✓  No skills gap — all JD tech keywords found in resume")


# ── Seniority detection ──────────────────────────────────

def detect_seniority(jd_text):
    """Decide whether the tailored summary should lead with a seniority prefix.

    Returns a string to substitute for <<SENIORITY>> in the summary, e.g.:
      - "Senior "  → JD signals senior/staff/lead/principal scope
      - ""         → JD reads as IC / mid-level / unspecified

    The trailing space is part of the substitution so that "Senior Backend Engineer"
    and "Backend Engineer" both render cleanly without manual spacing fixes.
    """
    text = jd_text.lower()

    # Negative signals force IC framing, even if a positive token appears
    # elsewhere (JDs often say "work with senior engineers" while hiring IC).
    negative = [r"\bjunior\b", r"\bjr\.?\b", r"\bmid[- ]level\b",
                r"\bentry[- ]level\b", r"\bintern\b", r"\bgraduate\b"]
    if any(re.search(p, text) for p in negative):
        return ""

    # Positive signals — word-boundary matched to avoid "lead" ⊂ "leadership"
    # and "sr" ⊂ unrelated tokens.
    positive = [r"\bsenior\b", r"\bsr\.?\b", r"\bstaff\b",
                r"\blead\b", r"\bprincipal\b"]
    if any(re.search(p, text) for p in positive):
        return "Senior "

    return ""


# ── Language sorting ─────────────────────────────────────

def sort_languages_by_jd(languages, jd_keywords, style="prose"):
    """Sort language list by relevance to JD and format as a string.

    style="prose" → "Python, C# (.NET), Java, and PHP" (Oxford comma, for summaries)
    style="list"  → "Python, C# (.NET), Java, PHP" (comma-only, for skill lists)
    """
    scored = []
    for lang in languages:
        score = sum(jd_keywords.get(kw.lower(), 0) for kw in lang.get("keywords", []))
        scored.append((score, lang["name"]))

    scored.sort(key=lambda x: (-x[0], x[1]))
    names = [name for _, name in scored]

    if style == "list" or len(names) <= 1:
        return ", ".join(names)
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + ", and " + names[-1]


# ── Main pipeline ────────────────────────────────────────

def tailor_resume(master_data_path, jd_path, template_path, output_path, profile="auto",
                  max_roles=5, max_bullets=4):
    """Main tailoring pipeline."""
    # Load data
    with open(master_data_path) as f:
        data = yaml.safe_load(f)

    with open(jd_path) as f:
        jd_text = f.read()

    with open(template_path) as f:
        template = f.read()

    # Extract JD keywords
    jd_keywords = extract_jd_keywords(jd_text)

    # Auto-detect or use specified profile
    if profile == "auto":
        profile = detect_profile(jd_keywords, jd_text)
        print(f"Auto-detected profile: {profile}")
    print(f"Using profile: {profile}")

    # Print top keywords for transparency (split into tech vs other)
    tech_kws = [(kw, s) for kw, s in jd_keywords.most_common(30) if kw in TECH_KEYWORDS]
    other_kws = [(kw, s) for kw, s in jd_keywords.most_common(30) if kw not in TECH_KEYWORDS]

    print("\nTop tech keywords (drive bullet selection):")
    if tech_kws:
        for kw, score in tech_kws[:10]:
            print(f"  {kw}: {score}")
    else:
        print("  (none found)")

    print("\nOther frequent terms:")
    for kw, score in other_kws[:8]:
        print(f"  {kw}: {score}")

    # Skills gap analysis
    _report_skills_gap(jd_keywords, data)

    # Select summary and substitute dynamic language list
    prof = data["profile"]
    summaries = prof.get("summaries", {})
    summary = summaries.get(profile, summaries.get("default", ""))
    languages_sorted = sort_languages_by_jd(prof.get("languages", []), jd_keywords)
    summary = summary.replace("<<LANGUAGES>>", languages_sorted)
    seniority = detect_seniority(jd_text)
    summary = summary.replace("<<SENIORITY>>", seniority)
    print(f"\nSeniority prefix: {seniority!r}")

    # Render sections
    experience_tex = render_experience_entries(
        data["experience"], jd_keywords, profile, max_roles=max_roles, max_bullets=max_bullets
    )
    languages_list = sort_languages_by_jd(prof.get("languages", []), jd_keywords, style="list")
    skills_tex = render_skills_entries(data["skills"], languages_list)
    education_tex = render_education_entries(data["education"])

    # Fill template
    output = template
    output = output.replace("<<NAME>>", escape_latex(prof["name"]))
    output = output.replace("<<LOCATION>>", escape_latex(prof["location"]))
    output = output.replace("<<EMAIL>>", prof["email"])
    output = output.replace("<<PHONE>>", escape_latex(prof["phone"]))
    output = output.replace("<<LINKEDIN>>", prof["linkedin"])
    output = output.replace("<<GITHUB>>", prof["github"])
    output = output.replace("<<WEBSITE>>", prof["website"])
    output = output.replace("<<SUMMARY>>", escape_latex(summary))
    output = output.replace("<<EXPERIENCE_ENTRIES>>", experience_tex)
    output = output.replace("<<SKILLS_ENTRIES>>", skills_tex)
    output = output.replace("<<EDUCATION_ENTRIES>>", education_tex)
    spoken_languages_tex = render_spoken_languages(data.get("spoken_languages", []))
    output = output.replace("<<LANGUAGES_SECTION>>", spoken_languages_tex)

    # Write output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(output)

    print(f"\nGenerated: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Tailor resume to job description")
    parser.add_argument("--jd", required=True, help="Path to job description text file")
    parser.add_argument("--profile", default="auto",
                        choices=["auto", "default", "backend", "devops", "fullstack"],
                        help="Resume profile to use (default: auto-detect from JD)")
    parser.add_argument("--master", default=None, help="Path to master_data.yml")
    parser.add_argument("--template", default=None, help="Path to LaTeX template")
    parser.add_argument("--output", default=None, help="Output .tex file path")
    parser.add_argument("--max-roles", type=int, default=5, help="Max experience entries to render")
    parser.add_argument("--max-bullets", type=int, default=4, help="Max bullets per role")

    args = parser.parse_args()

    # Resolve paths relative to tailored/ directory
    script_dir = Path(__file__).parent
    tailored_dir = script_dir.parent

    master = args.master or str(tailored_dir / "master_data.yml")
    template = args.template or str(tailored_dir / "templates" / "resume.tex")
    output = args.output or str(tailored_dir / "output" / "resume.tex")

    tailor_resume(master, args.jd, template, output, args.profile,
                  max_roles=args.max_roles, max_bullets=args.max_bullets)


if __name__ == "__main__":
    main()
