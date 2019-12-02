from crypto_tools import Crypto
from bitcoin_encoding import Bitcoin
from ethereum_encoding import Ethereum
from zcash_encoding import Zcash
import json


#--------Helper Objects for crypto and encoding-----------------------
crypto = Crypto()
txencoder = Bitcoin()
#txencoder = Zcash()
#txencoder = Ethereum('REPLACE WITH PATH TO IPC')

#--------Tag, challenge and response messages-------------------------
tag = '00000000'
challenge_message = 'tor----obfs3'
response_message = '111.111.111.111:2222KEYKEYKEYKEYKEYKEYKE'  # bitcoin response
#response_message = '111.222.333.444:5555'  # ethereum response

#--------Key lengths--------------------------------------------------
challenge_len = len(tag+challenge_message)
response_len = len(response_message)
paymentkey_len = 32

#--------Config file paths for user and decoder-----------------------
decoder_conf_file = 'config_files/decoder_config'
user_conf_file = 'config_files/user_config'




#====================================================================================================
# Stego-Bootstrapping Setup
# setup the generator and generate public and public key of decoder and write the necessary
# info to the config for both the user and decoder.
#====================================================================================================
def sb_set(decoder_conf_file, user_conf_file):

    sk_d,vk_d = crypto.generate_private_public_key() #public and private key of the decoder

    # write initialization info to decoder config file
    dec_config_file = open(decoder_conf_file,'w')
    st = {'SK': sk_d, 'VK':vk_d,  # private and public keys of the decoder
          'TAG': tag, 'CHA_LEN': challenge_len, 'RES_LEN': response_len, 'PAY_LEN': paymentkey_len}
    dec_config_file.write(json.dumps(st))
    dec_config_file.close()

    # write initialization and decoder public info to user config file
    sk_u,vk_u = crypto.generate_private_public_key()  # public and private key of the user
    usr_config_file = open(user_conf_file, 'w')
    st = {'VK_D': vk_d, # public key of decoder
          'SK': sk_u, 'VK': vk_u,  # public and private key of decoder
          'TAG': tag, 'CHA_LEN': challenge_len, 'RES_LEN': response_len, 'PAY_LEN': paymentkey_len}
    usr_config_file.write(json.dumps(st))
    usr_config_file.close()




#====================================================================================================
# Stego-Bootstrapping Encoding Forward
# This function is performed by the user to generate a challenge covertext.
# takes as input the public key of the decoder, challenge message and the tag as inputs.
#====================================================================================================
def sb_encf(user_conf_file_path, cm, tag):
    user_conf_file = open(user_conf_file_path) # the public data is stored in a config file named 'user_config'
    conf = json.load(user_conf_file)  # load the conf file into a json

    #vk_u,sk_u = crypto.generate_private_public_key() #public and private key of the user
    vk_u = conf['VK']  # public key of the user
    sk_u = conf['SK']  # private key of the user
    vk_d = conf['VK_D'] #load the public key of the decoder from the config file
    k_d = crypto.generate_symmetric_key(vk_d, sk_u) # generate a symmetric key using diffie-hellman key exchange
    k_c,k_r,sk_s = crypto.generate_subKeys(k_d, conf['CHA_LEN'], conf['RES_LEN'], conf['PAY_LEN']) # create sub keys from master key for encrypting and paying key

    ct_c = crypto.encrypt(tag+cm, k_c) # encrypt the challenge message cm where the tag is added to its beginning.
    vk_p = crypto.get_public_key(sk_s.hex())

    txid = txencoder.tx_encf(vk_p, ct_c, user_conf_file_path) # encode the challenge data into a transaction and send it
    print("challenge transaction sent to the blockchain: ", txid)
    return txid, k_d


