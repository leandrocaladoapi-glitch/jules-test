import re

# Regex patterns for Inclusion (Open Borders)
INCLUSION_TERMS = [
    r'remote worldwide',
    r'anywhere in the world',
    r'latam',
    r'south america',
    r'visa sponsorship',
    r'b2b contractor',
    r'remote - americas',
    r'global remote',
    r'remote globally',
    r'remote \(global\)'
]
INCLUSION_REGEX = re.compile(r'|'.join(INCLUSION_TERMS), re.IGNORECASE)

# Regex patterns for Exclusion (Red Flags)
EXCLUSION_TERMS = [
    r'us citizen',
    r'us only',
    r'eu only',
    r'no sponsorship',
    r'must reside in the us',
    r'must reside in the uk',
    r'uk resident',
    r'canada only',
    r'cleared', # Security clearances usually imply local citizenship
    r'security clearance'
]
EXCLUSION_REGEX = re.compile(r'|'.join(EXCLUSION_TERMS), re.IGNORECASE)

# Tech Stack keywords
TECH_STACK_KEYWORDS = {
    'Cloud': ['aws', 'gcp', 'azure', 'google cloud'],
    'Big Data': ['spark', 'databricks', 'hadoop', 'kafka', 'flink', 'snowflake', 'bigquery', 'redshift'],
    'Core': ['python', 'sql', 'scala', 'java', 'r']
}

def is_eligible(description):
    """
    Checks if a job description passes the Open Borders filter and doesn't hit Red Flags.
    Returns (True, proof_string) if eligible, (False, None) otherwise.
    """
    # 1. Check for red flags (Exclusion)
    if EXCLUSION_REGEX.search(description):
        return False, None

    # 2. Check for inclusion
    match = INCLUSION_REGEX.search(description)
    if match:
        # Find the surrounding text for context (proof)
        start = max(0, match.start() - 30)
        end = min(len(description), match.end() + 30)
        proof = description[start:end].strip()
        # Clean up whitespace
        proof = ' '.join(proof.split())
        return True, f"...{proof}..."

    return False, None

def extract_tech_stack(description):
    """
    Extracts tech stack keywords from the job description.
    Returns a comma-separated string of found technologies.
    """
    found_techs = set()
    description_lower = description.lower()

    # Use word boundaries for tech keywords to avoid partial matches (e.g. 'r' in 'word')
    for category, keywords in TECH_STACK_KEYWORDS.items():
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, description_lower):
                found_techs.add(keyword.title() if len(keyword) > 3 else keyword.upper())

    return ', '.join(sorted(list(found_techs))) if found_techs else "Not specified"
