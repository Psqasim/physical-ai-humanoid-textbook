#!/usr/bin/env python3
"""
Translation automation script for Docusaurus UI strings.

This script translates UI strings from code.json files using OpenAI GPT-4 API.
It supports batch translation with temperature=0.3 for consistent results.

Usage:
    python scripts/translate-ui-strings.py --target ur
    python scripts/translate-ui-strings.py --target ja
"""

import argparse
import json
import os
import sys
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / "backend" / ".env")


def load_source_strings(locale_dir: Path) -> dict:
    """Load source English strings to be translated."""
    code_json_path = locale_dir / "code.json"
    if code_json_path.exists():
        with open(code_json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def translate_strings(strings: dict, target_language: str) -> dict:
    """
    Translate strings to target language using OpenAI API.

    Args:
        strings: Dictionary of English strings to translate
        target_language: Target language code (ur, ja)

    Returns:
        Dictionary of translated strings
    """
    # Language names for prompts
    language_names = {
        'ur': 'Urdu (اردو)',
        'ja': 'Japanese (日本語)'
    }

    target_lang_name = language_names.get(target_language, target_language)

    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables")
        print("Please set it in backend/.env file")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    print(f"Translating {len(strings)} strings to {target_lang_name}...")

    translated_strings = {}
    batch_size = 20  # Process in batches to avoid token limits

    items = list(strings.items())
    total_batches = (len(items) + batch_size - 1) // batch_size

    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min((batch_num + 1) * batch_size, len(items))
        batch_items = items[start_idx:end_idx]

        # Prepare batch for translation
        batch_to_translate = {key: value for key, value in batch_items}

        # Create translation prompt
        prompt = f"""Translate the following Docusaurus UI strings from English to {target_lang_name}.

IMPORTANT RULES:
1. Translate ONLY the "message" field values
2. Keep the "description" fields in English (they are for developers)
3. Preserve all placeholders like {{count}}, {{mode}}, {{tagName}}, {{heading}}, etc.
4. Preserve all HTML entities and special characters
5. Maintain the same JSON structure
6. For technical terms like "GitHub", "Docs", keep them as-is or transliterate appropriately
7. Use natural, native {target_lang_name} phrasing

Input JSON:
{json.dumps(batch_to_translate, ensure_ascii=False, indent=2)}

Output the translated JSON with the same structure, translating only the "message" fields."""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"You are a professional translator specializing in UI/UX localization. You translate English UI strings to {target_lang_name} while preserving technical accuracy and natural phrasing."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Low temperature for consistent translations
                max_tokens=4000
            )

            # Parse the response
            translated_batch_text = response.choices[0].message.content

            # Extract JSON from response (remove markdown code blocks if present)
            if "```json" in translated_batch_text:
                translated_batch_text = translated_batch_text.split("```json")[1].split("```")[0].strip()
            elif "```" in translated_batch_text:
                translated_batch_text = translated_batch_text.split("```")[1].split("```")[0].strip()

            translated_batch = json.loads(translated_batch_text)
            translated_strings.update(translated_batch)

            print(f"  Batch {batch_num + 1}/{total_batches} completed ({end_idx}/{len(items)} strings)")

        except Exception as e:
            print(f"Error translating batch {batch_num + 1}: {str(e)}")
            # Keep original strings for failed batch
            translated_strings.update(batch_to_translate)

    print(f"Translation to {target_lang_name} completed!")
    return translated_strings


def save_translations(locale_dir: Path, translations: dict):
    """Save translated strings to code.json file."""
    code_json_path = locale_dir / "code.json"
    with open(code_json_path, 'w', encoding='utf-8') as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)
    print(f"Translations saved to {code_json_path}")


def main():
    parser = argparse.ArgumentParser(description='Translate Docusaurus UI strings')
    parser.add_argument('--target', required=True, choices=['ur', 'ja'],
                        help='Target language code')
    args = parser.parse_args()

    # Paths
    project_root = Path(__file__).parent.parent
    i18n_dir = project_root / "i18n"
    target_locale_dir = i18n_dir / args.target

    # Create target directory if it doesn't exist
    target_locale_dir.mkdir(parents=True, exist_ok=True)

    # Load source strings (from English or existing target)
    source_strings = load_source_strings(target_locale_dir)

    # Translate
    translated_strings = translate_strings(source_strings, args.target)

    # Save
    save_translations(target_locale_dir, translated_strings)

    print(f"Translation process complete for {args.target}")


if __name__ == "__main__":
    main()
