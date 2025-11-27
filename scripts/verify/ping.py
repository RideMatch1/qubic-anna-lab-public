from qubipy.rpc import rpc_client
rpc = rpc_client.QubiPy_RPC()
print("Latest tick:", rpc.get_latest_tick())
