"""Build the three local PBIR dashboard pages. Close Desktop before running."""
from pathlib import Path
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'power_bi/Mortgage_Lending_Intelligence.Report/definition'
PAGES = REPORT / 'pages'
NAVY, TEAL, INK, MUTED, LIGHT = '#17365D', '#087F8C', '#243746', '#536779', '#F3F6FA'

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

def lit(value):
    if isinstance(value, bool): value = str(value).lower()
    elif isinstance(value, (int, float)): value = f'{value}D'
    else: value = "'" + value.replace("'", "''") + "'"
    return {'expr': {'Literal': {'Value': value}}}

def color(value): return {'solid': {'color': lit(value)}}
def props(**kwargs): return [{'properties': kwargs}]
def field(table, name, measure=False):
    return {'Measure' if measure else 'Column': {'Expression': {'SourceRef': {'Entity': table}}, 'Property': name}}
def projection(table, name, measure=False, label=None):
    return {'field': field(table, name, measure), 'queryRef': f'{table}.{name}', 'nativeQueryRef': label or name, 'displayName': label or name}
def m(name, label=None): return projection('FactOutcomes',name,True,label)
def c(table,name,label=None): return projection(table,name,False,label)

def container(title=None, bg='#FFFFFF'):
    return {'title': props(show=lit(bool(title)), text=lit(title or ''), fontSize=lit(15), bold=lit(True),fontColor=color(NAVY)),
            'background': props(show=lit(True),color=color(bg),transparency=lit(0)),
            'border': props(show=lit(False)),
            'padding': props(top=lit(10),bottom=lit(10),left=lit(12),right=lit(12))}

counter=0
def visual(page,name,kind,x,y,w,h,query=None,objects=None,title=None,bg='#FFFFFF'):
    global counter
    counter+=1
    v={'visualType':kind,'visualContainerObjects':container(title,bg),'drillFilterOtherVisuals':True}
    if query: v['query']={'queryState':{role:{'projections':items} for role,items in query.items()}}
    if objects: v['objects']=objects
    doc={'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json',
         'name':name,'position':{'x':x,'y':y,'width':w,'height':h,'z':counter,'tabOrder':counter},'visual':v}
    write(PAGES/page/'visuals'/name/'visual.json',doc)
    return doc

def text(page,name,text,x,y,w,h,size=13,bold=False,fg=INK,bg='#FFFFFF'):
    paragraphs=[{'textRuns':[{'value':line,'textStyle':{'fontFamily':'Segoe UI','fontSize':f'{size}pt','fontWeight':'bold' if bold else 'normal','color':fg}}]} for line in text.split('\n')]
    doc=visual(page,name,'textbox',x,y,w,h,objects={'general':props(paragraphs=paragraphs)},bg=bg)
    doc['visual']['visualContainerObjects']['padding']=props(top=lit(0),bottom=lit(0),left=lit(10),right=lit(10))
    write(PAGES/page/'visuals'/name/'visual.json',doc)
    return doc

def card(page,name,measure,label,x,y,w=280,h=105):
    return visual(page,name,'cardVisual',x,y,w,h,{'Data':[m(measure,label)]},
      {'cardCalloutArea':[{'properties':{'show':lit(True)},'selector':{'id':'default'}}],
       'label':[{'properties':{'fontSize':lit(12),'fontColor':color(MUTED)},'selector':{'id':'default'}}],
       'value':[{'properties':{'fontSize':lit(29),'fontColor':color(TEAL),'labelDisplayUnits':lit(0)},'selector':{'id':'default'}}]})

def table(page,name,columns,x,y,w,h,title,totals=True,size=12):
    return visual(page,name,'tableEx',x,y,w,h,{'Values':columns},
      {'values':props(fontSize=lit(size),fontColorPrimary=color(INK),backColorPrimary=color('#FFFFFF'),backColorSecondary=color(LIGHT)),
       'columnHeaders':props(fontSize=lit(size),bold=lit(True),fontColor=color(NAVY),backColor=color(LIGHT),wordWrap=lit(True)),
       'total':props(totals=lit(totals),fontSize=lit(size),bold=lit(True)),
       'grid':props(rowPadding=lit(6),gridVertical=lit(False))},title)

