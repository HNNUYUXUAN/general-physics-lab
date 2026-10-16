"""Generate standalone Paclets and serialize Wolfram build/installation verification."""
from pathlib import Path
import json,os,shutil,subprocess,time
from physicslab.common.io import read_json,write_json
from physicslab.common.tex_boxes import wl_string,tex_boxes

from physicslab.common.manuscripts import unit_latex as unit_tex

def write_wl(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(''.join(c if ord(c)<128 else '\\:'+format(ord(c),'04x') for c in text),encoding='ascii')

KERNEL=r'''
BeginPackage["@@PACLET@@`"];
Analyze::usage="Analyze[] independently calculates this experiment from packaged observations.";
LabNotebookPath::usage="LabNotebookPath[] returns the bundled notebook path.";
OpenNotebook::usage="OpenNotebook[] opens the bundled notebook.";
ExecuteBlock::usage="ExecuteBlock[index] evaluates a reproducible analysis block.";
ResultsTable::usage="ResultsTable[table] displays a computed table.";
ResultsFigure::usage="ResultsFigure[key] plots this experiment's independently computed series.";
Explore::usage="Explore[key] opens a model exploration provided by the experiment.";
Begin["`Private`"];
$packageRoot=DirectoryName[DirectoryName[$InputFileName]];
$dataRoot=FileNameJoin[{$packageRoot,"data"}];
$analysisLoad=Check[Get[FileNameJoin[{$packageRoot,"Kernel","analysis.wl"}]],$Failed];
If[$analysisLoad===$Failed,Print["ANALYSIS_SOURCE_LOAD_FAILED"];Abort[]];
$author=Import[FileNameJoin[{$dataRoot,"authoring.json"}],"RawJSON"];
$math=Import[FileNameJoin[{$dataRoot,"math-map.json"}],"RawJSON"];
$display=Import[FileNameJoin[{$dataRoot,"display.json"}],"RawJSON"];
fontRuns[s_String]:=Map[StyleBox[StringJoin[#],FontFamily->If[First[ToCharacterCode[First[#]]]>=16^^2E80,"SimSun","Times New Roman"]]&,SplitBy[Characters[s],First[ToCharacterCode[#]]>=16^^2E80&]];
mathBoxes[s_String]:=FormBox[StyleBox[ToExpression[Lookup[$math,s,"\"?\""],InputForm],FontFamily->"Times New Roman",AutoSpacing->False,AutoMultiplicationSymbol->False,ShowAutoStyles->False],TraditionalForm];
textBoxes[s_String]:=Module[{pieces=StringSplit[s,RegularExpression["(\\$[^$]+\\$)"]->"$1"]},RowBox[Flatten[If[StringStartsQ[#,"$"],{mathBoxes[StringTrim[#,"$"]]},fontRuns[#]]&/@pieces,1]]];
styled[s_String]:=RawBoxes[textBoxes[s]];
styled[x_]:=If[NumberQ[x],NumberForm[N[x],10],x];
tableView[t_Association]:=Column[{If[TrueQ[$tableCaptioned],Nothing,styled["表　"<>Lookup[t,"title","计算结果"]]],Grid[Map[styled,Prepend[t["rows"],t["headers"]],{2}],Frame->None,Dividers->{None,{1->Black,2->Black,-1->Black}},Alignment->Center,Spacings->{1.1,.8},BaseStyle->{FontFamily->"Times New Roman",FontSize->13}]},Alignment->Center,Spacings->.6];
unitView[s_String]:=If[KeyExistsQ[$display["units"],s],RawBoxes[FormBox[StyleBox[ToExpression[$display["units"][s],InputForm],FontFamily->"Times New Roman",AutoSpacing->False,ShowAutoStyles->False],TraditionalForm]],styled[s]];
metricView[r_Association]:=tableView[<|"headers"->{"指标","数值","单位"},"rows"->KeyValueMap[{Lookup[$display["metric_labels"],#1,Lookup[#2,"label",#1]],#2["value"],unitView[#2["unit"]]}&,r["metrics"]]|>];
plotView[r_Association,key_String]:=Module[{s=r["series"][key],pts,k,b,plot,res,fit,x},
 s=Join[s,Lookup[$display["series"],key,<||>]];
 pts=Transpose[{s["x"],s["y"]}];
 plot=ListPlot[pts,PlotStyle->Black,PlotMarkers->If[TrueQ[Lookup[s,"model",False]],None,{Style["\[EmptyCircle]",Black,FontFamily->"Times New Roman"],11}],Joined->(TrueQ[Lookup[s,"connect",False]]||TrueQ[Lookup[s,"model",False]]),AspectRatio->If[TrueQ[Lookup[s,"equal_aspect",False]],1,1/GoldenRatio],Axes->False,Frame->{{True,False},{True,False}},FrameLabel->{styled[s["x_label"]],styled[s["y_label"]]},GridLines->{None,Automatic},GridLinesStyle->Directive[GrayLevel[.9],Thin],ImageSize->720,BaseStyle->{FontFamily->"Times New Roman",FontSize->15},PlotRange->All];
 If[TrueQ[Lookup[s,"fit",False]]&&Length[pts]>2,
 fit=LinearModelFit[pts,x,x];plot=Show[plot,Plot[fit[x],{x,Min[s["x"]],Max[s["x"]]},PlotStyle->Black]];
 res=ListPlot[Transpose[{s["x"],s["y"]-(fit/@s["x"])}],PlotStyle->Black,PlotMarkers->{Style["\[EmptyCircle]",Black,FontFamily->"Times New Roman"],11},Axes->False,Frame->{{True,False},{True,False}},FrameLabel->{styled[s["x_label"]],styled[Lookup[s,"residual_label","残差"]]},GridLines->{None,{0}},GridLinesStyle->GrayLevel[.8],ImageSize->720,BaseStyle->{FontFamily->"Times New Roman",FontSize->15},PlotRange->All];
 Column[{plot,res},Alignment->Center],plot]];
exploreView[key_]:=explore[key,r];
Analyze[]:=Join[compute[$dataRoot],<|"code_hashes"-><|"Kernel/analysis.wl"->IntegerString[FileHash[FileNameJoin[{$packageRoot,"Kernel","analysis.wl"}],"SHA256"],16,64]|>,"input_hashes"->AssociationMap[IntegerString[FileHash[FileNameJoin[{$dataRoot,#}],"SHA256"],16,64]&,Keys[Import[FileNameJoin[{$dataRoot,"input-hashes.json"}],"RawJSON"]]]|>];
LabNotebookPath[]:=FileNameJoin[{$packageRoot,"Notebooks","@@PACLET@@.nb"}];
OpenNotebook[]:=NotebookOpen[LabNotebookPath[]];
ResultsTable[t_Association]:=tableView[t];
ResultsFigure[key_String]:=plotView[Analyze[],key];
Explore[key_String]:=explore[key,Analyze[]];
ExecuteBlock[index_Integer]:=Block[{r=Analyze[],root=$dataRoot,$tableCaptioned=StringStartsQ[Lookup[$author["expansions"][[index]],"caption",""],"表"]},Block[{$Context="@@PACLET@@`Private`",$ContextPath={"@@PACLET@@`Private`","@@PACLET@@`","System`"}},ToExpression[$author["expansions"][[index]]["wolfram"],InputForm]]];
End[];EndPackage[];
'''

BUILD=r'''
root=DirectoryName[DirectoryName[$InputFileName]];
Get[FileNameJoin[{root,"Kernel","@@PACLET@@.wl"}]];
r=@@PACLET@@`Analyze[];
If[!AssociationQ[r]||!AssociationQ[r["metrics"]],Print["INVALID_RESULT"];Exit[1]];
Scan[CreateDirectory[FileNameJoin[{root,#}],CreateIntermediateDirectories->True]&,{"Notebooks","exports","dist"}];
blocks=Import[FileNameJoin[{root,"data","report.json"}],"RawJSON"];
a=Import[FileNameJoin[{root,"data","authoring.json"}],"RawJSON"];
fontRuns[s_String]:=Map[StyleBox[StringJoin[#],FontFamily->If[First[ToCharacterCode[First[#]]]>=16^^2E80,"SimSun","Times New Roman"]]&,SplitBy[Characters[s],First[ToCharacterCode[#]]>=16^^2E80&]];
mathBox[s_String]:=FormBox[StyleBox[ToExpression[s,InputForm],FontFamily->"Times New Roman",AutoSpacing->False,AutoMultiplicationSymbol->False,ShowAutoStyles->False],TraditionalForm];
rich[runs_List]:=TextData[Flatten[If[#["kind"]=="math",{Cell[BoxData[mathBox[#["boxes"]]],"InlineFormula",FontFamily->"Times New Roman"]},fontRuns[#["text"]]]&/@runs,1]];
tableBoxes[runs_List]:=RowBox[Flatten[If[#["kind"]=="math",{mathBox[#["boxes"]]},fontRuns[#["text"]]]&/@runs,1]];
input[h_HoldComplete]:=Cell[BoxData[ToBoxes[h/.HoldComplete->Defer,StandardForm]],"Input",CellOpen->False];
evaluated[h_HoldComplete]:=Module[{v=ReleaseHold[h],boxes},If[!FreeQ[v,$Failed]||v===Null||StringContainsQ[ToString[Head[v],InputForm],"`Private`"],Print["FAILED_OR_UNEVALUATED_OUTPUT: ",Short[v,2]];Exit[1]];
 If[!FreeQ[v,_Manipulate|_DynamicModule],v=Pane[v,{980,Automatic},Alignment->Center,ImageSizeAction->"ShrinkToFit"]];
 boxes=Block[{$ContextPath=Join[{"@@PACLET@@`Private`","@@PACLET@@`"},$ContextPath]},ToBoxes[v,StandardForm]];Cell[CellGroupData[{input[h],Cell[BoxData[boxes],"Output",TextAlignment->Center]},Open]]];
make[b_]:=Switch[b["type"],
 "heading",Cell[rich[b["runs"]],Switch[b["level"],1,"Title",2,"Section",3,"Subsection",_,"Subsubsection"]],
 "text",Cell[rich[b["runs"]],"Text"],
 "caption",Cell[rich[b["runs"]],"Caption",TextAlignment->Center],
 "math",Cell[BoxData[mathBox[b["boxes"]]],"DisplayFormula",TextAlignment->Center],
 "table",Cell[BoxData[ToBoxes[Grid[Map[RawBoxes[tableBoxes[#]]&,b["rows"],{2}],Dividers->{None,{1->Black,2->Black,-1->Black}},Alignment->Center,Spacings->{1.1,.8},BaseStyle->{FontSize->13,FontFamily->"Times New Roman"}],StandardForm]],"Output"],
 "figure",evaluated[With[{k=b["key"]},HoldComplete[@@PACLET@@`ResultsFigure[k]]]],
 "asset",Cell[BoxData[ToBoxes[Show[Import[FileNameJoin[{root,"assets",b["name"]}],"Graphics"],ImageSize->800],StandardForm]],"Output"],
 "compute",evaluated[With[{i=b["index"]},HoldComplete[@@PACLET@@`ExecuteBlock[i]]]],_,Nothing];
styles=Notebook[{
 Cell[StyleData[StyleDefinitions->"Default.nb"]],
 Cell[StyleData["Notebook"],FontFamily->"Times New Roman",FontColor->Black],
 Cell[StyleData["Title"],FontFamily->"SimSun",FontColor->Black,FontSize->28,FontWeight->"Plain",TextAlignment->Center,CellMargins->{{60,60},{24,24}}],
 Cell[StyleData["Section"],FontFamily->"SimSun",FontColor->Black,FontSize->23,FontWeight->"Plain",CellMargins->{{60,60},{18,30}}],
 Cell[StyleData["Subsection"],FontFamily->"SimSun",FontColor->Black,FontSize->19,FontWeight->"Plain"],
 Cell[StyleData["Subsubsection"],FontFamily->"SimSun",FontColor->Black,FontSize->17,FontWeight->"Plain"],
 Cell[StyleData["Text"],FontSize->16,LineSpacing->{1.5,2},CellMargins->{{60,60},{10,10}}],
 Cell[StyleData["Caption"],FontSize->16,TextAlignment->Center,CellMargins->{{60,60},{16,8}}],
 Cell[StyleData["Output"],FontSize->15,TextAlignment->Center,CellMargins->{{60,60},{12,12}}],
 Cell[StyleData["InlineFormula"],FontFamily->"Times New Roman",AutoSpacing->False,ShowAutoStyles->False,AutoMultiplicationSymbol->False],
 Cell[StyleData["DisplayFormula"],FontFamily->"Times New Roman",FontSize->18,AutoSpacing->False,ShowAutoStyles->False,AutoMultiplicationSymbol->False,TextAlignment->Center,CellMargins->{{60,60},{12,12}}]}];
cells=Join[{input[HoldComplete[PacletDirectoryLoad[DirectoryName[NotebookDirectory[]]];Needs["@@PACLET@@`"]]]},make/@blocks,{input[HoldComplete[@@PACLET@@`Analyze[]["metrics"]]]}];
nb=Notebook[cells,WindowTitle->a["title"],StyleDefinitions->styles,CellContext->Notebook,WindowSize->{1180,850},CommonDefaultFormatTypes->{"Output"->StandardForm},BaseStyle->{FontFamily->"Times New Roman",FontSize->16}];
Put[nb,@@PACLET@@`LabNotebookPath[]];
tests=TestReport[FileNameJoin[{root,"Tests","PackageTests.wlt"}]];
If[tests["TestsFailedCount"]!=0,Print[tests];Exit[1]];
resultExport=Check[Export[FileNameJoin[{root,"exports","wolfram.json"}],Join[r,<|"environment"-><|"wolfram"->$Version|>|>],"RawJSON"],$Failed];
If[resultExport===$Failed,Print["RESULT_EXPORT_FAILED"];Exit[1]];
Needs["PacletTools`"];
stage=FileNameJoin[{root,"dist","package-source","@@PACLET@@"}];
CreateDirectory[stage,CreateIntermediateDirectories->True];
CopyFile[FileNameJoin[{root,"PacletInfo.wl"}],FileNameJoin[{stage,"PacletInfo.wl"}]];
Scan[If[DirectoryQ[FileNameJoin[{root,#}]],CopyDirectory[FileNameJoin[{root,#}],FileNameJoin[{stage,#}]]]&,{"Kernel","Notebooks","data","Tests","assets"}];
packed=CreatePacletArchive[stage,FileNameJoin[{root,"dist"}]];
If[!FileExistsQ[FileNameJoin[{root,"dist","@@PACLET@@-0.1.0.paclet"}]],Print[packed];Exit[1]];
Print["WOLFRAM_BUILD_OK"];
'''

VERIFY=r'''
root=DirectoryName[DirectoryName[$InputFileName]];
archive=FileNameJoin[{root,"dist","@@PACLET@@-0.1.0.paclet"}];
installed=PacletInstall[archive,ForceVersionInstall->True];
Needs["@@PACLET@@`"];
r=@@PACLET@@`Analyze[];
installedRoot=DirectoryName[DirectoryName[@@PACLET@@`LabNotebookPath[]]];
If[installedRoot===root||!FileExistsQ[@@PACLET@@`LabNotebookPath[]],Print["NOT_INDEPENDENT"];Exit[1]];
reference=Import[FileNameJoin[{root,"exports","wolfram.json"}],"RawJSON"];
If[!AssociationQ[reference]||r["input_hashes"]=!=reference["input_hashes"],Print["INSTALLED_INPUT_MISMATCH"];Exit[1]];
If[Max[Abs[Lookup[Values[r["metrics"]],"value"]-Lookup[Values[reference["metrics"]],"value"]]]>10^-10,Print["INSTALLED_MISMATCH"];Exit[1]];
tests=TestReport[FileNameJoin[{installedRoot,"Tests","PackageTests.wlt"}]];
If[tests["TestsFailedCount"]!=0,Exit[1]];
nb=Get[@@PACLET@@`LabNotebookPath[]];
messages=0;outputs=Count[nb,Cell[_,"Output",___],Infinity];renders=0;renderFailures=0;
If[!@@SKIP@@,UsingFrontEnd[
 freshMetrics=Quiet[Check[NotebookEvaluate[@@PACLET@@`LabNotebookPath[],InsertResults->False],$Failed]];
 If[!AssociationQ[freshMetrics]||Abs[freshMetrics[First[Keys[r["metrics"]]]]["value"]-r["metrics"][First[Keys[r["metrics"]]]]["value"]]>10^-10,Print["NOTEBOOK_REEVALUATION_FAILED"];Exit[1]];
 (* WolframScript's output channel is OutputForm. Preserve the actual StandardForm
    outputs constructed by the kernel, as the approved pendulum verifier does. *)
 nb=Get[@@PACLET@@`LabNotebookPath[]];
 messages=Count[nb,Cell[_,"Message",___],Infinity];
 flatten[Cell[CellGroupData[x_,___]]]:=Flatten[flatten/@x];flatten[c_Cell]:={c};flat=Flatten[flatten/@First[nb]];
 indices=Flatten[Position[flat,Cell[_,"Section",___],{1}]];
 out=FileNameJoin[{root,"exports","visual"}];CreateDirectory[out];
 Do[segment=DeleteCases[Take[flat,{If[i==1,1,indices[[i]]],If[i<Length[indices],indices[[i+1]]-1,Length[flat]]}],Cell[_,"Input",___]];
 view=NotebookPut[Notebook[Append[segment,Cell[" ","Text"]],StyleDefinitions->(StyleDefinitions/.Options[nb,StyleDefinitions]),WindowSize->{1180,850},Visible->False]];
 rendered=Quiet[Rasterize[view,"Image",RasterSize->{1200,Automatic},ImageResolution->96,Background->White]];
 If[ImageQ[rendered],Export[FileNameJoin[{out,"section-"<>IntegerString[i,10,2]<>".png"}],rendered];renders++,
 NotebookClose[view];parts=Partition[segment,UpTo[8]];
 Do[view=NotebookPut[Notebook[Append[parts[[j]],Cell[" ","Text"]],StyleDefinitions->(StyleDefinitions/.Options[nb,StyleDefinitions]),WindowSize->{1180,850},Visible->False]];
 piece=Quiet[Rasterize[view,"Image",RasterSize->{1200,Automatic},ImageResolution->96,Background->White]];
 If[ImageQ[piece],Export[FileNameJoin[{out,"section-"<>IntegerString[i,10,2]<>"-part"<>IntegerString[j,10,2]<>".png"}],piece];renders++,renderFailures++];NotebookClose[view],{j,Length[parts]}];view=Null];If[view=!=Null,NotebookClose[view]],{i,Length[indices]}];
]];
record=<|"passed"->(tests["TestsFailedCount"]==0&&messages==0&&renderFailures==0),"tests_passed"->tests["TestsSucceededCount"],"installed_outside_source_tree"->True,"fresh_kernel_execution"->True,"frontend_evaluated"->!@@SKIP@@,"messages"->messages,"output_cells"->outputs,"section_renders"->renders,"render_failures"->renderFailures,"kernel"->$Version|>;
Export[FileNameJoin[{root,"exports","validation.json"}],record,"RawJSON"];
Print["WOLFRAM_VERIFY_OK"];
'''

def generate(paclet,entry,a):
    name=entry['paclet']
    # Encode worker-authored WL as ASCII before kernel execution.
    path=paclet/'Kernel/analysis.wl';write_wl(path,path.read_text(encoding='utf-8'))
    write_wl(paclet/f'Kernel/{name}.wl',KERNEL.replace('@@PACLET@@',name))
    write_wl(paclet/'Kernel/init.wl',f'Get[FileNameJoin[{{DirectoryName[$InputFileName],"{name}.wl"}}]];')
    write_wl(paclet/'PacletInfo.wl',f'PacletObject[<|"Name"->"{name}","Version"->"0.1.0","WolframVersion"->"14.0+","Description"->{wl_string(a["title"])},"Creator"->"Physics Lab Contributors","Extensions"->{{{{"Kernel","Root"->"Kernel","Context"->{{"{name}`"}}}},{{"Resource","Root"->".","Resources"->{{"Notebooks","data","assets"}}}}}}|>]')
    # Only notebook/package resources enter archives; build, exports, and dist are excluded.
    write_wl(paclet/'Support/build.wls',BUILD.replace('@@PACLET@@',name).replace('CreatePacletArchive[root,','CreatePacletArchive[root,'))
    payload=read_json(paclet/'data/report.json');mapping={}
    def collect(value):
        if isinstance(value,dict):
            if value.get('kind')=='math':mapping[value['text']]=value['boxes']
            for v in value.values():collect(v)
        elif isinstance(value,list):
            for v in value:collect(v)
    collect(payload)
    p=read_json(paclet/'data/python-reference.json')
    presentation={'metric_labels':{k:v.get('label',a.get('metric_labels',{}).get(k,k)) for k,v in p['metrics'].items()},'units':{},'series':{}}
    for value in p['metrics'].values():
        unit=value['unit'];tex=unit_tex(unit)
        if tex is not None:presentation['units'][unit]=tex_boxes(tex)
    for table in p.get('tables',{}).values():
        for text in table['headers']:
            for tex in __import__('re').findall(r'\$([^$]+)\$',str(text)):mapping[tex]=tex_boxes(tex)
    for s in p.get('series',{}).values():
        for key in ('x_label','y_label'):
            for tex in __import__('re').findall(r'\$([^$]+)\$',s[key]):mapping[tex]=tex_boxes(tex)
    for key,s in p.get('series',{}).items():
        meta={k:s[k] for k in ('x_label','y_label','label','fit','connect','model','equal_aspect') if k in s}
        unit=s.get('residual_unit',s['y_label'].split(' / ',1)[1] if ' / ' in s['y_label'] else '无量纲' if 'log' in s['y_label'].lower() or 'ln' in s['y_label'].lower() else '')
        meta['residual_label']='残差'+(' / '+unit if unit else '')
        presentation['series'][key]=meta
    def collect_labels(value):
        if isinstance(value,str):
            for tex in __import__('re').findall(r'\$([^$]+)\$',value):mapping[tex]=tex_boxes(tex)
        elif isinstance(value,dict):
            for child in value.values():collect_labels(child)
        elif isinstance(value,list):
            for child in value:collect_labels(child)
    collect_labels(p)
    collect_labels(presentation)
    # Private native exploration labels also use the same presentation grammar.
    source=__import__('re').sub(r'\\:([0-9a-fA-F]{4})',lambda m:chr(int(m[1],16)),path.read_text(encoding='ascii'))
    for literal in __import__('re').findall(r'"(?:\\.|[^"\\])*"',source):
        if '$' in literal:
            collect_labels(literal[1:-1].replace(r'\\','\\').replace(r'\"','"'))
    write_json(paclet/'data/math-map.json',mapping)
    write_json(paclet/'data/display.json',presentation)
    checks=[f'VerificationTest[NumberQ[{name}`Analyze[]["metrics"][{wl_string(k)}]["value"]],True,TestID->{wl_string("finite-"+k)}]' for k in a['comparison']]
    checks += [f'VerificationTest[FileExistsQ[{name}`LabNotebookPath[]],True,TestID->"notebook-entry"]',f'VerificationTest[FileNameTake[{name}`LabNotebookPath[]],"{name}.nb",TestID->"notebook-name"]']
    write_wl(paclet/'Tests/PackageTests.wlt','\n'.join(checks))

def run_kernel(script,log,expected,timeout=240):
    exe=Path(os.environ.get('WOLFRAMSCRIPT',r'C:/Program Files/Wolfram Research/WolframScript/wolframscript.exe'))
    with log.open('w',encoding='utf-8') as output:
        proc=subprocess.Popen([str(exe),'-file',str(script)],stdout=output,stderr=subprocess.STDOUT,cwd=script.parent)
        start=time.monotonic()
        while proc.poll() is None:
            if expected.exists() and ('WOLFRAM_VERIFY_OK' in log.read_text(encoding='utf-8',errors='replace') or 'WOLFRAM_BUILD_OK' in log.read_text(encoding='utf-8',errors='replace')):
                # The headless front end can keep wolframscript's process tree alive
                # after all verified outputs have been flushed. Stop only this runner.
                try:proc.wait(timeout=3)
                except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=15)
                return
            if time.monotonic()-start>timeout:
                proc.terminate();proc.wait(timeout=15)
                raise TimeoutError(log.read_text(encoding='utf-8',errors='replace')[-3000:])
            time.sleep(.5)
        if proc.returncode!=0 or not expected.exists():raise RuntimeError(log.read_text(encoding='utf-8',errors='replace')[-5000:])

def execute(paclet,run,skip_frontend):
    # Root orchestrator invokes this queue sequentially; lock also protects concurrent CLI invocations.
    project=Path(__file__).resolve().parents[1];lock=project/'.build/wolfram.lock';lock.parent.mkdir(exist_ok=True)
    with lock.open('x') as f:f.write(str(os.getpid()))
    try:
        run_kernel(paclet/'Support/build.wls',run/'wolfram-build.log',paclet/'exports/wolfram.json')
        text=VERIFY.replace('@@PACLET@@',paclet.name).replace('@@SKIP@@','True' if skip_frontend else 'False')
        script=paclet/'Support/verify-installed.wls';write_wl(script,text)
        run_kernel(script,run/'wolfram-verify.log',paclet/'exports/validation.json',timeout=300)
    finally:lock.unlink(missing_ok=True)
