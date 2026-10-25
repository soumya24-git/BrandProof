import re

PROMOTIONAL_PATTERNS = [
    (r"\b(?:guarantee[sd]?|guaranteed|100%|risk[- ]free)\b", "Absolute promise", "Absolute guarantees need explicit approved evidence."),
    (r"\b(?:best|#1|number one|leading|top[- ]rated)\b", "Superiority claim", "Comparative or ranking language needs a current, approved source."),
    (r"\b(?:proven|clinically tested|scientifically proven|increases?|boosts?|reduces?|improves?)\b", "Performance claim", "Performance claims should match an approved product fact."),
]

def evaluate(content, profile):
    findings = []
    lowered = content.casefold()
    for term in profile.restricted_words:
        if not isinstance(term, str) or not term.strip(): continue
        match = re.search(r"(?<!\w)" + re.escape(term.strip()) + r"(?!\w)", content, re.IGNORECASE)
        if match:
            findings.append({"id": f"restricted-{len(findings)}", "category": "Restricted term", "severity": "high", "excerpt": match.group(), "explanation": f'“{term}” is on the restricted words list.', "suggestion": f'Remove “{term}” or replace it with neutral, factual language.'})
    for phrase in profile.required_phrases:
        if isinstance(phrase, str) and phrase.strip() and phrase.casefold() not in lowered:
            findings.append({"id": f"required-{len(findings)}", "category": "Required phrase", "severity": "medium", "excerpt": "", "explanation": f'The approved phrase “{phrase}” is missing.', "suggestion": f'Add “{phrase}” where it reads naturally.'})
    facts = [f for f in profile.product_facts if isinstance(f, str)]
    fact_tokens = {token for fact in facts for token in re.findall(r"[a-z0-9]+", fact.casefold()) if len(token) > 3}
    seen = set()
    for pattern, kind, why in PROMOTIONAL_PATTERNS:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            if match.group().casefold() in seen: continue
            seen.add(match.group().casefold())
            tokens = {token for token in re.findall(r"[a-z0-9]+", match.group().casefold()) if len(token) > 3}
            supported = bool(tokens & fact_tokens) and any(match.group().casefold() in fact.casefold() for fact in facts)
            if not supported:
                findings.append({"id": f"claim-{len(findings)}", "category": kind, "severity": "high", "excerpt": match.group(), "explanation": f"{why} No matching approved product fact was found.", "suggestion": "Remove the claim or replace it with a specific statement supported by an approved product fact."})
    return findings
