root=DirectoryName[DirectoryName[$InputFileName]];
project=Nest[DirectoryName,root,3];
out=FileNameJoin[{project,".build","wolfram-visual"}];
If[!DirectoryQ[out],CreateDirectory[out,CreateIntermediateDirectories->True]];
archive=FileNameJoin[{root,"dist","PendulumLab-0.1.0.paclet"}];
(* The package name is project-specific. Preserve other installed versions. *)
existing=PacletFind["PendulumLab"];
recordPath=FileNameJoin[{project,"experiments","course-01","pendulum","results","wolfram-installed-validation.json"}];
If[existing=!={},
 installed=First[existing];
 currentInstalledHash=IntegerString[FileHash[FileNameJoin[{installed["Location"],"Kernel","PendulumLab.wl"}],"SHA256"],16,64];
 If[currentInstalledHash!=IntegerString[FileHash[FileNameJoin[{root,"Kernel","PendulumLab.wl"}],"SHA256"],16,64]||FileHash[FileNameJoin[{installed["Location"],"Notebooks","Pendulum.nb"}],"SHA256"]!=FileHash[FileNameJoin[{root,"Notebooks","Pendulum.nb"}],"SHA256"],
  prior=If[FileExistsQ[recordPath],Import[recordPath,"RawJSON"],<||>];
  If[Lookup[prior,"installed_code_hash",""]!=currentInstalledHash,Print["Existing installed PendulumLab differs from this project's recorded install; refusing to overwrite."];Exit[1]];
  installed=PacletInstall[archive,ForceVersionInstall->True,KeepExistingVersion->True,UpdatePacletSites->False]
 ],
 installed=PacletInstall[archive,KeepExistingVersion->True,UpdatePacletSites->False]
];
If[!MatchQ[installed,_PacletObject],Print[installed];Exit[1]];
Needs["PendulumLab`"];
installedRoot=PLRoot[];
If[ExpandFileName[installedRoot]===ExpandFileName[root],Print["Source package was loaded instead of installed package"];Exit[1]];
result=PLAnalyze[];
sourceResult=Import[FileNameJoin[{project,"experiments","course-01","pendulum","results","python.json"}],"RawJSON"];
If[result["input_hashes"]=!=sourceResult["input_hashes"]||Abs[result["metrics"]["gravity_fit"]["value"]-sourceResult["metrics"]["gravity_fit"]["value"]]>10^-10,Print["Installed result mismatch"];Exit[1]];
tests=TestReport[FileNameJoin[{installedRoot,"Tests","PackageTests.wlt"}]];
If[tests["TestsFailedCount"]!=0,Print["Installed tests failed"];Exit[1]];
(* A fresh WolframScript process invokes a front end to reevaluate all saved inputs. *)
UsingFrontEnd[
 evaluatedResult=Check[NotebookEvaluate[PLNotebookPath[],InsertResults->False],$Failed];
 If[!AssociationQ[evaluatedResult]||!KeyExistsQ[evaluatedResult,"gravity_fit"],Print["Notebook reevaluation failed"];Exit[1]];
 notebook=Get[PLNotebookPath[]];
 flattenCells[Cell[CellGroupData[x_,___]]]:=Flatten[flattenCells/@x];flattenCells[c_Cell]:={c};flat=Flatten[flattenCells/@First[notebook]];
 messages=Count[flat,Cell[_,"Message",___]];
 outputs=Count[flat,Cell[_,"Output",___]];
 indices=Flatten[Position[flat,Cell[_,"Section",___],{1}]];
 If[messages!=0||outputs!=Count[Get[FileNameJoin[{root,"Notebooks","Pendulum.nb"}]],Cell[_,"Output",___],Infinity]||Length[indices]!=7||Count[notebook,_GraphicsBox,Infinity]<2,Print[<|"messages"->messages,"outputs"->outputs,"sections"->Length[indices],"graphics"->Count[notebook,_GraphicsBox,Infinity]|>];Exit[1]];
 Do[
  segment=Take[flat,{If[i==1,1,indices[[i]]],If[i<Length[indices],indices[[i+1]]-1,Length[flat]]}];
  view=NotebookPut[Notebook[Append[segment,Cell[" ","Text"]],StyleDefinitions->(StyleDefinitions/.Options[notebook,StyleDefinitions]),WindowSize->{1180,850},Visible->False,BaseStyle->{FontSize->14,FontFamily->"Times New Roman"}]];
  rendered=Rasterize[view,"Image",ImageResolution->96,Background->White];
  Export[FileNameJoin[{out,"section-"<>IntegerString[i,10,2]<>".png"}],rendered];
  NotebookClose[view];
 ,{i,Length[indices]}];
];
record=<|"status"->"passed","installed_outside_source_tree"->True,"installed_code_hash"->result["code_hash"],"tests_passed"->tests["TestsSucceededCount"],"notebook_reevaluated"->True,"reevaluation_preserves_standardform_outputs"->True,"message_cells"->messages,"output_cells"->outputs,"section_renders"->Length[indices],"input_hashes"->result["input_hashes"],"kernel"->$Version|>;
Export[FileNameJoin[{project,"experiments","course-01","pendulum","results","wolfram-installed-validation.json"}],record,"RawJSON"];
Print[record];
