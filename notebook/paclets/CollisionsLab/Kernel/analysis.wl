compute[dir_] := Module[{cfg,p,m1,m2,ine,ela,v0,vc,v1,v2,pin,pout,eta,ein,eout,loss,theory,ratios,delta,inferred,ee,metrics,tables},
 cfg=Import[FileNameJoin[{dir,"experiment.json"}],"RawJSON"];p=cfg["parameters"];m1=p["mass1_g"]/1000;m2=p["mass2_g"]/1000;
 ine=Rest[Import[FileNameJoin[{dir,"data","inelastic.csv"}],"CSV"]];ela=Rest[Import[FileNameJoin[{dir,"data","elastic.csv"}],"CSV"]];
 If[Length[ine]!=5||Length[ela]!=5,Return[$Failed]];
 v0=ine[[All,2]]/100;vc=ine[[All,3]]/100;v1=(ela[[All,2]]+ela[[All,4]])/200;v2=ela[[All,3]]/100;
 pin=m1 v0;pout=(m1+m2)vc;eta=100(pin-pout)/pin;ein=m1 v0^2/2;eout=(m1+m2)vc^2/2;loss=100(ein-eout)/ein;
 theory=2 m1/(m1-m2);ratios=v2/v1;delta=100(ratios-theory)/theory;inferred=(m1 v1+m2 v2)/m1;ee=(v2-v1)/inferred;
 metrics=AssociationThread[{"mass_total","mean_momentum_deviation","max_momentum_deviation","mean_energy_loss","theoretical_energy_loss","theoretical_velocity_ratio","mean_velocity_ratio","mean_absolute_ratio_deviation","mean_conditional_restitution"},
 MapThread[<|"value"->N[#1],"unit"->#2,"label"->#3|>&,
 {{m1+m2,Mean[eta],Max[eta],Mean[loss],100 m2/(m1+m2),theory,Mean[ratios],Mean[Abs[delta]],Mean[ee]},
 {"kg","%","%","%","%","1","1","%","1"},
 {"\:7cfb\:7edf\:603b\:8d28\:91cf","\:975e\:5f39\:6027\:52a8\:91cf\:5e73\:5747\:76f8\:5bf9\:4e8f\:635f","\:975e\:5f39\:6027\:52a8\:91cf\:6700\:5927\:76f8\:5bf9\:4e8f\:635f","\:975e\:5f39\:6027\:52a8\:80fd\:5e73\:5747\:635f\:5931\:7387","\:7406\:60f3\:7c98\:5408\:78b0\:649e\:52a8\:80fd\:635f\:5931\:7387","\:7406\:60f3\:5f39\:6027\:78b0\:649e\:540e\:901f\:5ea6\:6bd4","\:6d4b\:5f97\:78b0\:540e\:901f\:5ea6\:6bd4\:5e73\:5747","\:901f\:5ea6\:6bd4\:5e73\:5747\:76f8\:5bf9\:5dee\:5f02","\:5047\:5b9a\:52a8\:91cf\:5b88\:6052\:7684\:6062\:590d\:7cfb\:6570\:5e73\:5747"}}]];
 tables=<|"inelastic_observations"-><|"headers"->{"\:5e8f\:53f7","$v_{10} / (\\mathrm{cm\\,s^{-1}})$","$v_{\\mathrm{c}} / (\\mathrm{cm\\,s^{-1}})$"},"rows"->ine|>,
 "elastic_observations"-><|"headers"->{"\:5e8f\:53f7","\:6ed1\:57571\:901f\:5ea6\:7b2c\:4e00\:6b21 / (cm s\:207b\:00b9)","\:6ed1\:57572\:901f\:5ea6 / (cm s\:207b\:00b9)","\:6ed1\:57571\:901f\:5ea6\:7b2c\:4e8c\:6b21 / (cm s\:207b\:00b9)"},"rows"->ela|>,
 "momentum"-><|"headers"->{"\:5e8f\:53f7","\:78b0\:524d\:52a8\:91cf / (kg m s\:207b\:00b9)","\:78b0\:540e\:52a8\:91cf / (kg m s\:207b\:00b9)","\:52a8\:91cf\:76f8\:5bf9\:4e8f\:635f / %","\:78b0\:524d\:52a8\:80fd / J","\:78b0\:540e\:52a8\:80fd / J","\:52a8\:80fd\:635f\:5931 / %"},"rows"->Table[Join[{i},N[{pin[[i]],pout[[i]],eta[[i]],ein[[i]],eout[[i]],loss[[i]]}]],{i,5}]|>,
 "ratios"-><|"headers"->{"\:5e8f\:53f7","\:6ed1\:57571\:5747\:901f / (cm s\:207b\:00b9)","\:6ed1\:57572\:901f\:5ea6 / (cm s\:207b\:00b9)","\:6d4b\:5f97\:901f\:5ea6\:6bd4","\:76f8\:5bf9\:7406\:8bba\:6bd4\:503c\:5dee\:5f02 / %","\:6761\:4ef6\:6062\:590d\:7cfb\:6570"},"rows"->Table[{i,N[100v1[[i]]],N[100v2[[i]]],N[ratios[[i]]],N[delta[[i]]],N[ee[[i]]]},{i,5}]|>|>;
 <|"metrics"->metrics,"tables"->tables,"series"-><|"momentum_deviation"-><|"x"->Range[5],"y"->N[eta],"x_label"->"\:6d4b\:91cf\:5e8f\:53f7","y_label"->"\:52a8\:91cf\:76f8\:5bf9\:4e8f\:635f / %"|>,"velocity_ratio"-><|"x"->Range[5],"y"->N[ratios],"x_label"->"\:6d4b\:91cf\:5e8f\:53f7","y_label"->"\:78b0\:540e\:901f\:5ea6\:6bd4"|>|>,"notes"->{"\:975e\:5f39\:6027\:6570\:636e\:6309\:91cd\:649e\:8f7b\:3001\:8f7b\:5757\:521d\:59cb\:9759\:6b62\:548c\:78b0\:540e\:7c98\:5408\:5904\:7406\:3002","\:5f39\:6027\:7ec4\:7f3a\:78b0\:524d\:901f\:5ea6\:ff0c\:65e0\:6cd5\:72ec\:7acb\:9a8c\:8bc1\:52a8\:91cf\:4e0e\:52a8\:80fd\:5b88\:6052\:6216\:76f4\:63a5\:6d4be\:3002","\:6761\:4ef6\:6062\:590d\:7cfb\:6570\:501f\:52a9\:5047\:5b9a\:52a8\:91cf\:5b88\:6052\:53cd\:63a8\:521d\:901f\:5ea6\:ff0c\:5c5e\:4e8e\:6a21\:578b\:8bca\:65ad\:3002"}|>
];
explore["restitution",r_] := With[{total=r["metrics"]["mass_total"]["value"],fraction=r["metrics"]["theoretical_energy_loss"]["value"]/100,v0=r["tables"]["inelastic_observations"]["rows"][[1,2]]/100},
 With[{m1=total(1-fraction),m2=total fraction},
 Manipulate[Plot[{(m1-x m2)v0/total,(1+x)m1 v0/total},{x,0,1},PlotStyle->{Black,Directive[GrayLevel[.4],Dashed]},
 PlotLegends->{Style["\:6ed1\:57571",FontFamily->"SimSun"],Style["\:6ed1\:57572",FontFamily->"SimSun"]},Frame->{{True,False},{True,False}},Axes->False,
 FrameLabel->{Style["\:6062\:590d\:7cfb\:6570 e",FontFamily->"SimSun"],Style["\:78b0\:540e\:901f\:5ea6 / (m s\:207b\:00b9)",FontFamily->"SimSun"]},BaseStyle->{FontFamily->"Times New Roman",FontSize->18},GridLines->Automatic,GridLinesStyle->Directive[GrayLevel[.9]],
 Epilog->{Black,PointSize[.018],Point[{{e,(m1-e m2)v0/total},{e,(1+e)m1 v0/total}}]},PlotRange->All,ImageSize->800,ImagePadding->{{95,30},{65,25}}],
 {{e,1,Style["\:6062\:590d\:7cfb\:6570",FontFamily->"SimSun"]},0,1,.01,Appearance->"Labeled"},ControlPlacement->Bottom,SaveDefinitions->True]]
];
