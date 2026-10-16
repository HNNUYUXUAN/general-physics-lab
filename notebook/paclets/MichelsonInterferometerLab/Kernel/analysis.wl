oaRows[root_,index_] := Rest[Import[FileNameJoin[{root,"data","observations-"<>IntegerString[index,10,2]<>".csv"}],"CSV"]];
oaNum[s_] := If[NumberQ[s],s,ToExpression[s]];
oaAngle[s_] := Module[{p},p=ToExpression/@StringCases[ToString[s],RegularExpression["-?[0-9]+(?:[.][0-9]+)?"]];p[[1]]+If[Length[p]>1,p[[2]]/60,0]+If[Length[p]>2,p[[3]]/3600,0]];
oaSep[a_,b_] := Abs[Mod[a-b+180,360]-180];
oaMeanA[v_] := {Mean[v],StandardDeviation[v]/Sqrt[Length[v]]};
oaMetric[v_,unit_,label_] := <|"value"->N[v],"unit"->unit,"label"->label|>;
oaTable[h_,r_] := <|"headers"->h,"rows"->r|>;
oaTex[s_] := Module[{q=ToString[s],p},If[StringContainsQ[q,"\:00b0"],p=StringCases[q,RegularExpression["[0-9]+(?:[.][0-9]+)?"]];If[Length[p]>=2,Return["$"<>p[[1]]<>"^{\\circ}"<>p[[2]]<>"^{\\prime}$"]]];StringReplace[q,{"\:03b8\:2081"->"$\\theta_1$","\:03b8\:2082"->"$\\theta_2$","\:03b8\:2083"->"$\\theta_3$","\:03b8\:2084"->"$\\theta_4$","\:03b4\:1d62"->"$\\delta_i$","\:03b4min,i"->"$\\delta_{\\min,i}$","\:03c6\:1d62"->"$\\varphi_i$","A\:1d62"->"$A_i$"}]];
oaSource[root_,index_] := Module[{raw},raw=Import[FileNameJoin[{root,"data","observations-"<>IntegerString[index,10,2]<>".csv"}],"CSV"];oaTable[oaTex/@First[raw],Map[oaTex,Rest[raw],{2}]]];


compute[root_] := Module[{rows,shift,wavelength,mean,ua},rows=Map[oaNum,oaRows[root,1],{2}];shift=rows[[All,4]]-rows[[All,3]];If[Min[shift]<=0||Min[rows[[All,2]]]<=0,Return[$Failed]];wavelength=2 shift/rows[[All,2]]10^6;{mean,ua}=oaMeanA[wavelength];
 <|"metrics"-><|"wavelength_mean_nm"->oaMetric[mean,"nm","\:6fc0\:5149\:6ce2\:957f\:5747\:503c"],"wavelength_type_a_nm"->oaMetric[ua,"nm","\:6ce2\:957f\:5747\:503cA\:7c7b\:5206\:91cf"],"relative_reference_difference_percent"->oaMetric[Abs[mean-632.8]/632.8 100,"%","\:76f8\:5bf9\:6307\:5b9a632.8nm\:7684\:5dee\:5f02"]|>,"tables"-><|"table1"->oaTable[{"\:6b21\:6570","\:6761\:7eb9\:6570 $N$","$d_1$ / mm","$d_2$ / mm","$\\Delta d$ / mm"},MapThread[Join[#1,{Round[#2,10^-8]}]&,{rows,shift}]],"table2"->oaTable[{"\:6b21\:6570","$\\Delta d$ / mm","$\\lambda$ / nm"},MapThread[{#1[[1]],Round[#2,10^-8],Round[#3,10^-6]}&,{rows,shift,wavelength}]]|>,"series"-><|"wavelength-repeat"-><|"x"->rows[[All,1]],"y"->wavelength,"x_label"->"\:6d4b\:91cf\:6b21\:6570","y_label"->"\:6fc0\:5149\:6ce2\:957f $\\lambda$ / nm","label"->"\:4e94\:6b21100\:6761\:7eb9\:8ba1\:6570"|>|>,"notes"->{"632.8nm\:662f\:6307\:5b9a\:5e38\:7528\:53c2\:8003\:503c\:ff0c\:672a\:9644\:672c\:6fc0\:5149\:5668\:6821\:51c6\:8bc1\:4e66\:3002","\:53ea\:6709\:91cd\:590d\:6027A\:7c7b\:5206\:91cf\:ff0c\:7f3a\:4eea\:5668\:4e0e\:8ba1\:6570\:7cfb\:7edf\:8bef\:5dee\:3002"}|>
];
