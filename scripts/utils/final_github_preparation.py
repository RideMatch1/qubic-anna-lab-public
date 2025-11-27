#!/usr/bin/env python3
"""
Final GitHub Preparation - Complete cleanup and update.

This script:
1. Scans all files in github_export/
2. Removes all emojis
3. Translates German to English
4. Removes LLM phrases
5. Makes content human-like
6. Updates with new analysis files
7. Prepares for commit
"""

import re
import shutil
from pathlib import Path
from typing import List, Dict
import sys

PROJECT_ROOT = Path(__file__).parent.parent.parent
GITHUB_EXPORT = PROJECT_ROOT / "github_export"

# New analysis files to add
NEW_ANALYSIS_FILES = [
 "FINAL_ANALYSIS_STATUS.md",
 "ANALYSIS_RESULTS_SUMMARY.md",
 "GEMINI_HANDOVER_COMPLETE.md",
 "outputs/analysis/mapping_database_summary.md",
 "outputs/analysis/pattern_discovery_results.json",
 "outputs/analysis/documented_vs_real_pattern_analysis.json",
]

def remove_emojis(text: str) -> str:
 """Remove all emojis."""
 emoji_pattern = r'[✅❌⚠️🎯📊💡🔬⭐🔍🚀📁📝💬🔧📋🎉💪🔥💯🌟✨🎊🎈🎁🎀🎂🎃🎄🎅🎆🎇🎈🎉🎊🎋🎌🎍🎎🎏🎐🎑🎒🎓🎔🎕🎖🎗🎘🎙🎚🎛🎜🎝🎞🎟🎠🎡🎢🎣🎤🎥🎦🎧🎨🎩🎪🎫🎬🎭🎮🎯🎰🎱🎲🎳🎴🎵🎶🎷🎸🎹🎺🎻🎼🎽🎾🎿🏀🏁🏂🏃🏄🏅🏆🏇🏈🏉🏊🏋🏌🏍🏎🏏🏐🏑🏒🏓🏔🏕🏖🏗🏘🏙🏚🏛🏜🏝🏞🏟🏠🏡🏢🏣🏤🏥🏦🏧🏨🏩🏪🏫🏬🏭🏮🏯🏰🏱🏲🏳🏴🏵🏶🏷🏸🏹🏺🏻🏼🏽🏾🏿😀😁😂😃😄😅😆😇😈😉😊😋😌😍😎😏😐😑😒😓😔😕😖😗😘😙😚😛😜😝😞😟😠😡😢😣😤😥😦😧😨😩😪😫😬😭😮😯😰😱😲😳😴😵😶😷😸😹😺😻😼😽😾😿🙀🙁🙂🙃🙄🙅🙆🙇🙈🙉🙊🙋🙌🙍🙎🙏]'
 return re.sub(emoji_pattern, '', text)

def translate_german_phrases(text: str) -> str:
 """Translate common German phrases."""
 translations = {
 r'\bWas wir haben\b': 'What we have',
 r'\bWas wir suchen\b': 'What we are looking for',
 r'\bDas Problem\b': 'The problem',
 r'\bErgebnis\b': 'Result',
 r'\bErkenntnis\b': 'Finding',
 r'\bNächste Schritte\b': 'Next steps',
 r'\bAlle Analysen erfolgreich\b': 'All analyses successful',
 r'\bFertig\b': 'Complete',
 r'\bBereit\b': 'Ready',
 r'\bWichtig\b': 'Important',
 r'\bHinweis\b': 'Note',
 r'\bAchtung\b': 'Warning',
 r'\bFehler\b': 'Error',
 r'\bErfolg\b': 'Success',
 r'\bAbgeschlossen\b': 'Completed',
 r'\bIn Bearbeitung\b': 'In progress',
 r'\bVorbereitet\b': 'Prepared',
 r'\bGeprüft\b': 'Checked',
 r'\bValidiert\b': 'Validated',
 r'\bAnalysiert\b': 'Analyzed',
 r'\bGetestet\b': 'Tested',
 r'\bGefunden\b': 'Found',
 r'\bNicht gefunden\b': 'Not found',
 r'\bFunktioniert\b': 'Works',
 r'\bFunktioniert nicht\b': 'Does not work',
 r'\bKritisch\b': 'Critical',
 r'\bWarnung\b': 'Warning',
 r'\bZusammenfassung\b': 'Summary',
 r'\bDetails\b': 'Details',
 r'\bWeitere Informationen\b': 'Further information',
 r'\bSiehe auch\b': 'See also',
 r'\bFür mehr Details\b': 'For more details',
 r'\bWeitere Schritte\b': 'Further steps',
 r'\bAls nächstes\b': 'Next',
 r'\bDann\b': 'Then',
 r'\bJetzt\b': 'Now',
 r'\bSpäter\b': 'Later',
 r'\bBereit for\b': 'Ready for',
 r'\bVorbereitet for\b': 'Prepared for',
 r'\bGeprüft und validiert\b': 'Checked and validated',
 }
 
 for pattern, replacement in translations.items():
 text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
 
 return text

