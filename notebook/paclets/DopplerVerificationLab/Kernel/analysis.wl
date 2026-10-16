compute[dir_] := Module[{cfg, records, x, y, xc, yc, k, b, res, rr, sy, uk, ub, f0, temp, speed, theoretical, uspeed, metrics, tables},
 cfg = Import[FileNameJoin[{dir,"experiment.json"}],"RawJSON"];
 records = Rest[Import[FileNameJoin[{dir,"data","observations.csv"}],"CSV"]];
 x = records[[All,2]]; y = records[[All,3]];
 If[Length[x]!=5 || !VectorQ[x,NumericQ] || !VectorQ[y,NumericQ],Return[$Failed]];
 f0 = cfg["parameters"]["source_frequency_hz"]; temp=cfg["parameters"]["temperature_c"];
 xc=x-Mean[x];yc=y-Mean[y];k=xc.yc/(xc.xc);b=Mean[y]-k Mean[x];res=y-k x-b;
 rr=xc.yc/Sqrt[(xc.xc)(yc.yc)];sy=Sqrt[res.res/(Length[x]-2)];uk=sy/Sqrt[xc.xc];ub=sy Sqrt[1/Length[x]+Mean[x]^2/(xc.xc)];
 speed=f0/k;theoretical=331.45 Sqrt[1+temp/273.15];uspeed=f0 uk/k^2;
 metrics=<|"slope"-><|"value"->N[k],"unit"->"Hz/(m/s)","label"->"\:9891\:7387\:901f\:5ea6\:62df\:5408\:659c\:7387","uncertainty"->N[uk]|>,
 "intercept"-><|"value"->N[b],"unit"->"Hz","label"->"\:62df\:5408\:622a\:8ddd","uncertainty"->N[ub]|>,
 "correlation"-><|"value"->N[rr],"unit"->"1","label"->"\:76f8\:5173\:7cfb\:6570"|>,
 "sound_speed"-><|"value"->N[speed],"unit"->"m/s","label"->"\:5b9e\:9a8c\:58f0\:901f","uncertainty"->N[uspeed]|>,
 "theoretical_speed"-><|"value"->N[theoretical],"unit"->"m/s","label"->"\:6e29\:5ea6\:6a21\:578b\:58f0\:901f"|>,
 "relative_deviation"-><|"value"->N[100 Abs[speed-theoretical]/theoretical],"unit"->"%","label"->"\:58f0\:901f\:76f8\:5bf9\:5dee\:5f02"|>,
 "intercept_offset"-><|"value"->N[b-f0],"unit"->"Hz","label"->"\:622a\:8ddd\:4e0e\:58f0\:6e90\:9891\:7387\:5dee"|>|>;
 tables=<|"observations"-><|"headers"->{"\:5e8f\:53f7","$v / (\\mathrm{m\\,s^{-1}})$","$f / \\mathrm{Hz}$"},"rows"->records|>,
 "processed"-><|"headers"->{"\:5e8f\:53f7","\:6a21\:578b\:9884\:6d4b\:9891\:7387 / Hz","\:62df\:5408\:6b8b\:5dee / Hz","\:6e29\:5ea6\:6a21\:578b\:9884\:6d4b\:9891\:7387 / Hz"},"rows"->Table[{i,N[k x[[i]]+b],N[res[[i]]],N[f0(1+x[[i]]/theoretical)]},{i,Length[x]}]|>|>;
 <|"metrics"->metrics,"tables"->tables,"series"-><|"doppler_fit"-><|"x"->N[x],"y"->N[y],"x_label"->"\:63a5\:6536\:5668\:901f\:5ea6 / (m s\:207b\:00b9)","y_label"->"\:63a5\:6536\:9891\:7387 / Hz","fit"->True|>|>,"notes"->{"\:58f0\:6e90\:56fa\:5b9a\:ff0c\:63a5\:6536\:5668\:5411\:58f0\:6e90\:8fd0\:52a8\:4e3a\:6b63\:3002","\:58f0\:901f\:4e0d\:786e\:5b9a\:5ea6\:53ea\:4f20\:64ad\:56de\:5f52\:659c\:7387\:6807\:51c6\:8bef\:5dee\:ff0c\:672a\:8ba1\:58f0\:6e90\:9891\:7387\:3001\:6d4b\:901f\:548c\:6e29\:5ea6\:4eea\:5668\:8bef\:5dee\:3002"}|>
];

explore["receiver-speed",r_] := With[{u=r["metrics"]["theoretical_speed"]["value"],f0=r["metrics"]["intercept"]["value"]-r["metrics"]["intercept_offset"]["value"]},
 Manipulate[Plot[f0(1+x/u),{x,-1.5,1.5},PlotStyle->Black,Frame->{{True,False},{True,False}},Axes->False,
 FrameLabel->{Style["\:63a5\:6536\:5668\:901f\:5ea6 / (m s\:207b\:00b9)",FontFamily->"SimSun"],Style["\:63a5\:6536\:9891\:7387 / Hz",FontFamily->"SimSun"]},
 BaseStyle->{FontFamily->"Times New Roman",FontSize->18},GridLines->Automatic,GridLinesStyle->Directive[GrayLevel[.9]],Epilog->{Black,PointSize[.018],Point[{v,f0(1+v/u)}]},PlotRange->All,ImageSize->800,ImagePadding->{{95,30},{65,25}}],
 {{v,0,Style["\:63a5\:6536\:5668\:901f\:5ea6 / (m/s)",FontFamily->"SimSun"]},-1.5,1.5,.03,Appearance->"Labeled"},ControlPlacement->Bottom,SaveDefinitions->True]
];
