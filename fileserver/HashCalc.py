from enum import Enum
import hashlib

class HashSumType(Enum):
	no_hash = 0
	md5 = 1
	sha1 = 2
	ripemd160 = 3
	sha224 = 4
	sha256 = 5
	sha384 = 6
	sha512 = 7
	whirlpool = 8

def hashsum(hash_sum_type, message):
	if (hash_sum_type.name in hashlib.algorithms_available):
		h = hashlib.new(hash_sum_type.name)
		h.update(str.encode(message))
		return h.hexdigest()
	elif (hash_sum_type == HashSumType.no_hash):
		return "0"
	else:
		raise Exception("Can not get hash algorithm")

def hashsumOfPassword(hash_sum_type, salt, password):
	saltBytes = salt.encode('raw_unicode_escape')
	passwordBytes = password.encode('raw_unicode_escape')
	return hashlib.pbkdf2_hmac(
		hash_sum_type.name, saltBytes, passwordBytes, 100000).hex()

def hashsum_of_file(hash_sum_type, f):
	if (hash_sum_type.name in hashlib.algorithms_available):
		h = hashlib.new(hash_sum_type.name)
		h.update(f.read())
		return h.hexdigest()
	elif (hash_sum_type == HashSumType.no_hash):
		return "0"
	else:
		raise Exception("Can not get hash algorithm")

def hashsum_of_data(hash_sum_type, data):
	if (hash_sum_type.name in hashlib.algorithms_available):
		h = hashlib.new(hash_sum_type.name)
		h.update(data)
		return h.hexdigest()
	elif (hash_sum_type == HashSumType.no_hash):
		return "0"
	else:
		raise Exception("Can not get hash algorithm")

def get_salted_password(salt, password):
    return hashsumOfPassword(HashSumType.sha512, salt, password)