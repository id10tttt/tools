# -*- coding: utf-8 -*-
from OpenSSL import crypto
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as Sign_PKCS1_v1_5
from Crypto.Hash import SHA
import base64
import json

# 杉德公钥证书路径
PUB_CER_PATH = ''

# 商户私钥路径
PRI_PFX_PATH = ''

# 证书密钥
CERT_PWD = ''


def get_public_cer_path():
    return PUB_CER_PATH


def get_private_pfx_path():
    return PRI_PFX_PATH


def get_sandpay_cert_password():
    return CERT_PWD


def get_public_key(cer_file_path):
    """
    从cer证书中提取公钥
    :param cer_file_path: cer证书存放的路径
    :return: 公钥
    """
    cert = crypto.load_certificate(crypto.FILETYPE_ASN1, open(cer_file_path, "rb").read())
    res = crypto.dump_publickey(crypto.FILETYPE_PEM, cert.get_pubkey()).decode("utf-8")
    return res.strip()


def get_private_key(pfx_file_path, password=None):
    """
    从pfx证书中提取私钥,如果证书已加密，需要输入密码
    :param pfx_file_path:pfx证书存放的路径
    :param password:证书密码
    :return:私钥
    """
    pfx = crypto.load_pkcs12(open(pfx_file_path, 'rb').read(), password)
    res = crypto.dump_privatekey(crypto.FILETYPE_PEM, pfx.get_privatekey()).decode("utf-8")
    return res.strip()


def sandpay_sign_message(message):
    """
    私钥签名
    :param message:
    :return:
    """
    private_key_path = get_private_pfx_path()
    sand_cer_password = get_sandpay_cert_password()
    private_key = get_private_key(private_key_path, password=sand_cer_password)
    return _sandpay_sign_message(private_key, message)


def _sandpay_sign_message(private_key, message):
    """
    签名 - 私钥签名
    :param private_key:
    :param message:
    :return:
    """
    public_key = RSA.importKey(private_key)
    signer = Sign_PKCS1_v1_5.new(public_key)
    sha_message = SHA.new(message.encode())
    sign_message = signer.sign(sha_message)
    sign_message = base64.b64encode(sign_message)
    return sign_message.decode()


def verify_sign_message(message, sign_message):
    public_key_path = get_public_cer_path()
    public_key = get_public_key(public_key_path)
    return _verify_sign_message(message, public_key, sign_message)


def _verify_sign_message(message, public_key, sign_message):
    """
    验证签名 - 公钥验签
    :param message:
    :param public_key:
    :param sign_message:
    :return:
    """
    sign_message = base64.b64decode(sign_message)
    public_key = RSA.importKey(public_key)
    verifier = Sign_PKCS1_v1_5.new(public_key)
    sha_message = SHA.new(message.encode())
    result = verifier.verify(sha_message, sign_message)
    return result
