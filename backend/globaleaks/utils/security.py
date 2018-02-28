# -*- coding: utf-8 -*-
import base64
import binascii
import json
import os
import random
import scrypt
import string
import time
from datetime import datetime

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import constant_time, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from globaleaks.rest import errors
from globaleaks.settings import Settings
from globaleaks.utils.utility import log

crypto_backend = default_backend()


def sha256(data):
    h = hashes.Hash(hashes.SHA256(), backend=crypto_backend)
    h.update(data)
    return binascii.b2a_hex(h.finalize())


def sha512(data):
    h = hashes.Hash(hashes.SHA512(), backend=crypto_backend)
    h.update(data)
    return binascii.b2a_hex(h.finalize())


def generateRandomReceipt():
    """
    Return a random receipt of 16 digits
    """
    return ''.join(random.SystemRandom().choice(string.digits) for _ in range(16)).encode('utf-8')


def generateRandomKey(N):
    """
    Return a random key of N characters in a-zA-Z0-9
    """
    return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(N)).encode('utf-8')


def generateRandomSalt():
    """
    Return a base64 encoded string with 128 bit of entropy
    """
    return base64.b64encode(os.urandom(16))


def generate_api_token():
    """
    creates an api token along with its corresponding hash digest.

    :rtype: A `tuple` containing (digest `str`, token `str`)
    """
    token = generateRandomKey(Settings.api_token_len)
    return token, sha512(token)


def _overwrite(absolutefpath, pattern):
    count = 0
    length = len(pattern)

    with open(absolutefpath, 'w+') as f:
        f.seek(0)
        while count < length:
            f.write(pattern)
            count += len(pattern)


def overwrite_and_remove(absolutefpath, iterations_number=1):
    """
    Overwrite the file with all_zeros, all_ones, random patterns

    Note: At each iteration the original size of the file is altered.
    """
    log.debug("Starting secure deletion of file %s", absolutefpath)

    randomgen = random.SystemRandom()

    try:
        # in the following loop, the file is open and closed on purpose, to trigger flush operations
        all_zeros = "\0\0\0\0" * 1024               # 4kb of zeros
        all_ones = "FFFFFFFF".decode("hex") * 1024  # 4kb of ones

        for iteration in range(iterations_number):
            OPTIMIZATION_RANDOM_BLOCK = randomgen.randint(4096, 4096 * 2)

            random_pattern = ""
            for _ in range(OPTIMIZATION_RANDOM_BLOCK):
                random_pattern += str(randomgen.randrange(256))

            log.debug("Excecuting rewrite iteration (%d out of %d)",
                      iteration, iterations_number)

            _overwrite(absolutefpath, all_zeros)
            _overwrite(absolutefpath, all_ones)
            _overwrite(absolutefpath, random_pattern)

    except Exception as excep:
        log.err("Unable to perform secure overwrite for file %s: %s",
                absolutefpath, excep)

    finally:
        try:
            os.remove(absolutefpath)
        except OSError as excep:
            log.err("Unable to perform unlink operation on file %s: %s",
                    absolutefpath, excep)

    log.debug("Performed deletion of file: %s", absolutefpath)


def directory_traversal_check(trusted_absolute_prefix, untrusted_path):
    """
    check that an 'untrusted_path' matches a 'trusted_absolute_path' prefix
    """
    if not os.path.isabs(trusted_absolute_prefix):
        raise Exception("programming error: trusted_absolute_prefix is not an absolute path: %s" %
                        trusted_absolute_prefix)

    untrusted_path = os.path.abspath(untrusted_path)

    if trusted_absolute_prefix != os.path.commonprefix([trusted_absolute_prefix, untrusted_path]):
        log.err("Blocked file operation for: (prefix, attempted_path) : ('%s', '%s')",
                trusted_absolute_prefix, untrusted_path)

        raise errors.DirectoryTraversalError


def hash_password(password, salt):
    """
    @param password: a unicode or utf-8 string
    @param salt: a password salt

    @return:
        the salted scrypt hash of the provided password
    """
    password = password.encode('utf-8')
    salt = salt.encode('utf-8')
    return scrypt.hash(password, salt).encode('hex')


def check_password(guessed_password, salt, password_hash):
    return constant_time.bytes_eq(hash_password(guessed_password, salt), bytes(password_hash))


def change_password(old_password_hash, old_password, new_password, salt):
    """
    @param old_password_hash: the stored password hash.
    @param old_password: The user provided old password for password change protection.
    @param new_password: The user provided new password.
    @param salt: The salt to be used for password hashing.

    @return:
        the scrypt hash in base64 of the new password
    """
    if not check_password(old_password, salt, old_password_hash):
        log.debug("change_password(): Error - provided invalid old_password")
        raise errors.InvalidOldPassword

    return hash_password(new_password, salt)