def slicer(page,name,table_name,col,label,x,y,w):
    return visual(page,name,'slicer',x,y,w,85,{'Values':[c(table_name,col,label)]},
      {'data':props(mode=lit('Dropdown')),'selection':props(strictSingleSelect=lit(False),selectAllCheckboxEnabled=lit(True),singleSelect=lit(False)),
       'items':props(fontSize=lit(13)), 'header':props(show=lit(False))},label)

def bar(page,name,category,measure,x,y,w,h,title,series=None):
    q={'Category':[category],'Y':[measure]}
    if series:q['Series']=[series]
    doc=visual(page,name,'barChart' if series else 'clusteredBarChart',x,y,w,h,q,
      {'categoryAxis':props(fontSize=lit(12),showAxisTitle=lit(False)),
       'valueAxis':props(fontSize=lit(11),showAxisTitle=lit(False),labelDisplayUnits=lit(0)),
       'labels':props(show=lit(not series),fontSize=lit(11),labelDisplayUnits=lit(0)),
       'dataPoint':props(defaultColor=color(TEAL)), 'legend':props(show=lit(bool(series)),fontSize=lit(11))},title)
    if series:
        del doc['visual']['objects']['dataPoint']
        write(PAGES/page/'visuals'/name/'visual.json',doc)
    return doc

def base(page,title,subtitle,index):
    write(PAGES/page/'page.json',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json',
      'name':page,'displayName':title,'displayOption':'FitToPage','height':900,'width':1600,
      'objects':{'background':props(color=color(LIGHT),transparency=lit(0))}})
    text(page,'header',f'QUANTRISK  /  MORTGAGE LENDING\n{title}',24,16,1552,92,23,True,'#FFFFFF',NAVY)
    text(page,'subtitle',subtitle,24,113,1552,43,13,False,MUTED,LIGHT)
    text(page,'footer',f'2025 HMDA snapshot · Delaware · Official FFIEC/CFPB public data | QuantRisk Analytics   •   {index}/3',24,858,1552,28,10,False,MUTED,LIGHT)

