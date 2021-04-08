from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

class ECDH():

    def __init__(self):
        self.curve = ec.SECP256R1()
        self.privKey = ec.generate_private_key(self.curve)
        self.pubKey = self.privKey.public_key()

    def getPrivateKey(self):
        return self.privKey

    def getPublicKey(self):
        return (self.pubKey.public_bytes(encoding=serialization.Encoding.X962, format=serialization.PublicFormat.CompressedPoint)).decode("ISO-8859-1")
