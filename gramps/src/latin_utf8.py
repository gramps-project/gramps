
import cStringIO

try:
    from xml.unicode.utf8_iso import code_to_utf8
    from xml.unicode.iso8859 import UTF8String

    def utf8_to_latin(s):
        y = UTF8String(s)
        return y.encode("iso-8859-1")

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

except:
    
    def utf8_to_latin(s):
        return s

    def latin_to_utf8(s):
        return s

        
