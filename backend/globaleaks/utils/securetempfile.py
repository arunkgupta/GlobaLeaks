# -*- coding: utf-8 -*-
import os
import tempfile
import time

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from globaleaks.rest import errors
from globaleaks.utils.security import crypto_backend, generateRandomKey


class SecureTemporaryFile(object):
    file = None

    def __init__(self, filesdir):
        """
        Create the AES Key to encrypt the uploaded file and initialize the cipher
        """
        self.key = os.urandom(32)
        self.key_id = generateRandomKey(16)
        self.key_counter_nonce = os.urandom(16)
        self.cipher = Cipher(algorithms.AES(self.key), modes.CTR(self.key_counter_nonce), backend=crypto_backend)
        self.filepath = os.path.join(filesdir, "%s.aes" % self.key_id)

    def open(self, mode):
        if self.file is None:
           if mode == 'w':
               self.file = open(self.filepath, 'a+')
               self.encdec = self.cipher.encryptor()
           else:
               self.file = open(self.filepath, 'r')
               self.encdec = self.cipher.decryptor()

        return self

    def write(self, data):
        if isinstance(data, unicode):
            data = data.encode('utf-8')

        self.file.write(self.encdec.update(data))

    def finalize_write(self):
        self.file.write(self.encdec.finalize())

    def read(self, c=None):
        if c is None:
            data = self.file.read()
        else:
            data = self.file.read(c)

        if data:
            return self.encdec.update(data)

        return self.encdec.finalize()

    def close(self):
        self.file.close()
        self.file = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        try:
            os.remove(self.filepath)
        except:
            pass
