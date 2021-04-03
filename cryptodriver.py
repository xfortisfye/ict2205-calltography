from Crypto.Signature import pss
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto import Random
import hashlib
import hmac
from math import ceil
import json
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import json
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad



import pyDHE


#temp
# def get_rsa_keypair():
#     key = RSA.generate(2048)
#     private_key = key.export_key()
#     public_key = key.public_key().export_key()
#     file_out = open("server_rsa_private_key.pem", "wb")
#     file_out.write(private_key)
#     file_out.close()
#     file_out = open("pub_key.pem", "wb")
#     file_out.write(public_key)
#     file_out.close()
#     return [private_key, public_key]


def hmac_sha256(key, data):
    return hmac.new(key, data, hashlib.sha256).digest()

def hkdf(length: int, ikm, salt: bytes = b"", info: bytes = b"") -> bytes:
    """Key derivation function"""
    hash_len = 32

    if len(salt) == 0:
        salt = bytes([0] * hash_len)
    prk = hmac_sha256(salt, ikm)
    t = b""
    okm = b""
    for i in range(ceil(length / hash_len)):
        t = hmac_sha256(prk, t + info + bytes([1 + i]))
        okm += t


    return okm[:length]


def encrypt_rsa_aes(recipient_key, data):
    output = ""
    data = data.encode("utf-8")
    session_key = get_random_bytes(16)
    # Encrypt the session key with the public RSA key
    recipient_key = RSA.import_key(recipient_key)
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Encrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data)
    for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext):
        output = output + x.decode("ISO-8859-1") + "{\n}"
    #print("\n")
    #print(output)
    return output

def decrypt_rsa_aes(own_private_key, encrypted_data):
    data = encrypted_data.split("{\n}")
    own_private_key = RSA.import_key(own_private_key)


    enc_session_key= data[0].encode("ISO-8859-1")
    nonce=data[1].encode("ISO-8859-1")
    tag=data[2].encode("ISO-8859-1")
    ciphertext=data[3].encode("ISO-8859-1")
    #for x in (own_private_key.size_in_bytes(), 16, 16, -1):




    # Decrypt the session key with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(own_private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    output = cipher_aes.decrypt_and_verify(ciphertext, tag)
    #print(output.decode("utf-8"))
    return output


def get_rsa_keypair():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.public_key().export_key()
    return [private_key, public_key]


#https://pycryptodome.readthedocs.io/en/latest/src/signature/pkcs1_pss.html
##PKCS#1 PSS (RSA)
# def make_rsa_sig():
#     message = "To be signed"
#     key = RSA.import_key(open('server_rsa_private_key.pem').read())
#     h = SHA256.new(message.encode())
#     signature = pss.new(key).sign(h)
#     return signature

def make_rsa_sig(private_key, message):
    key = RSA.import_key(private_key)
    h = SHA256.new(message.encode())
    signature = pss.new(key).sign(h)
    return signature


#https://pycryptodome.readthedocs.io/en/latest/src/signature/pkcs1_pss.html
##PKCS#1 PSS (RSA)
def verify_rsa_sig(public_key, message, signature):
    key = RSA.import_key(public_key)
    h = SHA256.new(message.encode())
    verifier = pss.new(key)
    try:
        verifier.verify(h, signature)
        print("The signature is authentic.")
        return True
    except (ValueError, TypeError):
        print("The signature is not authentic.")
        return False


def make_dhe_key_obj():
    key_obj = pyDHE.new()
    return key_obj

def make_dhe_keypair(key_obj):
    own_public_key = key_obj.getPublicKey()
    return str(own_public_key)

def make_dhe_sharedkey(key_obj, recepient_public_key):

    shared_key = key_obj.update(int(recepient_public_key))
    return str(shared_key)


def encrypt_aes_gcm(key, data):


    header = b"header"
    cipher = AES.new(key, AES.MODE_GCM)
    cipher.update(header)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode())

    json_k = ['nonce', 'header', 'ciphertext', 'tag']
    json_v = [b64encode(x).decode('utf-8') for x in (cipher.nonce, header, ciphertext, tag)]
    result = json.dumps(dict(zip(json_k, json_v)))
    return result

def decrypt_aes_gcm(key, data):
    try:
        b64 = json.loads(data)
        json_k = ['nonce', 'header', 'ciphertext', 'tag']
        jv = {k:b64decode(b64[k]) for k in json_k}

        cipher = AES.new(key, AES.MODE_GCM, nonce=jv['nonce'])
        cipher.update(jv['header'])
        plaintext = cipher.decrypt_and_verify(jv['ciphertext'], jv['tag'])
        print("The message was: " + plaintext.decode())
    except (ValueError, KeyError):
        print("Incorrect decryption")





# keypair1 = get_rsa_keypair()
# recipient_key = keypair1[1]
# own_private_key = keypair1[0]
#
#
#
#
#
# print("encrypting with this key: " + str(recipient_key))
#
#
# encrypted_data = encrypt_rsa_aes(recipient_key)
#
#
# print("\ndecrypting with this key: " + str(own_private_key))
#
# decrypt_rsa_aes(own_private_key, encrypted_data)


