
import json
from qubipy.crypto.utils import (
 kangaroo_twelve,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

layer2_data = {"Diagonal #1": {"parent": "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR", "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd", "identity": "CYTORJWZCJFCYXAHJPLPPCWPVOXTDZBWQYVWANQDYQCCIORJTVMPBIXBKIVP"}, "Diagonal #2": {"parent": "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ", "seed": "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr", "identity": "FPEXLMCOGJNYAAELTBSEDHAZCCNAGXJRPRFNBEXUKPDHFTVAHETKPANQCMLM"}, "Diagonal #3": {"parent": "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV", "seed": "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn", "identity": "ABCXUAPWHTDRJDASQEZSNCDAMXNJAXDTNESWQLNWPZBBUXDGNJLGYXETNGHN"}, "Diagonal #4": {"parent": "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC", "seed": "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht", "identity": "AGTIRJYQVZXUEFAUCPEBEYHDAFXZFMFOARDSUKLHHBETDIVPWVZMOORUOXSD"}, "Vortex #1": {"parent": "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF", "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml", "identity": "GNMLDHIPZJHJDNCCCRFHVDDPEIHJEWOPVVAXQRFIBYDZBNDHTELZIANUDAWB"}, "Vortex #2": {"parent": "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD", "seed": "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb", "identity": "ADVDNZIGNSCXAODGDMEXMKICVHFOHBROQQMVZOGAMVASHQURDBPDNJRJJQRM"}, "Vortex #3": {"parent": "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL", "seed": "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw", "identity": "HFVFDNEHUVRRBIESYPSSRPNJSVVSDBIPNAXAHIKISLAKYZFKMWNJXVVUEUQJ"}, "Vortex #4": {"parent": "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK", "seed": "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc", "identity": "BIARJWYAYURJYJBXXEDMQOKGSJXBFNWCDSHXZILITIDHCMJYUMPPXQZQAXNR"}}

print("=" * 80)
print("TEST: KANGAROOTWELVE ALS SUBSEED-DERIVATION")
print("=" * 80)
print()

results = []
matches = 0

for label, data in layer2_data.items():
 seed = data["seed"]
 expected_identity = data["identity"]
 
 print(f"{label}:")
 print(f" Seed: {seed}")
 print(f" Expected: {expected_identity[:40]}...")
 
 try:
 # Teste: subseed = kangaroo_twelve(seed_bytes, 55, 32)
 seed_bytes = seed.encode('utf-8')
 subseed = kangaroo_twelve(seed_bytes, len(seed_bytes), 32)
 
 # Private Key
 private_key = get_private_key_from_subseed(subseed)
 
 # Public Key
 public_key = get_public_key_from_private_key(private_key)
 
 # Identity
 derived = get_identity_from_public_key(public_key)
 
 print(f" Derived: {derived[:40]}...")
 
 match = derived == expected_identity
 if match:
 matches += 1
 print(f" ✅ MATCH!")
 else:
 print(f" ❌ Kein Match")
 
 results.append({
 "label": label,
 "seed": seed,
 "expected": expected_identity,
 "derived": derived,
 "match": match,
 })
 
 except Exception as e:
 print(f" ❌ Error: {e}")
 results.append({
 "label": label,
 "seed": seed,
 "expected": expected_identity,
 "error": str(e),
 })
 
 print()

# Zusammenfassung
print("=" * 80)
print("ERGEBNISSE")
print("=" * 80)
print()
print(f"Matches: {matches}/8")
print()

if matches == 8:
 print("✅✅✅ PERFEKT! Die korrekte Methode ist:")
 print(" subseed = kangaroo_twelve(seed_bytes, len(seed_bytes), 32)")
 print()
 print("Das bedeutet:")
 print(" get_subseed_from_seed(seed_bytes) = kangaroo_twelve(seed_bytes, 55, 32)")

# Speichere Ergebnisse
with open("outputs/derived/kangaroo_twelve_validation.json", "w") as f:
 json.dump({
 "method": "kangaroo_twelve(seed_bytes, len(seed_bytes), 32)",
 "matches": matches,
 "total": 8,
 "results": results,
 }, f, indent=2)

print()
print(f"✅ Ergebnisse gespeichert")
