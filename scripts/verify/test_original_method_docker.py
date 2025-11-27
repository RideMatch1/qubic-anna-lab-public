
import json
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

test_cases = [
 {
 "label": "Diagonal #1",
 "parent": "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR",
 "child": "CYTORJWZCJFCYXAHJPLPPCWPVOXTDZBWQYVWANQDYQCCIORJTVMPBIXBKIVP",
 "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd"
 },
 {
 "label": "Diagonal #2",
 "parent": "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ",
 "child": "CYTORJWZCJFCYXAHJPLPPCWPVOXTDZBWQYVWANQDYQCCIORJTVMPBIXBKIVP",
 "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd"
 },
 {
 "label": "Diagonal #3",
 "parent": "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV",
 "child": "CYTORJWZCJFCYXAHJPLPPCWPVOXTDZBWQYVWANQDYQCCIORJTVMPBIXBKIVP",
 "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd"
 },
 {
 "label": "Diagonal #4",
 "parent": "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC",
 "child": "CYTORJWZCJFCYXAHJPLPPCWPVOXTDZBWQYVWANQDYQCCIORJTVMPBIXBKIVP",
 "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd"
 },
 {
 "label": "Vortex #1",
 "parent": "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF",
 "child": "GNMLDHIPZJHJDNCCCRFHVDDPEIHJEWOPVVAXQRFIBYDZBNDHTELZIANUDAWB",
 "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml"
 },
 {
 "label": "Vortex #2",
 "parent": "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD",
 "child": "GNMLDHIPZJHJDNCCCRFHVDDPEIHJEWOPVVAXQRFIBYDZBNDHTELZIANUDAWB",
 "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml"
 },
 {
 "label": "Vortex #3",
 "parent": "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL",
 "child": "GNMLDHIPZJHJDNCCCRFHVDDPEIHJEWOPVVAXQRFIBYDZBNDHTELZIANUDAWB",
 "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml"
 },
 {
 "label": "Vortex #4",
 "parent": "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK",
 "child": "GNMLDHIPZJHJDNCCCRFHVDDPEIHJEWOPVVAXQRFIBYDZBNDHTELZIANUDAWB",
 "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml"
 }
]

results = []

for case in test_cases:
 try:
 # Seed-Extraktion checkn
 seed_original = case["parent"][:56].lower()[:55]
 seed_match = seed_original == case["seed"]
 
 # Derivation
 seed_bytes = bytes(case["seed"], 'utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 derived = get_identity_from_public_key(public_key)
 
 derived_match = derived == case["child"]
 
 results.append({
 "label": case["label"],
 "seed_match": seed_match,
 "derived_match": derived_match,
 "derived": derived,
 "expected": case["child"],
 })
 
 status = "✅" if derived_match else "❌"
 print(f"{status} {case['label']}: Seed={seed_match}, Derived={derived_match}")
 
 except Exception as e:
 results.append({
 "label": case["label"],
 "error": str(e),
 })
 print(f"❌ {case['label']}: Error={e}")

# Speichere Ergebnisse
with open("outputs/derived/original_method_validation.json", "w") as f:
 json.dump(results, f, indent=2)

# Zusammenfassung
matches = sum(1 for r in results if r.get("derived_match"))
print()
print(f"Ergebnis: {matches}/{len(test_cases)} Matches")
