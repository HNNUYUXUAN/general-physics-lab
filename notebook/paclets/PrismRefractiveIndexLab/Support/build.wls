
root=DirectoryName[DirectoryName[$InputFileName]];
Get[FileNameJoin[{root,"Kernel","PrismRefractiveIndexLab.wl"}]];
r=PrismRefractiveIndexLab`Analyze[];
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
 boxes=Block[{$ContextPath=Join[{"PrismRefractiveIndexLab`Private`","PrismRefractiveIndexLab`"},$ContextPath]},ToBoxes[v,StandardForm]];Cell[CellGroupData[{input[h],Cell[BoxData[boxes],"Output",TextAlignment->Center]},Open]]];
make[b_]:=Switch[b["type"],
 "heading",Cell[rich[b["runs"]],Switch[b["level"],1,"Title",2,"Section",3,"Subsection",_,"Subsubsection"]],
 "text",Cell[rich[b["runs"]],"Text"],
 "caption",Cell[rich[b["runs"]],"Caption",TextAlignment->Center],
 "math",Cell[BoxData[mathBox[b["boxes"]]],"DisplayFormula",TextAlignment->Center],
 "table",Cell[BoxData[ToBoxes[Grid[Map[RawBoxes[tableBoxes[#]]&,b["rows"],{2}],Dividers->{None,{1->Black,2->Black,-1->Black}},Alignment->Center,Spacings->{1.1,.8},BaseStyle->{FontSize->13,FontFamily->"Times New Roman"}],StandardForm]],"Output"],
 "figure",evaluated[With[{k=b["key"]},HoldComplete[PrismRefractiveIndexLab`ResultsFigure[k]]]],
 "asset",Cell[BoxData[ToBoxes[Show[Import[FileNameJoin[{root,"assets",b["name"]}],"Graphics"],ImageSize->800],StandardForm]],"Output"],
 "compute",evaluated[With[{i=b["index"]},HoldComplete[PrismRefractiveIndexLab`ExecuteBlock[i]]]],_,Nothing];
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
cells=Join[{input[HoldComplete[PacletDirectoryLoad[DirectoryName[NotebookDirectory[]]];Needs["PrismRefractiveIndexLab`"]]]},make/@blocks,{input[HoldComplete[PrismRefractiveIndexLab`Analyze[]["metrics"]]]}];
nb=Notebook[cells,WindowTitle->a["title"],StyleDefinitions->styles,CellContext->Notebook,WindowSize->{1180,850},CommonDefaultFormatTypes->{"Output"->StandardForm},BaseStyle->{FontFamily->"Times New Roman",FontSize->16}];
Put[nb,PrismRefractiveIndexLab`LabNotebookPath[]];
tests=TestReport[FileNameJoin[{root,"Tests","PackageTests.wlt"}]];
If[tests["TestsFailedCount"]!=0,Print[tests];Exit[1]];
resultExport=Check[Export[FileNameJoin[{root,"exports","wolfram.json"}],Join[r,<|"environment"-><|"wolfram"->$Version|>|>],"RawJSON"],$Failed];
If[resultExport===$Failed,Print["RESULT_EXPORT_FAILED"];Exit[1]];
Needs["PacletTools`"];
stage=FileNameJoin[{root,"dist","package-source","PrismRefractiveIndexLab"}];
CreateDirectory[stage,CreateIntermediateDirectories->True];
CopyFile[FileNameJoin[{root,"PacletInfo.wl"}],FileNameJoin[{stage,"PacletInfo.wl"}]];
Scan[If[DirectoryQ[FileNameJoin[{root,#}]],CopyDirectory[FileNameJoin[{root,#}],FileNameJoin[{stage,#}]]]&,{"Kernel","Notebooks","data","Tests","assets"}];
packed=CreatePacletArchive[stage,FileNameJoin[{root,"dist"}]];
If[!FileExistsQ[FileNameJoin[{root,"dist","PrismRefractiveIndexLab-0.1.0.paclet"}]],Print[packed];Exit[1]];
Print["WOLFRAM_BUILD_OK"];
