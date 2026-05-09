# Scanner

Part of a suite of tools designed to clean up `.txt` files for LLM fine-tuning.

## What it does

Scanner reads all `.txt` files in a given directory and replaces non-ASCII Unicode characters with their closest ASCII equivalent (e.g. curly quotes become straight quotes, em dashes become `--`, and so on).

- If a file has **5 or fewer** characters requiring replacement, it is cleaned and saved automatically.
- If a file has **more than 5** characters requiring replacement, it is flagged for human review and left untouched.

## Command-line options

```
python scanner.py [directory] [-llm] [-save]
```

- **directory** — path to the folder containing `.txt` files. If omitted, the program will prompt for it.
- **-llm** — when the program encounters U+FFFD (Unicode's catch-all replacement character for unknown or corrupted characters), it calls a local LLM served by [LM Studio](https://lmstudio.ai) and asks it to infer the most likely intended character from context. Files repaired this way are saved automatically.
- **-save** — forces the program to save files even if more than 5 corrupted characters remain. Useful after visually inspecting a flagged file and confirming it is safe to clean.

## Requirements

- Python 3
- [requests](https://pypi.org/project/requests/) (`pip install requests`)
- [LM Studio](https://lmstudio.ai) running locally on port 1234 (only required for `-llm` mode)
