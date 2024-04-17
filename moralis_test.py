from moralis import evm_api
import json

f = open("tokens")
s = f.read()
tokensDict = json.loads(s)
api_key = tokensDict["moralis_api_key"]

params = {
  "chain": "polygon",
  "format": "decimal",
  "media_items": False,
  "address": "0x63C18042Ff056493c62bc74d04A32F03a5813798"
}

result = evm_api.nft.get_wallet_nfts(
  api_key=api_key,
  params=params,
)

print(result)

# converting it to json because of unicode characters
# print(json.dumps(result, indent=4))