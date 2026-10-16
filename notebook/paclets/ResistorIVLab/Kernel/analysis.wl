fitLine[x_List,y_List]:=Module[{xm=Mean[x],ym=Mean[y],a,b,res,sse,sst},a=Total[(x-xm)(y-ym)]/Total[(x-xm)^2];b=ym-a xm;res=y-a x-b;sse=Total[res^2];sst=Total[(y-ym)^2];{a,b,If[sst==0,1,1-sse/sst],Sqrt[sse/Length[x]]}];

compute[dir_]:=Module[{cfg,data,diode,metrics=<||>,tables=<||>,series=<||>,original={},derived={},fitrows={},add,key,items,u,i,resistance,avg,origin,slope,intercept,r2,rmse,title,beta,lnis,diodeR2,x},
 cfg=Import[FileNameJoin[{dir,"experiment.json"}],"RawJSON"];
 data=Rest[Import[FileNameJoin[{dir,"data","resistors.csv"}],"CSV"]];
 diode=Rest[Import[FileNameJoin[{dir,"data","diode.csv"}],"CSV"]];
 add[k_,v_,unit_,label_]:=AssociateTo[metrics,k-><|"value"->N[v],"unit"->unit,"label"->label|>];
 Do[
 key=connection<>"_"<>resistor;items=Select[data,#[[1]]==connection&&#[[2]]==resistor&];
 u=N[items[[All,3]]];i=N[items[[All,4]]]/1000;resistance=u/i;avg=Mean[resistance];origin=Total[i u]/Total[i^2];
 {slope,intercept,r2,rmse}=fitLine[i,u];title=If[connection=="internal","\:5185\:63a5\:6cd5","\:5916\:63a5\:6cd5"];
 MapThread[add[key<>"_"<>#1,#2,#3,title<>" "<>resistor<>" "<>#4]&,
 {{"R_mean","R_origin","R_slope","U_intercept","fit_R2","fit_rmse"},{avg,origin,slope,intercept,r2,rmse},{"\:03a9","\:03a9","\:03a9","V","1","V"},{"\:9010\:70b9\:7535\:963b\:5747\:503c","\:8fc7\:539f\:70b9\:62df\:5408\:7535\:963b","\:542b\:622a\:8ddd\:62df\:5408\:7535\:963b","\:7535\:538b\:62df\:5408\:622a\:8ddd","\:62df\:5408\:51b3\:5b9a\:7cfb\:6570","\:7535\:538b\:62df\:5408\:5747\:65b9\:6839\:6b8b\:5dee"}}];
 AppendTo[original,Join[{title,resistor,"$U/\\mathrm{V}$"},u,{"2 V"}]];
 AppendTo[original,Join[{"","","$I/\\mathrm{mA}$"},i 1000,{cfg["current_ranges_mA"][resistor]}]];
 AppendTo[derived,Join[{title,resistor},Round[resistance,.001],{Round[avg,.001]}]];
 AppendTo[fitrows,{title,resistor,Round[avg,.001],Round[origin,.001],Round[slope,.001],Round[intercept,.000001],Round[r2,.000001]}];
 AssociateTo[series,key-><|"x"->i 1000,"y"->u,"x_label"->"\:7535\:6d41 $I\\,/\\,\\mathrm{mA}$","y_label"->"\:7535\:538b $U\\,/\\,\\mathrm{V}$","label"->title<>" "<>resistor,"fit"->True|>],
 {connection,{"internal","external"}},{resistor,{"R1","R2"}}];
 u=N[diode[[All,1]]];i=N[diode[[All,2]]];
 add["diode_current_06",i[[6]],"mA","0.60 V\:65f6\:8bb0\:5f55\:7535\:6d41"];
 add["diode_current_065",i[[7]],"mA","0.65 V\:65f6\:8bb0\:5f55\:7535\:6d41\:ff08\:91cf\:7a0b\:5f85\:6838\:ff09"];
 add["diode_gain_04_06",i[[6]]/i[[3]],"1","0.40\:20130.60 V\:7535\:6d41\:589e\:5927\:500d\:6570"];
 {beta,lnis,diodeR2,rmse}=fitLine[u[[3;;6]],Log[i[[3;;6]]]];
 add["diode_log_slope_04_06",beta,"1/V","0.40\:20130.60 V\:534a\:5bf9\:6570\:659c\:7387"];
 add["diode_log_R2_04_06",diodeR2,"1","0.40\:20130.60 V\:534a\:5bf9\:6570\:51b3\:5b9a\:7cfb\:6570"];
 AssociateTo[series,"diode_forward"-><|"x"->u,"y"->i,"x_label"->"\:6b63\:5411\:7535\:538b $U\\,/\\,\\mathrm{V}$","y_label"->"\:6b63\:5411\:7535\:6d41 $I\\,/\\,\\mathrm{mA}$","label"->"\:4e8c\:6781\:7ba1\:6b63\:5411\:8bb0\:5f55\:ff08\:6700\:9ad8\:70b9\:91cf\:7a0b\:5f85\:6838\:ff09"|>];
 AssociateTo[series,"diode_log"-><|"x"->u[[3;;6]],"y"->Log[i[[3;;6]]],"x_label"->"\:6b63\:5411\:7535\:538b $U\\,/\\,\\mathrm{V}$","y_label"->"$\\ln[I/(1\\,\\mathrm{mA})]$","label"->"0.40\:20130.60 V \:534a\:5bf9\:6570\:5206\:6790","fit"->True|>];
 AssociateTo[tables,"observations"-><|"headers"->Join[{"\:63a5\:6cd5","\:5143\:4ef6","\:7269\:7406\:91cf"},ToString/@Range[7],{"\:91cf\:7a0b"}],"rows"->original|>];
 AssociateTo[tables,"point_resistance"-><|"headers"->Join[{"\:63a5\:6cd5","\:5143\:4ef6"},Table["$R_"<>ToString[j]<>"/\\Omega$",{j,7}],{"\:5747\:503c / \:03a9"}],"rows"->derived|>];
 AssociateTo[tables,"fits"-><|"headers"->{"\:63a5\:6cd5","\:5143\:4ef6","\:5747\:503c / \:03a9","\:8fc7\:539f\:70b9\:62df\:5408 / \:03a9","\:542b\:622a\:8ddd\:659c\:7387 / \:03a9","\:622a\:8ddd / V","$r^2$"},"rows"->fitrows|>];
 AssociateTo[tables,"diode"-><|"headers"->Join[{"\:7269\:7406\:91cf"},ToString/@Range[7],{"\:91cf\:7a0b"}],"rows"->{Join[{"$U/\\mathrm{V}$"},u,{"2 V"}],Join[{"$I/\\mathrm{mA}$"},i,{"2 mA\:ff08\:6700\:9ad8\:70b9\:8d85\:51fa\:ff0c\:5f85\:6838\:ff09"}],Join[{"\:53cd\:5411\:7279\:6027"},ConstantArray["\:672a\:6d4b",7],{"\:2014"}]}|>];
 Do[
 x=N[10^(Range[-80,480]/80)];
 AssociateTo[series,"loading_k"<>ToString[k]-><|"x"->Log[10,x],"y"->100 x/(x+k),"x_label"->"$\\log_{10}(R_x/R_A)$","y_label"->"\:5916\:63a5\:6cd5\:76f8\:5bf9\:8bef\:5dee\:7edd\:5bf9\:503c / %","label"->"\:6a21\:578b RV/RA="<>ToString[k],"model"->True|>];
 add["model_k"<>ToString[k]<>"_crossover",(Sqrt[1+4 k]+1)/2,"1","\:7b49\:76f8\:5bf9\:8bef\:5dee\:65f6\:7684\:6a21\:578bRx/RA"],
 {k,cfg["model"]["voltmeter_ammeter_ratios"]}];
 <|"metrics"->metrics,"tables"->tables,"series"->series,"notes"->{"R2\:4f4e\:7535\:6d41\:8bb0\:5f55\:53ea\:67090.001 mA\:6b65\:8fdb\:ff0c\:5747\:503c\:4e0e\:62df\:5408\:7684\:5dee\:5f02\:4e0d\:80fd\:5ffd\:7565\:3002","\:4e8c\:6781\:7ba14.511 mA\:9ad8\:4e8e\:8868\:51852 mA\:91cf\:7a0b\:ff0c\:4fdd\:7559\:8bb0\:5f55\:4f46\:672a\:7528\:4e8e\:534a\:5bf9\:6570\:62df\:5408\:3002","\:672a\:6d4b\:53cd\:5411\:7279\:6027\:ff0c\:4e0d\:80fd\:636e\:6b64\:5b9e\:9a8c\:9a8c\:8bc1\:5355\:5411\:5bfc\:7535\:6027\:3002"}|>];

explore["fit",r_]:=Manipulate[Module[{s=r["series"][key],x,y,a,b,r2,rmse,selected},
 x=s["x"];y=s["y"];selected=Range[If[high,4,1],7];{a,b,r2,rmse}=fitLine[x[[selected]],y[[selected]]];
 Column[{GraphicsRow[{
 Show[ListPlot[Transpose[{x,y}],PlotStyle->Black,PlotMarkers->{"\:25cb",10}],Plot[a z+b,{z,Min[x],Max[x]},PlotStyle->Black],Frame->{{True,False},{True,False}},Axes->False,FrameLabel->{styled["\:7535\:6d41 I / mA"],styled["\:7535\:538b U / V"]},ImageSize->470],
 ListLinePlot[Transpose[{x,y-a x-b}],PlotStyle->Black,PlotMarkers->{"\:25cb",10},Frame->{{True,False},{True,False}},Axes->False,FrameLabel->{styled["\:7535\:6d41 I / mA"],styled["\:7535\:538b\:6b8b\:5dee / V"]},ImageSize->470]},ImageSize->1000],
 Style[Row[{styled["\:62df\:5408\:7535\:963b = "],NumberForm[1000 a,{10,3}],styled[" \:03a9\:ff1b\:622a\:8ddd = "],NumberForm[b,{8,6}],styled[" V"]}],FontFamily->"Times New Roman",FontSize->16]},Alignment->Center]],
 {{key,"internal_R1",styled["\:5143\:4ef6\:4e0e\:63a5\:6cd5"]},{"internal_R1"->styled["\:5185\:63a5 R1"],"external_R1"->styled["\:5916\:63a5 R1"],"internal_R2"->styled["\:5185\:63a5 R2"],"external_R2"->styled["\:5916\:63a5 R2"]}},{{high,False,styled["\:4ec5\:9ad8\:7535\:538b4\:70b9\:62df\:5408"]},{False,True}},SaveDefinitions->True];

explore["loading",r_]:=Manipulate[LogLogPlot[{100/t,100 t/(t+k)},{t,.1,10^6},PlotStyle->{Black,Directive[Black,Dashed]},Frame->{{True,False},{True,False}},Axes->False,FrameLabel->{styled["\:7535\:963b\:6bd4 Rx / RA"],styled["\:76f8\:5bf9\:52a0\:8f7d\:8bef\:5dee\:7edd\:5bf9\:503c / %"]},PlotLegends->{styled["\:5185\:63a5\:6cd5"],styled["\:5916\:63a5\:6cd5"]},ImageSize->950,BaseStyle->{FontFamily->"Times New Roman",FontSize->16}],
 {{k,10000,styled["\:6a21\:578b\:4eea\:8868\:5185\:963b\:6bd4 RV/RA"]},{1000->Pane[Style["1000",FontFamily->"Times New Roman",FontSize->14],{82,24},Alignment->Center],10000->Pane[Style["10000",FontFamily->"Times New Roman",FontSize->14],{82,24},Alignment->Center],1000000->Pane[Style["1000000",FontFamily->"Times New Roman",FontSize->14],{82,24},Alignment->Center]},ControlType->SetterBar},SaveDefinitions->True];
