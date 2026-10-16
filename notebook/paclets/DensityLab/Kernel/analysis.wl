compute[dir_] := Module[
  {cfg, solid, liquid, vectors, means, m, a, e, w, b, rw, limit, ua, ub, uc,
   rs, rb, ds, dl, usa, uba, us, ul, metrics, tables, shifts, series, metric},
  cfg = Import[FileNameJoin[{dir, "experiment.json"}], "RawJSON"];
  solid = Rest[Import[FileNameJoin[{dir, "data", "solid.csv"}], "CSV"]];
  liquid = Rest[Import[FileNameJoin[{dir, "data", "liquid.csv"}], "CSV"]];
  vectors = Join[Transpose[solid][[2 ;; 3]], Transpose[liquid][[2 ;; 4]]];
  If[!And @@ (Length[#] == 3 && VectorQ[#, NumericQ] & /@ vectors), Return[$Failed]];
  means = Mean /@ vectors;
  {m, a, e, w, b} = means;
  If[!TrueQ[m > a > 0 && b > e && w > e], Return[$Failed]];
  rw = cfg["parameters"]["water_density_g_cm3"];
  limit = cfg["parameters"]["assumed_mass_error_limit_g"];
  ua = StandardDeviation[#]/Sqrt[Length[#]] & /@ vectors;
  ub = limit/Sqrt[3]; uc = Sqrt[ua^2 + ub^2];
  rs = rw m/(m - a); rb = rw (b - e)/(w - e);
  ds = {-rw a/(m - a)^2, rw m/(m - a)^2};
  dl = {rw (b - w)/(w - e)^2, -rw (b - e)/(w - e)^2, rw/(w - e)};
  usa = Sqrt[Total[(ds ua[[1 ;; 2]])^2]];
  uba = Sqrt[Total[(dl ua[[3 ;; 5]])^2]];
  us = Sqrt[Total[(ds uc[[1 ;; 2]])^2]];
  ul = Sqrt[Total[(dl uc[[3 ;; 5]])^2]];
  metric[v_, unit_] := <|"value" -> N[v], "unit" -> unit|>;
  metrics = AssociationThread[
    {"air_mass", "submerged_mass", "empty_mass", "water_total_mass", "brine_total_mass"},
    metric[#, "g"] & /@ means];
  AssociateTo[metrics, {
    "solid_density" -> <|"value" -> N[rs], "unit" -> "g/cm^3", "uncertainty" -> N[us]|>,
    "liquid_density" -> <|"value" -> N[rb], "unit" -> "g/cm^3", "uncertainty" -> N[ul]|>,
    "solid_uncertainty_a" -> metric[usa, "g/cm^3"],
    "liquid_uncertainty_a" -> metric[uba, "g/cm^3"],
    "solid_uncertainty_conditional" -> metric[us, "g/cm^3"],
    "liquid_uncertainty_conditional" -> metric[ul, "g/cm^3"],
    "solid_relative_uncertainty" -> metric[100 us/rs, "%"],
    "liquid_relative_uncertainty" -> metric[100 ul/rb, "%"],
    "solid_volume" -> metric[(m - a)/rw, "cm^3"],
    "bottle_volume" -> metric[(w - e)/rw, "cm^3"]}];
  tables = <|
    "solid_observations" -> <|"headers" -> {"\:6d4b\:91cf\:6b21\:6570", "$m / \\mathrm{g}$", "$m_{\\mathrm{s}} / \\mathrm{g}$"},
       "rows" -> Append[solid, {"\:5e73\:5747\:503c", m, a}]|>,
    "liquid_observations" -> <|"headers" -> {"\:6d4b\:91cf\:6b21\:6570", "$m_0 / \\mathrm{g}$", "$m_{\\mathrm{w}} / \\mathrm{g}$", "$m_{\\mathrm{b}} / \\mathrm{g}$"},
       "rows" -> Append[liquid, {"\:5e73\:5747\:503c", e, w, b}]|>,
    "mass_uncertainty" -> <|"headers" -> {"\:8d28\:91cf", "$u_A / \\mathrm{g}$", "$u_B / \\mathrm{g}$", "$u_c / \\mathrm{g}$"},
       "rows" -> MapThread[{#1, N[#2], N[ub], N[#3]} &, {{"$m$", "$m_{\\mathrm{s}}$", "$m_0$", "$m_{\\mathrm{w}}$", "$m_{\\mathrm{b}}$"}, ua, uc}]|>,
    "density_results" -> <|"headers" -> {"\:5bf9\:8c61", "$\\rho / (\\mathrm{g\\,cm^{-3}})$", "$u_A(\\rho) / (\\mathrm{g\\,cm^{-3}})$", "$u_c(\\rho) / (\\mathrm{g\\,cm^{-3}})$"},
       "rows" -> {{"\:5408\:91d1\:5757", N[rs], N[usa], N[us]}, {"\:76d0\:6c34", N[rb], N[uba], N[ul]}}|>,
    "sensitivity" -> <|"headers" -> {"\:8f93\:5165\:8d28\:91cf", "$\\partial\\rho/\\partial m / \\mathrm{cm^{-3}}$", "\:6761\:4ef6\:65b9\:5dee\:8d21\:732e\:5360\:6bd4 / %"},
       "rows" -> Join[
         MapThread[{#1, N[#2], N[100 (#2 #3)^2/us^2]} &, {{"$m$", "$m_{\\mathrm{s}}$"}, ds, uc[[1 ;; 2]]}],
         MapThread[{#1, N[#2], N[100 (#2 #3)^2/ul^2]} &, {{"$m_0$", "$m_{\\mathrm{w}}$", "$m_{\\mathrm{b}}$"}, dl, uc[[3 ;; 5]]}]]|>|>;
  shifts = N[Range[-50, 50]/1000];
  series = <|
    "solid_repeat" -> <|"x" -> {1, 2, 3}, "y" -> N[MapThread[rw #1/(#1 - #2) &, vectors[[1 ;; 2]]]], "x_label" -> "\:6d4b\:91cf\:6b21\:6570", "y_label" -> "\:5408\:91d1\:5bc6\:5ea6 $\\rho_{\\mathrm{s}}$ / (g cm$^{-3}$)"|>,
    "liquid_repeat" -> <|"x" -> {1, 2, 3}, "y" -> N[MapThread[rw (#3 - #1)/(#2 - #1) &, vectors[[3 ;; 5]]]], "x_label" -> "\:6d4b\:91cf\:6b21\:6570", "y_label" -> "\:76d0\:6c34\:5bc6\:5ea6 $\\rho_{\\mathrm{b}}$ / (g cm$^{-3}$)"|>,
    "apparent_bias" -> <|"x" -> shifts, "y" -> N[rw m/(m - a - shifts)], "x_label" -> "\:89c6\:8d28\:91cf\:504f\:79fb $\\delta m_{\\mathrm{s}}$ / g", "y_label" -> "\:5408\:91d1\:5bc6\:5ea6 $\\rho_{\\mathrm{s}}$ / (g cm$^{-3}$)"|>|>;
  <|"metrics" -> metrics, "tables" -> tables, "series" -> series,
    "notes" -> {"0.01 g \:8bef\:5dee\:9650\:6765\:81ea\:8bfb\:6570\:4f4d\:6570\:63a8\:65ad\:ff0cA+B \:4e0d\:786e\:5b9a\:5ea6\:4e3a\:6761\:4ef6\:7ed3\:679c\:3002", "\:5ffd\:7565\:6c34\:5bc6\:5ea6\:7684\:4e0d\:786e\:5b9a\:5ea6\:ff1b\:5404\:6b21\:79f0\:91cf\:5747\:503c\:7684\:534f\:65b9\:5dee\:6309\:96f6\:5904\:7406\:ff0c\:5171\:4eab\:7a7a\:74f6\:8d28\:91cf\:901a\:8fc7\:504f\:5bfc\:76f4\:63a5\:4f20\:64ad\:3002"}|>
];

densityDerivation[] := Column[{
 TraditionalForm[HoldForm[Subscript[\[Rho], s] == Subscript[\[Rho], w] m/(m - Subscript[m, s])]],
 TraditionalForm[HoldForm[Subscript[\[Rho], b] == Subscript[\[Rho], w] (Subscript[m, b] - Subscript[m, 0])/(Subscript[m, w] - Subscript[m, 0])]],
 TraditionalForm[HoldForm[{-(Subscript[\[Rho], w] Subscript[m, s])/(m - Subscript[m, s])^2, Subscript[\[Rho], w] m/(m - Subscript[m, s])^2}]],
 TraditionalForm[HoldForm[{Subscript[\[Rho], w] (Subscript[m, b] - Subscript[m, w])/(Subscript[m, w] - Subscript[m, 0])^2, -Subscript[\[Rho], w] (Subscript[m, b] - Subscript[m, 0])/(Subscript[m, w] - Subscript[m, 0])^2, Subscript[\[Rho], w]/(Subscript[m, w] - Subscript[m, 0])}]]},
 Alignment -> Center, Spacings -> 1, BaseStyle -> {FontFamily -> "Times New Roman", FontSize -> 18}];

explore["mass-bias", r_] := With[
 {m = r["metrics"]["air_mass"]["value"],
  a = r["metrics"]["submerged_mass"]["value"],
  rw = r["metrics"]["solid_density"]["value"] (r["metrics"]["air_mass"]["value"] - r["metrics"]["submerged_mass"]["value"])/r["metrics"]["air_mass"]["value"]},
 Manipulate[
  Plot[rw m/(m - a - x), {x, -.05, .05}, PlotStyle -> Black,
   Frame -> {{True, False}, {True, False}}, Axes -> False,
   FrameLabel -> {
    Row[{Style["\:89c6\:8d28\:91cf\:504f\:79fb", FontFamily -> "SimSun"], Style[" / g", FontFamily -> "Times New Roman"]}],
    Row[{Style["\:5408\:91d1\:5bc6\:5ea6", FontFamily -> "SimSun"], Style[" / (g ", FontFamily -> "Times New Roman"], Superscript[Style["cm", FontFamily -> "Times New Roman"], -3], Style[")", FontFamily -> "Times New Roman"]}]},
   BaseStyle -> {FontFamily -> "Times New Roman", FontSize -> 18},
   GridLines -> Automatic, GridLinesStyle -> Directive[GrayLevel[.9]],
   Epilog -> {Black, PointSize[.018], Point[{delta, rw m/(m - a - delta)}]},
   PlotRange -> All, ImageSize -> 800, ImagePadding -> {{95, 30}, {65, 25}}],
  {{delta, 0, Style["\:89c6\:8d28\:91cf\:504f\:79fb / g", FontFamily -> "SimSun"]}, -.05, .05, .001, Appearance -> "Labeled"},
  SaveDefinitions -> True, ControlPlacement -> Bottom]
];
