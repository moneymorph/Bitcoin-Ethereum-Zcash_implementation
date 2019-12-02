import binascii as bina
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from keys.generator import KeyGenerator
from ecdsa import SigningKey, VerifyingKey, SECP256k1, ellipticcurve, numbertheory

# ECDSA curve using secp256k1 is defined by: y**2 = x**3 + 7
# This is done modulo p which (secp256k1) is:
# p is the finite field prime number and is equal to:
# 2^256 - 2^32 - 2^9 - 2^8 - 2^7 - 2^6 - 2^4 - 1
# Note that we could alse get that from ecdsa lib from the curve, e.g.:
# SECP256k1.__dict__['curve'].__dict__['_CurveFp__p']
_p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
# Curve's a and b are (y**2 = x**3 + a*x + b)
_a = 0x0000000000000000000000000000000000000000000000000000000000000000
_b = 0x0000000000000000000000000000000000000000000000000000000000000007
# Curve's generator point is:
_Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
_Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
# prime number of points in the group (the order)
_order = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# The ECDSA curve (secp256k1) is:
# Note that we could get that from ecdsa lib, e.g.:
# SECP256k1.__dict__['curve']
_curve = ellipticcurve.CurveFp( _p, _a, _b )

# The generator base point is:
# Note that we could get that from ecdsa lib, e.g.:
# SECP256k1.__dict__['generator']
_G = ellipticcurve.Point( _curve, _Gx, _Gy, _order )



class Crypto:
    def __init__(self):
        #self.curve = curve
        self.kg = KeyGenerator()

    # -----------------------------------------------------------------------------------------
    # xor function
    @staticmethod
    def xor(xs, ys): #takes in two byte arrays and xors them and returns a byte array
        return bytes(a ^ b for (a, b) in zip(xs, ys))


    # -----------------------------------------------------------------------------------------
    # encrypt message
    @staticmethod
    def encrypt(message, k): #message is str and k is bytes string
        cipher = Crypto.xor(k, message.encode())
        cipher = bina.hexlify(cipher).decode() # string representation of the cipher
        # print("\nMessage: ", bina.hexlify(message.encode()).decode())
        # print("Encryption Key:", bina.hexlify(k).decode())
        # print("Covertext: ", cipher)
        return cipher


    # -----------------------------------------------------------------------------------------
    # decrypt message
    @staticmethod
    def decrypt(cipher, k): #cipher is a hex string and k is byte string
        # k_hex = bina.hexlify(k)  # convert key to hex
        # cipher_hex = bina.hexlify(cipher)  # convert cipher to hex
        message = Crypto.xor(k, bina.unhexlify(cipher)) # the xor takes inputs as bytes
        message = message.decode()   # string representation
        return message


    # -----------------------------------------------------------------------------------------
    # generate private and public key
    def generate_private_public_key(self):
        sk = self.kg.generate_key()
        vk = self.get_public_key(sk)
        return sk,vk


    # -----------------------------------------------------------------------------------------
    # generate pulic key from private key
    def get_public_key(self, sk):
        vk = self.kg.private_to_public(sk)
        return vk


    # -----------------------------------------------------------------------------------------
    # generate symmetric key between the decoder and user using static Diffie-Hellman
    @staticmethod
    def generate_symmetric_key(vk_hex, sk):
        sk = int(sk, 16)
        vk_point = ellipticcurve.Point(_curve, int(vk_hex[:64], 16), int(vk_hex[64:], 16), _order)
        shared_key = vk_point * sk
        return shared_key


    # -----------------------------------------------------------------------------------------
    # key derivation function
    @staticmethod
    def generate_subKeys(masterkey, challenge_len, response_len, paykey_len): # masterkey is a curve point
        key_len = challenge_len + response_len + paykey_len
        symetric_key = HKDF(algorithm=hashes.SHA256(), length=key_len, salt=None, info=b'handshake data',
                        backend=default_backend()).derive(masterkey.__str__().encode())
        return symetric_key[0:challenge_len], \
               symetric_key[challenge_len:challenge_len+response_len], \
               symetric_key[challenge_len+response_len:]
        # the returned keys are in byte strings




if __name__ == '__main__':

    kg = KeyGenerator()
    sk_hex = kg.generate_key()
    vk = kg.private_to_public(sk_hex)

    c = Crypto()
    sk, vk = c.generate_private_public_key()
    shared_key = c.generate_symmetric_key(vk, sk)

    print(shared_key)
    print(c.generate_subKeys(shared_key, 10,10,10))


