from bitcoinutils.setup import setup
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.keys import P2pkhAddress, PrivateKey, PublicKey
from bitcoinutils.script import Script
from bitcoinutils.proxy import NodeProxy
import json
from crypto_tools import Crypto
from ecdsa import SigningKey, VerifyingKey, SECP256k1, ellipticcurve, numbertheory
from keys.bitcoin_keys import BitcoinWallet
import os
import time
import subprocess


zcash_cli = 'REPLACE WITH PATH TO ZCASH CLI'
conf_file = '-conf=REPLACE WITH PATH TO CONF FILE'
public_address_decoder_shielded = "ztestsapling1hkwvecp9cyz057k765nvatkrpkqzwek7jwm797mgfgsjzl0605s6r6c0crvrxyk6f0psgjd0r2e"
public_address_decoder_transparent = "tmLWDd6NpjyCgcTWSKoAebX9H25oR6YUVst"

class Zcash():
    def __init__(self):
        self.challenge_len = 20
        self.response_len = 40
        self.address_len = 176 #88*2 for hex representation (addresses are 88 bytes)
        self.tx_addr_dict = {}


    # ==============================================================================================================
    # Encode the challenge data into a bitcoin transaction.
    # The function takes as input the publickey of the paying address,
    # challenge ciphertext and user private key(in the conf file)
    # ==============================================================================================================
    def tx_encf(self, vk_p, ct_c, user_conf_file_path):
        user_conf_file = open(user_conf_file_path)
        conf = json.load(user_conf_file)
        self.challenge_len = conf['CHA_LEN']
        self.response_len = conf['RES_LEN']

        #--------------------import the private key of the user to wallet and fund it----------------
        sk_u = conf['SK']
        sk_u = PrivateKey(secret_exponent=int(sk_u,16))
        cmd = os.popen(zcash_cli+" "+conf_file+' importprivkey '+sk_u.to_wif()+' \"label\" false')
        addr_u = cmd.read()
        print("\nuser's address: ", addr_u)

        # ---------------------setup a change shielded address for the user----------------------------
        cmd = os.popen(zcash_cli + " " + conf_file + ' z_getnewaddress ')  # create a new shielded address
        self.public_address_user_shielded = cmd.read()
        #self.public_address_user_shielded ="ztestsapling13y3ujgw6swemw4lhlk9786g3wngfgqmxjdy7f0d5wg6jz0yvmntnk5u4agvxt3zptght5rftmtj"
        print("change shielded address: ", self.public_address_user_shielded)

        cmd = os.popen(zcash_cli + " " + conf_file + ' z_exportkey ' + self.public_address_user_shielded)  # export the private key
        sk_change_shielded = cmd.read()
        print("paying shielded private key: ", sk_change_shielded)
        #---------------------setup the tx to send-----------------------------
        tx = ' \'[{\"address\": \"' + addr_u.strip() + '\", \"amount\":0.82},' + \
                '{\"address\": \"' + public_address_user_shielded.strip() + '\", \"amount\":0},' + \
                '{ \"address\": \"' + public_address_decoder_shielded.strip() + '\", \"amount\":0.01, \"memo\": \"' \
                    + ct_c + self.public_address_user_shielded.encode().hex() + '\"}]\''

        cmd = zcash_cli + ' ' + conf_file + ' z_sendmany ' + addr_u.strip()  + tx + ' 1 0'
        tx_operation_id = os.popen(cmd).read()
        print("tx1 operation id: ", tx_operation_id)
        return tx_operation_id
        #txid= 46388ce88b4ab7692b9a511c1f340407e852303a229bb8a75dbad7bf3a79de1b



    # ================================================================================================
    # This function given a tx hash, decodes it and returns the user's public key and ciphertext
    # ================================================================================================
    def tx_decf(self, tx_hash):
        decoded_tx = self.get_tx(tx_hash)
        #--------------------get the public key of the user------------------------------
        if len(decoded_tx['vin']) != 1 or len(decoded_tx['vShieldedOutput']) != 2:
            return -1,-1
        try:
            vk_u_compressed = decoded_tx['vin'][0]['scriptSig']['hex'][-66:]
            vk_u = PublicKey(vk_u_compressed).to_hex(compressed=False)[2:]
        except:
            return -1,-1
        #--------------------get the ciphertext------------------------------------------
        cmd = os.popen(zcash_cli + " " + conf_file + ' z_listreceivedbyaddress ' + public_address_decoder_shielded)
        tx_json = json.loads(cmd.read())[-1]
        ct_c = tx_json['memo'][:self.challenge_len*2]
        self.tx_addr_dict[tx_hash] = bytes.fromhex(tx_json['memo'][self.challenge_len*2:self.challenge_len*2+self.address_len]).decode()
        return vk_u, ct_c



    # ================================================================================================
    # Encode the response data into a bitcoin transaction.
    # The function takes as input the private key of the paying key (derived from the shared key)
    # and the response data (ciphertext)
    # ================================================================================================
    def tx_encb(self, sk_s, ct_r, txid):
        addr_u = self.tx_addr_dict[txid]

        # ---------------------setup the tx to send-----------------------------
        tx = ' \'[{\"address\": \"' + public_address_decoder_transparent.strip() + '\", \"amount\":0.82},' + \
             '{\"address\": \"' + public_address_decoder_shielded.strip() + '\", \"amount\":0},' + \
             '{\"address\": \"' + addr_u.strip() + '\", \"amount\":0, \"memo\": \"' + ct_r + '\"}]\''
        cmd = zcash_cli + ' ' + conf_file + ' z_sendmany ' + public_address_decoder_transparent.strip() + tx + ' 1 0'
        tx_operation_id = os.popen(cmd).read()
        print("tx2 operation id: ", tx_operation_id)

        return tx_operation_id
        #txid=3120fedf71e52f6cc2a5434657055d0156a722297c68f3b610268cca685a6184


    # ================================================================================================
    # Given a block id and an public key of transaction return the encoded data in that transaction
    # ================================================================================================
    def tx_decb(self, block_id, vk_p):
        ts = time.time()
        txs_hashes = self.get_block_txs(block_id)  # Get the hash of transactions inside this block
        tf =time.time()
        print("block fetch: ", (tf-ts)*1000)
        print(len(txs_hashes))
        for tx_hash in txs_hashes:
            print(tx_hash)
            try:
                decoded_tx = self.get_tx(tx_hash)

                if len(decoded_tx['vin']) != 1 or len(decoded_tx['vShieldedOutput']) != 2:
                    continue
            except:
                continue

            # --------------------get the ciphertext------------------------------------------
            try:
                cmd = os.popen(
                    zcash_cli + " " + conf_file + ' z_listreceivedbyaddress ' + self.public_address_user_shielded)
                tx_json = json.loads(cmd.read())[0]
                print(tx_json)
                ct_r = tx_json['memo'][:self.response_len*2]
                return ct_r
            except:
                pass

        return None


    # ================================================================================================
    # Given a json of a transaction given its hash value.
    # ================================================================================================
    def get_tx(self, tx_hash):
        try: # get raw transaction and decode it
            cmd = zcash_cli + ' ' + conf_file + ' getrawtransaction ' +  tx_hash.strip()
            raw_tx = os.popen(cmd).read()

            cmd = zcash_cli + ' ' + conf_file + ' decoderawtransaction ' + raw_tx.strip()
            decoded_tx = json.loads(os.popen(cmd).read())
            return decoded_tx
        except:
            print("error in decoding a transaction with hash: ", tx_hash)
            return None


    # ================================================================================================
    # Given a block id return the hashes of the transactions in that block.
    # ================================================================================================
    def get_block_txs(self, block_id):
        cmd = zcash_cli + ' ' + conf_file + ' getblockhash ' + str(block_id)
        block_hash = os.popen(cmd).read()

        cmd = zcash_cli + ' ' + conf_file + ' getblock ' + block_hash
        block_info = json.loads(os.popen(cmd).read())
        txs_hashes = block_info['tx']  # Get the hash of transactions inside this block
        return txs_hashes

    # ================================================================================================
    # Given a operation id return the txid.
    # ================================================================================================
    def get_txid(self, operation_id):
        cmd = zcash_cli + ' ' + conf_file + ' z_getoperationresult ' +  '\'[\"' + operation_id.strip() + '\"]\''
        txid = json.loads(os.popen(cmd).read()[0])['result']['txid']
        return txid




