import cologne_phonetics


def phonetic(s, encode=True):
    codes = [code for __, code in cologne_phonetics.encode(s)]
    if encode:
        return ':' + ':'.join(codes) + ':'
    else:
        return codes
