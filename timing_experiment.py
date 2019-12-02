from crypto_tools import Crypto
from bitcoin_encoding import Bitcoin
from ethereum_encoding import Ethereum
from zcash_encoding import Zcash
import json
import time



#--------Helper Objects for crypto and encoding-----------------------
crypto = Crypto()

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
conf_u = json.load(open(user_conf_file))
conf_d = json.load(open(decoder_conf_file))



############################################################################################
#                          TIMING OF CRYPTO FUNCTIONS
############################################################################################

iterations = 100

#---------------KEY GENERATION TIMING---------------------
t_start = time.time()
for i in range(0,iterations):
    sk,vk = crypto.generate_private_public_key() #public and private key of the decoder
t_stop = time.time()
print("Average key generation time in milliseconds: ", (t_stop - t_start)/iterations*1000)


#---------------KEY EXCHANGE TIMING---------------------
t_start = time.time()
for i in range(0,iterations):
    sk = conf_u['SK']
    vk = conf_d['VK']
    k_d = crypto.generate_symmetric_key(vk, sk)
t_stop = time.time()
print("Average key exchange time in milliseconds: ", (t_stop - t_start)/iterations*1000)


#---------------KEY EXCHANGE TIMING---------------------
t_start = time.time()
for i in range(0,iterations):
    k_c, k_r,_  = crypto.generate_subKeys(k_d, conf_u['CHA_LEN'], conf_u['RES_LEN'], conf_u['PAY_LEN'])
t_stop = time.time()
print("Average key derivation time in milliseconds: ", (t_stop - t_start)/iterations*1000)


#---------------ENCRYPTION TIMING---------------------
t_start = time.time()
for i in range(0,iterations):
    cipher = crypto.encrypt(response_message, k_r)
t_stop = time.time()
print("Average encryption time in milliseconds: ", (t_stop - t_start)/iterations*1000)

#---------------DECRYPTION TIMING---------------------
t_start = time.time()
for i in range(0,iterations):
    message = crypto.decrypt(cipher, k_r)
t_stop = time.time()
print("Average decryption time in milliseconds: ", (t_stop - t_start)/iterations*1000)


