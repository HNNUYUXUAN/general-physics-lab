(* Executed in RLCResonanceLab`Private`; canonical data paths are relative to dir. *)
halfPower[f_List,v_List]:=Module[{p,level,left,right,cross},
 p=First[Ordering[v,-1]];level=v[[p]]/Sqrt[2];
 cross[i_]:=f[[i]]+(level-v[[i]])(f[[i+1]]-f[[i]])/(v[[i+1]]-v[[i]]);
 left=cross[Last[Select[Range[p-1],v[[#]]<=level<=v[[#+1]]&]]];
 right=cross[First[Select[Range[p,Length[v]-1],v[[#+1]]<=level<=v[[#]]&]]];
 {f[[p]],v[[p]],left,right}];

compute[dir_]:=Module[{cfg,data,rv,metrics=<||>,tables=<||>,series=<||>,estimates={},voltageRows={},frequencyRows={},add,gid,cap,groupRows,f,theory,v,peak,vmax,f1,f2,band,q,stem,frequency,relative,part,start,stop,rows,ul,uc,asymmetry,xs},
 cfg=Import[FileNameJoin[{dir,"experiment.json"}],"RawJSON"];
 data=Rest[Import[FileNameJoin[{dir,"data","response.csv"}],"CSV"]];
 rv=Rest[Import[FileNameJoin[{dir,"data","resonance_voltages.csv"}],"CSV"]];
 add[k_,val_,unit_]:=AssociateTo[metrics,k-><|"value"->N[val],"unit"->unit|>];
 Do[
 gid=group["id"];cap=group["capacitance_F"];
 groupRows=Select[data,First[#]==gid&];f=N[groupRows[[All,2]]];
 theory=1/(2 Pi Sqrt[cfg["inductance_H"] cap]);add[gid<>"_f_theory",theory,"Hz"];
 Do[
 v=N[groupRows[[All,If[resistor=="R1",3,4]]]];
 {peak,vmax,f1,f2}=halfPower[f,v];band=f2-f1;q=peak/band;stem=gid<>"_"<>resistor;
 MapThread[add[stem<>"_"<>#1,#2,#3]&,
 {{"f_peak","U_peak","f_low","f_high","bandwidth","Q_bandwidth"},{peak,vmax,f1,f2,band,q},{"Hz","V","Hz","Hz","Hz","1"}}];
 AppendTo[estimates,{gid,resistor,peak,Round[vmax,.001],Round[f1,.001],Round[f2,.001],Round[band,.001],Round[q,.001]}];
 AssociateTo[series,stem-><|"x"->f,"y"->v,"x_label"->"\:9891\:7387 $f\\,/\\,\\mathrm{Hz}$","y_label"->("\:7535\:963b\:7535\:538b $U_{"<>resistor<>"}\\,/\\,\\mathrm{V}$"),"label"->gid<>" / "<>resistor|>];
 AssociateTo[series,stem<>"_normalized"-><|"x"->f,"y"->v/vmax,"x_label"->"\:9891\:7387 $f\\,/\\,\\mathrm{Hz}$","y_label"->"\:5f52\:4e00\:5316\:7535\:538b $U_R/U_{R,\\max}$","label"->gid<>" / "<>resistor|>],
 {resistor,{"R1","R2"}}];
 frequency=metrics[gid<>"_R1_f_peak"]["value"];relative=100(frequency-theory)/theory;
 add[gid<>"_relative_error_percent",relative,"%"];
 AppendTo[frequencyRows,{gid,cap 10^6,Round[theory,.001],frequency,Round[relative,.001]}];
 Do[
 {part,start,stop}=spec;
 rows={{"$f/\\mathrm{Hz}$"}~Join~Take[f,{start+1,stop}]};
 Do[AppendTo[rows,{"$U_{"<>resistor<>"}/\\mathrm{V}$"}~Join~N[Take[groupRows[[All,If[resistor=="R1",3,4]]],{start+1,stop}]]],{resistor,{"R1","R2"}}];
 AssociateTo[tables,gid<>"_"<>part-><|"headers"->Join[{"\:7269\:7406\:91cf"},ToString/@Range[start+1,stop]],"rows"->rows|>],
 {spec,If[gid=="C02",{{"a",0,10},{"b",10,20}},{{"a",0,Length[f]}}]}],
 {group,cfg["groups"]}];
 Do[
 {gid,resistor,ul,uc}=row;ul=N[ul];uc=N[uc];q=(ul+uc)/(2 cfg["source_voltage_nominal_V"]);
 add[gid<>"_"<>resistor<>"_Q_voltage",q,"1"];
 asymmetry=100 Abs[ul-uc]/((ul+uc)/2);add[gid<>"_"<>resistor<>"_voltage_asymmetry_percent",asymmetry,"%"];
 AppendTo[voltageRows,{gid,resistor,ul,uc,Round[q,.001],Round[asymmetry,.001]}],{row,rv}];
 AssociateTo[tables,"frequencies"-><|"headers"->{"\:7ec4\:522b","$C/\\mu\\mathrm{F}$","$f_{0,\\mathrm{th}}/\\mathrm{Hz}$","$f_{\\mathrm{peak}}/\\mathrm{Hz}$","\:76f8\:5bf9\:504f\:5dee / %"},"rows"->frequencyRows|>];
 AssociateTo[tables,"bandwidth"-><|"headers"->{"\:7ec4\:522b","\:7535\:963b\:8bbe\:7f6e","$f_{\\mathrm{peak}}/\\mathrm{Hz}$","$U_{R,\\max}/\\mathrm{V}$","$f_1/\\mathrm{Hz}$","$f_2/\\mathrm{Hz}$","$B/\\mathrm{Hz}$","$Q_B$"},"rows"->estimates|>];
 AssociateTo[tables,"voltage_ratio"-><|"headers"->{"\:7ec4\:522b","\:7535\:963b\:8bbe\:7f6e","$U_L/\\mathrm{V}$","$U_C/\\mathrm{V}$","$Q_U$","\:4e24\:7535\:538b\:76f8\:5bf9\:5dee / %"},"rows"->voltageRows|>];
 xs=N[Range[200,600]/400];
 Do[
 AssociateTo[series,"model_Q"<>ToString[q]-><|"x"->xs,"y"->(1/Sqrt[1+q^2(#-1/#)^2]&/@xs),"x_label"->"\:9891\:7387\:6bd4 $f/f_0$","y_label"->"\:5f52\:4e00\:5316\:7535\:6d41 $I/I_{\\max}$","label"->"\:7406\:60f3\:6a21\:578b Q = "<>ToString[q],"model"->True|>];
 add["model_Q"<>ToString[q]<>"_response_09",1/Sqrt[1+q^2(.9-1/.9)^2],"1"];add["model_Q"<>ToString[q]<>"_peak",1,"1"],
 {q,cfg["model"]["quality_factors"]}];
 <|"metrics"->metrics,"tables"->tables,"series"->series,"notes"->{"\:534a\:529f\:7387\:9891\:7387\:7531\:76f8\:90bb\:89c2\:6d4b\:70b9\:7ebf\:6027\:63d2\:503c\:ff0c\:672a\:62df\:5408\:6216\:8865\:9020\:89c2\:6d4b\:3002","\:7535\:538b\:6bd4\:54c1\:8d28\:56e0\:6570\:4ee5\:6e90\:7535\:538b\:7ea6 1 V \:4e3a\:6761\:4ef6\:ff1b\:4e0e\:5e26\:5bbd\:6cd5\:7684\:5dee\:5f02\:672a\:5f52\:56e0\:4e8e\:672a\:7ecf\:6d4b\:91cf\:7684\:5185\:963b\:3002"}|>];

explore["resonance",r_]:=Manipulate[Module[{f0=1/(2 Pi Sqrt[.1 c]),amp,phase},
 amp[f_]:=1/Sqrt[1+q^2(f/f0-f0/f)^2];
 phase[f_]:=-ArcTan[q(f/f0-f0/f)]/Degree;
 Column[{
 GraphicsRow[{
 Plot[amp[f],{f,.5 f0,1.5 f0},PlotStyle->Black,Frame->{{True,False},{True,False}},Axes->False,FrameLabel->{styled["\:9891\:7387 f / Hz"],styled["\:5f52\:4e00\:5316\:7535\:6d41 I / Imax"]},PlotRange->{0,1.05},GridLines->{None,{1/Sqrt[2]}},GridLinesStyle->Directive[GrayLevel[.8],Dashed],BaseStyle->{FontFamily->"Times New Roman",FontSize->16}],
 Plot[phase[f],{f,.5 f0,1.5 f0},PlotStyle->Black,Frame->{{True,False},{True,False}},Axes->False,FrameLabel->{styled["\:9891\:7387 f / Hz"],styled["\:7535\:6d41\:76f8\:4f4d \:03c6 / \:00b0"]},PlotRange->{-90,90},BaseStyle->{FontFamily->"Times New Roman",FontSize->16}]},ImageSize->1000],
 Style[Row[{styled["f\:2080 = "],NumberForm[f0,{8,3}],styled[" Hz\:ff1bB = "],NumberForm[f0/q,{8,3}],styled[" Hz"]}],FontFamily->"Times New Roman",FontSize->16]},Alignment->Center]],
 {{q,8,styled["\:6a21\:578b\:54c1\:8d28\:56e0\:6570 Q"]},2,25,.5},{{c,.2*10^-6,styled["\:7535\:5bb9 C"]},{.2*10^-6->Pane[Style["0.2 \:03bcF",FontFamily->"Times New Roman",FontSize->14],{72,24},Alignment->Center],.1*10^-6->Pane[Style["0.1 \:03bcF",FontFamily->"Times New Roman",FontSize->14],{72,24},Alignment->Center]}},SaveDefinitions->True];
