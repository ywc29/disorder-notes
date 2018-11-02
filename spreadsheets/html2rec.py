#!/usr/bin/env python2

def main():
    parser = Parser()
    parser.feed(sys.stdin.read()) ; parser.close()
    flushRows() ; sys.stderr.write("\n")

import re, os, sys, HTMLParser, htmlentitydefs
headings = heads = None
rows = [] ; curRow = [] ; curCell = [] ; colspan = 0
print "# -*- mode: rec -*-\n"
def flushRows():
    global rows
    if not rows: return
    if heads==None: firstFlush()
    for i in colsFold: rows = map(lambda r:r[:i-1]+[" ".join(r[i-1:i+1])]+r[i+1:],rows)
    if "." in sys.argv[1]:
        rt,rs = sys.argv[1].split(".",1)
        print "Record_Type:",rt
        print "Record_SubType:",rs
    else: print "Record_Type:",sys.argv[1]
    for h,v in zip(heads,zip(*rows)):
        v = " ".join(v).strip() # TODO: try "\n+ ".join ?
        if h and v:
            v2 = re.sub("<[^>]*>","",v)
            print h+": "+v2
            if not v==v2:
                for note in re.findall("<[^/][^>]*>([^<][^<]*)</[^>]*>",v):
                    note = note.strip()
                    if note: print "# NOTE:",note
    print
    rows = []
    sys.stderr.write(".")
def firstFlush():
    global heads,colsFold ; colsFold = []
    heads = headings[:]
    i = 1
    while i < len(heads):
        while i < len(heads) and not heads[i]:
            heads = heads[:i]+heads[i+1:]
            colsFold.append(i)
        i += 1
class Parser(HTMLParser.HTMLParser):
    def handle_starttag(self, tag, attrs):
        global colspan, endNeed
        if tag=="td":
            attrsD = dict(attrs)
            if "colspan" in attrsD:
                colspan = int(attrsD["colspan"])
            else: colspan = 1
            style = re.sub(" *font-size:[0-9]*pt; *","",attrsD.get("style","").strip())
            if style:
                curCell.append('<span style="'+style+'">')
                endNeed = '</span>'
            else: endNeed = ""
        elif colspan: curCell.append("<"+tag+"".join(" "+a+'="'+v+'"' for a,v in attrs)+">")
    def handle_endtag(self, tag):
        global curRow, curCell, colspan, headings
        if tag=="td":
            curCell.append(endNeed)
            if endNeed and len(curCell)==2:
                curCell=[] # <span...></span>
            curRow.append("".join(curCell).replace("<b></b>",""))
            curCell = []
            curRow += [""]*(colspan-1)
            colspan = 0
        elif tag=="tr":
            if not headings:
                curRow = map(lambda x:re.sub("<[^>]*>","",x).replace("-","_").replace(" ","_"),curRow)
                while curRow and not curRow[-1]:
                    curRow=curRow[:-1]
                if len(curRow)==1: sys.argv[1] += "\nRecordType_Descr: "+curRow[0]
                elif curRow:
                    headings = curRow
                    if headings[0]=="1": headings[0] = ""
                    print "%allowed: Record_Type Record_SubType RecordType_Descr "+" ".join(h for h in headings if h)+"\n"
            else:
                if curRow[0]: flushRows()
                rows.append(curRow)
            curRow = []
        elif colspan: curCell.append("</"+tag+">")
    def handle_data(self,data):
        data = data.strip()
        if data and colspan: curCell.append(data)
    def handle_entityref(self,name):
        if name in htmlentitydefs.name2codepoint and not name in ['lt','gt','amp']: self.handle_data(unichr(htmlentitydefs.name2codepoint[name]).encode('utf-8'))
    def handle_charref(self,name):
        if name.startswith('x'): d=unichr(int(name[1:],16))
        else: d=unichr(int(name))
        if d in u'<>&': pass # leave entity ref as-is
        else: self.handle_data(d.encode('utf-8'))
if __name__=="__main__": main()
