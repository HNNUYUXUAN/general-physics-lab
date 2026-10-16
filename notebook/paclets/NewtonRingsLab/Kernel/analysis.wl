nrRows[path_] := Module[{raw}, raw = Rest[Import[path, "CSV"]]; Map[If[StringQ[#], ToExpression[#], #] &, raw, {2}]];
nrMetric[value_, unit_] := <|"value" -> N[value], "unit" -> unit|>;
nrTable[headers_, rows_] := <|"headers" -> headers, "rows" -> rows|>;

compute[dir_] := Module[{cfg, wavelength, separation, rings, wedge, orders, diameters, squared, centered, slope, intercept, residuals, slopeUncertainty, pairs, radii, thicknesses, meanH, meanHA, lookup},
  cfg = Import[FileNameJoin[{dir, "experiment.json"}], "RawJSON"];
  wavelength = cfg["parameters"]["wavelength_nm"] 10^-6;
  separation = cfg["parameters"]["order_separation"];
  rings = nrRows[FileNameJoin[{dir, "data", "rings.csv"}]];
  wedge = nrRows[FileNameJoin[{dir, "data", "wedge.csv"}]];
  orders = rings[[All, 1]];
  diameters = rings[[All, 3]] - rings[[All, 2]];
  If[Length[DeleteDuplicates[orders]] != Length[orders] || Length[orders] < 3 || Min[diameters] <= 0 || Min[wedge[[All, {2, 3, 4}]]] <= 0, Return[$Failed]];
  squared = diameters^2;
  centered = orders - Mean[orders];
  slope = centered.(squared - Mean[squared])/(centered.centered);
  intercept = Mean[squared] - slope Mean[orders];
  residuals = squared - slope orders - intercept;
  slopeUncertainty = Sqrt[(residuals.residuals)/(Length[orders] - 2)/(centered.centered)];
  lookup = Association[MapThread[Round[#1] -> {#2, #3} &, {orders, diameters, squared}]];
  pairs = Table[If[KeyExistsQ[lookup, m + separation], {m, m + separation, lookup[m][[1]], lookup[m + separation][[1]], (lookup[m + separation][[2]] - lookup[m][[2]])/(4 separation wavelength)}, Nothing], {m, Sort[Keys[lookup]]}];
  If[Length[pairs] == 0, Return[$Failed]];
  radii = pairs[[All, 5]];
  thicknesses = Map[#[[2]] wavelength #[[4]]/(2 #[[3]]) &, wedge];
  meanH = Mean[thicknesses]; meanHA = StandardDeviation[thicknesses]/Sqrt[Length[thicknesses]];
  <|
    "metrics" -> <|
      "wavelength_nm" -> nrMetric[wavelength 10^6, "nm"],
      "radius_pair_mean_mm" -> nrMetric[Mean[radii], "mm"],
      "radius_pair_sd_mm" -> nrMetric[StandardDeviation[radii], "mm"],
      "radius_fit_mm" -> nrMetric[slope/(4 wavelength), "mm"],
      "radius_fit_standard_error_mm" -> nrMetric[slopeUncertainty/(4 wavelength), "mm"],
      "diameter_squared_slope_mm2" -> nrMetric[slope, "mm^2"],
      "diameter_squared_intercept_mm2" -> nrMetric[intercept, "mm^2"],
      "fit_r_squared" -> nrMetric[1 - (residuals.residuals)/((squared - Mean[squared]).(squared - Mean[squared])), "1"],
      "wire_diameter_um" -> nrMetric[meanH 1000, "um"],
      "wire_diameter_type_a_um" -> nrMetric[meanHA 1000, "um"],
      "wedge_angle_urad" -> nrMetric[Mean[Map[#[[2]] wavelength/(2 #[[3]]) &, wedge]] 10^6, "urad"]
    |>,
    "tables" -> <|
      "rings" -> nrTable[{"\:6697\:73af\:7ea7\:6570 $m$", "\:5de6\:8bfb\:6570 / mm", "\:53f3\:8bfb\:6570 / mm", "$D_m$ / mm"}, MapThread[{Round[#1[[1]]], #1[[2]], #1[[3]], Round[#2, .001]} &, {rings, diameters}]],
      "wedge" -> nrTable[{"\:6b21\:6570", "\:6761\:7eb9\:95f4\:9694\:6570 $N$", "$l_N$ / mm", "$L$ / mm"}, Map[{Round[#[[1]]], Round[#[[2]]], #[[3]], #[[4]]} &, wedge]],
      "pairs" -> nrTable[{"$m$", "$m+p$", "$D_m$ / mm", "$D_{m+p}$ / mm", "$R$ / mm"}, Map[{#[[1]], #[[2]], Round[#[[3]], .001], Round[#[[4]], .001], Round[#[[5]], .001]} &, pairs]],
      "thickness" -> nrTable[{"\:6b21\:6570", "$l_N$ / mm", "$h$ / mm"}, MapThread[{Round[#1[[1]]], #1[[3]], Round[#2, 10^-8]} &, {wedge, thicknesses}]],
      "fit" -> nrTable[{"$m$", "$D_m^2$ / mm$^2$", "\:62df\:5408\:503c / mm$^2$", "\:6b8b\:5dee / mm$^2$"}, MapThread[{Round[#1], Round[#2, 10^-6], Round[slope #1 + intercept, 10^-6], Round[#3, 10^-6]} &, {orders, squared, residuals}]]
    |>,
    "series" -> <|
      "ring-fit" -> <|"x" -> orders, "y" -> squared, "x_label" -> "\:6697\:73af\:7ea7\:6570 $m$", "y_label" -> "\:76f4\:5f84\:5e73\:65b9 $D_m^2$ / mm$^2$", "label" -> "\:89c2\:6d4b\:503c", "fit" -> True|>,
      "wire-repeat" -> <|"x" -> wedge[[All, 1]], "y" -> thicknesses 1000, "x_label" -> "\:6d4b\:91cf\:6b21\:6570", "y_label" -> "\:7ec6\:4e1d\:76f4\:5f84 $h$ / \:03bcm", "label" -> "\:4e94\:6b21\:91cd\:590d\:6d4b\:91cf"|>
    |>,
    "notes" -> {"\:9694\:7ea7\:5dee\:7684\:56db\:4e2a\:4f30\:8ba1\:5171\:4eab\:6697\:73af\:8bfb\:6570\:ff0c\:5f7c\:6b64\:76f8\:5173\:ff1b\:5176\:6807\:51c6\:5dee\:4ec5\:8868\:5f81\:7ed3\:679c\:79bb\:6563\:ff0c\:4e0d\:4f5c\:4e3a\:5747\:503c\:6807\:51c6\:4e0d\:786e\:5b9a\:5ea6\:3002", "\:62df\:5408\:6807\:51c6\:8bef\:5dee\:53ea\:6765\:81ea\:6b8b\:5dee\:ff0c\:672a\:5305\:542b\:663e\:5fae\:955c\:3001\:6ce2\:957f\:4e0e\:6a21\:578b\:7cfb\:7edf\:5206\:91cf\:3002", "\:7ec6\:4e1d\:76f4\:5f84 A \:7c7b\:4e0d\:786e\:5b9a\:5ea6\:53ea\:8868\:793a\:4e94\:6b21\:91cd\:590d\:6d4b\:91cf\:5747\:503c\:7684\:968f\:673a\:5206\:91cf\:3002", "N \:6309\:8bb0\:5f55\:7684 20 \:4e2a\:6761\:7eb9\:95f4\:9694\:4f7f\:7528\:ff0c\:6761\:7eb9\:7aef\:70b9\:8ba1\:6570\:7ea6\:5b9a\:672a\:53e6\:9644\:8bb0\:5f55\:3002"}
  |>
];

nrFitView[r_, drop_Integer] := Module[{x, y, keep, a, b, lambda, xx},
  x = r["series"]["ring-fit"]["x"]; y = r["series"]["ring-fit"]["y"];
  keep = If[drop == 0, Range[Length[x]], DeleteCases[Range[Length[x]], drop]];
  lambda = r["metrics"]["wavelength_nm"]["value"] 10^-6;
  a = ((x[[keep]] - Mean[x[[keep]]]).(y[[keep]] - Mean[y[[keep]]]))/Total[(x[[keep]] - Mean[x[[keep]]])^2];
  b = Mean[y[[keep]]] - a Mean[x[[keep]]];
  Column[{Row[{Style["\:66f2\:7387\:534a\:5f84 ", FontFamily -> "SimSun"], Style[Row[{"R = ", NumberForm[a/(4 lambda), {8, 3}], " mm"}], FontFamily -> "Times New Roman"]}],
    Show[ListPlot[Transpose[{x[[keep]], y[[keep]]}], PlotStyle -> Black, PlotMarkers -> {Graphics[{White, Disk[], Black, Circle[]}], 11}],
      Plot[a xx + b, {xx, 5, 30}, PlotStyle -> Directive[Black, AbsoluteThickness[1.5]]], Frame -> {{True, False}, {True, False}}, Axes -> False,
      FrameLabel -> {Row[{Style["\:6697\:73af\:7ea7\:6570 ", FontFamily -> "SimSun"], Style["m", FontFamily -> "Times New Roman"]}], Row[{Style["\:76f4\:5f84\:5e73\:65b9 ", FontFamily -> "SimSun"], Style[Row[{Superscript["D", 2], " / ", Superscript["mm", 2]}], FontFamily -> "Times New Roman"]}]},
      GridLines -> Automatic, GridLinesStyle -> GrayLevel[.9], BaseStyle -> {FontFamily -> "Times New Roman", FontSize -> 17}, ImageSize -> 650, ImagePadding -> {{75, 25}, {60, 25}}, PlotRange -> {{4, 31}, {0, 62}}]}, Alignment -> Center]
];
nrGapView[r_, fraction_] := Module[{radius, lambda, x, y},
  radius = r["metrics"]["radius_fit_mm"]["value"]; lambda = r["metrics"]["wavelength_nm"]["value"] 10^-6;
  DensityPlot[(1 - Cos[4 Pi (fraction lambda + (x^2 + y^2)/(2 radius))/lambda])/2, {x, -4, 4}, {y, -4, 4},
    ColorFunction -> (GrayLevel[#] &), ColorFunctionScaling -> False, PlotLegends -> BarLegend[{GrayLevel, {0, 1}}, LegendLabel -> Row[{"I / ", Subscript["I", "max"]}]],
    FrameLabel -> {Row[{Style["\:6a2a\:5411\:4f4d\:7f6e ", FontFamily -> "SimSun"], Style["x / mm", FontFamily -> "Times New Roman"]}], Row[{Style["\:7eb5\:5411\:4f4d\:7f6e ", FontFamily -> "SimSun"], Style["y / mm", FontFamily -> "Times New Roman"]}]},
    PlotPoints -> 601, MaxRecursion -> 0, ImageSize -> 610, BaseStyle -> {FontFamily -> "Times New Roman", FontSize -> 17}]
];
explore["ring-selection", r_] := Manipulate[nrFitView[r, drop], {{drop, 0, "\:6570\:636e\:9009\:62e9"}, {0 -> "\:5168\:90e8\:516d\:7ec4", 1 -> "\:6682\:6392\:9664\:7b2c5\:7ea7", 2 -> "\:6682\:6392\:9664\:7b2c10\:7ea7", 3 -> "\:6682\:6392\:9664\:7b2c15\:7ea7", 4 -> "\:6682\:6392\:9664\:7b2c20\:7ea7", 5 -> "\:6682\:6392\:9664\:7b2c25\:7ea7", 6 -> "\:6682\:6392\:9664\:7b2c30\:7ea7"}}, SaveDefinitions -> True];
explore["contact-gap", r_] := Manipulate[nrGapView[r, fraction], {{fraction, 0, "\:4e2d\:5fc3\:95f4\:9699 t\:2080 / \:03bb"}, 0, .5, .05, Appearance -> "Labeled"}, SaveDefinitions -> True];
