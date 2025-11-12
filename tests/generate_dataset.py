import os

# Define the directory to store the dataset
DATASET_DIR = os.path.join('tests', 'dataset')
POSITIVE_DIR = os.path.join(DATASET_DIR, 'positive')
NEGATIVE_DIR = os.path.join(DATASET_DIR, 'negative')

# Define sensitive data samples that match your detectors.py
SENSITIVE_DATA = {
    "pos_0.txt": "My credit card is 4242424242424242. Please charge it for the full amount.",
    "pos_1.txt": "Please use my India PAN: ABCDE1234F. Thank you.",
    "pos_2.txt": "Here is a US SSN for testing: 123-45-6789. Keep it secret.",
     API_KEY_PART_1 = "sk_live_aBcDeFgHiJkLmNoPq"
     API_KEY_PART_2 = "RsTuVwXyZ1234567890"
    "pos_3.txt": f"This is a very long API key: {API_KEY_PART_1}{API_KEY_PART_2}",
}

# Define non-sensitive data samples
NON_SENSITIVE_DATA = {
    "neg_0.txt": "This is a normal text file with no sensitive information.",
    "neg_1.txt": "The quick brown fox jumps over the lazy dog.",
    "neg_2.txt": "Meeting notes: Discuss project timeline and budget.",
}

def generate_files():
    print("Generating test dataset...")
    
    # Create directories
    os.makedirs(POSITIVE_DIR, exist_ok=True)
    os.makedirs(NEGATIVE_DIR, exist_ok=True)

    # Create positive (sensitive) files
    for filename, content in SENSITIVE_DATA.items():
        filepath = os.path.join(POSITIVE_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created {filepath}")

    # Create negative (non-sensitive) files
    for filename, content in NON_SENSITIVE_DATA.items():
        filepath = os.path.join(NEGATIVE_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created {filepath}")

    print("\nDataset generation complete.")

if __name__ == "__main__":
    generate_files()
