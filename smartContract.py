def smartContractFunctions(contract_address, button, memberWallet = False, payeesList = False, sharesList = False):
    import json
    from web3 import Web3
    from web3.middleware import geth_poa_middleware
    from urllib import response # for command line arguments
    import requests # for http requests

    # payeesList = ['0x63C18042Ff056493c62bc74d04A32F03a5813798','0xf48B3847936bB9cc96A3cFB0F01Eb1057cCFa349']
    #sharesList = [5,5]

   
    f = open("tokens")
    s = f.read()
    tokensDict = json.loads(s)
    private_key = tokensDict["private_key"]


    
    account_from = {
    'private_key': private_key,
    'address': '0x63C18042Ff056493c62bc74d04A32F03a5813798',
    }

    #https://polygon-mainnet.infura.io/v3/a31017990a434050ab5b5dad42ba299a
    #https://polygon-mumbai.infura.io/v3/a31017990a434050ab5b5dad42ba299a
    provider_url = 'https://polygon-mainnet.infura.io/v3/a31017990a434050ab5b5dad42ba299a'
    web3 = Web3(Web3.HTTPProvider(provider_url))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    #We dont need abi for checking address balance
    if button != "Contract Balance":
      polygon_api_key = 'WZ1FEBAQFZ4S44E74JZ7PQSW1SARSH48KT'
      #https://api-testnet.polygonscan.com
      #https://api.polygonscan.com/
      ABI_ENDPOINT = f'https://api.polygonscan.com/api?module=contract&apikey={polygon_api_key}&action=getabi&address={contract_address}'#Need api key else rate limit
      response = requests.get(ABI_ENDPOINT)
      response_json = response.json()
      abi_json = json.loads(response_json['result'])
      contract_abi = json.dumps(abi_json, indent=4, sort_keys=True)
      contract = web3.eth.contract(address=contract_address, abi = contract_abi)
    

    #different function for different button


    if button == 'Contract Balance':
      polygon_api_key = 'WZ1FEBAQFZ4S44E74JZ7PQSW1SARSH48KT'
      tokenTicker = 'MATIC'
      balance_endpoint = 'https://api.polygonscan.com/api?module=account&action=balance&address=%s&apikey=%s'%(contract_address, polygon_api_key)
      response = requests.get(balance_endpoint)
      response_json = response.json()
      result = json.loads(response_json['result'])
      balance = web3.fromWei(result,"ether")
        
      Crypto_Compare_API_Key = 'e62dcb469049b91441eabec0e18d8036fd1ae52d28f6d57352a8f23f043f83dc'
      Token_Price_Endpoint = 'https://min-api.cryptocompare.com/data/price?fsym=%s&tsyms=USD&api_key=%s'%(tokenTicker, Crypto_Compare_API_Key)
      response = requests.get(Token_Price_Endpoint)
      response_json = response.json()
      tokenPrice = response_json['USD']
      contractDollarBalance = float(balance) * float(tokenPrice)
      return([contractDollarBalance, balance])


    if button == 'Contract Matic':
      balance_endpoint = 'https://api.polygonscan.com/api?module=account&action=balance&address=0xb6506ee5F7cF6802eF7D1B651E7f2A5af1B6949a&apikey=WZ1FEBAQFZ4S44E74JZ7PQSW1SARSH48KT'
      response = requests.get(balance_endpoint)
      response_json = response.json()
      result = json.loads(response_json['result'])
      balance = web3.fromWei(result,"ether")
      return('Contract address **'+contract_address+'** has **'+str(balance)+'** Matic')

          
    if button == 'Releaseable Matic':
      canRelease = contract.functions.releasable(memberWallet).call()
      canRelease = web3.fromWei(canRelease, "ether")#make it correct decimal place
      return('You have **'+str(canRelease)+'** MATIC to withdraw')
    
    if button == 'Release Matic':
        
      try:
        contract_tx = contract.functions.release(memberWallet).buildTransaction(
            {
                'from': account_from['address'],
                'nonce': web3.eth.get_transaction_count(account_from['address']),
            }
        )
        
        tx_create = web3.eth.account.sign_transaction(contract_tx, account_from['private_key'])
  
        # 7. Send tx and wait for receipt
        tx_hash = web3.eth.send_raw_transaction(tx_create.rawTransaction)
       # tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        return('Succesfully released Matic to wallet address **' + memberWallet + '**')
          
      except:#There are actually 2 errors with same web3.exceptions.ContractLogicError, no shares and not due payment, I used blanket over error type
        return('Your account is not due payment')
      
    if button == 'Clear Payees':
      contract_tx = contract.functions._clearPayees().buildTransaction(
              {
                  'from': account_from['address'],
                  'nonce': web3.eth.get_transaction_count(account_from['address']),
              }
          )
      
      tx_create = web3.eth.account.sign_transaction(contract_tx, account_from['private_key'])
      # 7. Send tx and wait for receipt
      tx_hash = web3.eth.send_raw_transaction(tx_create.rawTransaction)
      #pause for clearPayees to work before _addPayees else "payee already added"
      tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
      print("tx_receipt: "+str(tx_receipt))


    if button == 'Add Payees':
      #try:
        contract_tx = contract.functions._addPayees(payeesList, sharesList).buildTransaction(
            {
                'from': account_from['address'], #If nonce error, try again
                'nonce': web3.eth.get_transaction_count(account_from['address']),
            }
        )

        tx_create = web3.eth.account.sign_transaction(contract_tx, account_from['private_key'])
        # 7. Send tx and wait for receipt
        tx_hash = web3.eth.send_raw_transaction(tx_create.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        # print("tx_receipt: "+str(tx_receipt))

          
      #except:
        #return('returnFail')


      
      
