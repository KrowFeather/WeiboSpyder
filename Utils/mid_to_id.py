def mid_to_id(murl=None):
    ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    DICT = {}

    def get_dict():
        for index in range(len(ALPHABET)):
            DICT[ALPHABET[index]] = index

    # 62 to 10
    def key62_to_key10(str_62):
        value = 0
        for s in str_62:
            value = value * 62 + DICT[s]
        return value

    get_dict()
    length = len(murl)
    mid = ''
    group = int(length / 4)
    last_count = length % 4

    for loop in range(group):
        value = key62_to_key10(murl[length - (loop + 1) * 4:length - loop * 4])
        mid = str(value) + mid
    if last_count:
        value = key62_to_key10(murl[:length - group * 4])
        mid = str(value) + mid
    return mid


