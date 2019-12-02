from bitcoinutils.setup import setup
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.keys import P2pkhAddress, PrivateKey, PublicKey
from bitcoinutils.script import Script
from bitcoinutils.proxy import NodeProxy
import json
import time
from ecdsa import SigningKey, VerifyingKey, SECP256k1, ellipticcurve, numbertheory
from keys.bitcoin_keys import BitcoinWallet



class Bitcoin():
    def __init__(self):
        setup('testnet')
        self.proxy = NodeProxy('bitcoinrpc', '123456').get_proxy()

    # ==============================================================================================================
    # Encode the challenge data into a bitcoin transaction.
    # The function takes as input the publickey of the paying address,
    # challenge ciphertext and user private key(in the conf file)
    # ==============================================================================================================
    def tx_encf(self, vk_p, ct_c, user_conf_file_path):
        user_conf_file = open(user_conf_file_path)
        conf = json.load(user_conf_file)

        sk_u = conf['SK']
        sk_u = PrivateKey(secret_exponent=int(sk_u,16))
        vk_u = sk_u.get_public_key()
        addr_u = vk_u.get_address().to_string()

        #txid = '826711590bb543028418d312cf2229eba1b4fbf295fa73dbc37654085e1fc925'
        #txid = '49ab8b8f6913d5fb97c067fe9466710f62e195bab5366e484d1b2334a5b5c0c8'
        #tx_index = 1
        txid = input("Fund the address: {0} \nand insert the txid:\n".format(addr_u))
        tx_index = input("tx_index:\n")
        print("txid: ", txid)
        print("tx_index: ", tx_index)

        signed_tx_hex = self._tx_encf('04'+vk_p, ct_c, sk_u, txid, int(tx_index))
        #tx_hash = "88e602cc4766edd442ee99270f2e94bf6f7625a9b49721311fc9bba4dfe8defa"
        tx_hash = self.proxy.sendrawtransaction(signed_tx_hex)
        return tx_hash


    def _tx_encf(self, vk_p, ct_c, sk_u, txin_id, txin_index):
        # create transaction input from tx id of UTXO
        txin = TxInput(txin_id, txin_index)

        # having the vk_p from the shared key generate the corresponding address for decoder to use to respond
        vk_p = PublicKey(vk_p)
        addr_p = vk_p.get_address().to_string()

        # create transaction output using P2PKH scriptPubKey for paying address
        paying_addr = P2pkhAddress(addr_p)
        paying_txout = TxOutput(0.00002, paying_addr.to_script_pub_key())

        # create an output where the address is the ciphertext
        cipher_txout = TxOutput(0.00001, Script(['OP_HASH160', ct_c, 'OP_EQUAL']))


        # create transaction from inputs/outputs -- default locktime is used
        tx = Transaction([txin], [paying_txout, cipher_txout])
        #print("\nRaw unsigned transaction:\n" + tx.serialize())

        # use private key corresponding to the address that contains the UTXO we are trying to spend to sign the input
        vk_u = sk_u.get_public_key()
        addr_u = vk_u.get_address().to_string()

        # note that we pass the scriptPubkey as one of the inputs of sign_input because it is used to replace
        # the scriptSig of the UTXO we are trying to spend when creating the transaction digest
        from_addr = P2pkhAddress(addr_u)
        sig = sk_u.sign_input(tx, 0, from_addr.to_script_pub_key()) # 0 is for the index of the input

        # set the scriptSig (unlocking script)
        vk_u = vk_u.to_hex()
        txin.script_sig = Script([sig, vk_u])
        signed_tx = tx.serialize()

        print("Users input address: ", addr_u)
        print("Decoder paying address: ", addr_p)
        print("\nRaw signed transaction:\n" + signed_tx)

        return signed_tx



    # ================================================================================================
    # This function given a tx hash, decodes it and returns the user's public key and ciphertext
    # ================================================================================================
    def tx_decf(self, tx_hash):
        raw_tx = self.proxy.getrawtransaction(tx_hash)  # get the raw transaction from the hash of the tx
        decoded_tx = self.proxy.decoderawtransaction(raw_tx) # decode the raw transaction and get the json format

        # check to see if the tx has 1 input and two outputs and is of type pay2pubkeyhash and pay2scripthash
        if len(decoded_tx['vin']) != 1 or len(decoded_tx['vout']) != 2:
            return -1,-1
        if decoded_tx['vout'][0]['scriptPubKey']['hex'][:6] != '76a914' or decoded_tx['vout'][0]['scriptPubKey']['hex'][-4:] != '88ac': #pay2pubkeyhash
            return -1,-1
        if decoded_tx['vout'][1]['scriptPubKey']['hex'][:4] != 'a914' or decoded_tx['vout'][1]['scriptPubKey']['hex'][-2:] != '87':    #pay2scripthash
            return -1,-1

        try:
            vk_u_compressed = decoded_tx['vin'][0]['scriptSig']['hex'][-66:]
            vk_u = PublicKey(vk_u_compressed).to_hex(compressed=False)[2:]
            ct_c = decoded_tx['vout'][1]['scriptPubKey']['hex'][4:-2]
            return vk_u, ct_c
        except:
            return -1,-1



    # ================================================================================================
    # Encode the response data into a bitcoin transaction.
    # The function takes as input the private key of the paying key (derived from the shared key)
    # and the response data (ciphertext)
    # ================================================================================================

    def tx_encb(self, sk_s, ct_r, txid):
        sk_s = PrivateKey(secret_exponent=int(sk_s,16))
        signed_tx_hex = self._tx_encb(sk_s, ct_r,  txid, txin_index=0)
        #tx_hash = "33f4e564128ab824fe5864cc281ee16cb4f58db502a682fb7dca07bf36717b11"
        tx_hash = self.proxy.sendrawtransaction(signed_tx_hex)
        return tx_hash


    def _tx_encb(self, sk_s, ct_r, txin_id, txin_index):
        # create transaction input from tx id of UTXO
        txin = TxInput(txin_id, txin_index)

        # create an output where the address is the ciphertext[0:20]
        cipher1_txout = TxOutput(0.000001, Script(['OP_DUP', 'OP_HASH160', ct_r[:40], 'OP_EQUALVERIFY', 'OP_CHECKSIG']))

        # create another output where the address is the ciphertext[20:40]
        cipher2_txout = TxOutput(0.000001, Script(['OP_HASH160', ct_r[40:], 'OP_EQUAL']))

        # create transaction from inputs/outputs -- default locktime is used
        tx = Transaction([txin], [cipher1_txout, cipher2_txout])
        #print("\nRaw unsigned transaction:\n" + tx.serialize())

        # use private key corresponding to the address that contains the UTXO we are trying to spend to sign the input
        vk_p = sk_s.get_public_key()
        addr_p = vk_p.get_address().to_string()

        # note that we pass the scriptPubkey as one of the inputs of sign_input because it is used to replace
        # the scriptSig of the UTXO we are trying to spend when creating the transaction digest
        from_addr = P2pkhAddress(addr_p)
        sig = sk_s.sign_input(tx, 0, from_addr.to_script_pub_key())

        # set the scriptSig (unlocking script)
        vk_p = vk_p.to_hex()
        txin.script_sig = Script([sig, vk_p])
        signed_tx = tx.serialize()

        print("\nRaw signed transaction:\n" + signed_tx)
        return signed_tx


    # ================================================================================================
    # Given a block id and an public key of transaction return the encoded data in that transaction
    # ================================================================================================
    def tx_decb(self, block_id, vk_p):
        txs_hashes = self.get_block_txs(block_id)  # Get the hash of transactions inside this block
        for tx_hash in txs_hashes:
            raw_tx = self.proxy.getrawtransaction(tx_hash)  # get the raw transaction from the hash of the tx
            decoded_tx = self.proxy.decoderawtransaction(raw_tx) # decode the raw transaction and get the json format

            # check to see if the tx has 1 input and two outputs and is of type pay2pubkeyhash
            if len(decoded_tx['vin']) != 1 or len(decoded_tx['vout']) != 2:
                continue
            if decoded_tx['vout'][0]['scriptPubKey']['hex'][:6] != '76a914' or decoded_tx['vout'][0]['scriptPubKey']['hex'][-4:] != '88ac':  # pay2pubkeyhash
                continue
            if decoded_tx['vout'][1]['scriptPubKey']['hex'][:4] != 'a914' or decoded_tx['vout'][1]['scriptPubKey']['hex'][-2:] != '87':  # pay2scripthash
                continue

            try:
                vk_p_compressed = decoded_tx['vin'][0]['scriptSig']['hex'][-66:]
                ct_r1 = decoded_tx['vout'][0]['scriptPubKey']['hex'][6:-4]
                ct_r2 = decoded_tx['vout'][1]['scriptPubKey']['hex'][4:-2]
                if vk_p_compressed == PublicKey('04'+vk_p).to_hex(compressed=True):
                    print("Found the transaction with response message")
                    return ct_r1 + ct_r2
            except:
                continue

        return None


    # ================================================================================================
    # Given a block id return the hashes of the transactions in that block.
    # ================================================================================================
    def get_block_txs(self, block_id):
        block_hash = self.proxy.getblockhash(block_id)
        block_info = self.proxy.getblock(block_hash)
        txs_hashes = block_info['tx']  # Get the hash of transactions inside this block
        return txs_hashes



