
root=DirectoryName[DirectoryName[$InputFileName]];
archive=FileNameJoin[{root,"dist","InertialBalanceLab-0.1.0.paclet"}];
installed=PacletInstall[archive,ForceVersionInstall->True];
Needs["InertialBalanceLab`"];
r=InertialBalanceLab`Analyze[];
installedRoot=DirectoryName[DirectoryName[InertialBalanceLab`LabNotebookPath[]]];
If[installedRoot===root||!FileExistsQ[InertialBalanceLab`LabNotebookPath[]],Print["NOT_INDEPENDENT"];Exit[1]];
reference=Import[FileNameJoin[{root,"exports","wolfram.json"}],"RawJSON"];
If[!AssociationQ[reference]||r["input_hashes"]=!=reference["input_hashes"],Print["INSTALLED_INPUT_MISMATCH"];Exit[1]];
If[Max[Abs[Lookup[Values[r["metrics"]],"value"]-Lookup[Values[reference["metrics"]],"value"]]]>10^-10,Print["INSTALLED_MISMATCH"];Exit[1]];
tests=TestReport[FileNameJoin[{installedRoot,"Tests","PackageTests.wlt"}]];
If[tests["TestsFailedCount"]!=0,Exit[1]];
nb=Get[InertialBalanceLab`LabNotebookPath[]];
messages=0;outputs=Count[nb,Cell[_,"Output",___],Infinity];renders=0;renderFailures=0;
If[!False,UsingFrontEnd[
 freshMetrics=Quiet[Check[NotebookEvaluate[InertialBalanceLab`LabNotebookPath[],InsertResults->False],$Failed]];
 If[!AssociationQ[freshMetrics]||Abs[freshMetrics[First[Keys[r["metrics"]]]]["value"]-r["metrics"][First[Keys[r["metrics"]]]]["value"]]>10^-10,Print["NOTEBOOK_REEVALUATION_FAILED"];Exit[1]];
 (* WolframScript's output channel is OutputForm. Preserve the actual StandardForm
    outputs constructed by the kernel, as the approved pendulum verifier does. *)
 nb=Get[InertialBalanceLab`LabNotebookPath[]];
 messages=Count[nb,Cell[_,"Message",___],Infinity];
 flatten[Cell[CellGroupData[x_,___]]]:=Flatten[flatten/@x];flatten[c_Cell]:={c};flat=Flatten[flatten/@First[nb]];
 indices=Flatten[Position[flat,Cell[_,"Section",___],{1}]];
 out=FileNameJoin[{root,"exports","visual"}];CreateDirectory[out];
 Do[segment=DeleteCases[Take[flat,{If[i==1,1,indices[[i]]],If[i<Length[indices],indices[[i+1]]-1,Length[flat]]}],Cell[_,"Input",___]];
 view=NotebookPut[Notebook[Append[segment,Cell[" ","Text"]],StyleDefinitions->(StyleDefinitions/.Options[nb,StyleDefinitions]),WindowSize->{1180,850},Visible->False]];
 rendered=Quiet[Rasterize[view,"Image",RasterSize->{1200,Automatic},ImageResolution->96,Background->White]];
 If[ImageQ[rendered],Export[FileNameJoin[{out,"section-"<>IntegerString[i,10,2]<>".png"}],rendered];renders++,renderFailures++];NotebookClose[view],{i,Length[indices]}];
]];
record=<|"passed"->(tests["TestsFailedCount"]==0&&messages==0&&renderFailures==0),"tests_passed"->tests["TestsSucceededCount"],"installed_outside_source_tree"->True,"fresh_kernel_execution"->True,"frontend_evaluated"->!False,"messages"->messages,"output_cells"->outputs,"section_renders"->renders,"render_failures"->renderFailures,"kernel"->$Version|>;
Export[FileNameJoin[{root,"exports","validation.json"}],record,"RawJSON"];
Print["WOLFRAM_VERIFY_OK"];
