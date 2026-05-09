import os
import string
import argparse
import requests

REPLACEMENT_CHAR = '�'
LM_STUDIO_URL = 'http://localhost:1234/v1/chat/completions'

def repair_line_with_llm(line):
    prompt = (
        "The following line of text contains one or more Unicode replacement characters "
        "(U+FFFD) that stand in for corrupted or missing characters. "
        "Please repair the line by replacing the broken character(s) with whatever makes "
        "the most sense in context. Return only the repaired line, nothing else.\n\n"
        f"Line: {line}"
    )
    payload = {
        "model": "local-model",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }
    response = requests.post(LM_STUDIO_URL, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content'].strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', nargs='?', default=None)
    parser.add_argument('-llm', action='store_true', help='Use LLM to repair U+FFFD replacement characters')
    parser.add_argument('-save', action='store_true', help='Save files even if more than 5 weird characters remain')
    args = parser.parse_args()

    directory = args.directory
    if not directory:
        directory = input("Enter directory: ")
    directory = directory.strip("'\"")
    print(f"Checking directory: {directory}")
    if not os.path.isdir(directory):
        print("Invalid directory")
        return

    txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]

    # Replacements for non-standard quotes
    replacements = {
        '‘': "'",
        '’': "'",
        '“': '"',
        '”': '"',
        '—': '--',
        '–': '-',
        '…': '...',
        '•': '-',
        '©': ' ',
        '«': '"',
        '»': '"',
        '£': '$',
        '¯': '-',
        '°': '',
        '·': '.',
        '¤': '$',
        '„': '"',
        '￼': '',
        '‎': '',
        '﻿': '',
        ' ': ' ',
        '˝': '"',
        '‚': "'",
        '‹': "'",
        '­': '',
        '●': '-',
        '\x91': "'",
        '╝': '',
        '‡': '',
        '‟': '"',
        '❤': '',
        '☺': '',
        '¥': '$',
        '¬': '',
        '｣': "'",
        ' ': ' ',
        '¨': '',
        ' ': '\n',
        '⁄': '/',
        '‑': '-',
        ' ': ' ',
        '¢': '',
        '®': '',
        '×': '*',
        '´': "'",
        '​': '',
        '€': '$',
        '™': '',
        '☰': '',
        '″': '"',
        '╔': '',
        '˜': '',
    }

    for filename in txt_files:
        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(filepath, 'r', encoding='latin-1') as f:
                    content = f.read()
            except UnicodeDecodeError:
                print(f"{filename}: Could not decode")
                continue

        # Apply replacements for non-standard characters
        original_content = content
        for old, new in replacements.items():
            content = content.replace(old, new)

        # LLM repair of U+FFFD replacement characters
        llm_repaired = False
        if args.llm and REPLACEMENT_CHAR in content:
            lines = content.split('\n')
            repaired_lines = []
            for line in lines:
                if REPLACEMENT_CHAR in line:
                    print(f"{filename}: Found unknown character (U+FFFD) in line: {line[:120]!r}")
                    try:
                        repaired = repair_line_with_llm(line)
                        print(f"{filename}: LLM repaired to: {repaired[:120]!r}")
                        repaired_lines.append(repaired)
                        llm_repaired = True
                    except Exception as e:
                        print(f"{filename}: LLM error - {e}")
                        repaired_lines.append(line)
                else:
                    repaired_lines.append(line)
            content = '\n'.join(repaired_lines)

        # Check if content was modified
        modified = content != original_content

        weird_chars = set()
        weird_count = 0
        for char in content:
            if ord(char) > 127 and not char.isalnum():
                weird_chars.add(char)
                weird_count += 1

        if weird_chars:
            if weird_count > 5:
                print(f"\033[91m{filename}: CORRUPTED - Found {weird_count} weird characters\033[0m")
            for char in sorted(weird_chars, key=ord):
                print(f"{filename}: Found {repr(char)} (ord={ord(char)})")

        # Save if: few weird chars remain, LLM made repairs, or -save flag is set
        if modified and (weird_count <= 5 or llm_repaired or args.save):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"{filename}: Cleaned and saved")
        elif modified:
            print(f"{filename}: Skipped - needs human review")

if __name__ == "__main__":
    main()
