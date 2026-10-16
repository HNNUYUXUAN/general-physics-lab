lineFit[x_, y_] := Module[{xc, yc, k, c, res, sse, rr, sy, uk, ucc},
 xc = x - Mean[x]; yc = y - Mean[y]; k = xc.yc/(xc.xc); c = Mean[y] - k Mean[x];
 res = y - (k x + c); sse = res.res; rr = xc.yc/Sqrt[(xc.xc) (yc.yc)];
 sy = Sqrt[sse/(Length[x] - 2)]; uk = sy/Sqrt[xc.xc]; ucc = sy Sqrt[1/Length[x] + Mean[x]^2/(xc.xc)];
 {k, c, rr, sse, uk, ucc, res}];

compute[dir_] := Module[{cfg, records, s, gravity, masses = {}, averages = {}, uas = {}, processed = {}, raw = {}, block, vals, row, acc, k, c, rr, sse, uk, ucc, residual, k2, c2, r2, tail, metrics = <||>, tables, series, add},
 cfg = Import[FileNameJoin[{dir, "experiment.json"}], "RawJSON"];
 records = Rest[Import[FileNameJoin[{dir, "data", "observations.csv"}], "CSV"]];
 s = cfg["parameters"]["gate_spacing_m"]; gravity = cfg["parameters"]["gravity_m_s2"];
 Do[
  block = Select[records, #[[1]] == group &]; If[Length[block] != 5, Return[$Failed]];
  vals = Table[
    acc = If[row[[4]] == "direct", row[[7]], (row[[6]]^2 - row[[5]]^2)/(200 s)];
    AppendTo[raw, {group, row[[3]], row[[2]], If[row[[4]] == "direct", row[[7]], row[[5]]], If[row[[4]] == "direct", "\:2014", row[[6]]], row[[7]]}];
    AppendTo[processed, {group, row[[2]], N[acc], N[acc - row[[7]]]}]; acc,
    {row, block}];
  AppendTo[masses, block[[1, 3]]]; AppendTo[averages, Mean[vals]]; AppendTo[uas, StandardDeviation[vals]/Sqrt[5]],
  {group, 1, 5}];
 {k, c, rr, sse, uk, ucc, residual} = lineFit[averages, masses];
 add[key_, val_, unit_, label_] := AssociateTo[metrics, key -> <|"value" -> N[val], "unit" -> unit, "label" -> label|>];
 add[key_, val_, unit_, label_, u_] := AssociateTo[metrics, key -> <|"value" -> N[val], "unit" -> unit, "label" -> label, "uncertainty" -> N[u]|>];
 Do[add["acceleration_" <> ToString[i], averages[[i]], "cm/s^2", "\:7b2c" <> ToString[i] <> "\:7ec4\:5e73\:5747\:52a0\:901f\:5ea6", uas[[i]]], {i, 5}];
 add["slope", k, "g/(cm/s^2)", "\:8d28\:91cf\:2014\:52a0\:901f\:5ea6\:62df\:5408\:659c\:7387", uk];
 add["intercept", c, "g", "\:62df\:5408\:622a\:8ddd", ucc];
 add["correlation", rr, "1", "\:76f8\:5173\:7cfb\:6570"]; add["r_squared", rr^2, "1", "\:51b3\:5b9a\:7cfb\:6570"];
 add["inferred_system_mass", 100 gravity k, "g", "\:659c\:7387\:63a8\:7b97\:7cfb\:7edf\:8d28\:91cf", 100 gravity uk];
 add["equivalent_resistance", gravity c/1000, "N", "\:622a\:8ddd\:7b49\:6548\:963b\:529b", gravity ucc/1000];
 add["sse", sse, "g^2", "\:62df\:5408\:6b8b\:5dee\:5e73\:65b9\:548c"];
 {k2, c2, r2, tail} = Join[Take[lineFit[Rest[averages], Rest[masses]], 3], {0}];
 add["slope_without_group1", k2, "g/(cm/s^2)", "\:53bb\:6389\:7b2c\:4e00\:7ec4\:540e\:7684\:659c\:7387"];
 add["intercept_without_group1", c2, "g", "\:53bb\:6389\:7b2c\:4e00\:7ec4\:540e\:7684\:622a\:8ddd"];
 add["correlation_without_group1", r2, "1", "\:53bb\:6389\:7b2c\:4e00\:7ec4\:540e\:7684\:76f8\:5173\:7cfb\:6570"];
 tables = <|
 "observations" -> <|"headers" -> {"\:7ec4\:522b", "$m_0 / \\mathrm{g}$", "\:6b21\:6570", "\:6570\:636e1\:ff08\:901f\:5ea6\:6216\:52a0\:901f\:5ea6\:ff09", "\:6570\:636e2\:901f\:5ea6 / (cm s\:207b\:00b9)", "\:8bb0\:5f55\:52a0\:901f\:5ea6 / (cm s\:207b\:00b2)"}, "rows" -> raw|>,
 "recalculation" -> <|"headers" -> {"\:7ec4\:522b", "\:6b21\:6570", "\:91c7\:7528\:52a0\:901f\:5ea6 / (cm s\:207b\:00b2)", "\:76f8\:5bf9\:8bb0\:5f55\:5217\:5dee\:503c / (cm s\:207b\:00b2)"}, "rows" -> processed|>,
 "summary" -> <|"headers" -> {"\:7ec4\:522b", "$m_0 / \\mathrm{g}$", "$F / \\mathrm{N}$", "$\\bar a / (\\mathrm{cm\\,s^{-2}})$", "$u_A(\\bar a) / (\\mathrm{cm\\,s^{-2}})$", "\:8d28\:91cf\:62df\:5408\:6b8b\:5dee / g"},
  "rows" -> Table[{i, N[masses[[i]]], N[masses[[i]] gravity/1000], N[averages[[i]]], N[uas[[i]]], N[residual[[i]]]}, {i, 5}]|>|>;
 series = <|"force_acceleration" -> <|"x" -> N[averages], "y" -> N[masses], "x_label" -> "\:5e73\:5747\:52a0\:901f\:5ea6 / (cm s\:207b\:00b2)", "y_label" -> "\:60ac\:6302\:8d28\:91cf / g", "fit" -> True|>,
 "force_residual" -> <|"x" -> N[averages], "y" -> N[residual], "x_label" -> "\:5e73\:5747\:52a0\:901f\:5ea6 / (cm s\:207b\:00b2)", "y_label" -> "\:8d28\:91cf\:62df\:5408\:6b8b\:5dee / g"|>|>;
 <|"metrics" -> metrics, "tables" -> tables, "series" -> series, "notes" -> {"F1\:4e3a\:76f4\:63a5\:52a0\:901f\:5ea6\:ff1bF2-F5\:7531\:539f\:59cb\:901f\:5ea6\:53ca0.500m\:95f4\:8ddd\:91cd\:7b97\:3002", "\:56de\:5f52\:4e3a\:7b49\:6743\:666e\:901a\:6700\:5c0f\:4e8c\:4e58\:ff1b\:659c\:7387\:4e0e\:622a\:8ddd\:4e0d\:786e\:5b9a\:5ea6\:53ea\:8868\:793a\:56de\:5f52\:6b8b\:5dee\:4f30\:8ba1\:3002", "\:6ca1\:6709\:7cfb\:7edf\:72ec\:7acb\:79f0\:91cf\:503c\:53ca\:4eea\:5668\:7cbe\:5ea6\:ff0c\:4e0d\:80fd\:58f0\:79f0\:5b8c\:6210\:5b8c\:6574\:4e0d\:786e\:5b9a\:5ea6\:8bc4\:4f30\:6216\:4e25\:683c\:6bd4\:4f8b\:9a8c\:8bc1\:3002"}|>
];

explore["fit-selection", r_] := With[{xx = r["series"]["force_acceleration"]["x"], yy = r["series"]["force_acceleration"]["y"]},
 Manipulate[Module[{indices, fit, low, high},
  indices = If[selection == 0, Range[5], DeleteCases[Range[5], selection]];
  fit = lineFit[xx[[indices]], yy[[indices]]]; low = Min[xx] - 5; high = Max[xx] + 5;
  Show[Plot[fit[[1]] x + fit[[2]], {x, low, high}, PlotStyle -> Black],
    ListPlot[Transpose[{xx, yy}], PlotStyle -> Black, PlotMarkers -> {"\:25cb", 12}],
    Frame -> {{True, False}, {True, False}}, Axes -> False,
    FrameLabel -> {Style["\:5e73\:5747\:52a0\:901f\:5ea6 / (cm s\:207b\:00b2)", FontFamily -> "SimSun"], Style["\:60ac\:6302\:8d28\:91cf / g", FontFamily -> "SimSun"]},
    BaseStyle -> {FontFamily -> "Times New Roman", FontSize -> 18},
    GridLines -> Automatic, GridLinesStyle -> Directive[GrayLevel[.9]],
    PlotRange -> All, ImageSize -> 800, ImagePadding -> {{95, 30}, {65, 25}}]],
  {{selection, 0, Style["\:62df\:5408\:7ec4\:522b", FontFamily -> "SimSun"]}, {0 -> "\:5168\:90e8\:4e94\:7ec4", 1 -> "\:7701\:7565\:7b2c1\:7ec4", 2 -> "\:7701\:7565\:7b2c2\:7ec4", 3 -> "\:7701\:7565\:7b2c3\:7ec4", 4 -> "\:7701\:7565\:7b2c4\:7ec4", 5 -> "\:7701\:7565\:7b2c5\:7ec4"}, ControlType -> PopupMenu},
  SaveDefinitions -> True, ControlPlacement -> Bottom]
];
