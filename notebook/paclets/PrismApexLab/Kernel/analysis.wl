oaRows[root_,index_] := Rest[Import[FileNameJoin[{root,"data","observations-"<>IntegerString[index,10,2]<>".csv"}],"CSV"]];
oaNum[s_] := If[NumberQ[s],s,ToExpression[s]];
oaAngle[s_] := Module[{p},p=ToExpression/@StringCases[ToString[s],RegularExpression["-?[0-9]+(?:[.][0-9]+)?"]];p[[1]]+If[Length[p]>1,p[[2]]/60,0]+If[Length[p]>2,p[[3]]/3600,0]];
oaSep[a_,b_] := Abs[Mod[a-b+180,360]-180];
oaMeanA[v_] := {Mean[v],StandardDeviation[v]/Sqrt[Length[v]]};
oaMetric[v_,unit_,label_] := <|"value"->N[v],"unit"->unit,"label"->label|>;
oaTable[h_,r_] := <|"headers"->h,"rows"->r|>;
oaTex[s_] := Module[{q=ToString[s],p},If[StringContainsQ[q,"\:00b0"],p=StringCases[q,RegularExpression["[0-9]+(?:[.][0-9]+)?"]];If[Length[p]>=2,Return["$"<>p[[1]]<>"^{\\circ}"<>p[[2]]<>"^{\\prime}$"]]];StringReplace[q,{"\:03b8\:2081"->"$\\theta_1$","\:03b8\:2082"->"$\\theta_2$","\:03b8\:2083"->"$\\theta_3$","\:03b8\:2084"->"$\\theta_4$","\:03b4\:1d62"->"$\\delta_i$","\:03b4min,i"->"$\\delta_{\\min,i}$","\:03c6\:1d62"->"$\\varphi_i$","A\:1d62"->"$A_i$"}]];
oaSource[root_,index_] := Module[{raw},raw=Import[FileNameJoin[{root,"data","observations-"<>IntegerString[index,10,2]<>".csv"}],"CSV"];oaTable[oaTex/@First[raw],Map[oaTex,Rest[raw],{2}]]];


compute[root_] := Module[{cfg,rows,angles,left,right,values,mean,ua,ub,uc,metrics,tables,unused},
 cfg=Import[FileNameJoin[{root,"experiment.json"}],"RawJSON"];rows=oaRows[root,1];angles=Map[oaAngle,rows[[All,2;;5]],{2}];
 left=oaSep[#[[1]],#[[3]]]&/@angles;right=oaSep[#[[2]],#[[4]]]&/@angles;values=(left+right)/4;
 {mean,ua}=oaMeanA[values];ub=cfg["parameters"]["angle_error_bound_arcmin"]/60/Sqrt[3];uc=Sqrt[ua^2+ub^2];
 metrics=<|"angle_mean_deg"->oaMetric[mean,"deg","\:9876\:89d2\:5747\:503c"],"angle_type_a_arcmin"->oaMetric[ua 60,"arcmin","\:89d2\:5ea6\:5747\:503cA\:7c7b\:5206\:91cf"],"angle_type_b_arcmin"->oaMetric[ub 60,"arcmin","\:6307\:5b9a\:8bef\:5dee\:9650B\:7c7b\:5206\:91cf"],"angle_combined_arcmin"->oaMetric[uc 60,"arcmin","\:4e24\:5206\:91cf\:5408\:6210\:6807\:51c6\:4e0d\:786e\:5b9a\:5ea6"]|>;
 tables=Association[Table["table"<>ToString[i]->oaSource[root,i],{i,{1}}]];
 AssociateTo[tables,"table2"->oaTable[{"\:6b21\:6570","\:5de6\:6e38\:6807\:89d2\:5dee / \:00b0","\:53f3\:6e38\:6807\:89d2\:5dee / \:00b0","\:9876\:89d2 / \:00b0"},MapThread[{oaNum[#1[[1]]],Round[#2,10^-8],Round[#3,10^-8],Round[#4,10^-8]}&,{rows,left,right,values}]]];
 
 <|"metrics"->metrics,"tables"->tables,"series"-><|"angle-repeat"-><|"x"->Range[Length[rows]],"y"->values,"x_label"->"\:6d4b\:91cf\:6b21\:6570","y_label"->"\:9876\:89d2 / \:00b0","label"->"\:53cc\:6e38\:6807\:7ed3\:679c"|>|>,"notes"->{"\:5706\:5468\:6700\:77ed\:89d2\:5dee\:5904\:7406\:8de8\:96f6\:8bfb\:6570\:3002", "\:8bef\:5dee\:96501\:89d2\:5206\:6309\:6700\:7ec8\:89d2\:5ea6\:4f30\:8ba1\:7684\:5747\:5300\:5206\:5e03\:9650\:503c\:91c7\:7528\:ff1b\:672a\:542b\:5168\:90e8\:6821\:51c6\:7cfb\:7edf\:5206\:91cf\:3002"}|>
];
