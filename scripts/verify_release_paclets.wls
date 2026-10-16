(* Validate independently installed distribution archives in a fresh kernel. *)
$HistoryLength=0;
project=DirectoryName[DirectoryName[$InputFileName]];
entries=Import[FileNameJoin[{project,"experiments","registry.json"}],"RawJSON"]["experiments"];
records={};
Do[
 name=entry["paclet"];
 archive=FileNameJoin[{project,entry["paclet_archive"]}];
 installed=PacletInstall[archive,ForceVersionInstall->True,UpdatePacletSites->False];
 If[!MatchQ[installed,_PacletObject],Print["INSTALL_FAILED ",name];Exit[1]];
 $ContextPath={"System`","Global`"};
 Needs[name<>"`"];
 analyze=If[name==="PendulumLab","PLAnalyze[]","Analyze[]"];
 notebookFunction=If[name==="PendulumLab","PLNotebookPath[]","LabNotebookPath[]"];
 result=ToExpression[name<>"`"<>analyze];
 notebookPath=ToExpression[name<>"`"<>notebookFunction];
 installedRoot=DirectoryName[DirectoryName[notebookPath]];
 If[StringStartsQ[ExpandFileName[installedRoot],ExpandFileName[FileNameJoin[{project,"notebook","paclets"}]]],Print["SOURCE_LOADED ",name];Exit[1]];
 reference=Import[FileNameJoin[{project,"experiments",entry["id"],"results","wolfram.json"}],"RawJSON"];
 If[result["input_hashes"]=!=reference["input_hashes"],Print["INPUT_MISMATCH ",name];Exit[1]];
 keys=Keys[reference["metrics"]];
 errors=Table[Abs[N[result["metrics"][key]["value"]]-N[reference["metrics"][key]["value"]]]/Max[1,Abs[N[reference["metrics"][key]["value"]]]],{key,keys}];
 If[!And@@(NumberQ/@errors)||Max[errors]>10^-10,Print["RESULT_MISMATCH ",name];Exit[1]];
 licenseFiles={"LICENSE","LICENSING.md","THIRD_PARTY_NOTICES.md","LICENSES/CC-BY-4.0.txt"};
 If[!And@@(FileExistsQ[FileNameJoin[{installedRoot,#}]]&/@licenseFiles),Print["LICENSE_MISSING ",name];Exit[1]];
 If[Head[Get[notebookPath]]=!=Notebook,Print["NOTEBOOK_INVALID ",name];Exit[1]];
 tests=TestReport[FileNameJoin[{installedRoot,"Tests","PackageTests.wlt"}]];
 If[tests["TestsFailedCount"]!=0,Print["TEST_FAILED ",name];Exit[1]];
 AppendTo[records,<|"experiment_id"->entry["id"],"status"->"passed","installed_independently"->True,"metric_count"->Length[keys],"max_relative_difference"->Max[errors],"tests_passed"->tests["TestsSucceededCount"],"notebook_valid"->True,"license_files_present"->True|>];
 Print["PACLET_OK ",entry["id"]];
 Export[FileNameJoin[{project,".build","release","paclet-installation.json"}],<|"kernel"->$Version,"session"->"fresh WolframScript kernel","packages"->records|>,"RawJSON"],
 {entry,entries}];
Print["RELEASE_PACLETS_OK ",Length[records]];
