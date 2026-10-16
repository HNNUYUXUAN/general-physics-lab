(* ::Package:: *)
BeginPackage["PendulumLab`"];
PLRoot::usage="PLRoot[] returns the self-contained paclet directory.";
PLNotebookPath::usage="PLNotebookPath[] returns the bundled notebook path.";
PLOpenNotebook::usage="PLOpenNotebook[] opens the bundled notebook.";
PLConfig::usage="PLConfig[] reads the shared experiment specification.";
PLInputHashes::usage="PLInputHashes[] hashes the bundled canonical inputs.";
PLRawData::usage="PLRawData[] returns validated observations as associations.";
PLAnalyze::usage="PLAnalyze[] independently computes measured results and model scenarios.";
PLFitLine::usage="PLFitLine[x,y] computes an intercept-enabled OLS fit and standard error.";
PLPeriod::usage="PLPeriod[angleRadians,length,gravity] gives the nonlinear period.";
PLSimulate::usage="PLSimulate[config,gravity] solves the undamped pendulum from rest.";
PLFitPlot::usage="PLFitPlot[] returns a native fit and residual graphic.";
PLTrajectoryPlot::usage="PLTrajectoryPlot[] compares nonlinear and linear motion.";
PLScanPlot::usage="PLScanPlot[] plots amplitude-dependent period and gravity bias.";
PLExplorer::usage="PLExplorer[] gives an interactive nonlinear pendulum model.";
PLTable::usage="PLTable[kind] displays compact Chinese-labelled measured and computed tables.";
PLSymbolicDerivation::usage="PLSymbolicDerivation[] displays the symbolic gravity and uncertainty formulas.";
PLSummary::usage="PLSummary provides a visual pendulum laboratory view.";
PLMeasurementView::usage="PLMeasurementView provides a visual pendulum laboratory view.";
PLMeasurementExplorer::usage="PLMeasurementExplorer provides a visual pendulum laboratory view.";
PLFitView::usage="PLFitView provides a visual pendulum laboratory view.";
PLFitExplorer::usage="PLFitExplorer provides a visual pendulum laboratory view.";
PLModelView::usage="PLModelView provides a visual pendulum laboratory view.";
PLModelExplorer::usage="PLModelExplorer provides a visual pendulum laboratory view.";
PLAmplitudeView::usage="PLAmplitudeView provides a visual pendulum laboratory view.";
PLAmplitudeExplorer::usage="PLAmplitudeExplorer provides a visual pendulum laboratory view.";
PLPrintView::usage="PLPrintView[expression] applies bilingual print typography.";
Begin["`Private`"];
$root=DirectoryName[DirectoryName[$InputFileName]];
PLRoot[]:=$root;
PLNotebookPath[]:=FileNameJoin[{$root,"Notebooks","Pendulum.nb"}];
PLOpenNotebook[]:=NotebookOpen[PLNotebookPath[]];
PLConfig[]:=Import[FileNameJoin[{$root,"data","experiment.json"}],"RawJSON"];
hash[path_]:=IntegerString[FileHash[path,"SHA256"],16,64];
PLInputHashes[]:=AssociationMap[hash[FileNameJoin[{$root,"data",#}]]&, {"experiment.json","data/measurements.csv","data/diameters.csv","data/provenance.json"}];
readTable[name_]:=Module[{t=Import[FileNameJoin[{$root,"data","data",name}],"CSV"]},AssociationThread[First[t],#]& /@ Rest[t]];
PLRawData[]:=Module[{c=PLConfig[],t=readTable["measurements.csv"],d=readTable["diameters.csv"],groups,values},
 If[Length[t]!=c["expected_runs"] c["repeats_per_run"]||Length[d]!=c["diameter_repeats"],Return[Failure["Count",<||>]]];
 If[Length[DeleteDuplicates[Lookup[t,{"run_id","repeat_id"}]]]!=Length[t]||Length[DeleteDuplicates[Lookup[d,"repeat_id"]]]!=Length[d],Return[Failure["Duplicate",<||>]]];
 values=Flatten[{Lookup[t,{"string_length_cm","elapsed_time_s"}],Lookup[d,"diameter_cm"]}];
 If[!AllTrue[values,NumericQ[#]&&TrueQ[#>0]&]||!AllTrue[Lookup[t,"oscillations"],#==c["oscillations"]&],Return[Failure["Values",<||>]]];
 groups=GatherBy[t,#["run_id"]&];
 If[Sort[Lookup[First /@ groups,"run_id"]]!=Range[c["expected_runs"]]||!AllTrue[groups,Length[#]==c["repeats_per_run"]&&Length[DeleteDuplicates[Lookup[#,"string_length_cm"]]]==1&&Sort[Lookup[#,"repeat_id"]]==Range[c["repeats_per_run"]]&],Return[Failure["Groups",<||>]]];
 <|"timing"->t,"diameters"->d|>
];
PLFitLine[x_List,y_List]:=Module[{dx,dy,sxx,k,b,res,se},
 If[Length[x]!=Length[y]||Length[x]<3||!AllTrue[Join[x,y],NumberQ[#]&&TrueQ[Im[#]==0]&],Return[Failure["FitInput",<||>]]];
 dx=x-Mean[x];dy=y-Mean[y];sxx=dx.dx;
 If[!TrueQ[sxx>0],Return[Failure["FitLength",<||>]]];
 k=(dx.dy)/sxx;b=Mean[y]-k Mean[x];res=y-(k x+b);se=Sqrt[(res.res)/(Length[x]-2)/sxx];
 <|"slope"->k,"intercept"->b,"slope_se"->se,"r_squared"->If[dy.dy==0,1.,1-(res.res)/(dy.dy)],"residuals"->res|>
];
PLPeriod[a_?NumericQ,l_?NumericQ,g_?NumericQ]:=If[Abs[a]<Pi&&l>0&&g>0,4 Sqrt[l/g] EllipticK[Sin[a/2]^2],Failure["PeriodDomain",<||>]];
PLSimulate[c_Association,g_?NumericQ]:=Module[{s=c["simulation"],l,a,theta,t,sol,times,angles,velocities,energy,cross,period,linear},
 l=s["length_m"];a=N[s["initial_angle_deg"] Degree];
 If[s["initial_angular_velocity_rad_s"]!=0||!TrueQ[0<Abs[a]<Pi]||!TrueQ[l>0&&g>0],Return[Failure["SimulationInput",<||>]]];
 sol=NDSolveValue[{theta''[t]+g/l Sin[theta[t]]==0,theta[0]==a,theta'[0]==0},theta,{t,0,s["duration_s"]},AccuracyGoal->11,PrecisionGoal->10,MaxStepSize->.02];
 times=N[Subdivide[0,s["duration_s"],s["samples"]-1]];angles=sol /@ times;velocities=sol' /@ times;
 energy=.5 l^2 velocities^2+g l (1-Cos[angles]);linear=a Cos[Sqrt[g/l] times];
 cross=t/.FindRoot[sol[t]==0,{t,PLPeriod[a,l,g]/4}];period=4 cross;
 <|"time_s"->times,"angle_rad"->angles,"angular_velocity_rad_s"->velocities,"linear_angle_rad"->linear,"period_ode_s"->period,"period_exact_s"->PLPeriod[a,l,g],"relative_energy_drift"->Max[Abs[energy-First[energy]]]/First[energy]|>
];
metric[v_,u_]:=<|"value"->N[v],"unit"->u|>;
PLAnalyze[]:=Module[{c=PLConfig[],raw=PLRawData[],t,d,dm,du,p,fit,g,gu,metrics,l,t0,scan,s,a,tt,tm,tu,period,pu,eff},
 If[FailureQ[raw],Return[raw]];t=raw["timing"];d=N[Lookup[raw["diameters"],"diameter_cm"]/100];dm=Mean[d];du=StandardDeviation[d]/Sqrt[Length[d]];
 p=Table[
   s=Select[t,#["run_id"]==run&];tt=N[Lookup[s,"elapsed_time_s"]];tm=Mean[tt];tu=StandardDeviation[tt]/Sqrt[Length[tt]];
   l=First[s]["string_length_cm"]/100;eff=l+dm/2;period=tm/c["oscillations"];pu=tu/c["oscillations"];
   <|"run_id"->run,"string_length_m"->N[l],"effective_length_m"->eff,"mean_time_s"->tm,"time_mean_u_a_s"->tu,"period_s"->period,"period_u_a_s"->pu,"period_squared_s2"->period^2,"period_squared_u_a_s2"->2 period pu,"gravity_individual_m_s2"->4 Pi^2 eff/period^2|>,{run,c["expected_runs"]}];
 fit=PLFitLine[Lookup[p,"effective_length_m"],Lookup[p,"period_squared_s2"]];g=4 Pi^2/fit["slope"];gu=g fit["slope_se"]/fit["slope"];
 metrics=<|"diameter_mean"->metric[dm,"m"],"diameter_mean_u_a"->metric[du,"m"],"slope"->metric[fit["slope"],"s^2/m"],"intercept"->metric[fit["intercept"],"s^2"],"slope_standard_error"->metric[fit["slope_se"],"s^2/m"],"gravity_fit"->metric[g,"m/s^2"],"gravity_regression_standard_error"->metric[gu,"m/s^2"],"gravity_individual_mean"->metric[Mean[Lookup[p,"gravity_individual_m_s2"]],"m/s^2"],"r_squared"->metric[fit["r_squared"],"1"],"reference_relative_difference_pct"->metric[100(g/c["reference_gravity_m_s2"]-1),"%"]|>;
 l=c["simulation"]["length_m"];t0=2 Pi Sqrt[l/g];
 scan=Table[period=PLPeriod[N[a Degree],l,g];<|"angle_deg"->a,"period_s"->period,"linear_period_s"->t0,"period_excess_pct"->100(period/t0-1),"gravity_bias_pct"->100((t0/period)^2-1)|>,{a,c["simulation"]["scan_angles_deg"]}];
 <|"schema_version"->1,"experiment_id"->c["experiment_id"],"engine"->"wolfram","input_hashes"->PLInputHashes[],"code_hash"->hash[FileNameJoin[{$root,"Kernel","PendulumLab.wl"}]],"environment"-><|"wolfram"->$Version|>,"uncertainty_scope"->c["analysis"]["uncertainty_scope"],"model_parameters"->c["simulation"],"metrics"->metrics,"processed"->p,"residuals_s2"->fit["residuals"],"simulation"->PLSimulate[c,g],"amplitude_scan"->scan|>
];
$blue=GrayLevel[.1];$gold=GrayLevel[.4];
$ink=Black;$muted=GrayLevel[.25];
$style={FontFamily->"Times New Roman",FontSize->14,FontColor->$ink};
table[headers_,rows_]:=Grid[Prepend[rows/.v_Real:>NumberForm[v,8],headers],Frame->All,Alignment->Left,Spacings->{1,.7},Background->White,BaseStyle->{FontFamily->"Times New Roman",FontSize->14}];
PLTable["timing"]:=table[{"\:7ec4\:53f7","\:91cd\:590d","\:6446\:7ebf\:957f / cm","\:5168\:632f\:52a8\:6b21\:6570","\:8ba1\:65f6 / s"},Lookup[PLRawData[]["timing"],{"run_id","repeat_id","string_length_cm","oscillations","elapsed_time_s"}]];
PLTable["diameters"]:=table[{"\:91cd\:590d","\:7403\:76f4\:5f84 / cm"},Lookup[PLRawData[]["diameters"],{"repeat_id","diameter_cm"}]];
PLTable["processed"]:=With[{p=PLAnalyze[]["processed"]},Column[{
 table[{"\:7ec4\:53f7","\:6709\:6548\:6446\:957f / m","\:5e73\:5747\:8ba1\:65f6 / s","\:5468\:671f / s","\:5468\:671f\:5e73\:65b9 / s\:00b2","\:9010\:7ec4 g / (m/s\:00b2)"},Lookup[p,{"run_id","effective_length_m","mean_time_s","period_s","period_squared_s2","gravity_individual_m_s2"}]],
 table[{"\:7ec4\:53f7",DisplayForm[RowBox[{SubscriptBox["u","A"],"(",OverscriptBox["t","_"],") / s"}]],DisplayForm[RowBox[{SubscriptBox["u","A"],"(T) / s"}]],DisplayForm[RowBox[{SubscriptBox["u","A"],"(",SuperscriptBox["T","2"],") / ",SuperscriptBox["s","2"]}]]},Lookup[p,{"run_id","time_mean_u_a_s","period_u_a_s","period_squared_u_a_s2"}]]},Spacings->1.5]];
PLTable["metrics"]:=Module[{m=PLAnalyze[]["metrics"],keys,labels},keys=Keys[m];labels={"\:5e73\:5747\:7403\:76f4\:5f84","\:76f4\:5f84\:5747\:503cA\:7c7b\:4e0d\:786e\:5b9a\:5ea6","\:62df\:5408\:659c\:7387","\:62df\:5408\:622a\:8ddd","\:659c\:7387\:56de\:5f52\:6807\:51c6\:8bef","\:62df\:5408\:91cd\:529b\:52a0\:901f\:5ea6","\:91cd\:529b\:56de\:5f52\:6807\:51c6\:8bef","\:9010\:7ec4\:91cd\:529b\:5e73\:5747\:503c","\:51b3\:5b9a\:7cfb\:6570","\:76f8\:5bf9\:6bd4\:8f83\:503c\:7684\:5dee\:5f02"};table[{"\:6307\:6807","\:6570\:503c","\:5355\:4f4d"},MapThread[{#1,m[#2]["value"],m[#2]["unit"]}&,{labels,keys}]]];
PLTable["amplitude_scan"]:=table[{"\:6446\:89d2 / \:00b0","\:975e\:7ebf\:6027\:5468\:671f / s","\:5c0f\:89d2\:5ea6\:5468\:671f / s","\:5468\:671f\:589e\:91cf / %","\:91cd\:529b\:4f30\:8ba1\:504f\:5dee / %"},Lookup[PLAnalyze[]["amplitude_scan"],{"angle_deg","period_s","linear_period_s","period_excess_pct","gravity_bias_pct"}]];
PLFitPlot[]:=Module[{r=PLAnalyze[],p,x,y,k,b,fit,res},p=r["processed"];x=Lookup[p,"effective_length_m"];y=Lookup[p,"period_squared_s2"];k=r["metrics"]["slope"]["value"];b=r["metrics"]["intercept"]["value"];
 fit=Show[ListPlot[Transpose[{x,MapThread[Around,{y,Lookup[p,"period_squared_u_a_s2"]}]}],PlotStyle->$blue,PlotMarkers->{Graphics[{EdgeForm[Directive[Black,AbsoluteThickness[1.2]]],White,Disk[]}],9}],Plot[k z+b,{z,Min[x]-.02,Max[x]+.02},PlotStyle->$gold],Frame->{{True,False},{True,False}},FrameStyle->Directive[Black,Thin],FrameTicksStyle->Directive[Black,13],LabelStyle->Directive[Black,14],GridLines->{None,Automatic},GridLinesStyle->Directive[GrayLevel[0.91],Thin],Axes->False,FrameLabel->{Row[{"\:6709\:6548\:6446\:957f ",DisplayForm[SuperscriptBox[StyleBox["L",FontSlant->"Italic"],"\[Prime]"]]," / m"}],Row[{DisplayForm[SuperscriptBox[StyleBox["T",FontSlant->"Italic"],"2"]]," / ",Superscript["s",2]}]},BaseStyle->$style,ImageSize->760,ImagePadding->{{85,20},{55,35}}];
 res=ListPlot[Transpose[{x,MapThread[Around,{1000 r["residuals_s2"],1000 Lookup[p,"period_squared_u_a_s2"]}]}],Frame->{{True,False},{True,False}},FrameStyle->Directive[Black,Thin],FrameTicksStyle->Directive[Black,13],LabelStyle->Directive[Black,14],GridLines->{None,Automatic},GridLinesStyle->Directive[GrayLevel[0.91],Thin],Axes->False,PlotStyle->$blue,PlotMarkers->{Graphics[{EdgeForm[Directive[Black,AbsoluteThickness[1.2]]],White,Disk[]}],9},FrameLabel->{"\:6709\:6548\:6446\:957f L\:2032 / m",Row[{"\:6b8b\:5dee / (",Superscript[10,-3]," ",Superscript["s",2],")"}]},BaseStyle->$style,ImageSize->760,ImagePadding->{{85,20},{55,35}}];Column[{fit,res},Alignment->Center]];
PLTrajectoryPlot[]:=Module[{s=PLAnalyze[]["simulation"],t},t=s["time_s"];
 Column[{ListLinePlot[{Transpose[{t,s["angle_rad"]/Degree}],Transpose[{t,s["linear_angle_rad"]/Degree}]},Frame->{{True,False},{True,False}},FrameStyle->Directive[Black,Thin],FrameTicksStyle->Directive[Black,13],LabelStyle->Directive[Black,14],GridLines->{None,Automatic},GridLinesStyle->Directive[GrayLevel[0.91],Thin],Axes->False,FrameLabel->{"\:65f6\:95f4 / s","\:6446\:89d2 / \:00b0"},PlotLegends->{"\:975e\:7ebf\:6027\:6570\:503c\:89e3","\:5c0f\:89d2\:5ea6\:89e3\:6790\:89e3"},PlotStyle->{$blue,Directive[$gold,Dashed]},BaseStyle->$style,ImageSize->760,ImagePadding->{{85,20},{55,35}}],ListLinePlot[Transpose[{t,s["angular_velocity_rad_s"]}],Frame->{{True,False},{True,False}},FrameStyle->Directive[Black,Thin],FrameTicksStyle->Directive[Black,13],LabelStyle->Directive[Black,14],GridLines->{None,Automatic},GridLinesStyle->Directive[GrayLevel[0.91],Thin],Axes->False,FrameLabel->{"\:65f6\:95f4 / s","\:89d2\:901f\:5ea6 / (rad/s)"},PlotStyle->$blue,BaseStyle->$style,ImageSize->760,ImagePadding->{{85,20},{55,35}}]}]];
PLScanPlot[]:=Module[{s=PLAnalyze[]["amplitude_scan"]},GraphicsRow[{
 ListLinePlot[Transpose[{Lookup[s,"angle_deg"],Lookup[s,"period_excess_pct"]}],Frame->{{True,False},{True,False}},FrameStyle->Directive[Black,Thin],FrameTicksStyle->Directive[Black,13],LabelStyle->Directive[Black,14],GridLines->{None,Automatic},GridLinesStyle->Directive[GrayLevel[0.91],Thin],Axes->False,FrameLabel->{"\:521d\:59cb\:6446\:89d2 / \:00b0","\:5468\:671f\:589e\:91cf / %"},PlotStyle->$blue,PlotMarkers->{Graphics[{EdgeForm[Directive[Black,AbsoluteThickness[1.2]]],White,Disk[]}],9},BaseStyle->$style],
 ListLinePlot[Transpose[{Lookup[s,"angle_deg"],Lookup[s,"gravity_bias_pct"]}],Frame->{{True,False},{True,False}},FrameStyle->Directive[Black,Thin],FrameTicksStyle->Directive[Black,13],LabelStyle->Directive[Black,14],GridLines->{None,Automatic},GridLinesStyle->Directive[GrayLevel[0.91],Thin],Axes->False,FrameLabel->{"\:521d\:59cb\:6446\:89d2 / \:00b0","\:91cd\:529b\:4f30\:8ba1\:504f\:5dee / %"},PlotStyle->$gold,PlotMarkers->{Graphics[{EdgeForm[Directive[Black,AbsoluteThickness[1.2]]],White,Disk[]}],9},BaseStyle->$style]},ImageSize->780]];
PLExplorer[]:=With[{grav=PLAnalyze[]["metrics"]["gravity_fit"]["value"]},Manipulate[Module[{f,z,t},f=NDSolveValue[{z''[t]+grav/len Sin[z[t]]==0,z[0]==angle Degree,z'[0]==0},z,{t,0,10}];Plot[{f[t]/Degree,angle Cos[Sqrt[grav/len]t]},{t,0,10},Frame->{{True,False},{True,False}},FrameStyle->Directive[Black,Thin],FrameTicksStyle->Directive[Black,13],LabelStyle->Directive[Black,14],GridLines->{None,Automatic},GridLinesStyle->Directive[GrayLevel[0.91],Thin],Axes->False,FrameLabel->{"\:65f6\:95f4 / s","\:6446\:89d2 / \:00b0"},PlotLegends->{"\:975e\:7ebf\:6027","\:5c0f\:89d2\:5ea6"},PlotStyle->{$blue,Directive[$gold,Dashed]},BaseStyle->$style,ImageSize->760,ImagePadding->{{85,20},{55,35}}]],{{angle,20,mixedText["\:521d\:59cb\:6446\:89d2 / \:00b0"]},1,60,1},{{len,1,mixedText["\:6446\:957f / m"]},.2,2,.1},AppearanceElements->None,Paneled->False,ControlPlacement->Top,SaveDefinitions->False,Initialization:>(Needs["PendulumLab`"])]];
PLSymbolicDerivation[]:=Block[{k,g,u},Module[{solution,propagation,expressions},
 solution=g/.First[Solve[k==4 Pi^2/g,g]];
 propagation=Refine[Abs[D[solution,k]],k>0];
 expressions={g==solution,Subscript[u,g]==propagation Subscript[u,k]};
 Column[(DisplayForm[ToBoxes[#,TraditionalForm]/.t_String:>StringReplace[t,"PendulumLab`Private`"->""]]& /@ expressions),BaseStyle->{FontFamily->"Times New Roman",FontSize->18}]
]];
PLSummary[]:=With[{m=PLAnalyze[]["metrics"]},Grid[{
 {Style["\:62df\:5408\:91cd\:529b\:52a0\:901f\:5ea6",13,Gray],Style["\:56de\:5f52\:6807\:51c6\:8bef",13,Gray],Style["\:89c2\:6d4b\:8bbe\:8ba1",13,Gray]},
 {Style[Row[{NumberForm[m["gravity_fit"]["value"],{9,6}]," m/s\:00b2"}],25,$blue],Style[Row[{NumberForm[m["gravity_regression_standard_error"]["value"],{8,6}]," m/s\:00b2"}],23,$blue],Style["6 \:7ec4 \:00d7 3 \:6b21",23,$blue]}},
 Spacings->{3,1.2},Alignment->Left,Background->White,BaseStyle->$style]];
PLMeasurementView[run_Integer:0]:=Module[{raw=PLRawData[]["timing"],groups,series},
 groups=If[run==0,Range[6],{run}];
 series=Table[With[{v=N[Lookup[Select[raw,#["run_id"]==i&],"elapsed_time_s"]]},Transpose[{Range[3],1000(v-Mean[v])}]],{i,groups}];
 ListLinePlot[series,Frame->{{True,False},{True,False}},FrameStyle->Directive[Black,Thin],FrameTicksStyle->Directive[Black,13],LabelStyle->Directive[Black,14],GridLines->{None,Automatic},GridLinesStyle->Directive[GrayLevel[0.91],Thin],Axes->False,FrameLabel->{"\:91cd\:590d\:6d4b\:91cf\:5e8f\:53f7","\:8ba1\:65f6\:51cf\:53bb\:672c\:7ec4\:5747\:503c / ms"},PlotMarkers->{Graphics[{EdgeForm[Directive[Black,AbsoluteThickness[1.2]]],White,Disk[]}],9},
 PlotStyle->Take[{Directive[Black],Directive[GrayLevel[.25],Dashed],Directive[GrayLevel[.4],Dotted],Directive[Black,DotDashed],Directive[GrayLevel[.3],Dashed],Directive[GrayLevel[.5],Dotted]},Length[groups]],PlotLegends->("\:7b2c "<>ToString[#]<>" \:7ec4"& /@ groups),PlotRange->All,ImageSize->750,BaseStyle->$style]];
PLMeasurementExplorer[]:=Manipulate[PLMeasurementView[run],{{run,0,mixedText["\:67e5\:770b\:6d4b\:91cf\:7ec4"]},Prepend[Table[i->("\:7b2c "<>ToString[i]<>" \:7ec4"),{i,6}],0->"\:5168\:90e8\:516d\:7ec4"],ControlType->PopupMenu},AppearanceElements->None,Paneled->False,ControlPlacement->Top,SaveDefinitions->False,Initialization:>(Needs["PendulumLab`"])];
PLFitView[omit_Integer:0]:=Module[{p=PLAnalyze[]["processed"],x,y,f,k,b,err,g,plot,res},
 If[omit>0,p=Select[p,#["run_id"]!=omit&]];x=Lookup[p,"effective_length_m"];y=Lookup[p,"period_squared_s2"];err=Lookup[p,"period_squared_u_a_s2"];
 f=PLFitLine[x,y];k=f["slope"];b=f["intercept"];g=4 Pi^2/k;
 plot=Show[ListPlot[Transpose[{x,MapThread[Around,{y,err}]}],PlotStyle->$blue,PlotMarkers->{Graphics[{EdgeForm[Directive[Black,AbsoluteThickness[1.2]]],White,Disk[]}],9}],
 Plot[k z+b,{z,.49,1.04},PlotStyle->$gold],Frame->{{True,False},{True,False}},FrameStyle->Directive[Black,Thin],FrameTicksStyle->Directive[Black,13],LabelStyle->Directive[Black,14],GridLines->{None,Automatic},GridLinesStyle->Directive[GrayLevel[0.91],Thin],Axes->False,FrameLabel->{Row[{"\:6709\:6548\:6446\:957f ",DisplayForm[SuperscriptBox[StyleBox["L",FontSlant->"Italic"],"\[Prime]"]]," / m"}],Row[{DisplayForm[SuperscriptBox[StyleBox["T",FontSlant->"Italic"],"2"]]," / ",Superscript["s",2]}]},ImageSize->760,ImagePadding->{{85,20},{55,35}},BaseStyle->$style];
 res=ListPlot[Transpose[{x,MapThread[Around,{1000 f["residuals"],1000 err}]}],Frame->{{True,False},{True,False}},FrameStyle->Directive[Black,Thin],FrameTicksStyle->Directive[Black,13],LabelStyle->Directive[Black,14],GridLines->{None,Automatic},GridLinesStyle->Directive[GrayLevel[0.91],Thin],Axes->False,
 PlotStyle->$blue,PlotMarkers->{Graphics[{EdgeForm[Directive[Black,AbsoluteThickness[1.2]]],White,Disk[]}],9},FrameLabel->{"\:6709\:6548\:6446\:957f L\:2032 / m",Row[{"\:6b8b\:5dee / (",Superscript[10,-3]," ",Superscript["s",2],")"}]},ImageSize->760,ImagePadding->{{85,20},{55,35}},AspectRatio->.28,BaseStyle->$style];
 Column[{Style[Row[{"g = ",NumberForm[g,{9,6}]," m/s\:00b2    k = ",NumberForm[k,{9,6}]," s\:00b2/m"}],19,$blue],plot,res}]];
PLFitExplorer[]:=Manipulate[PLFitView[omit],{{omit,0,mixedText["\:654f\:611f\:6027\:63a2\:7d22"]},Prepend[Table[i->("\:6682\:4e0d\:7eb3\:5165\:7b2c "<>ToString[i]<>" \:7ec4"),{i,6}],0->"\:5168\:90e8\:6570\:636e"],ControlType->PopupMenu},AppearanceElements->None,Paneled->False,ControlPlacement->Top,SaveDefinitions->False,Initialization:>(Needs["PendulumLab`"])];
modelSolution[a_?NumericQ,l_?NumericQ,g_?NumericQ]:=modelSolution[a,l,g]=Module[{z,t},
 NDSolveValue[{z''[t]+g/l Sin[z[t]]==0,z[0]==a Degree,z'[0]==0},z,{t,0,10},AccuracyGoal->10,PrecisionGoal->9]];
PLModelView[a_?NumericQ,l_?NumericQ,time_?NumericQ,linear_:True]:=Module[{g=PLAnalyze[]["metrics"]["gravity_fit"]["value"],f,t,pos,motion,angle,velocity,phase,period},
 f=modelSolution[a,l,g];pos={l Sin[f[time]],-l Cos[f[time]]};period=PLPeriod[a Degree,l,g];
 motion=Graphics[{
 {GrayLevel[0.54],Rectangle[{-.24l,.02l},{.24l,.07l}]},
 {GrayLevel[0.687],Thin,Table[Line[{{q l,.07l},{(q+.05)l,.13l}}],{q,-.24,.19,.05}]},
 {GrayLevel[0.693],Dashed,Line[{{0,0},{0,-1.1l}}]},
 {$ink,AbsoluteThickness[2.2],Line[{{0,0},pos}],Disk[{0,0},.022l]},
 {$blue,Disk[pos,.065l],Lighter[$blue,.55],Disk[pos+{-.018l,.020l},.016l]},
 {GrayLevel[0.693],Thin,Line[{{-.58l,0},{-.58l,-l}}],Line[{{-.63l,0},{-.53l,0}}],Line[{{-.63l,-l},{-.53l,-l}}]},
 Text[Style[Row[{"\:2113 = ",NumberForm[l,{3,1}]," m"}],11,$muted],{-.75l,-.5l}],
 Text[Style["\:60ac\:70b9 O",11,$muted],{0,.22l}],
 Text[Style["\:5e73\:8861\:4f4d\:7f6e",11,$muted],{0,-1.19l}]
 },PlotRange->{{-.95l,.95l},{-1.3l,.33l}},ImageSize->{360,270},ImagePadding->{{25,25},{20,28}},
 BaseStyle->$style];

 angle=Plot[Evaluate[If[TrueQ[linear],{f[t]/Degree,a Cos[Sqrt[g/l]t]},f[t]/Degree]],{t,0,10},
 Frame->{{True,False},{True,False}},FrameStyle->Directive[Black,Thin],FrameTicksStyle->Directive[Black,13],LabelStyle->Directive[Black,14],GridLines->{None,Automatic},GridLinesStyle->Directive[GrayLevel[0.91],Thin],Axes->False,FrameLabel->{"\:65f6\:95f4 / s","\:6446\:89d2 / \:00b0"},PlotStyle->{$blue,Directive[$gold,Dashed]},
 ImageSize->{360,270},ImagePadding->{{62,18},{45,28}},AspectRatio->.65,BaseStyle->$style];
 velocity=Plot[f'[t],{t,0,10},Frame->{{True,False},{True,False}},FrameStyle->Directive[Black,Thin],FrameTicksStyle->Directive[Black,13],LabelStyle->Directive[Black,14],GridLines->{None,Automatic},GridLinesStyle->Directive[GrayLevel[0.91],Thin],Axes->False,FrameLabel->{"\:65f6\:95f4 / s","\:89d2\:901f\:5ea6 / (rad/s)"},
 PlotStyle->$blue,ImageSize->{360,270},ImagePadding->{{62,18},{45,28}},AspectRatio->.65,BaseStyle->$style];
 phase=ParametricPlot[{f[t]/Degree,f'[t]},{t,0,10},Frame->{{True,False},{True,False}},FrameStyle->Directive[Black,Thin],FrameTicksStyle->Directive[Black,13],LabelStyle->Directive[Black,14],GridLines->{None,Automatic},GridLinesStyle->Directive[GrayLevel[0.91],Thin],Axes->False,
 FrameLabel->{"\:6446\:89d2 / \:00b0","\:89d2\:901f\:5ea6 / (rad/s)"},PlotStyle->$blue,Epilog->{$gold,PointSize[.025],Point[{f[time]/Degree,f'[time]}]},ImageSize->{360,270},ImagePadding->{{62,18},{45,28}},AspectRatio->.65,BaseStyle->$style];
 Column[{Style[Row[{"\:975e\:7ebf\:6027\:5468\:671f ",NumberForm[period,{8,5}]," s    \:5468\:671f\:589e\:91cf ",NumberForm[100(period/(2 Pi Sqrt[l/g])-1),{6,3}]," %"}],18,$blue],
 GraphicsGrid[{{motion,angle},{phase,velocity}},ImageSize->800,Spacings->{24,22}]}]];
PLModelExplorer[]:=Manipulate[PLModelView[angle,len,time,linear],
 {{angle,20,mixedText["\:521d\:59cb\:6446\:89d2 / \:00b0"]},1,60,1,Appearance->"Labeled"},
 {{len,1.,mixedText["\:6446\:957f / m"]},.5,1.5,.1,Appearance->"Labeled"},
 {{time,0.,mixedText["\:65f6\:95f4 / s"]},0.,10.,.05,ControlType->Animator,AnimationRunning->False,AnimationRate->.7},
 {{linear,True,mixedText["\:663e\:793a\:5c0f\:89d2\:5ea6\:89e3"]},{True,False}},TrackedSymbols:>{angle,len,time,linear},
 AppearanceElements->None,Paneled->False,ControlPlacement->Top,SaveDefinitions->False,Initialization:>(Needs["PendulumLab`"]),SynchronousUpdating->False];
PLAmplitudeView[a_?NumericQ]:=Module[{g=PLAnalyze[]["metrics"]["gravity_fit"]["value"],l=PLConfig[]["simulation"]["length_m"],t0,ex,bias,z},
 t0=2 Pi Sqrt[l/g];ex[z_?NumericQ]:=100(PLPeriod[z Degree,l,g]/t0-1);bias[z_?NumericQ]:=100((t0/PLPeriod[z Degree,l,g])^2-1);
 Column[{Style[Row[{a,"\:00b0\:ff1a\:5468\:671f\:589e\:91cf ",NumberForm[ex[a],{6,3}]," %\:ff1bg \:504f\:5dee ",NumberForm[bias[a],{6,3}]," %"}],18,$blue],
 GraphicsRow[{Plot[ex[z],{z,1,60},Frame->{{True,False},{True,False}},FrameStyle->Directive[Black,Thin],FrameTicksStyle->Directive[Black,13],LabelStyle->Directive[Black,14],GridLines->{None,Automatic},GridLinesStyle->Directive[GrayLevel[0.91],Thin],Axes->False,FrameLabel->{"\:521d\:59cb\:6446\:89d2 / \:00b0","\:5468\:671f\:589e\:91cf / %"},PlotStyle->$blue,Epilog->{$blue,PointSize[.025],Point[{a,ex[a]}]},BaseStyle->$style],
 Plot[bias[z],{z,1,60},Frame->{{True,False},{True,False}},FrameStyle->Directive[Black,Thin],FrameTicksStyle->Directive[Black,13],LabelStyle->Directive[Black,14],GridLines->{None,Automatic},GridLinesStyle->Directive[GrayLevel[0.91],Thin],Axes->False,FrameLabel->{"\:521d\:59cb\:6446\:89d2 / \:00b0","\:91cd\:529b\:4f30\:8ba1\:504f\:5dee / %"},PlotStyle->$gold,Epilog->{$gold,PointSize[.025],Point[{a,bias[a]}]},BaseStyle->$style]},ImageSize->800]}]];
PLAmplitudeExplorer[]:=Manipulate[PLAmplitudeView[a],{{a,20,mixedText["\:521d\:59cb\:6446\:89d2 / \:00b0"]},1,60,1,Appearance->"Labeled"},AppearanceElements->None,Paneled->False,ControlPlacement->Top,SaveDefinitions->False,Initialization:>(Needs["PendulumLab`"])];

mixedText[s_String]:=Row[Map[Style[StringJoin[#],FontFamily->If[First[ToCharacterCode[First[#]]]>=16^^2E80,"SimSun","Times New Roman"]]&,SplitBy[Characters[s],First[ToCharacterCode[#]]>=16^^2E80&]]];
mixedText/:MakeBoxes[mixedText[s_String],fmt_]:=RowBox[Map[StyleBox[StringJoin[#],FontFamily->If[First[ToCharacterCode[First[#]]]>=16^^2E80,"SimSun","Times New Roman"]]&,SplitBy[Characters[s],First[ToCharacterCode[#]]>=16^^2E80&]]];
PLPrintView[v_]:=v/.s_String/;StringContainsQ[s,RegularExpression["[\:4e00-\:9fa5]"]]:>mixedText[s];
Scan[(DownValues[#]=DownValues[#]/.HoldPattern[RuleDelayed[lhs_,rhs_]]:>RuleDelayed[lhs,PLPrintView[rhs]])&,
 {PLFitPlot,PLTrajectoryPlot,PLScanPlot,PLMeasurementView,PLFitView,PLModelView,PLAmplitudeView,PLTable}];

PLModelView[]:=PLModelView[20,1.,0.,True];
PLAmplitudeView[]:=PLAmplitudeView[20];

End[];
EndPackage[];
