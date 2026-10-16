root=DirectoryName[DirectoryName[$InputFileName]];
Scan[If[!DirectoryQ[FileNameJoin[{root,#}]],CreateDirectory[FileNameJoin[{root,#}]]]& ,{"Notebooks","exports","dist"}];
PacletDirectoryLoad[root];Needs["PendulumLab`"];
r=PLAnalyze[];
If[FailureQ[r],Print[r];Exit[1]];
fontRuns[s_String]:=Map[StyleBox[StringJoin[#],FontFamily->If[First[ToCharacterCode[First[#]]]>=16^^2E80,"SimSun","Times New Roman"]]&,SplitBy[Characters[s],First[ToCharacterCode[#]]>=16^^2E80&]];
mathBox[s_String]:=Module[{h,t,parts,decimals,digitCount,boxes,formats},
 t=StringTrim[s,{" ", ".", ","}];
 If[t=="E",Return["E"]];
 If[StringContainsQ[t,"\\%"],
  parts=StringSplit[t,"="];If[Length[parts]>1,Return[RowBox[Riffle[mathBox/@parts,"="]]]];
  parts=StringSplit[t,"\\times"];If[Length[parts]>1,Return[RowBox[Riffle[mathBox/@parts,"\[Times]"]]]];
  If[StringEndsQ[t,"\\%"],Return[RowBox[{mathBox[StringDrop[t,-2]],"%"}]]]];
 parts=StringSplit[t,",\\qquad "];
 If[Length[parts]>1,Return[RowBox[Riffle[mathBox/@parts,RowBox[{",","  "}]]]]];
 If[StringStartsQ[t,"\\ddot\\theta+"],Return[RowBox[{OverscriptBox["\[Theta]","\[DoubleDot]"],"+",FractionBox["g",SuperscriptBox["L","\[Prime]"]],StyleBox["sin",FontSlant->"Plain"],"\[Theta]","=","0"}]]];
 If[StringStartsQ[t,"\\frac{E}{m}"],Return[RowBox[{FractionBox["E","m"],"=",FractionBox["1","2"],SuperscriptBox[RowBox[{"(",SuperscriptBox["L","\[Prime]"],OverscriptBox["\[Theta]","."],")"}],"2"],"+","g",SuperscriptBox["L","\[Prime]"],"(","1","-",StyleBox["cos",FontSlant->"Plain"],"\[Theta]",")"}]]];
 If[StringStartsQ[t,"T_{\\mathrm{exact}}"],Return[RowBox[{SubscriptBox["T",StyleBox["exact",FontSlant->"Plain"]],"=","4",SqrtBox[FractionBox[SuperscriptBox["L","\[Prime]"],"g"]]," ",StyleBox["K",FontSlant->"Plain"],"(",SuperscriptBox[StyleBox["sin",FontSlant->"Plain"],"2"],"(",FractionBox[SubscriptBox["\[Theta]","0"],"2"],")",")"}]]];
 If[!StringContainsQ[t,"\\left|"],t=StringReplace[t,RegularExpression["\\|([^|]+)\\|"]:>"\\left|$1\\right|"]];
 h=Quiet[Check[ToExpression[t,TeXForm,HoldComplete],$Failed]];
 If[!FreeQ[h,$Failed],Print["TEX_FAILURE: "<>t];Exit[1]];
 decimals=StringCases[t,RegularExpression["[0-9]+\\.[0-9]+"]];
 digitCount[n_]:=Module[{matches=Select[decimals,Abs[ToExpression[#]-Abs[n]]<10^-12&]},If[matches==={},6,StringLength[Last[StringSplit[First[matches],"."]]]]];
 formats=Table[With[{v=n,a=Abs[n],d=digitCount[n]},v->If[v<0,-NumberForm[a,{20,d}],NumberForm[v,{20,d}]]],{n,DeleteDuplicates[Cases[h,_Real,Infinity]]}];
 h=h/.formats;
 boxes=Check[ToBoxes[h/.HoldComplete->Defer,TraditionalForm],$Failed];
 If[boxes===$Failed,Print["TEX_BOX_FAILURE: "<>t];Exit[1]];
 boxes/."\[ExponentialE]"->"E"];

tableBoxes[runs_List]:=RowBox[Flatten[Map[If[#["kind"]=="math",{mathBox[#["text"]]},fontRuns[#["text"]]]&,runs],1]];
rich[runs_List]:=TextData[Flatten[Map[If[#["kind"]=="math",{Cell[BoxData[mathBox[#["text"]]],"InlineFormula",FontFamily->"Times New Roman"]},fontRuns[#["text"]]]&,runs],1]];
input[h_HoldComplete]:=Cell[BoxData[ToBoxes[h/.HoldComplete->Defer,StandardForm]],"Input",CellOpen->False,FontFamily->"Times New Roman"];
evaluated[h_HoldComplete]:=Module[{v=ReleaseHold[h]},Cell[CellGroupData[{input[h],Cell[BoxData[ToBoxes[v,StandardForm]],"Output",FontFamily->"Times New Roman"]},Open]]];
blocks=Import[FileNameJoin[{root,"data","report.json"}],"RawJSON"];
make[b_]:=Switch[b["type"],
 "heading",Cell[rich[b["runs"]],Switch[b["level"],1,"Title",2,"Section",3,"Subsection",_,"Subsubsection"]],
 "text",Cell[rich[b["runs"]],"Text"],
 "caption",Cell[rich[b["runs"]],"Caption",TextAlignment->Center],
 "math",Cell[BoxData[mathBox[b["text"]]],"DisplayFormula",FontFamily->"Times New Roman",TextAlignment->Center],
 "table",Cell[BoxData[ToBoxes[Grid[Map[RawBoxes[tableBoxes[#]]&,b["runs"],{2}],Frame->None,Dividers->{None,{1->Black,2->Black,-1->Black}},Alignment->Center,Spacings->{1.1,.8},BaseStyle->{FontFamily->"Times New Roman",FontSize->13}],StandardForm]],"Output"],
 "figure",evaluated[HoldComplete[PLFitPlot[]]],
 "compute",evaluated[ToExpression[b["text"],InputForm,HoldComplete]],
 _,Nothing];
cells=Join[{input[HoldComplete[PacletDirectoryLoad[DirectoryName[NotebookDirectory[]]];Needs["PendulumLab`"]]]},make/@blocks,
 {input[HoldComplete[KeyTake[PLAnalyze[]["metrics"],{"gravity_fit","gravity_regression_standard_error"}]]]}];
styles=Notebook[{
 Cell[StyleData[StyleDefinitions->"Default.nb"]],
 Cell[StyleData["Notebook"],FontFamily->"Times New Roman",FontColor->Black],
 Cell[StyleData["Title"],FontFamily->"SimSun",FontColor->Black,FontSize->28,FontWeight->"Plain",TextAlignment->Center,CellMargins->{{60,60},{24,24}}],
 Cell[StyleData["Section"],FontFamily->"SimSun",FontColor->Black,FontSize->23,FontWeight->"Plain",CellMargins->{{60,60},{18,30}}],
 Cell[StyleData["Subsection"],FontFamily->"SimSun",FontColor->Black,FontSize->19,FontWeight->"Plain"],
 Cell[StyleData["Subsubsection"],FontFamily->"SimSun",FontColor->Black,FontSize->17,FontWeight->"Plain"],
 Cell[StyleData["Text"],FontFamily->"Times New Roman",FontSize->16,LineSpacing->{1.5,2},CellMargins->{{60,60},{10,10}}],
 Cell[StyleData["Caption"],FontFamily->"Times New Roman",FontSize->16,TextAlignment->Center,CellMargins->{{60,60},{16,8}}],
 Cell[StyleData["Output"],TextAlignment->Center,FontFamily->"Times New Roman",FontSize->15,CellMargins->{{60,60},{12,12}}],
 Cell[StyleData["DisplayFormula"],FontFamily->"Times New Roman",FontSize->18,CellMargins->{{60,60},{12,12}}]}];
nb=Notebook[cells,WindowTitle->"\:5355\:6446\:6d4b\:91cd\:529b\:52a0\:901f\:5ea6 - \:7f2a\:96e8\:8f69 2414050120",StyleDefinitions->styles,CommonDefaultFormatTypes->{"Output"->StandardForm},CellContext->Notebook,WindowSize->{1180,850},Magnification->1,BaseStyle->{FontSize->16,FontFamily->"Times New Roman"}];
Put[nb,PLNotebookPath[]];
reloaded=Get[PLNotebookPath[]];
report=TestReport[FileNameJoin[{root,"Tests","PackageTests.wlt"}]];
structureOK=Head[reloaded]===Notebook&&Count[reloaded,Cell[_,"Section",___],Infinity]==7&&Count[reloaded,Cell[_,"DisplayFormula",___],Infinity]>=10;
Export[FileNameJoin[{root,"exports","wolfram.json"}],r,"RawJSON"];
check=<|"kernel"->$Version,"tests_passed"->report["TestsSucceededCount"],"tests_failed"->report["TestsFailedCount"],"notebook_structure"->structureOK,"output_cells"->Count[reloaded,Cell[_,"Output",___],Infinity],"sections"->7,"font_families"->{"SimSun","Times New Roman"}|>;
Export[FileNameJoin[{root,"exports","tests.json"}],check,"RawJSON"];Print[check];
If[!TrueQ[structureOK]||report["TestsFailedCount"]!=0,Print[report];Exit[1]];
(* Stage only distributable resources, keeping build outputs out of the archive. *)
stage=FileNameJoin[{root,"dist","package-source","PendulumLab"}];
If[ExpandFileName[stage]=!=FileNameJoin[{ExpandFileName[root],"dist","package-source","PendulumLab"}],Exit[1]];
If[DirectoryQ[stage]&&!FileExistsQ[FileNameJoin[{stage,"PacletInfo.wl"}]],Print["Unexpected package staging contents"];Exit[1]];
If[DirectoryQ[stage],DeleteDirectory[stage,DeleteContents->True]];
CreateDirectory[stage,CreateIntermediateDirectories->True];
CopyFile[FileNameJoin[{root,"PacletInfo.wl"}],FileNameJoin[{stage,"PacletInfo.wl"}]];
Scan[CopyDirectory[FileNameJoin[{root,#}],FileNameJoin[{stage,#}]]&, {"Kernel","Notebooks","data","Tests"}];
Needs["PacletTools`"];
archive=FileNameJoin[{root,"dist","PendulumLab-0.1.0.paclet"}];
If[FileExistsQ[archive],DeleteFile[archive]];
packed=CreatePacletArchive[stage,FileNameJoin[{root,"dist"}]];
If[!FileExistsQ[archive],Print[packed];Exit[1]];
Print["PACLET_BUILD_OK"];

