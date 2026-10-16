"""Print-oriented typography shared by the report and notebooks."""
INK='#171717'
TEAL='#171717'
COPPER='#626262'
MUTED='#444444'
GRID='#e3e3e3'
FONT='Times New Roman, SimSun, serif'
EXPORT_CSS='''<style>
body{background:white!important;color:#111!important;font-family:"Times New Roman","SimSun",serif!important}
main,main *{box-sizing:border-box}main{max-width:1100px;margin:32px auto 64px;padding:35px 48px!important;background:white}
.jp-Notebook,.jp-Cell{padding:0!important;background:white!important}.jp-Cell{margin-bottom:18px!important}
.jp-InputPrompt,.jp-OutputPrompt{display:none!important}
.jp-InputArea,.jp-OutputArea,.jp-OutputArea-child,.jp-RenderedHTMLCommon{padding-left:0!important;margin-left:0!important}
.jp-RenderedHTMLCommon,.jp-RenderedHTMLCommon *{font-family:"Times New Roman","SimSun",serif}
.jp-RenderedHTMLCommon{font-size:18px!important;line-height:1.85!important;color:#111!important;padding:0!important}
h1{font-size:30px!important;text-align:center;font-weight:normal!important;margin:12px 0 28px!important}
h2{font-size:25px!important;font-weight:normal!important;margin:38px 0 18px!important;padding:0!important;color:black!important}
h3{font-size:21px!important;font-weight:normal!important;margin:28px 0 14px!important;color:black!important}
h4{font-size:19px!important;font-weight:normal!important;margin:22px 0 12px!important;color:black!important}
p{margin:12px 0!important}a{color:#222!important;text-decoration:underline!important}
table{width:100%;border-collapse:collapse!important;font-size:16px!important;margin:20px 0!important;border-top:1.5px solid black!important;border-bottom:1.5px solid black!important}
thead{border-bottom:1px solid black!important}td,th{text-align:center!important;padding:9px 8px!important;background:white!important;border:0!important;color:black!important;font-weight:normal!important}
tbody tr{background:white!important}tbody tr+tr{border-top:1px solid #eee}
.jp-OutputArea-output{max-width:100%;padding:0!important;overflow-x:auto}.jp-RenderedImage img,main img{max-width:100%;display:block;margin:18px auto}
.lab-figure{width:100%;background:white;margin:20px 0 30px;overflow:hidden}
.jp-InputArea,.jp-RenderedHTMLCommon pre,.jp-RenderedHTMLCommon code{font-family:"Times New Roman","SimSun",serif!important}
.jp-OutputArea-output,.jp-OutputArea-child{max-height:none!important}.anchor-link{display:none!important}.static-reference{margin:15px 0;font-family:"Times New Roman","SimSun",serif}.static-reference summary{cursor:pointer;font-size:16px;color:#333;padding:8px 0}
@media(max-width:800px){main{margin:0;padding:24px 20px!important}.jp-RenderedHTMLCommon{font-size:17px!important}h1{font-size:27px!important}table{font-size:14px!important}td,th{padding:8px 5px!important}}
.academic-caption{text-align:center!important;font-size:17px!important;margin:14px 0 22px!important}
@media print{main{margin:0;padding:0!important}.modebar{display:none!important}}
</style>'''
def polish_export(html):
    from bs4 import BeautifulSoup
    soup=BeautifulSoup(html,"html.parser")
    for cell in soup.select(".jp-CodeCell:not(.celltag_report-figure)"):
        for output in list(cell.select(".jp-OutputArea-child")):
            if output.select_one("img"):
                details=soup.new_tag("details",attrs={"class":"static-reference"})
                caption=soup.new_tag("summary");caption.string="静态图（默认参数）"
                details.append(caption);output.replace_with(details);details.append(output)
    import re
    for p in soup.select('p'):
        if re.match(r'^[图表] \d+\s',p.get_text()):p['class']=list(p.get('class',[]))+['academic-caption']
    html=str(soup)
    return html.replace('</head>',EXPORT_CSS+'</head>',1)
