def auto_decode(data:bytes,codec=('utf-8','gbk','gb2312')):
    '''自动尝试多种编码decode'''
    for code in codec:
        try:
            return data.decode(code)
        except Exception as ex:
            pass
    raise UnicodeDecodeError('decode fail')