compute[dir_] := Module[{cfg,p,stat,dyn,dx,force,ks,mask,kstat,period,ut,kd,uk,x,y,xc,slope,intercept,metrics,rows},
 cfg=Import[FileNameJoin[{dir,"experiment.json"}],"RawJSON"];p=cfg["parameters"];
 stat=Rest[Import[FileNameJoin[{dir,"data","static.csv"}],"CSV"]];dyn=Rest[Import[FileNameJoin[{dir,"data","periods.csv"}],"CSV"]];
 dx=(stat[[All,4]]-p["initial_position_cm"])/100;force=stat[[All,3]] p["gravity_m_s2"]/1000;ks=force/dx;
 If[Length[ks]!=5||Length[dyn]!=13||Min[dx]<=0,Return[$Failed]];
 mask=Flatten[Position[stat[[All,5]],1]];kstat=Mean[ks[[mask]]];period=Mean[dyn[[All,2]]];ut=StandardDeviation[dyn[[All,2]]]/Sqrt[13];
 kd=4 Pi^2(p["oscillator_mass_g"]/1000)/period^2;uk=2 kd ut/period;
 x=dx[[mask]];y=force[[mask]];xc=x-Mean[x];slope=xc.(y-Mean[y])/(xc.xc);intercept=Mean[y]-slope Mean[x];
 metrics=<|"static_stiffness"-><|"value"->N[kstat],"unit"->"N/m","label"->"\:9759\:6001\:9010\:7ec4\:52b2\:5ea6\:7cfb\:6570\:5e73\:5747"|>,
 "static_stiffness_all"-><|"value"->N[Mean[ks]],"unit"->"N/m","label"->"\:5168\:90e8\:4e94\:7ec4\:9759\:6001\:6bd4\:503c\:5e73\:5747"|>,
 "static_fit_slope"-><|"value"->N[slope],"unit"->"N/m","label"->"\:6e90\:4fdd\:7559\:7ec4\:9759\:6001\:62df\:5408\:659c\:7387"|>,
 "static_fit_intercept"-><|"value"->N[intercept],"unit"->"N","label"->"\:6e90\:4fdd\:7559\:7ec4\:9759\:6001\:62df\:5408\:622a\:8ddd"|>,
 "mean_period"-><|"value"->N[period],"unit"->"s","label"->"\:5e73\:5747\:5468\:671f","uncertainty"->N[ut]|>,
 "period_sum"-><|"value"->N[Total[dyn[[All,2]]]],"unit"->"s","label"->"\:5468\:671f\:603b\:548c"|>,
 "dynamic_stiffness"-><|"value"->N[kd],"unit"->"N/m","label"->"\:52a8\:6001\:52b2\:5ea6\:7cfb\:6570","uncertainty"->N[uk]|>,
 "relative_difference"-><|"value"->N[100 Abs[kd-kstat]/kstat],"unit"->"%","label"->"\:52a8\:9759\:6001\:76f8\:5bf9\:5dee\:5f02"|>|>;
 rows=Table[{stat[[i,1]],"$"<>StringReplace[stat[[i,2]],{"m1"->"m_1","m2"->"m_2","m3"->"m_3"}]<>"$",stat[[i,3]],stat[[i,4]],N[dx[[i]]],N[force[[i]]],N[ks[[i]]],If[stat[[i,5]]==1,"\:4fdd\:7559","\:5254\:9664"]},{i,5}];
 <|"metrics"->metrics,"tables"-><|
 "static"-><|"headers"->{"\:5e8f\:53f7","\:7ec4\:5408","$m / \\mathrm{g}$","$x / \\mathrm{cm}$","$\\Delta x / \\mathrm{m}$","$F / \\mathrm{N}$","$k / (\\mathrm{N\\,m^{-1}})$","\:6e90\:62a5\:544a\:5e73\:5747\:503c\:9009\:7528"},"rows"->rows|>,
 "periods"-><|"headers"->{"\:5e8f\:53f7",1,2,3,4,5,6,7},"rows"->{Prepend[dyn[[1;;7,2]],"$T / \\mathrm{s}$"],{"\:5e8f\:53f7",8,9,10,11,12,13,"\:2014"},Join[{"$T / \\mathrm{s}$"},dyn[[8;;13,2]],{"\:2014"}]}|>|>,
 "series"-><|"static_force"-><|"x"->N[dx],"y"->N[force],"x_label"->"\:4f38\:957f\:91cf / m","y_label"->"\:8f7d\:8377\:91cd\:529b / N","fit"->True|>,
 "period_sequence"-><|"x"->dyn[[All,1]],"y"->dyn[[All,2]],"x_label"->"\:6d4b\:91cf\:5e8f\:53f7","y_label"->"\:5468\:671f / s"|>|>,
 "notes"->{"\:9759\:6001\:4e3b\:7ed3\:679c\:6cbf\:7528\:6e90\:62a5\:544a\:660e\:786e\:5254\:9664\:7b2c1\:7ec4\:7684\:9009\:62e9\:ff0c\:4f46\:4fdd\:7559\:8be5\:89c2\:6d4b\:53ca\:5168\:7ec4\:5e73\:5747\:4f5c\:654f\:611f\:6027\:6bd4\:8f83\:3002","\:52a8\:6001\:516c\:5f0f\:672a\:8ba1\:5f39\:7c27\:8d28\:91cf\:ff1b\:5468\:671fA\:7c7b\:53ca\:52a8\:6001k\:4e0d\:786e\:5b9a\:5ea6\:672a\:542b\:8d28\:91cf\:548c\:8ba1\:65f6\:5668\:7cfb\:7edf\:8bef\:5dee\:3002","\:9759\:6001\:6563\:70b9\:56fe\:7684\:5168\:4e94\:7ec4\:62df\:5408\:4ec5\:4f9b\:6b8b\:5dee\:8bca\:65ad\:ff1b\:6e90\:4fdd\:7559\:7ec4\:62df\:5408\:53c2\:6570\:53e6\:884c\:8ba1\:7b97\:3002"}|>
];
explore["spring-mass",r_] := With[{tt=r["metrics"]["mean_period"]["value"],kk=r["metrics"]["dynamic_stiffness"]["value"]},
 Manipulate[Plot[kk+4 Pi^2 x/(3000 tt^2),{x,0,50},PlotStyle->Black,Frame->{{True,False},{True,False}},Axes->False,
 FrameLabel->{Style["\:5047\:8bbe\:5f39\:7c27\:8d28\:91cf / g",FontFamily->"SimSun"],Style["\:56fa\:5b9a\:5468\:671f\:6240\:9700\:52b2\:5ea6\:7cfb\:6570 / (N m\:207b\:00b9)",FontFamily->"SimSun"]},BaseStyle->{FontFamily->"Times New Roman",FontSize->18},GridLines->Automatic,GridLinesStyle->Directive[GrayLevel[.9]],Epilog->{Black,PointSize[.018],Point[{mass,kk+4 Pi^2 mass/(3000 tt^2)}]},PlotRange->All,ImageSize->800,ImagePadding->{{100,30},{65,25}}],
 {{mass,0,Style["\:5047\:8bbe\:5f39\:7c27\:8d28\:91cf / g",FontFamily->"SimSun"]},0,50,1,Appearance->"Labeled"},ControlPlacement->Bottom,SaveDefinitions->True]
];