#====================================================================================================
# Stego-Bootstrapping Decoding Forward
# This function is performed by the decoder to extract the challenge message and the symmetric key.
# takes as input the private key of the decoder and the block id to check for challenge messages.
#====================================================================================================
def sb_decf(decoder_conf_file_path, block_id):
    conf_file = open(decoder_conf_file_path)  # the public data is stored in a config file named 'decoder_config'
    conf = json.load(conf_file)  # load the conf file into a json
    sk_d = conf['SK']   #private key of the decoder
    txs = txencoder.get_block_txs(block_id)  # get all the transactions of the block
    for tx in txs:
        vk_u, ct_c = txencoder.tx_decf(tx)   # retrieve the public key of the user and the challenge covertext
        if vk_u == -1:
            continue

        try:
            k_d = crypto.generate_symmetric_key(vk_u, sk_d) # generate a symmetric key using diffie-hellman key exchange
            k_c, k_r, sk_s = crypto.generate_subKeys(k_d, conf['CHA_LEN'], conf['RES_LEN'], conf['PAY_LEN'])  # create sub keys from master key for encrypting and paying key
            cm = crypto.decrypt(ct_c, k_c)  # decrypt the challenge ciphertext
            if cm[:len(tag)] == conf['TAG']:   # check to see if the message has the tag
                print("challenge message: ", cm[len(tag):])
                return cm[len(tag):], k_d, tx
        except:
            continue
    return None


#====================================================================================================
# Stego-Bootstrapping Encoding Backward
# This function is performed by the decoder to generate a response covertext.
# takes as input the public data of the decoder, response message and the shared key.
#====================================================================================================
def sb_encb(decoder_conf_file_path, rm, k_d, txid=None):
    conf_file = open(decoder_conf_file_path)  # the public data is stored in a config file named 'decoder_config'
    conf = json.load(conf_file)  # load the conf file into a json

    k_c, k_r, sk_s = crypto.generate_subKeys(k_d, conf['CHA_LEN'], conf['RES_LEN'], conf['PAY_LEN'])  # create sub keys from master key for encrypting and paying key
    ct_r = crypto.encrypt(rm, k_r)  # encrypt the response message cr

    txhash = txencoder.tx_encb(sk_s.hex(), ct_r, txid=txid)  # encode the challenge data into a transaction and send it
    print("response transaction sent to the blockchain: ", txhash)
    return txhash


#====================================================================================================
# Stego-Bootstrapping Decoding Backward
# This function is performed by the user to extract the response message.
# takes as input the config file of user, shared key and the block number to look for the response message.
#====================================================================================================
def sb_decb(user_conf_file_path, k_d, block_id):
    conf_file = open(user_conf_file_path)
    conf = json.load(conf_file)  # load the conf file into a json

    k_c, k_r, sk_s = crypto.generate_subKeys(k_d, conf['CHA_LEN'], conf['RES_LEN'], conf['PAY_LEN'])  # create sub keys from master key for encrypting and paying key
    vk_p = crypto.get_public_key(sk_s.hex())

    ct_r = txencoder.tx_decb(block_id, vk_p)  # get the response ciphertext from the tx of vk_p in the block
    rm = crypto.decrypt(ct_r, k_r)  # decrypt the response ciphertext
    print("response message: ", rm)




# =======================================================
# MAIN
# =======================================================
if __name__ == "__main__":

    #--------------Setup----------------------------------------
    sb_set(decoder_conf_file, user_conf_file) #setup the protocol and write the public information into the config files.
    print("setup done")
    print("\n-----------------------------\n")

    #--------------USER: Encoding Forward Direction-------------
    tx_hash_challenge, k_d_usr = sb_encf(user_conf_file, challenge_message, tag)
    print("\n-----------------------------\n")


    #--------------DECODER: Decoding Forward Direction----------
    block_id = int(input("which block is the challenge encoding in? "))
    cm, k_d_dec, txid  = sb_decf(decoder_conf_file, block_id)
    print("\n-----------------------------\n")


    #--------------DECODER: Encoding Backward Direction---------
    tx_hash_reponse = sb_encb(decoder_conf_file, response_message, k_d_dec, txid)
    print("\n-----------------------------\n")


    #--------------USER: Decoding Backward Direction------------
    block_id = int(input("which block is the response encoding in? "))
    rm = sb_decb(user_conf_file, k_d_usr, block_id)



