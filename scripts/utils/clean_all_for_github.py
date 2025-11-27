#!/usr/bin/env python3
"""
Clean all files for GitHub - Remove emojis, German, LLM phrases.

This script processes all MD files and cleans them completely.
"""

import re
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent.parent
GITHUB_EXPORT = PROJECT_ROOT / "github_export"

def clean_file(file_path: Path):
 """Clean a single file."""
 try:
 content = file_path.read_text(encoding='utf-8')
 
 # Remove emojis
 emoji_pattern = r'[✅❌⚠️🎯📊💡🔬⭐🔍🚀📁📝💬🔧📋🎉💪🔥💯🌟✨🎊🎈🎁🎀🎂🎃🎄🎅🎆🎇🎈🎉🎊🎋🎌🎍🎎🎏🎐🎑🎒🎓🎔🎕🎖🎗🎘🎙🎚🎛🎜🎝🎞🎟🎠🎡🎢🎣🎤🎥🎦🎧🎨🎩🎪🎫🎬🎭🎮🎯🎰🎱🎲🎳🎴🎵🎶🎷🎸🎹🎺🎻🎼🎽🎾🎿🏀🏁🏂🏃🏄🏅🏆🏇🏈🏉🏊🏋🏌🏍🏎🏏🏐🏑🏒🏓🏔🏕🏖🏗🏘🏙🏚🏛🏜🏝🏞🏟🏠🏡🏢🏣🏤🏥🏦🏧🏨🏩🏪🏫🏬🏭🏮🏯🏰🏱🏲🏳🏴🏵🏶🏷🏸🏹🏺🏻🏼🏽🏾🏿😀😁😂😃😄😅😆😇😈😉😊😋😌😍😎😏😐😑😒😓😔😕😖😗😘😙😚😛😜😝😞😟😠😡😢😣😤😥😦😧😨😩😪😫😬😭😮😯😰😱😲😳😴😵😶😷😸😹😺😻😼😽😾😿🙀🙁🙂🙃🙄🙅🙆🙇🙈🙉🙊🙋🙌🙍🙎🙏]'
 content = re.sub(emoji_pattern, '', content)
 
 # Translate German phrases
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
 r'\bDatum\b': 'Date',
 r'\bAktuell\b': 'Current',
 r'\bMomentan\b': 'Currently',
 r'\bHeute\b': 'Today',
 r'\bGestern\b': 'Yesterday',
 r'\bMorgen\b': 'Tomorrow',
 r'\bDiese Woche\b': 'This week',
 r'\bLetzte Woche\b': 'Last week',
 r'\bNächste Woche\b': 'Next week',
 r'\bDieser Monat\b': 'This month',
 r'\bLetzter Monat\b': 'Last month',
 r'\bNächster Monat\b': 'Next month',
 r'\bDieses Jahr\b': 'This year',
 r'\bLetztes Jahr\b': 'Last year',
 r'\bNächstes Jahr\b': 'Next year',
 r'\bSeit\b': 'Since',
 r'\bBis\b': 'Until',
 r'\bVon\b': 'From',
 r'\bNach\b': 'After',
 r'\bVor\b': 'Before',
 r'\bWährend\b': 'During',
 r'\bWährenddessen\b': 'Meanwhile',
 r'\bGleichzeitig\b': 'At the same time',
 r'\bParallel\b': 'In parallel',
 r'\bSeriell\b': 'Serially',
 r'\bSequentiell\b': 'Sequentially',
 r'\bParallele\b': 'Parallel',
 r'\bSerielle\b': 'Serial',
 r'\bSequenzielle\b': 'Sequential',
 r'\bGleichzeitige\b': 'Simultaneous',
 r'\bSimultane\b': 'Simultaneous',
 r'\bSchnelle\b': 'Fast',
 r'\bLangsame\b': 'Slow',
 r'\bSchnell\b': 'Fast',
 r'\bLangsam\b': 'Slow',
 r'\bSchneller\b': 'Faster',
 r'\bLangsamer\b': 'Slower',
 r'\bAm schnellsten\b': 'Fastest',
 r'\bAm langsamsten\b': 'Slowest',
 r'\bSchnellste\b': 'Fastest',
 r'\bLangsamste\b': 'Slowest',
 r'\bGeschwindigkeit\b': 'Speed',
 r'\bGeschwindigkeiten\b': 'Speeds',
 r'\bTempo\b': 'Pace',
 r'\bTempi\b': 'Paces',
 r'\bRate\b': 'Rate',
 r'\bRaten\b': 'Rates',
 }
 
 for pattern, replacement in translations.items():
 content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
 
 # Remove LLM phrases
 llm_phrases = [
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
 
 for pattern, replacement in llm_phrases:
 content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
 
 # Clean up spacing
 content = re.sub(r' +', ' ', content)
 content = re.sub(r'\n{3,}', '\n\n', content)
 
 # Remove excessive punctuation
 content = re.sub(r'!{2,}', '!', content)
 content = re.sub(r'\?{2,}', '?', content)
 content = re.sub(r'\.{3,}', '...', content)
 
 # Write back
 file_path.write_text(content, encoding='utf-8')
 return True
 except Exception as e:
 print(f"Error cleaning {file_path}: {e}")
 return False

def main():
 """Main function."""
 print("=" * 80)
 print("CLEAN ALL FILES FOR GITHUB")
 print("=" * 80)
 print()
 
 if not GITHUB_EXPORT.exists():
 print(f"Error: {GITHUB_EXPORT} not found")
 return
 
 # Find all MD files
 md_files = list(GITHUB_EXPORT.rglob('*.md'))
 print(f"Found {len(md_files)} MD files")
 print()
 
 cleaned = 0
 for md_file in md_files:
 print(f"Cleaning: {md_file.relative_to(GITHUB_EXPORT)}")
 if clean_file(md_file):
 cleaned += 1
 
 print()
 print("=" * 80)
 print(f"Cleaned {cleaned} files")
 print("=" * 80)

if __name__ == "__main__":
 main()

