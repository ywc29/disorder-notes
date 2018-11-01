import re
from HTMLParser import HTMLParser,HTMLParseError
headings = None
rows = [] ; curRow = [] ; curCell = [] ; colspan = 0
def flushRows():
    global rows
    if not rows: return
    lastH = None
    for h,v in zip(headings,zip(*rows)):
        v = " ".join(v).strip()
        if not h:
            if not lastH or not v: continue
            h = lastH
        print h+": "+v
        lastH = h
    print
    rows = []
class Parser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        global colspan, endNeed
        if tag=="td":
            attrsD = dict(attrs)
            if "colspan" in attrsD:
                colspan = int(attrsD["colspan"])
            else: colspan = 1
            style = re.sub("font-size:[0-9]*pt; *","",attrsD.get("style","").strip())
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
            if not headings: headings = map(lambda x:re.sub("<[^>]*>","",x),curRow)
            else:
                if curRow[0]: flushRows()
                rows.append(curRow)
            curRow = []
        elif colspan: curCell.append("</"+tag+">")
    def handle_data(self,data):
        data = data.strip()
        if data and colspan: curCell.append(data)
parser = Parser()
parser.feed(open("Condition-freq.Sheet1.html").read()) ; parser.close()
flushRows()
