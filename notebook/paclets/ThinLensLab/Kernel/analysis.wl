tlRows[path_] := Map[If[StringQ[#],ToExpression[#],#]&,Rest[Import[path,"CSV"]],{2}];
tlTable[h_,r_] := <|"headers"->h,"rows"->r|>;
tlDerived[raw_,values_] := MapThread[Join[{Round[#1[[1]]]}, Rest[#1], {Round[#2,10^-6]}]&,{raw,values}];
compute[dir_] := Module[{auto,uv,bessel,concave,f1,f2,f3,f4,fs,means,errors,names,keys,metrics,raw},
  {auto,uv,bessel,concave}=tlRows[FileNameJoin[{dir,"data",#}]]&/@{"autocollimation.csv","conjugates.csv","bessel.csv","concave.csv"};
  If[Min[Length/@{auto,uv,bessel,concave}]<2 || Min[Join[auto[[All,2;;]],uv[[All,2;;]],bessel[[All,2;;]],concave[[All,2;;]]]]<=0 || Min[concave[[All,3]]-concave[[All,2]]]<=0 || Min[bessel[[All,2]]-bessel[[All,3]]]<=0,Return[$Failed]];
  f1=auto[[All,2]]; f2=uv[[All,2]]uv[[All,3]]/(uv[[All,2]]+uv[[All,3]]);
  f3=(bessel[[All,2]]^2-bessel[[All,3]]^2)/(4 bessel[[All,2]]);
  f4=-concave[[All,2]]concave[[All,3]]/(concave[[All,3]]-concave[[All,2]]);
  fs={f1,f2,f3,f4};means=Mean/@fs;errors=(StandardDeviation[#]/Sqrt[Length[#]]&)/@fs;
  names={"\:81ea\:51c6\:76f4\:6cd5","\:7269\:8ddd\:50cf\:8ddd\:6cd5","\:4e8c\:6b21\:6210\:50cf\:6cd5","\:8f85\:52a9\:6210\:50cf\:6cd5\:ff08\:51f9\:900f\:955c\:ff09"};keys={"autocollimation","conjugates","bessel","concave"};
  metrics=Association[Flatten[Table[{keys[[i]]<>"_mean_cm"-><|"value"->N[means[[i]]],"unit"->"cm","label"->names[[i]]<>"\:7126\:8ddd\:5747\:503c"|>,keys[[i]]<>"_type_a_cm"-><|"value"->N[errors[[i]]],"unit"->"cm","label"->names[[i]]<>"\:5747\:503cA\:7c7b\:5206\:91cf"|>},{i,4}]]];
  AssociateTo[metrics,"convex_method_average_cm"-><|"value"->Mean[means[[1;;3]]],"unit"->"cm","label"->"\:4e09\:79cd\:51f8\:900f\:955c\:65b9\:6cd5\:7b49\:6743\:5e73\:5747"|>];
  raw=Map[Join[{Round[First[#]]},Rest[#]]&,#]&;
  <|"metrics"->metrics,"tables"-><|
    "autocollimation"->tlTable[{"\:6b21\:6570","$f$ / cm"},raw[auto]],
    "conjugates"->tlTable[{"\:6b21\:6570","$u$ / cm","$v$ / cm"},raw[uv]],
    "bessel"->tlTable[{"\:6b21\:6570","$D$ / cm","$d$ / cm"},raw[bessel]],
    "concave"->tlTable[{"\:6b21\:6570","$a$ / cm","$b$ / cm"},raw[concave]],
    "conjugates_f"->tlTable[{"\:6b21\:6570","$u$ / cm","$v$ / cm","$f$ / cm"},tlDerived[uv,f2]],
    "bessel_f"->tlTable[{"\:6b21\:6570","$D$ / cm","$d$ / cm","$f$ / cm"},tlDerived[bessel,f3]],
    "concave_f"->tlTable[{"\:6b21\:6570","$a$ / cm","$b$ / cm","$f$ / cm"},tlDerived[concave,f4]],
    "summary"->tlTable[{"\:65b9\:6cd5","\:7126\:8ddd\:5747\:503c / cm","\:5747\:503cA\:7c7b\:5206\:91cf / cm"},MapThread[{#1,Round[#2,10^-6],Round[#3,10^-6]}&,{names,means,errors}]]|>,
    "series"-><|
      "conjugates-repeat"-><|"x"->uv[[All,1]],"y"->f2,"x_label"->"\:6d4b\:91cf\:6b21\:6570","y_label"->"\:7126\:8ddd $f$ / cm","label"->"\:7269\:8ddd\:50cf\:8ddd\:6cd5"|>,
      "concave-repeat"-><|"x"->concave[[All,1]],"y"->f4,"x_label"->"\:6d4b\:91cf\:6b21\:6570","y_label"->"\:51f9\:900f\:955c\:7126\:8ddd $f$ / cm","label"->"\:8f85\:52a9\:6210\:50cf\:6cd5"|>|>,
    "notes"->{"A\:7c7b\:5206\:91cf\:4ec5\:7531\:5404\:65b9\:6cd5\:4e94\:6b21\:91cd\:590d\:503c\:4f30\:8ba1\:ff0c\:7f3a\:5c11\:4eea\:5668\:3001\:4f4d\:7f6e\:5224\:5b9a\:548c\:6a21\:578b\:8bef\:5dee\:ff0c\:4e0d\:80fd\:5408\:6210\:4e3a\:5b8c\:6574\:4e0d\:786e\:5b9a\:5ea6\:3002","\:4e09\:79cd\:51f8\:900f\:955c\:65b9\:6cd5\:7b49\:6743\:5e73\:5747\:4e3a\:63cf\:8ff0\:7edf\:8ba1\:ff0c\:672a\:8fdb\:884c\:7cbe\:5ea6\:52a0\:6743\:ff1b\:5171\:4eab\:6837\:54c1\:548c\:6807\:5c3a\:ff0c\:4e0d\:4f5c\:4e3a\:72ec\:7acb\:91cd\:590d\:6d4b\:91cf\:4f30\:8ba1\:4e0d\:786e\:5b9a\:5ea6\:3002","\:65e0\:900f\:955c\:6807\:79f0\:503c\:6216\:6821\:51c6\:503c\:ff0c\:4e0d\:636e\:65b9\:6cd5\:95f4\:63a5\:8fd1\:5224\:65ad\:51c6\:786e\:5ea6\:3002"}|>
];
tlRayView[r_,ratio_] := Module[{f,u,v,mag},
  f=r["metrics"]["conjugates_mean_cm"]["value"];u=ratio f;v=f u/(u-f);mag=-v/u;
  Column[{Style[Row[{"u = ",NumberForm[u,{7,2}]," cm; v = ",NumberForm[v,{7,2}]," cm; M = ",NumberForm[mag,{6,3}]}],FontFamily->"Times New Roman"],
    Graphics[{GrayLevel[.7],Line[{{-4.2 f,0},{6.3 f,0}}],Black,AbsoluteThickness[1.5],Line[{{-u,1},{0,1},{v,mag}}],Dashed,Line[{{-u,1},{0,0},{v,mag}}],Dotted,Line[{{-u,1},{0,mag},{v,mag}}],Dashing[{}],AbsoluteThickness[2],Arrow[{{-u,0},{-u,1}}],Arrow[{{v,0},{v,mag}}],Dashed,Line[{{0,-3.5},{0,3.5}}]},
      Frame->{{True,False},{True,False}},FrameLabel->{Row[{styled["\:6cbf\:5149\:8f74\:4f4d\:7f6e "],"x / cm"}],styled["\:6a2a\:5411\:9ad8\:5ea6 / \:4efb\:610f\:5355\:4f4d"]},PlotRange->{{-4.2 f,6.3 f},{-5.5,2}},AspectRatio->.45,ImageSize->650,ImagePadding->{{75,25},{60,25}},BaseStyle->{FontFamily->"Times New Roman",FontSize->17}]
  },Alignment->Center]
];
tlBesselView[r_,q_] := Module[{f,dd,gap,z,left,right,selection},
  f=r["metrics"]["conjugates_mean_cm"]["value"];dd=q f;gap=Sqrt[Max[0,dd^2-4 dd f]];
  selection={{q,(dd-gap)/2},{q,(dd+gap)/2}};
  left[z_]:=(z f-Sqrt[(z f)^2-4 z f^2])/2;right[z_]:=(z f+Sqrt[(z f)^2-4 z f^2])/2;
  Show[Plot[{left[z],right[z]},{z,4,8},PlotStyle->{Directive[Black,AbsoluteThickness[1.5]],Directive[Black,Dashed,AbsoluteThickness[1.5]]}],ListPlot[selection,PlotStyle->Black,PlotMarkers->{Graphics[{White,Disk[],Black,Circle[]}],11}],
    Frame->{{True,False},{True,False}},Axes->False,FrameLabel->{Row[{styled["\:7269\:5c4f\:8ddd\:79bb "],"D / f"}],styled["\:8ddd\:7269\:7684\:900f\:955c\:4f4d\:7f6e / cm"]},GridLines->Automatic,GridLinesStyle->GrayLevel[.9],ImageSize->650,ImagePadding->{{75,25},{60,25}},BaseStyle->{FontFamily->"Times New Roman",FontSize->17},PlotRange->All]
];
explore["ray-geometry",r_] := Manipulate[tlRayView[r,q],{{q,2,styled["\:7269\:8ddd u/f"]},1.2,4,.2,Appearance->"Labeled"},SaveDefinitions->True];
explore["bessel-branches",r_] := Manipulate[tlBesselView[r,q],{{q,5,styled["\:7269\:5c4f\:8ddd\:79bb D/f"]},4,8,.2,Appearance->"Labeled"},SaveDefinitions->True];
