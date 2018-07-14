def generate_spam_flag():
    import base64, hashlib, os, re
    encode = lambda s: re.sub(r'[a-z/+=\n]', r'', base64.encodebytes(s).decode()).upper()
    secret = '1234'

    prefix = encode(os.urandom(64))[:16]
    suffix = encode(hashlib.sha256((prefix + secret).encode()).digest())[:15]
    return prefix + suffix + '='


def is_spam_flag(flag):
    import base64, hashlib, re
    encode = lambda s: re.sub(r'[a-z/+=\n]', r'', base64.encodebytes(s).decode()).upper()
    secret = '1234'

    prefix = flag[:16].upper()
    suffix = encode(hashlib.sha256((prefix + secret).encode()).digest())[:15]
    return flag[16:].upper() == suffix + '='


def test():
    import base64, hashlib, os, re
    encode = lambda s: re.sub(r'[a-z/+=\n]', r'', base64.encodebytes(s).decode()).upper()
    for i in range(10**4):
        flag = encode(os.urandom(128))[:31] + '='
        if i < 30:
            print(flag)
        assert not is_spam_flag(flag)

    for i in range(10**3):
        assert is_spam_flag(generate_spam_flag())

    print('Ok')


if __name__ == '__main__':
    test()
