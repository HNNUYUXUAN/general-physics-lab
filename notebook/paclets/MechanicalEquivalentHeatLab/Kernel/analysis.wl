heatRegression[x_,y_] := Module[{xc=x-Mean[x],yc=y-Mean[y],a,b,r,res,sy,ua,ub},
 a=xc.yc/(xc.xc);b=Mean[y]-a Mean[x];r=xc.yc/Sqrt[(xc.xc)(yc.yc)];res=y-a x-b;sy=Sqrt[res.res/(Length[x]-2)];ua=sy/Sqrt[xc.xc];ub=sy Sqrt[1/Length[x]+Mean[x]^2/(xc.xc)];{a,b,r,ua,ub}];
compute[dir_] := Module[{cfg,data,t,temp,a,b,rr,ua,ub,early,late,endpoint,metrics,rows},
 cfg=Import[FileNameJoin[{dir,"experiment.json"}],"RawJSON"];
 data=Rest[Import[FileNameJoin[{dir,"data","temperatures.csv"}],"CSV"]];
 If[Length[data]!=30,Return[$Failed]];
 t=data[[All,2]]60;temp=data[[All,3]];{a,b,rr,ua,ub}=heatRegression[t,temp];
 early=First[heatRegression[t[[1;;15]],temp[[1;;15]]]];late=First[heatRegression[t[[16;;30]],temp[[16;;30]]]];endpoint=(Last[temp]-First[temp])/(Last[t]-First[t]);
 metrics=<|"heating_slope"-><|"value"->N[a],"unit"->"K/s","label"->"\:5168\:533a\:95f4\:6e29\:5347\:62df\:5408\:659c\:7387","uncertainty"->N[ua]|>,
 "temperature_intercept"-><|"value"->N[b],"unit"->"K","label"->"\:62df\:5408\:521d\:6e29\:622a\:8ddd","uncertainty"->N[ub]|>,
 "correlation"-><|"value"->N[rr],"unit"->"1","label"->"\:76f8\:5173\:7cfb\:6570"|>,
 "endpoint_slope"-><|"value"->N[endpoint],"unit"->"K/s","label"->"\:9996\:5c3e\:6e29\:5347\:901f\:7387"|>,
 "early_slope"-><|"value"->N[early],"unit"->"K/s","label"->"\:524d15\:70b9\:62df\:5408\:659c\:7387"|>,
 "late_slope"-><|"value"->N[late],"unit"->"K/s","label"->"\:540e15\:70b9\:62df\:5408\:659c\:7387"|>,
 "total_temperature_rise"-><|"value"->N[Last[temp]-First[temp]],"unit"->"K","label"->"\:9996\:5c3e\:6e29\:5347"|>,
 "source_slope_difference"-><|"value"->N[100(a-cfg["source_reported"]["slope_k_s"])/cfg["source_reported"]["slope_k_s"]],"unit"->"%","label"->"\:76f8\:5bf9\:6e90\:4eea\:5668\:659c\:7387\:5dee\:5f02"|>|>;
 rows=Table[Join[data[[i]],data[[i+15]]],{i,15}];
 <|"metrics"->metrics,"tables"-><|"observations"-><|"headers"->{"\:5e8f\:53f7","$t / \\mathrm{min}$","$T / \\mathrm{K}$","\:5e8f\:53f7","$t / \\mathrm{min}$","$T / \\mathrm{K}$"},"rows"->rows|>,
 "fit_values"-><|"headers"->{"\:65f6\:95f4 / min","\:6e29\:5ea6 / K","\:62df\:5408\:6e29\:5ea6 / K","\:6b8b\:5dee / K"},"rows"->Table[{N[t[[i]]/60],N[temp[[i]]],N[a t[[i]]+b],N[temp[[i]]-a t[[i]]-b]},{i,30}]|>|>,
 "series"-><|"heating_curve"-><|"x"->N[t],"y"->N[temp],"x_label"->"\:52a0\:70ed\:65f6\:95f4 / s","y_label"->"\:6c34\:6e29 / K","fit"->True|>|>,"notes"->{"J=4.21J/cal\:4e3a\:6e90\:62a5\:544a\:8bb0\:5f55\:7ed3\:679c\:ff0c\:7f3a\:5c11\:5b9e\:9645\:7535\:538b/\:7535\:6d41\:53ca\:603b\:70ed\:5bb9\:ff0c\:65e0\:6cd5\:72ec\:7acb\:91cd\:7b97\:3002","\:7535\:538b20V\:3001\:7535\:6d41.495A\:4ec5\:4e3a\:64cd\:4f5c\:8bbe\:5b9a\:8fd1\:4f3c\:503c\:ff0c\:672a\:89c6\:4e3a\:5b9e\:9645\:6d4b\:91cf\:3002","\:7ebf\:6027\:56de\:5f52\:4e0d\:4f1a\:81ea\:52a8\:5b8c\:6210\:6563\:70ed\:4fee\:6b63\:3002"}|>
];
explore["fit-window",r_] := With[{tt=r["series"]["heating_curve"]["x"],yy=r["series"]["heating_curve"]["y"]},
 Manipulate[Module[{indices,fit},indices=Switch[window,0,Range[30],1,Range[15],2,Range[16,30],3,Range[6,25]];fit=heatRegression[tt[[indices]],yy[[indices]]];
 Show[Plot[fit[[1]]x+fit[[2]],{x,First[tt],Last[tt]},PlotStyle->Black],ListPlot[Transpose[{tt,yy}],PlotStyle->Black,PlotMarkers->{"\:25cb",10}],
 Frame->{{True,False},{True,False}},Axes->False,FrameLabel->{Style["\:52a0\:70ed\:65f6\:95f4 / s",FontFamily->"SimSun"],Style["\:6c34\:6e29 / K",FontFamily->"SimSun"]},BaseStyle->{FontFamily->"Times New Roman",FontSize->18},GridLines->Automatic,GridLinesStyle->Directive[GrayLevel[.9]],PlotRange->All,ImageSize->800,ImagePadding->{{95,30},{65,25}}]],
 {{window,0,Style["\:62df\:5408\:533a\:95f4",FontFamily->"SimSun"]},{0->"\:5168\:90e830\:70b9",1->"\:524d15\:70b9",2->"\:540e15\:70b9",3->"\:4e2d\:95f420\:70b9"},ControlType->PopupMenu},ControlPlacement->Bottom,SaveDefinitions->True]
];
