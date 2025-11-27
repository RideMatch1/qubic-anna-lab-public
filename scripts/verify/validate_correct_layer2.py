
import json
import time
from qubipy.rpc import rpc_client

layer2_data = [["Diagonal #1", "CYTORJWZCJFCYXAHJPLPPCWPVOXTDZBWQYVWANQDYQCCIORJTVMPBIXBKIVP"], ["Diagonal #2", "FPEXLMCOGJNYAAELTBSEDHAZCCNAGXJRPRFNBEXUKPDHFTVAHETKPANQCMLM"], ["Diagonal #3", "ABCXUAPWHTDRJDASQEZSNCDAMXNJAXDTNESWQLNWPZBBUXDGNJLGYXETNGHN"], ["Diagonal #4", "AGTIRJYQVZXUEFAUCPEBEYHDAFXZFMFOARDSUKLHHBETDIVPWVZMOORUOXSD"], ["Vortex #1", "GNMLDHIPZJHJDNCCCRFHVDDPEIHJEWOPVVAXQRFIBYDZBNDHTELZIANUDAWB"], ["Vortex #2", "ADVDNZIGNSCXAODGDMEXMKICVHFOHBROQQMVZOGAMVASHQURDBPDNJRJJQRM"], ["Vortex #3", "HFVFDNEHUVRRBIESYPSSRPNJSVVSDBIPNAXAHIKISLAKYZFKMWNJXVVUEUQJ"], ["Vortex #4", "BIARJWYAYURJYJBXXEDMQOKGSJXBFNWCDSHXZILITIDHCMJYUMPPXQZQAXNR"]]

rpc = rpc_client.QubiPy_RPC()
results = []

for label, identity in layer2_data:
 try:
 time.sleep(1.5)
 balance_data = rpc.get_balance(identity)
 
 if balance_data:
 results.append({
 "label": label,
 "identity": identity,
 "exists": True,
 "balance": balance_data.get("balance", "0"),
 "valid_for_tick": balance_data.get("validForTick", 0),
 })
 else:
 results.append({
 "label": label,
 "identity": identity,
 "exists": False,
 })
 except Exception as e:
 results.append({
 "label": label,
 "identity": identity,
 "error": str(e),
 })

with open("outputs/derived/correct_layer2_onchain_validation.json", "w") as f:
 json.dump(results, f, indent=2)

verified = sum(1 for r in results if r.get("exists"))
print(f"On-chain verifiziert: {verified}/{len(results)}")
