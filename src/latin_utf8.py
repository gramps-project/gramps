

from xml.unicode.utf8_iso import utf8_to_code, code_to_utf8

import cStringIO

def utf8_to_latin(s):
    buff = cStringIO.StringIO()
    while s:
        try:
            head,s = utf8_to_code(1,s)
        except Exception,e:
            from traceback import print_exc
            print_exc()
            head = ''
            s = s[1:0]
        buff.write(head)
    ans = buff.getvalue()
    buff.close()
    return ans

def latin_to_utf8(s):
    buff = cStringIO.StringIO()
    for c in s:
        try:
            cv = code_to_utf8(1,c)
        except Exception,e:
            from traceback import print_exc
            print_exc()
            cv = ''
        buff.write(cv)
    ans = buff.getvalue()
    buff.close()
    return ans