if __name__=='__main__':
    backup=ROOT/'reports/generated/power_bi/layout_before_dashboard.zip'
    if not backup.exists():
        backup.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(backup,'w',zipfile.ZIP_DEFLATED) as z:
            for p in REPORT.rglob('*'):
                if p.is_file():z.write(p,p.relative_to(REPORT))
    # Remove only previous report-page JSON files, after preserving them above.
    for p in PAGES.rglob('*.json'): p.unlink()
    overview,lending,quality='66b0727775d10616d0c5','lending','quality'
    base(overview,'Management overview','Observed application outcomes | Home purchase · first lien · principal residence · site-built · 1–4 units',1)
    slicer(overview,'product','DimProduct','product_name','Loan product',24,166,330)
    text(overview,'scope','Closed-end, non-reverse, non-business loans. All loan types.\nApplications = actions 1–5; decisions = actions 1–3. Purchases and preapprovals excluded.',378,166,1198,85,13,False,INK)
    for i,(measure,label) in enumerate([('Applications','Applications (actions 1–5)'),('Decisions','Decisions (actions 1–3)'),('Originations','Originations (action 1)'),('Denial Rate','Denials / decisions'),('Approval Rate','Approvals / decisions')]):
        card(overview,f'kpi{i}',measure,label,24+i*312,267,304,112)
    bar(overview,'volume',c('DimProduct','product_name','Product'),m('Applications'),24,395,560,278,'Application volume by product')
    table(overview,'products',[c('DimProduct','product_name','Product'),m('Applications'),m('Decisions'),m('Originations'),m('Denied'),m('Denial Rate')],600,395,976,278,'Product outcomes — counts and decision denominator')
    for i,(measure,label) in enumerate([('Origination Share','Originations / applications'),('Withdrawal Share','Withdrawn / applications'),('Incomplete Share','Incomplete / applications'),('Approved Not Accepted Share','Not accepted / approvals')]):
        card(overview,f'share{i}',measure,label,24+i*390,689,382,100)
    text(overview,'interpretation','Rates are withheld when their denominator is below 30; counts remain visible. Approvals include originated and approved-not-accepted applications.\nAnnual observed outcomes are not a tracked conversion funnel, default model or recommendation for any applicant.',24,800,1552,51,11,False,MUTED,LIGHT)

    base(lending,'Lending outcomes','Compare observed outcomes within product groups. Differences in applicant and loan composition can explain differences between lenders.',2)
    slicer(lending,'lender','DimLender','respondent_name','Lender (search or select)',24,166,850)
    slicer(lending,'product','DimProduct','product_name','Loan product',890,166,400)
    text(lending,'reset','Clear selections with the eraser\non each slicer; Ctrl selects multiple.',1306,166,270,85,11,False,MUTED)
    for i,(measure,label) in enumerate([('Applications','Selected applications'),('Decisions','Selected decisions'),('Denied','Selected denials'),('Denial Rate','Denials / decisions')]):
        card(lending,f'kpi{i}',measure,label,24+i*390,267,382,105)
    doc=table(lending,'lenders',[c('DimLender','respondent_name','Lender'),c('DimProduct','product_name','Product'),m('Applications'),m('Decisions'),m('Originations'),m('Denied'),m('Denial Rate'),m('Decision Rate Status','Rate status')],24,388,1552,355,'Lender × product — alphabetical; application populations only',False,11)
    doc['visual']['query']['sortDefinition']={'sort':[{'field':field('DimLender','respondent_name'),'direction':'Ascending'}],'isDefaultSort':True}
    doc['filterConfig']={'filters':[{'name':'hasapplications','field':field('FactOutcomes','Applications',True),'type':'Advanced','filter':{'Version':2,'From':[{'Name':'f','Entity':'FactOutcomes','Type':0}],'Where':[{'Condition':{'Comparison':{'ComparisonKind':1,'Left':{'Measure':{'Expression':{'SourceRef':{'Source':'f'}},'Property':'Applications'}},'Right':{'Literal':{'Value':'0L'}}}}}]}}]}
    write(PAGES/lending/'visuals/lenders/visual.json',doc)
    text(lending,'method','Denial rate = action 3 / actions 1+2+3. A blank rate means fewer than 30 decisions or no decision population.\nThis is descriptive lender comparison, not a performance ranking or causal assessment. Institutions are identified by LEI; names are labels.\nThe table excludes lender/product combinations with no applications. Purchases and preapproval actions do not enter these rates.',24,759,1552,92,12,False,MUTED)

    base(quality,'Data quality — statewide','Fixed statewide cohort of 10,623 originations. This page is independent of lender and product selections on the other pages.',3)
    text(quality,'audit','SOURCE RECONCILED\n55,183 Delaware records\nAll 8 action totals and amounts matched',24,166,500,106,16,True,NAVY)
    text(quality,'lenders','LENDER REFERENCE\n558 / 558 LEIs matched\nOfficial 2025 snapshot transmittal sheet',540,166,510,106,16,True,NAVY)
    text(quality,'controls','RAW DATA PRESERVED\n99 original fields · SHA-256 recorded\nIndependent CSV-to-output validation',1066,166,510,106,16,True,NAVY)
    bar(quality,'coverage',c('StatewideCoverage','field','Field'),m('Coverage Records','Records'),24,288,850,370,'Value availability by field (10,623 per field)',c('StatewideCoverage','value_status','Status'))
    table(quality,'coverage_table',[c('StatewideCoverage','field','Field'),c('StatewideCoverage','value_status','Status'),m('Coverage Records','Count'),m('Coverage Share','Share')],890,288,686,370,'Field coverage — all statuses',False,11)
    text(quality,'limitations','READING THE DATA\nNumeric availability is not a test of economic validity or field applicability. Blank does not mean zero. NA and Exempt remain separate.\nPublic HMDA values include privacy modifications, rounded amounts and suppressed information. There are no subsequent repayment/default outcomes.\nLTV mapping remains unresolved and is excluded from typed analysis. 104 identical-public-row excess occurrences are retained; identity is not available.',24,674,1552,118,12,False,INK)
    text(quality,'boundary','US mortgage-market evidence only. No causal claims about demographic differences, legal discrimination conclusions or individual lending recommendations.',24,806,1552,43,11,False,MUTED,LIGHT)
    write(PAGES/'pages.json',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json','pageOrder':[overview,lending,quality],'activePageName':overview})
    print(f'Created 3 pages and {counter} visuals. Open the PBIP in Desktop to verify rendering.')