def remove_llm_phrases(text: str) -> str:
 """Remove LLM-typical phrases."""
 phrases = [
 (r'\bAs you can see\b', ''),
 (r'\bTo summarize\b', ''),
 (r'\bIn conclusion\b', ''),
 (r'\bIt is important to note\b', ''),
 (r'\bIt should be noted\b', ''),
 (r'\bThis is interesting\b', ''),
 (r'\bThis is important\b', ''),
 (r'\bLet me explain\b', ''),
 (r'\bI should mention\b', ''),
 (r'\bPlease note that\b', 'Note: '),
 (r'\bKeep in mind that\b', ''),
 (r'\bMake sure to\b', ''),
 (r'\bDon\'t forget to\b', ''),
 (r'\bRemember to\b', ''),
 (r'\bBe sure to\b', ''),
 (r'\bFeel free to\b', ''),
 (r'\bIn this case\b', ''),
 (r'\bIn other words\b', ''),
 (r'\bTo put it simply\b', ''),
 (r'\bFirst and foremost\b', 'First'),
 (r'\bLast but not least\b', 'Finally'),
 (r'\bNeedless to say\b', ''),
 (r'\bIt goes without saying\b', ''),
 (r'\bWith that said\b', ''),
 (r'\bThat being said\b', ''),
 (r'\bHaving said that\b', ''),
 (r'\bLet\'s\b', ''),
 (r'\bHere\'s\b', ''),
 (r'\bHere are\b', ''),
 ]
 
 for pattern, replacement in phrases:
 text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
 
 # Clean up spacing
 text = re.sub(r' +', ' ', text)
 text = re.sub(r'\n{3,}', '\n\n', text)
 
 return text

def clean_content(content: str) -> str:
 """Complete content cleaning."""
 # Remove emojis
 content = remove_emojis(content)
 
 # Translate German
 content = translate_german_phrases(content)
 
 # Remove LLM phrases
 content = remove_llm_phrases(content)
 
 # Remove excessive punctuation
 content = re.sub(r'!{2,}', '!', content)
 content = re.sub(r'\?{2,}', '?', content)
 content = re.sub(r'\.{3,}', '...', content)
 
 return content

def clean_file(file_path: Path) -> bool:
 """Clean a single file."""
 try:
 content = file_path.read_text(encoding='utf-8')
 cleaned = clean_content(content)
 file_path.write_text(cleaned, encoding='utf-8')
 return True
 except Exception as e:
 print(f" Error cleaning {file_path}: {e}")
 return False

def main():
 """Main function."""
 print("=" * 80)
 print("FINAL GITHUB PREPARATION")
 print("=" * 80)
 print()
 
 if not GITHUB_EXPORT.exists():
 print(f"Error: {GITHUB_EXPORT} not found")
 return
 
 # Clean all MD files in github_export
 print("Cleaning all MD files in github_export/...")
 md_files = list(GITHUB_EXPORT.rglob('*.md'))
 cleaned_count = 0
 
 for md_file in md_files:
 print(f" Cleaning: {md_file.relative_to(GITHUB_EXPORT)}")
 if clean_file(md_file):
 cleaned_count += 1
 
 print(f"\nCleaned {cleaned_count} files")
 print()
 
 # Add new analysis files
 print("Adding new analysis files...")
 for file_path_str in NEW_ANALYSIS_FILES:
 source = PROJECT_ROOT / file_path_str
 if source.exists():
 if file_path_str.startswith('outputs/'):
 dest = GITHUB_EXPORT / file_path_str
 else:
 dest = GITHUB_EXPORT / source.name
 
 dest.parent.mkdir(parents=True, exist_ok=True)
 
 # Clean and copy
 content = source.read_text(encoding='utf-8')
 cleaned = clean_content(content)
 dest.write_text(cleaned, encoding='utf-8')
 print(f" Added: {dest.relative_to(GITHUB_EXPORT)}")
 else:
 print(f" Not found: {file_path_str}")
 
 print()
 print("=" * 80)
 print("PREPARATION COMPLETE")
 print("=" * 80)
 print(f"Files ready in: {GITHUB_EXPORT}")
 print()
 print("Next steps:")
 print("1. Review cleaned files")
 print("2. Commit: git add . && git commit -m 'Update: Clean analysis files'")
 print("3. Push: git push")
 print()

if __name__ == "__main__":
 main()

