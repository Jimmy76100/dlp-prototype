# extractor.py
import textract

def extract_text_from_file(path):
    try:
        text = textract.process(path).decode('utf-8', errors='ignore')
    except Exception as e:
        print("extract error", e)
        text = ""
    return text
