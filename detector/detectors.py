# detectors.py
import re
import hashlib

# Example regex definitions
REGEXES = {
    "CREDIT_CARD_LUHN": re.compile(r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b"),
    "PAN_INDIA": re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),  # India PAN
    "SSN_US": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "API_KEY_LIKE": re.compile(r"\b[A-Za-z0-9_\-]{20,50}\b")
}

def luhn_check(number_str):
    digits = [int(c) for c in number_str if c.isdigit()]
    checksum = 0
    dbl = False
    for d in reversed(digits):
        if dbl:
            d *= 2
            if d > 9: d -= 9
        checksum += d
        dbl = not dbl
    return checksum % 10 == 0

def find_patterns(text):
    matches = {}
    for name, regex in REGEXES.items():
        found = regex.findall(text)
        # for credit card, apply Luhn filter for fewer false positives
        if name == "CREDIT_CARD_LUHN":
            found = [f for f in found if luhn_check(f)]
        if found:
            matches[name] = found
    return matches

def sha256_of_bytes(b):
    return hashlib.sha256(b).hexdigest()
