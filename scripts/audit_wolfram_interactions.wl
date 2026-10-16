(* Standalone helper. Loading defines functions only; it never opens notebooks.
   Root runs this in its serialized Wolfram queue, for example:
   Get[".../rollout/wolfram_interaction_response_audit.wl"];
   InteractionResponseAudit`AuditProject[projectRoot, {"course-01/density"}, outputJSON];
   Use All instead of the ID list for every newly authored package. *)
BeginPackage["InteractionResponseAudit`"];
AuditProject::usage="AuditProject[projectRoot, ids|All, outputJSON] evaluates actual held Manipulate model bodies at default and one changed value per declared control.";
SelfCheck::usage="SelfCheck[] verifies capture, numeric/enumerated/multiple-control parsing and graphics-response fingerprints using synthetic controls.";
Begin["`Private`"];

SetAttributes[captureManipulate, HoldAllComplete];
captureManipulate[args___] := HoldComplete[args];
heldParts[h_HoldComplete] := Table[Extract[h, {i}, HoldComplete], {i, Length[h]}];
numericScalarQ[x_] := NumericQ[x] && TrueQ[Im[N[x]] == 0];
scalarQ[x_] := numericScalarQ[x] || StringQ[x] || x === True || x === False;
scalarEqual[a_, b_] := If[NumericQ[a] && NumericQ[b], TrueQ[a == b], SameQ[a, b]];
heldName[HoldComplete[s_Symbol]] := Context[Unevaluated[s]] <> SymbolName[Unevaluated[s]];
heldRule[HoldComplete[s_Symbol], value_] := HoldPattern[s] -> value;
failure[reason_] := <|"status" -> "needs_review", "reason" -> reason|>;
finiteOutputQ[output_] := FreeQ[output, $Failed | $Aborted | $TimedOut | _Failure | Indeterminate | ComplexInfinity | _DirectedInfinity];

(* Labels in enumeration rules are never used as parameter values. *)
choiceValues[HoldComplete[values_List]] := Module[{raw = ReleaseHold[HoldComplete[values]], result},
 result = raw /. Rule[value_, label_] :> value;
 If[VectorQ[result, scalarQ], result, $Failed]
];
choiceValues[_] := $Failed;
parseControl[HoldComplete[{{symbol_Symbol, default_, label___}, domain___}]] := Module[
 {held = HoldComplete[symbol], initial, parts, first, choices, low, high, step, alternative, candidates},
 initial = Quiet[Check[ReleaseHold[HoldComplete[default]], $Failed]];
 If[!scalarQ[initial], Return[failure["Non-scalar or dependent default requires explicit review"]]];
 parts = heldParts[HoldComplete[domain]];
 If[parts === {}, Return[failure["Control has no declared parameter domain"]]];
 first = First[parts]; choices = choiceValues[first];
 If[choices =!= $Failed,
   If[!AnyTrue[choices, scalarEqual[#, initial] &], Return[failure["Default is outside the declared enumeration"]]];
   candidates = Select[choices, !scalarEqual[#, initial] &];
   If[candidates === {}, Return[failure["No non-default enumerated value exists"]]];
   alternative = First[candidates],
   If[Length[parts] < 2, Return[failure["Unsupported control specification"]]];
   low = Quiet[Check[ReleaseHold[parts[[1]]], $Failed]];
   high = Quiet[Check[ReleaseHold[parts[[2]]], $Failed]];
   If[!numericScalarQ[low] || !numericScalarQ[high] || !numericScalarQ[initial] || !TrueQ[low <= initial <= high] || !TrueQ[low < high],
     Return[failure["Numeric domain/default could not be verified"]]];
   step = If[Length[parts] >= 3, Quiet[Check[ReleaseHold[parts[[3]]], $Failed]], $Failed];
   candidates = If[numericScalarQ[step] && TrueQ[step > 0],
     Select[{initial + step, initial - step}, TrueQ[low <= # <= high] && !TrueQ[# == initial] &],
     Select[{(low + high)/2, low, high}, !TrueQ[# == initial] &]];
   If[candidates === {}, Return[failure["No verified non-default numeric value exists"]]];
   alternative = First[candidates]
 ];
 <|"status" -> "parsed", "symbol" -> held, "name" -> heldName[held], "default" -> initial, "changed" -> alternative,
   "specification_sha256" -> IntegerString[Hash[HoldComplete[{{symbol, default, label}, domain}], "SHA256"], 16, 64]|>
];
parseControl[_] := failure["Control shape is unsupported; no default/domain guessed"];
optionSpecQ[HoldComplete[_Rule | _RuleDelayed]] := True;
optionSpecQ[_] := False;
separatorSpecQ[HoldComplete[Delimiter | _String]] := True;
separatorSpecQ[_] := False;

(* Fingerprint model geometry plus markers. Epilog matters for controls that
   move a selected marker along an otherwise fixed curve. Plot labels, sampled
   rendering metadata and Manipulate UI do not count as physical response. *)
(* Strip charting tags and user-interface wrappers while retaining primitives
   and geometric transforms. Plotting may allocate fresh Tag$ symbols on each
   evaluation; these tags are not a model response. Tooltip text is likewise
   excluded, but the underlying geometric expression remains. *)
stripGeometricMetadata[expression_] := expression //. {
 HoldPattern[Annotation[geometry_, metadata___]] :> geometry,
 HoldPattern[Tooltip[geometry_, metadata___]] :> geometry,
 HoldPattern[StatusArea[geometry_, metadata___]] :> geometry,
 HoldPattern[Mouseover[geometry_, alternate___]] :> geometry,
 HoldPattern[EventHandler[geometry_, handlers___]] :> geometry,
 HoldPattern[Button[geometry_, action___]] :> geometry,
 HoldPattern[Interpretation[geometry_, interpretation___]] :> geometry,
 HoldPattern[TagBox[geometry_, tags___]] :> geometry,
 HoldPattern[TooltipBox[geometry_, tags___]] :> geometry,
 HoldPattern[AnnotationBox[geometry_, tags___]] :> geometry
};
graphicsPayload[g_] := Module[{normal = Normal[g], overlays},
 (* Preserve both immediate and delayed overlay rules, including options
    nested in an option list. Check the actual graphic and its Normal form:
    Normal may reorganize Charting structures. Repeated overlays are deduped. *)
 overlays = DeleteDuplicates[Join[
   Cases[{g, normal}, HoldPattern[Rule[(Epilog | Prolog), value_]] :> value, Infinity],
   Cases[{g, normal}, HoldPattern[RuleDelayed[(Epilog | Prolog), value_]] :> value, Infinity]
 ]];
 stripGeometricMetadata[{First[normal], overlays}]
];
payload[output_] := Module[{graphics},
 graphics = Cases[output, g : (_Graphics | _Graphics3D) :> graphicsPayload[g], {0, Infinity}];
 If[graphics === {}, output, graphics]
];
unresolvedHeads[output_, context_String] := DeleteDuplicates[Join[
 Cases[output, expression : (_Plot | _ListPlot | _ListLinePlot | _ParametricPlot | _LogLogPlot | _Show | _Module | _With | _If | _Switch | _Which | _NDSolve | _DSolve | _NIntegrate | _FindRoot | _LinearModelFit | _Manipulate | _DynamicModule | _Dynamic) :> ToString[Head[expression], InputForm], {0, Infinity}],
 Cases[output, expression : head_Symbol[___] /; StringStartsQ[Context[Unevaluated[head]], context] :> Context[Unevaluated[head]] <> SymbolName[Unevaluated[head]], {0, Infinity}]
]];
evaluateBody[body_HoldComplete, controls_List, values_List, context_String] := Module[
 {rules, output, messages, unresolved, fingerprint},
 rules = MapThread[heldRule[#1["symbol"], #2] &, {controls, values}];
 Block[{$MessageList = {}},
  output = Quiet[TimeConstrained[CheckAbort[ReleaseHold[body /. rules], $Aborted], 90, $TimedOut]];
  messages = ToString[#, InputForm] & /@ $MessageList
 ];
 unresolved = unresolvedHeads[output, context];
 fingerprint = IntegerString[Hash[payload[output], "SHA256"], 16, 64];
 <|"status" -> If[finiteOutputQ[output] && output =!= Null && messages === {} && unresolved === {}, "evaluated", "needs_review"],
   "output_head" -> ToString[Head[output], InputForm], "response_sha256" -> fingerprint,
   "graphics_count" -> Length[Cases[output, _Graphics | _Graphics3D, {0, Infinity}]],
   "messages" -> messages, "unresolved_heads" -> unresolved|>
];

auditHeld[captured_, context_String] := Module[{args, body, specs, controls, defaults, baseline, repeat, changes, values, trial},
 If[!MatchQ[captured, _HoldComplete] || Length[captured] < 2, Return[failure["Actual explore did not produce one captured Manipulate"]]];
 args = heldParts[captured]; body = First[args];
 specs = Select[Rest[args], !optionSpecQ[#] && !separatorSpecQ[#] &];
 controls = parseControl /@ specs;
 If[controls === {} || AnyTrue[controls, #["status"] =!= "parsed" &],
   Return[<|"status" -> "needs_review", "reason" -> "Some actual control specifications are unsupported", "control_parse" -> (KeyDrop[#, {"symbol"}] & /@ controls)|>]];
 defaults = Lookup[controls, "default"];
 baseline = evaluateBody[body, controls, defaults, context];
 repeat = evaluateBody[body, controls, defaults, context];
 changes = Table[
  values = ReplacePart[defaults, i -> controls[[i]]["changed"]];
  trial = evaluateBody[body, controls, values, context];
  Join[KeyDrop[controls[[i]], {"symbol", "status"}], <|"evaluation" -> trial,
    "response_changed" -> (baseline["response_sha256"] =!= trial["response_sha256"]),
    "status" -> If[baseline["status"] === "evaluated" && repeat["status"] === "evaluated" && baseline["response_sha256"] === repeat["response_sha256"] && trial["status"] === "evaluated" && baseline["response_sha256"] =!= trial["response_sha256"], "passed", "needs_review"]|>],
  {i, Length[controls]}];
 <|"status" -> If[AllTrue[changes, #["status"] === "passed" &], "passed", "needs_review"],
   "held_body_sha256" -> IntegerString[Hash[body, "SHA256"], 16, 64], "default_evaluation" -> baseline,
   "default_repeat" -> repeat, "default_deterministic" -> (baseline["response_sha256"] === repeat["response_sha256"]), "controls" -> changes|>
];

SelfCheck[] := Module[{captured, report, unsupported, metadataStable, geometrySensitive, epilogSensitive, delayedEpilogSensitive, mixedNumericEnumeration},
 captured = Block[{System`Manipulate = captureManipulate},
   Manipulate[Graphics[{Point[{x, y}]}], {{x, 0, "x"}, 0, 2, .5}, {{y, 1, "y"}, {0 -> "zero", 1 -> "one"}}]];
 report = auditHeld[captured, "NoSyntheticPrivateContext`"];
 unsupported = parseControl[HoldComplete[{z, 0, 1}]];
 mixedNumericEnumeration = parseControl[HoldComplete[{{z, 1, "numeric enumeration"}, {0.5, 1.0, 2.0}}]];
 metadataStable = SameQ[
   Hash[payload[Graphics[Annotation[Tooltip[Point[{0, 1}], "first tooltip"], Unique["tag"]]]], "SHA256"],
   Hash[payload[Graphics[Annotation[Tooltip[Point[{0, 1}], "second tooltip"], Unique["tag"]]]], "SHA256"]];
 geometrySensitive = UnsameQ[
   Hash[payload[Graphics[Point[{0, 1}]]], "SHA256"],
   Hash[payload[Graphics[Point[{0, 2}]]], "SHA256"]];
 epilogSensitive = UnsameQ[
   Hash[payload[Graphics[Line[{{0, 0}, {1, 1}}], Epilog -> Point[{0, 0}]]], "SHA256"],
   Hash[payload[Graphics[Line[{{0, 0}, {1, 1}}], Epilog -> Point[{1, 1}]]], "SHA256"]];
 delayedEpilogSensitive = UnsameQ[
   Hash[payload[Graphics[Line[{{0, 0}, {1, 1}}], Epilog :> Point[{0, 0}]]], "SHA256"],
   Hash[payload[Graphics[Line[{{0, 0}, {1, 1}}], Epilog :> Point[{1, 1}]]], "SHA256"]];
 <|"status" -> If[report["status"] === "passed" && Length[report["controls"]] === 2 && unsupported["status"] === "needs_review" && metadataStable && geometrySensitive && epilogSensitive && delayedEpilogSensitive && mixedNumericEnumeration["status"] === "parsed" && !scalarEqual[mixedNumericEnumeration["default"], mixedNumericEnumeration["changed"]], "passed", "needs_review"],
   "multiple_control_model" -> report, "unsupported_control_preserved" -> unsupported,
   "metadata_independent_fingerprint" -> metadataStable, "geometry_sensitive_fingerprint" -> geometrySensitive,
   "epilog_sensitive_fingerprint" -> epilogSensitive, "delayed_epilog_sensitive_fingerprint" -> delayedEpilogSensitive,
   "integer_default_real_enumeration" -> KeyDrop[mixedNumericEnumeration, {"symbol"}]|>
];

auditExperiment[base_String, item_Association] := Module[
 {id = item["id"], exp, author, paclet, context, package, keys, loaded, loadMessages, r, fn, reports, captured, captureMessages, hashes},
 exp = FileNameJoin[Prepend[StringSplit[id, "/"], FileNameJoin[{base, "experiments"}]]];
 If[Lookup[item, "status", ""] === "approved_baseline", Return[<|"experiment" -> id, "status" -> "approved_baseline_untouched"|>]];
 author = Quiet[Check[Import[FileNameJoin[{exp, "authoring.json"}], "RawJSON"], $Failed]];
 If[!AssociationQ[author], Return[Join[<|"experiment" -> id|>, failure["Authoring manifest is unavailable"]]]];
 keys = DeleteDuplicates[Flatten[StringCases[Lookup[#, "wolfram", ""], RegularExpression["exploreView\\[\"([^\"]+)\"\\]"] -> "$1"] & /@ Lookup[author, "expansions", {}]]];
 If[keys === {}, Return[<|"experiment" -> id, "status" -> "not_applicable_static", "provided_controls" -> 0|>]];
 paclet = author["paclet"]; context = paclet <> "`Private`";
 package = FileNameJoin[{base, "notebook", "paclets", paclet, "Kernel", paclet <> ".wl"}];
 Block[{$ContextPath = {"System`"}, $MessageList = {}},
  loaded = Quiet[Check[Get[package], $Failed]];
  loadMessages = ToString[#, InputForm] & /@ $MessageList
 ];
 If[loaded === $Failed, Return[Join[<|"experiment" -> id, "package_load_messages" -> loadMessages|>, failure["Package loading failed"]]]];
 r = Quiet[Check[ToExpression[paclet <> "`Analyze[]", InputForm], $Failed]];
 If[!AssociationQ[r], Return[Join[<|"experiment" -> id|>, failure["Actual package Analyze failed"]]]];
 fn = ToExpression[context <> "explore", InputForm];
 reports = Table[
  Block[{$MessageList = {}},
   captured = Quiet[TimeConstrained[Block[{System`Manipulate = captureManipulate}, fn[key, r]], 90, $TimedOut]];
   captureMessages = ToString[#, InputForm] & /@ $MessageList
  ];
  Join[<|"key" -> key, "capture_messages" -> captureMessages|>,
   If[captureMessages === {}, auditHeld[captured, context], failure["Messages occurred while calling the actual explore before capture"]]], {key, keys}];
 hashes = <|"analysis.wl" -> IntegerString[FileHash[FileNameJoin[{DirectoryName[package], "analysis.wl"}], "SHA256"], 16, 64],
   "authoring.json" -> IntegerString[FileHash[FileNameJoin[{exp, "authoring.json"}], "SHA256"], 16, 64]|>;
 <|"experiment" -> id, "paclet" -> paclet, "status" -> If[AllTrue[reports, #["status"] === "passed" &], "passed", "needs_review"],
   "source_hashes" -> hashes, "input_hashes" -> Lookup[r, "input_hashes", <||>], "models" -> reports|>
];

(* Exact numeric control values such as Pi/4 are evaluated exactly above.
   JSON stores their numeric value; unsupported symbolic audit metadata remains
   explicit InputForm text rather than making Export silently fail. *)
jsonSafe[a_Association] := Map[jsonSafe, a];
jsonSafe[a_List] := jsonSafe /@ a;
jsonSafe[x_] := Which[
 StringQ[x] || IntegerQ[x] || Head[x] === Real || x === True || x === False || x === Null, x,
 numericScalarQ[x], N[x],
 True, ToString[x, InputForm]
];

AuditProject[base_String, requested : (All | _List), outputFile_String] := Module[{registry, items, self, reports, summary},
 self = SelfCheck[];
 If[self["status"] =!= "passed", summary = <|"status" -> "harness_needs_review", "self_check" -> self|>,
  registry = Import[FileNameJoin[{base, "experiments", "registry.json"}], "RawJSON"];
  items = registry["experiments"];
  If[requested =!= All, items = Select[items, MemberQ[requested, #["id"]] &]];
  reports = auditExperiment[base, #] & /@ items;
  summary = <|"status" -> If[AnyTrue[reports, #["status"] === "needs_review" &], "needs_review", "passed"],
    "method" -> "Actual explore captured using Block on Manipulate and HoldAllComplete; real model-body evaluation at all defaults and one declared non-default per control; geometric/Epilog response fingerprints; no UI click claim.",
    "wolfram_version" -> $Version, "evaluated_at" -> DateString[Now, "ISODateTime"], "self_check" -> self, "experiments" -> reports|>
 ];
 Export[outputFile, jsonSafe[summary], "RawJSON"]; summary
];
End[];
EndPackage[];
