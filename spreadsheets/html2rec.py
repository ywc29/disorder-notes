#!/usr/bin/env python2
import re, os, sys, HTMLParser
headings = None
rows = [] ; curRow = [] ; curCell = [] ; colspan = 0
print "# -*- mode: rec -*-\n"
def flushRows():
    global rows
    if not rows: return
    i = 1
    heads = headings[:]
    while i < len(heads):
        while i < len(heads) and not heads[i]:
            heads = heads[:i]+heads[i+1:]
            rows = map(lambda r:r[:i-1]+[" ".join(r[i-1:i+1])]+r[i+1:],rows)
        i += 1
    for h,v in zip(heads,zip(*rows)):
        v = " ".join(v).strip()
        if h and v: print h+": "+v
    print
    rows = []
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
                headings = map(lambda x:re.sub("<[^>]*>","",x).replace(" ","-"),curRow)
                print "%allowed: "+" ".join(h for h in headings if h)+"\n"
            else:
                if curRow[0]: flushRows()
                rows.append(curRow)
            curRow = []
        elif colspan: curCell.append("</"+tag+">")
    def handle_data(self,data):
        data = data.strip()
        if data and colspan: curCell.append(data)

parser = Parser()
parser.feed(sys.stdin.read()) ; parser.close()
flushRows()
