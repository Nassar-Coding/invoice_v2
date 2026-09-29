# Independent G4 and G5 audit — Agent 2

Date: 29 September 2026. Read-only audit of the implementation and authoritative challenge source.

**G4: NOT PASS. G5: NOT PASS.** There are **ten frozen blocker classes: G4-B01–G4-B04 and G5-B01–G5-B06**. G5 also depends on closure of the four G4 blockers. The passing population checks and reproducible artifacts are real evidence, but they do not cover the counterexamples below. Neither gate is independently closed; progression on the assumption that G4/G5 are validated is not authorized.

This report distinguishes supplied-population observations from constructed, same-format counterexamples. It does **not** assert that every affected or uncertain invoice is actually erroneous. No target prevalence was used. No implementation repository file, branch, tag, commit or generated deliverable was modified. Verification ran fetched code with in-memory inputs and outputs; this report is outside the repository.

## 1. Identity, governing requirements and verification

| Item | Independently verified state |
|---|---|
| Current `main`, checked again before finishing | `13eb7684a52dc9634c364bf9d9b3ba3087f882c1` |
| `gate4` commit | `9fa5514a88af49b9daf9c982c7c4352dc8ef984b` |
| `gate4` annotated tag object | `53e5a78d261eef638e09d224095c5c18225c1f11` |
| `gate5` commit | `13eb7684a52dc9634c364bf9d9b3ba3087f882c1` |
| `gate5` annotated tag object | `606a170b0e531d1cc6d17d7a1cf59edab441f106` |
| Challenge-source commit | `aef4924dc32506b4587de8b788b5a947e6beffec` |
| Reproduced current run context | `a54286f537e4149b` |

The [gate4-to-gate5 comparison][diff45] contains no change to the G4 engine, so the G4 code evaluated at current main is also the tagged G4 code. The [G3-to-G4 history][diff34] establishes packets at `91e785e`, reader results at `3b4e4fd`, then the state implementation at `b758791`. G5 history similarly puts its sample packets/readings before the implementation outputs. This supports the claimed preparation sequence, but does not make reader premises or dispositions authoritative.

The governing [Phase 2 plan, §2, lines 52–57][plan] requires:

| Gate | Required exit evidence | Audit conclusion |
|---|---|---|
| G4 | Independent multi-invoice histories; correct ordering, resets, allocation and replay; no event or adjustment counted twice | Normal-population reproduction and several controls pass. Exactly-once interval handling, uncertain chronology and completion of deferred band checks fail the demonstrated cases. |
| G5 | All twelve checks combined; correct full totals including nonlinear deductions/tax; coverage, findings, amount status and evidence; monetary/procedural distinction; independently reconciled invoices | All 2,806 rows are produced, but selection of missing facts, unresolved totals, payment duties, joint scenarios, discount-charge obligations and causal categories are not reliably handled. |

**Independently reproduced evidence:**

- All **10,330** challenge-source files matched the committed input manifest byte for byte.
- The actual G2 → G3 → G4 → G5 population path processed **7,746 civil lines and 91,244 drilling lines**, producing all **2,806** template outcomes.
- G4 summary, decision scopes, changed-line output and every generated G4 ledger matched the committed Git blobs. All four rendered G5 outputs also matched their committed blobs, including outcomes and the serialized submission representation. Rendering/comparison was in memory; no submission file was written.
- Counts reproduced: **88/900 civil flags**, **125/1,906 drilling flags**; no supplied invoice was marked unpriceable.
- The 24-history/48-reader G4 comparison and 25-invoice/50-reader G5 comparison reproduced the committed comparison results.
- G4 Y2 ordering, Y3 reset/counting, Y4 allocation, Y5 replay, Y6 exactly-once and Y7 checks passed on their normal population inputs. G5 Z1–Z4, Z6 and Z7 passed on the supplied population, including its monetary billing perturbation. G3/G4 result digests remained unchanged by downstream processing.
- The adversarial examples below used the real implementation. Raw-history fixtures were converted in memory into the normal CSV/text inputs and passed through G2/G3/G4, then G5. Invoice-only perturbations are identified separately.

**Limits:** I did not independently reproduce the literal fresh-clone shell invocation or the reported full 580-test count. Reproducing outputs is evidence of committed-state integrity, not proof of source-correct outcomes. A verifier passing on the supplied population establishes little about a branch absent from that population.

## 2. Frozen blocker register

Classification uses the user's criteria: **(a)** supplied-result effect; **(b)** a silent value, payability, flag, category, total or confidence error on unseen same-format inputs; **(c)** regression. A failure does not need to occur in the present population to qualify under (b).

| ID | Blocker | Criterion demonstrated | G5 dependency |
|---|---|---|---|
| G4-B01 | Annual-footage processing counts duplicate PD-210 quantities and can restore their full value | (b) | Service totals, DS-900, VAT, final total and findings |
| G4-B02 | PD-210 overlap allocation is pairwise, not a complete joint allocation | (b) | Allowed quantities, line values, invoice scenarios and confidence |
| G4-B03 | Missing chronology silently removes contributors or chooses an identity/order | (b) | Bands, release amounts, recipient/repeat identity and confidence |
| G4-B04 | A settled civil band can leave a wrong displayed rate unresolved and pass the invoice | (b) | False unflagged result at 0.95 |
| G5-B01 | Claim-stated missing facts select contract value and nominally passing outcomes | (a), (b) | Direct G5 defect; 2,079 supplied unflagged rows rely on the policy |
| G5-B02 | Unknown-total fallback copies billed amounts, including failed lines, and bypasses DDS aggregation | (b) | Direct G5 defect |
| G5-B03 | Adjustment/release checks test presence rather than the actual payment obligation | (b), demonstrated by perturbing supplied invoices | Direct G5 defect; depends on valid G4 accounts |
| G5-B04 | Independent local scenario dimensions are merged into one global dimension | (b) | Missing legal combinations, false unformed status and confidence |
| G5-B05 | DS-900 is checked only in aggregate; multiple discount charges can pass | (b), demonstrated by perturbing a supplied invoice | Direct G5 defect |
| G5-B06 | A monetary consequence of an out-of-term line creates an unsupported rate category | (b) | Direct category defect and incompatible Z4 assumption |

These ten classes, including their explicitly described variants, are the complete blocker set from this discovery audit. The required-closure paragraphs below define their recheck scope. Nonblocking observations in §6 do not enlarge this set. Subsequent work should fix and specifically recheck these failures, rather than start another discovery round; only a qualifying defect caused or exposed by corrective changes can add a blocker under the user's rule.

## 3. G4 blockers and their downstream consequences

### G4-B01 — Annual footage counts duplicates and overwrites prior allocation

**Evidence.** In [g4_dds.py, lines 455–458][dds-count], annual reading A sums the original **G3** quantities, before G4 duplicate allocation. [Lines 489–520][dds-reprice] rebuild a charge from its G3 interval and replace its alternatives, losing the earlier `stands` allocation. The source requires the annual band to reflect metres already drilled, while the same PD-210 metres cannot be charged twice: DDS Schedule 2 Part 2, p17; Clauses 23 and 29, pp6–7. This fails even under the implementation's adopted Q11 A; no decision between Q11 A/B is needed to demonstrate it. [DDS contract][dds].

**Reproduced variants, from the raw DDS-H06 history format:**

1. Start with 39,990 PD-210 metres in the Contract Year, then two charges for the **same 20-metre interval, 44,490–44,510**, on the same well/day. Reading A prices the one admissible interval at **USD 1,934.50**: 10 m × 98.70 plus 10 m × the rounded 96% rate of 94.75. After annual repricing, **both** lines retain 20 m and USD 1,934.50, with no standing-charge dimension. G5 produces **USD 4,373,273.73**; with that interval counted once, the same adopted reading yields **USD 4,371,138.04**, after the required discount and VAT. The synthetic header was not calibrated to make the test pass; these are reconstruction values.
2. Start with 39,950 prior metres, then duplicate 20-metre charges, then a later distinct 20-metre interval. Unique prior metres for the last charge are **39,970**, so its reading-A value is **USD 1,974.00**. The implementation uses **39,990**, splits it at the annual boundary and gives **USD 1,934.50**. The valid USD 1,974.00 alternative is absent.

**Control evidence.** Y4, when actually applied to the first fixture, rejects it for the intended reason: two charges stand in the same PD-210 group. The normal-population run does not exercise this interaction. Y3's purported independent recount also uses G3 quantities; Y6's identity-level checks are insufficient to establish unique physical footage. This is a coverage/oracle defect, not an unrelated test-harness failure.

**Required closure.** Annual state must count admissible metres exactly once under each carried reading and must preserve preceding G4 exclusions/allocations when repricing. Recheck both variants, overlap/band interactions and replay after removing/correcting an earlier charge. An independent interval-based expected result must reject double footage even when each line/event ID is unique. Reconstruct the affected DDS invoice through DS-900 and VAT from corrected service values. No reopening of Q11's already recorded interpretation is required.

### G4-B02 — Overlap alternatives omit valid joint allocations

**Evidence.** [g4_dds.py, lines 316–381][dds-overlap] considers a line as keeper or subtracts **one** overlapping neighbour. It does not subtract the union of multiple earlier/admissible intervals. A single `stands` value cannot represent a legal allocation involving several distinct nonoverlapping keepers. DDS Cl.29 expressly allows different depth intervals on one day, while Cl.23 prices their metres. [DDS pp6–7][dds].

**Reproduction.** One well/day has A = **1,500–1,600**, B = **1,550–1,650**, C = **1,600–1,700**, each 100 m, entirely at **USD 58.15/m**. Two legal examples are:

| Allocation | A | B | C | Total unique service value |
|---|---:|---:|---:|---:|
| A and C stand before B | 100 m / 5,815.00 | **0 m / 0.00** | 100 m / 5,815.00 | USD 11,630.00 |
| B stands first | 50 m / 2,907.50 | 100 m / 5,815.00 | 50 m / 2,907.50 | USD 11,630.00 |

G4 gives B only **100 m or 50 m**; it omits the admissible zero outcome. G5 cannot form all of the purported joint scenarios and falls back to a bill-dependent working total. In the reproduced packet it returned `formed=False`, confidence **0.30**, expected total **USD 14,537.50**, while its one formed scenario totaled **USD 13,374.50** including VAT. The header in that packet also had an arithmetic discrepancy; that separate finding is not the basis of this blocker.

**Control gap.** Y4's `_one_stands` check counts nonzero charges in a group. For partial overlaps, multiple nonzero residual charges can be correct; the required invariant concerns duplicate **metres**, not a blanket one-charge rule. [verify_g4.py, allocation checks][v4-allocation].

**Required closure.** Carry a valid joint allocation domain over interval coverage, including simultaneous subtraction by more than one overlapping interval and retention of nonoverlapping portions. Every represented scenario must count each metre at most once. If a complete value cannot be established, carry honest unresolved bounds instead of presenting an incomplete finite domain as complete. Verify two partial overlaps, the demonstrated three-interval chain, contained/exact duplicates and the annual-band interaction in G4-B01. The oracle must check physical interval coverage and the resulting quantities/values, without using billing to choose an allocation.

### G4-B03 — Unknown chronology becomes omission or an arbitrary ordering

**Evidence and three demonstrated variants.**

1. Civil bands: [`_cy` and `_bands`][cw-chronology] skip a line with no work date. In raw CW-H01, blanking the date on the first **600 m² B.22.010** measurement correctly leaves that line unresolved at G3. G4 nevertheless gives a later 500 m² line a **determined SAR 37,250.00**. With the first 600 m² before it, its valid value is **SAR 36,356.00**. Whether those earlier metres belong before it has not been established; omission does not establish zero prior contribution.
2. Civil retention: [g4_cw.py, lines 812–843][cw-release] omits applications with no submission date from both ordering and the earlier-retention set. In raw CW-H10, blanking the first application's submission date changes the release from **SAR 192.49 to SAR 96.15**, with `not_established=[]` and count zero. The missing application could be earlier, so the smaller amount is not established.
3. DDS repeated-charge identity: [G5 `standing_map`, lines 151–177][g5-standing] substitutes `"9999"` for a missing invoice date. In raw DDS-H01, blanking the first invoice's submission date selects the other invoice's charge as the keeper with `tie=False`. G5 reports a definite repeat allocation, no open reading or missing-input notice, and confidence **0.80**. The adopted earlier-submission policy does not authorize treating an unknown date as the latest date.

The relevant duties are civil chronological bands, Cl.44 and 45A, and DDS once-only allocation under the adopted Q7 policy. The plan also requires different clocks and unresolved inputs to remain distinguishable from zero/default values. [CW pp24–25, p8, p32][cw]; [DDS p7][dds]; [plan §§4,6][plan].

**Required closure.** Unknown chronology must remain a possible contributor/candidate in every affected band, recipient and payment-history calculation. Do not silently drop it or use a sentinel to select a winner. Recheck all three demonstrated variants, including their later-invoice amounts, repeat/recipient identities and confidence. A scope can remain determined only where the missing datum provably cannot change it. Ownership of the G5 `standing_map` component remains G5, but this is one shared uncertainty-propagation blocker, not an additional ID.

### G4-B04 — A resolved band does not complete the deferred rate/arithmetic check

**Evidence.** [`_rate_after_band`, lines 608–624][cw-rate] marks a wrong displayed rate unresolved whenever the billed amount happens to match an admissible amount. It does this even when **one band and one rate are fully determined**. G5 uses established findings and amount differences, so this residual uncertainty disappears from the invoice outcome. Civil Cl.27–28 and Cl.42 require the applicable rate and charge content; a correct amount does not make an incorrect stated rate correct. [CW pp6,8][cw].

**Reproduction.** First-band B.22.010, **600 m²**, no earlier history, zone Z1: correct rate **SAR 74.50**, amount **SAR 44,700.00**. State the other band's rate **71.52**, but retain amount 44,700.00 and a consistent header/retention/net. G3 correctly defers the unknown-band check. G4 establishes the first band but leaves `rate_differs` unresolved. G5 returns **flag 0, confidence 0.95**, no findings, no missing inputs and no open readings. The claim's displayed multiplication is also inconsistent: 600 × 71.52 = 42,912.00.

**Required closure.** Complete deferred rate and arithmetic checks against each established state/scenario. The demonstrated wrong rate must not become an unqualified pass because its amount is correct. Preserve legitimate split-band and genuine reading/order alternatives; do not reintroduce G3's previously rejected blanket arithmetic finding on valid splits. Recheck correct/incorrect rates independently of correct/incorrect amounts, with single-band, split-band and actually unresolved state fixtures. G5 must retain the resulting finding and appropriate confidence.

## 4. Additional G5 blockers

### G5-B01 — The invoice's own unsupported statement selects its contractual value

**Evidence.** [`fixed_for`, lines 233–249][g5-facts] copies the invoice's class/ground statement into the assignment used to select a priced alternative. `open_dims` then removes these fact dimensions from the scenarios. Nomination is detected for a confidence cap, but the non-nominated outcome is not evaluated as an invoice scenario. Thus computing all class prices upstream does **not** prevent billing from selecting the downstream contract value.

DDS Cl.4 assigns well class to the written call-off and keeps it for the well; Cl.23 assigns performance-section nomination to the call-off. Civil Cl.5, S4 and the previously closed ground-evidence rules assign ground to appropriate source evidence, not an uncorroborated application statement. [DDS pp3,6][dds]; [CW pp3,10][cw]. The [plan][plan] explicitly separates claims from contract/evidence authority. No new source provision authorizing substitution is identified in [Q9-3][g5-decisions].

**Reproduction and population scope.** Actual **MDS-00753**, header HPHT, returns **flag 0 / USD 49,892.39 / 0.80**. Changing only its header class to Standard, with the evidence and G3/G4 admissible values unchanged, produces **flag 1 / USD 49,113.13 / 0.80**. This is selection of the contract amount by the claim, not merely a diagnostic comparison. The reproduced population includes **1,781 drilling + 298 civil = 2,079 unflagged rows at 0.80** under the policy; **2,390 PD-210 lines in 638 invoices** depend on nomination. This does not establish that all those rows are wrong; it establishes that their unsupported facts have been resolved by the claim.

**Required closure.** Preserve materially admissible class, ground and nominated/not-nominated outcomes until source evidence or an explicit, source-consistent unresolved-output policy disposes of them. A working estimate must not be selected by whichever unsupported statement the invoice supplies and then described as validated contractual value. Test claim-only changes, inconsistent statements for the same well, and both nomination outcomes through flag, amount status, total, category and confidence. A blanket default or blanket query is not mandated by this audit; any adopted rule must distinguish missing evidence from an established breach and comply with the existing no-claim-authority boundary. The full affected population must be replayed.

### G5-B02 — Unknown totals still follow billing and lose DDS aggregation

**Evidence.** [`outcome` and `_best_supported`, lines 422–465][g5-fallback] replace missing line values with the claimed amount, or zero if that is missing, and sum them. There is no enforcement of Q9-4's own restriction that a billed fallback is available only when no check on that line failed. For DDS this fallback also bypasses reconstruction of DS-900 and VAT.

**Reproduction.** A raw PD-210 input with **missing start depth**, end depth 1,500 m, quantity 50 and billed amount **USD 2,117.50** survives G2/G3 correctly as unresolved. G5 has an established `depths_missing` finding and `formed=False`, but writes expected total **2,117.50**. Changing the claimed amount to **9,999** changes the expected total to **9,999**, despite the continuing missing-depth defect and additional arithmetic failures. Neither result is an established full invoice total. This is the real input path, not an engine stub.

**Z4 conclusion.** The earlier first-wrong-scenario defect was fixed: working-reading totals in the supplied, fully formed population no longer move under Z4's monetary perturbation. However, **zero supplied invoices exercise this fallback**, and [`perturb_billing`][z4] excludes class/ground/nomination inputs. Its population PASS therefore establishes neither a general no-billing-authority guarantee nor safe unknown-total handling.

**Required closure.** Remove silent billed/zero substitution for unvalued components. Preserve unknown or supported bounded totals explicitly; any later numeric export policy must be named, owned and not misrepresented as a contract calculation. Check failed-line and no-established-failure variants, missing billed amounts, partially formed civil/DDS invoices, and DDS discount/VAT interaction. Extend Z4 to execute those branches and require a properly formed full invoice total whenever a numeric value is asserted as such. Do not solve this by lowering confidence on an otherwise unsupported copied number.

### G5-B03 — Payment duties are checked for zero versus nonzero, not correctness

**Evidence.** [G5 evaluation, lines 323–387][g5-payment] tests whether an adjustment or release is zero; it does not reconcile the actual value, lawful recipient, timing or once-only posting against G4's account. A release recipient represented as a tie dictionary never equals an invoice ID, so that duty is skipped entirely. Civil Cl.31A/45A and DDS Cl.36A require the actual adjustment/release obligation, not an arbitrary nonzero field. [CW p32 and A3 p43][cw]; [DDS p35 and A3 p42][dds].

**Demonstrated variants:**

| Input perturbation or raw history | Actual G5 behavior |
|---|---|
| Actual PA-00443: replace zero adjustment with **SAR 0.01**, update net consistently | Changes from flag 1 / 0.50 to **flag 0 / 0.95**. The relevant Q12-A adjustment is SAR 60,508.18; one cent cannot discharge it. |
| Actual PA-00047: add unsupported **SAR 12,345.67 adjustment**, update net consistently | Remains **flag 0 / 0.95**. |
| Actual PA-00047: instead add **SAR 12,345.67 retention release** outside the lawful release recipient, update net | Also remains **flag 0 / 0.95**. |
| Actual PA-00678: set required retention release to **SAR 0.01**, update net | Removes `release_omitted`; independent defects still flag this invoice. The release account is in the millions, so presence is insufficient. |
| CW-H10: tie PA-9A003 and PA-9A004 on the first post-completion submission date; both show zero release | G4 correctly carries a tie and **SAR 192.49** release. G5 marks **both unflagged / 0.95**, with no open recipient outcome. |
| Correctly zero release account, as in the isolated out-of-term fixture in G5-B06 | G5 adds `release_omitted` merely because the field is zero, despite no positive release being due. |

The optional Q2-B path also obtains an adjustment by taking the minimum of an account range (`_a3_difference`), rather than selecting a jointly supported scenario. This is part of the same obligation/scenario closure, not authority to change the adopted Q2-A total definition.

**Required closure.** Reconcile the claimed payment fields to the actual scenario-specific G4 amounts and recipients, including ties, unknown amounts, zero entitlement, early/wrong recipient, partial/nonzero wrong amounts and repeated posting. A3/release already present must be checked as well as omitted values. Keep payment-only effects outside the judged total under adopted Q2 A, while retaining their correct flag/category. If another Q2 reading is reported, calculate its discount/tax at the specified stage without substituting a range endpoint for missing state. Recheck all demonstrated variants and both contracts' adjustment paths.

### G5-B04 — Independent local alternatives are forced into one global choice

**Evidence.** [`open_dims` and `outcome`][g5-scenarios] combine alternatives by a generic name such as `order`, without identifying the local band/date group. Two independent same-date groups therefore share one assignment. The same structural risk concerns independent `stands`/`earlier` groups. This is a failure to compose G4's alternatives, not a request to invent a different contract reading.

**Raw-history witness.** All work is Z1, March 2025. One invoice has B.22.010 quantities **1,100** on March 1 and **150** on March 2, plus A.13.010 quantities **4,900** on March 3 and **150** on March 4. A second invoice has another **150 B.22.010** on March 2 and **150 A.13.010** on March 4, in a different area so they are not duplicates. These are two independent band-edge order choices. The two alternatives per group give **four** legal combinations:

| Invoice | Complete possible totals, SAR |
|---|---|
| PA-X01 | **187,953.50; 188,066.50; 188,251.50; 188,364.50** |
| PA-X02 | **13,393.50; 13,506.50; 13,691.50; 13,804.50** |

The first invoice's fixed lines total 174,560.00; its variable B.22 line is 10,728.00 or 11,026.00 and its variable A.13 line is 2,665.50 or 2,778.50. These independently establish the table.

G5 creates **three generic `order` assignments**, only one of which forms a complete invoice, then returns `formed=False`, confidence **0.30**, and only one total per invoice. Z6 and Z7 both pass that result. The fixture header also had an arithmetic discrepancy; its presence does not explain missing legal combinations or false unformed status.

**Required closure.** Namespace local choices by the evidence/state group they govern. Preserve required correlation within a group and independence between separate groups. Verify the four totals above, two independent duplicate/tie groups, and interaction with genuinely global readings such as Q12. No invalid combination may masquerade as missing input, and no legal combination may disappear merely because another group uses the same generic dimension name. Update the oracle to enumerate expected legal combinations independently of the engine's own dimension collection.

### G5-B05 — Multiple DS-900 charges pass when their sum is correct

**Evidence.** [G5 lines 296–302][g5-ds] sum DS-900 amounts and immediately skip the line. Only the aggregate discount is checked later. DDS **Cl.38, p8** requires a **single negative DS-900 charge**; correct aggregate arithmetic does not discharge that requirement. G3 explicitly defers this invoice-level duty. [DDS contract][dds].

**Reproduction.** Actual **MDS-00018** has a DS-900 charge of **USD −45,109.68**, and reconstructed invoice total **USD 1,532,527.31**. Split that discount into two distinct lines of **USD −22,554.84** each, leaving the combined discount and header unchanged. G5 still returns **flag 0 / confidence 0.80**. No billed-value discrepancy exists to rescue detection.

**Required closure.** Verify the source-prescribed discount charge's cardinality and negative sign as well as its amount, threshold, rounding and contribution to net/VAT. Recheck the demonstrated split, one correctly formed charge, omitted required charge, and extra/offsetting charges. Assign explicit treatment to applicable DS-900 content checks instead of bypassing all line checks. Do not indiscriminately impose ordinary-service report/date/unit requirements on the special discount charge where the source does not establish them.

A secondary probe with quantity 7 and rate −1 but the same discount amount also passed. Because Cl.38 is a special amount rule rather than a Schedule 1 service rate, that observation is **not** used to invent an independent quantity-one or ordinary-rate obligation. The blocker is established by the unambiguous single-charge requirement.

### G5-B06 — Out-of-term rejection creates a false rate category

**Evidence.** [G5 lines 312–319][g5-cause] ignores a `term` finding as a cause of the line's value change and adds `rate_differs` when the rejected line has zero allowed quantity. Separately, [Z4 lines 158–167][z4] classifies every term finding as procedural and rejects a zero expected total, even where the already-closed G3 rule correctly makes out-of-term work nonpayable. These assumptions are incompatible with G3's established consequence and Q9-6's root-cause categorization.

**Reproduction.** One B.22.010 line, **600 m² at SAR 74.50 = 44,700.00**, dated **2 October 2026**, after civil completion as extended on 30 September. Header period/submission and its stated arithmetic are otherwise coherent. G3 finds **only `out_of_term`** and correctly values the work at zero. G5 additionally reports **`rate_differs`** although the stated rate is correct. It also reports the zero-release issue covered in G5-B03. Z3 accepts the invented category because it checks consistency with the engine's finding list, not the source of the finding.

This is not an allegation that actual PA-00375's rate finding is false: I inspected that line and it also has a genuine local rate difference. The blocker is the isolated same-format counterexample above.

**Required closure.** Attribute findings to the actual violated obligation, not automatically to the numeric difference caused by another rule. Correctly priced but nonpayable work must retain its term/eligibility cause without a fabricated rate category. Preserve an independently demonstrated rate error when one actually exists. Z4 must distinguish monetary term consequences from genuinely procedural timing/identity breaches; correcting this category must not make a source-correct zero valuation fail its verifier.

## 5. Findings on the six requested high-risk questions

### 5.1 Claim-stated class, ground and nomination

**Not consistent with the no-claim-authority boundary.** G5-B01 gives the direct code and mutation evidence. The assertion in Q9-3 that upstream computation of every alternative means the claim is never used to price is insufficient: **selection of which amount is the invoice's expected contractual total is itself a valuation decision**. Capping confidence at 0.80 discloses concern but does not supply authority. The 2,079 rows must be described as fact-dependent working outcomes, not independently validated passes.

### 5.2 Q12 and the 5 January 2026 reset

**The adopted anniversary reset is source-supported; no Q12 blocker is raised.** I read the original **civil p32, Clause 3A**. Its first-year definition ends immediately before the first anniversary, and subsequent years start on anniversaries. The final-year/extension wording stops an extension itself from creating a year; it does not clearly freeze the originally planned final year so that an ordinary anniversary can never occur. With commencement on **5 January 2025**, reset on **5 January 2026** is the better-supported reading. [CW p32][cw].

The existing no-reset alternative was retained by G4, and the reproduced G5 effect is **88 → 248 civil flags**, affecting **270 lines / 181 invoices**. Those numbers describe sensitivity; they do not prove the chosen reading. [G5 report, decision table][g5-report]; [decision effects][effects]. The earlier scope description of 268 versus generated 270 should be reconciled as documentation, not treated as contractual evidence.

### 5.3 Civil 9.8%, rate 38 and duplicate 18

**The percentage is not a failure criterion, and neither category can simply be dismissed as a systematic misreading.** The summary's 38 and 18 are exact **category combinations** (`rate` alone; `duplicate` alone), not counts of every invoice containing either category. [Committed summary][g5-summary].

The **38 rate-only** invoices divide materially:

- **Eight** are order-sensitive outcomes at **0.50**, not rate errors established under every admissible order: PA-00140, PA-00155, PA-00303, PA-00382, PA-00459, PA-00506, PA-00611 and PA-00778. Their flags follow the declared Q9-2 ambiguity policy. Their working totals can equal billing while another order differs; billing must not choose the order.
- **Three** rely solely on the unsupported ground-fact selection at G5: PA-00291, PA-00509 and PA-00898. These fall under G5-B01. PA-00320 also has a ground-statement issue, but an independent B.25.010 rate finding exists, so it is not in this solely-ground subset.
- The remaining **27** contain established local/state price differences. They do not all arise from one reset rule. For example, PA-00496-02, A.13.010, has **401 m³**: base 18.90 × Z4 1.28 × band 94% gives rounded **22.74**, amount **9,118.74**, instead of billed **24.19 / 9,700.19**. PA-00871-04, B.23.010, has **2 tonnes**: the applicable 97% band gives **4,575.88 / 9,151.76**, instead of **4,717.40 / 9,434.80**. These follow civil Cl.27–28, Schedule 1, zones and Schedule 4 Part 3. [CW pp6,17–25][cw]; [G4 changed lines][g4-changes]. This is support for the identified discrepancies, not a claim that every other fact on those invoices is independently settled.

The **18 duplicate-only** rows concern repeated **A.16.010 weekly measurements**. G4's broader duplicate population is **20 groups**: **19 weekly groups** and one E.52.010 group; 21 later lines are disallowed, including one already nonpayable at G3. A weekly log evidenced one week, not a fresh weekly entitlement for each day named on repeated lines. Schedule 5's daily entries establish whether the week is measurable; they do not multiply that week into separate weekly charges. Cl.44 disallows measuring the same item twice. [CW pp8,27,33 and A.16.010 schedule row][cw].

For example, one DW-00004 weekly group has PA-00431-07 submitted 28 February, PA-00309-05 submitted 2 March, and PA-00059-01 submitted 10 March; the differing work dates lie within the same evidenced week. That is a substantive duplicate basis. Which application bears the rejection still depends on the disclosed interpretation of “later,” discussed next. There is no justification for removing such findings merely to move 9.8% toward 5–8%.

### 5.4 Z4 and expected totals following the bill

**The narrow reported correction works; the general claim does not.** Population monetary perturbation leaves formed working-reading totals unchanged. G5-B02 shows that the fallback still copies billed amounts; G5-B01 shows claim-stated facts select a priced alternative. Both mechanisms must be corrected before saying that no expected total follows billing. The fact that the current population contains no unformed totals explains the fallback test's blind spot.

### 5.5 “Later measurement,” weekly measurement and 41 alternatives

**Weekly measurement has a source basis. Later submission is a defensible disclosed working interpretation, not an independently compelled equivalence.** Cl.44 does not explicitly define “later” as submission order. [G4 report §8][g4-report] candidly records that three of four civil readers left submission order, application number and work date open. Submission order is coherent with applications presenting measurements, and work-date differences inside the same weekly record do not create multiple weeks. The challenge README permits a reasoned, recorded choice where wording is genuinely ambiguous. This audit therefore does not create a separate blocker merely because readers preferred another plausible interpretation. Maintain the qualification and its sensitivity under G6/G7; do not label reader disagreement unanimous validation.

I reproduced **59 G4 comparison disagreements**, dispositioned **41 both / 16 engine / 2 presentation**, with 28 reader results agreeing in full. “Both” means a reader's value survives among alternatives; it does **not** establish that every combination of alternatives is valid or that the invoice-level result is correct. G4-B02 and G5-B04 are concrete failures of that stronger claim. Reader disagreements on Contract Year, counting unpaid measurements, standing charges and residual hour/event readings must retain their actual decision status. [History comparison][g4-comparison]; [dispositions][g4-dispositions].

### 5.6 Independent sample of 25 invoices

**Enough to demonstrate 25 conditional reconciliations; not enough to validate the stated population-wide rules.** The sample is deliberately mixed: seven seeded random band-free civil applications, six seeded random drilling invoices capped at 22 lines, plus selected feature cases. This is useful coverage work, not a representative estimate of population accuracy.

More significantly, [the reader premises, lines 53–81][sample-premises] prescribe Q12, the later-submission policy, and computing with the invoice's own class/ground/nomination. Readers can independently calculate within those premises without independently testing whether those premises are justified. The **48/50 agreements**, and two source-dispositioned differences, reproduced. They support the sampled arithmetic and named rule applications; they do not validate Q9-3, 2,079 unsupported-fact passes, confidence calibration, unknown-total fallback, joint local scenario composition or annual-footage/duplicate interactions.

Sample size alone is **nonblocking**: the plan's G5 exit condition does not prescribe a statistical sample size. The demonstrated semantic/calculation defects are blockers. G6 owns stratified review of apparent passes and residual clusters, including the frozen failure classes; G7 owns honest confidence/decision-log reporting. [G5 report §§4,8][g5-report]; [plan G6/G7][plan].

## 6. Carry-forward items and the state of earlier gates

| Nonblocking item | Why it is not a separate blocker here | Owner |
|---|---|---|
| “Later” equals later submission | Reasonable disclosed interpretation, not unambiguous source wording; disagreement alone is not a defect | G6 sensitivity review; G7 decision log |
| Residual open hour/event readings, same-day exclusion and recipient interpretations | Keeping materially plausible alternatives is appropriate; the blocking issue is incorrect composition/treatment, already identified above | G6 disposition; G7 unresolved-output policy |
| 25-invoice sample's selection bias and same-model readers | Limits what agreement establishes; no mandated statistical sample size was breached | G6 broader apparent-pass/residual review |
| Confidence values are judgment conventions, not calibrated probabilities | Disclosed convention is permissible; false certainty caused by omitted scenarios is already blocked | G7 labeling; G6 evidence review |
| Population prevalence discussed as corroboration in the G5 report | Must not become an optimization target; Q12 has independent textual support, while Q9-3 is separately blocked | G6 methodology; G7 report wording |
| README/task checklist lag and 268/270 scope-text mismatch | Reproducible committed outputs provide the substantive scope; documentation should agree | G7 documentation, with G6 scope confirmation |
| Literal clean-clone/full-test-count claim not independently rerun | Core outputs and targeted controls were independently reproduced, but this stronger claim remains unconfirmed by this audit | G7 final reproduction |
| DS-900 quantity/rate-content treatment beyond Cl.38 | The single-charge defect is established; a special discount should not acquire invented ordinary-service obligations | G6 source review of remaining content treatment |

**G0–G3:** No modification to their substantive engine/source terms was found in the G4/G5 changes under audit. The complete source manifest and current G2 context reproduced, and upstream result objects were preserved by downstream execution. Their previous independent closure remains standing; this is not another G3 discovery round. The new G4/G5 layers do, however, mishandle some uncertainty that the earlier layers correctly preserved. That must be fixed at the responsible later layer rather than reclassified as permission to use missing facts as truth.

**Committed-state integrity:** Established. The artifacts belong to the fetched implementation and reproduce. This does not turn an incorrect rule into a correct rule. The repository's gate tags prove the tagged snapshots and asserted chronology, not independent gate passage.

## 7. Closure and recheck boundary

**G4 remains NOT PASS until G4-B01–G4-B04 are closed.** Its current supplied-population calculations reproduce, but its unseen-input state failures satisfy the user's explicit blocker criterion (b).

**G5 remains NOT PASS until G5-B01–G5-B06 and its dependencies on G4-B01–G4-B04 are closed.** In particular, G4-B01/B02 affect DDS service/discount/VAT totals; G4-B03 affects both pricing history and payment/duplicate identities; G4-B04 affects the existence of a finding and final confidence. Correcting G5 alone cannot validate outcomes built on those defective G4 states.

Each correction should demonstrate the stated witnesses and variants, reject the old defect for its intended reason, preserve unaffected supplied results or explain every changed result, and reproduce the corrected artifacts. The exact changes in population counts are an audit result, never an acceptance target. Later-gate review can continue to own the nonblocking items, but cannot be used to declare these demonstrated G4/G5 failures closed.

**The blocker set is frozen to the ten IDs in §2. No findings have been held back for a later round.** This report does not authorize implementation, G6, final classification changes or submission generation; it completes the requested read-only audit.

Approximate active audit time: **45 minutes**, excluding the interruption between messages. This includes source/scan review, fetched-code population replay, targeted adversarial histories, artifact comparisons and report preparation.

[plan]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/artifacts/phase_inputs/Phase2_plan.md#L45-L57
[diff34]: https://github.com/Nassar-Coding/invoice_v2/compare/gate3-r5...gate4
[diff45]: https://github.com/Nassar-Coding/invoice_v2/compare/gate4...gate5
[cw]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/contract/CW-2025-0417-CIV.pdf
[dds]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/drilling_services/contract/DDS-2025-118.pdf
[dds-count]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/audit/g4_dds.py#L432-L475
[dds-reprice]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/audit/g4_dds.py#L489-L524
[dds-overlap]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/audit/g4_dds.py#L316-L381
[v4-allocation]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/tools/verify_g4.py#L278-L370
[cw-chronology]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/audit/g4_cw.py#L363-L384
[cw-release]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/audit/g4_cw.py#L775-L847
[cw-rate]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/audit/g4_cw.py#L608-L624
[g5-standing]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/audit/g5_outcomes.py#L151-L177
[g5-facts]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/audit/g5_outcomes.py#L233-L269
[g5-fallback]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/audit/g5_outcomes.py#L396-L465
[g5-payment]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/audit/g5_outcomes.py#L323-L387
[g5-scenarios]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/audit/g5_outcomes.py#L396-L456
[g5-ds]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/audit/g5_outcomes.py#L286-L369
[g5-cause]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/audit/g5_outcomes.py#L312-L319
[z4]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/tools/verify_g5.py#L157-L193
[sample-premises]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/tools/g5_samples.py#L53-L81
[g5-decisions]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/spec/g5_decisions.yaml
[g4-report]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/Phase3_G4.md
[g5-report]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/Phase3_G5.md
[g4-changes]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/verification/g4/changed_lines.jsonl
[g4-comparison]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/verification/g4/history_comparison.json
[g4-dispositions]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/verification/g4/history_dispositions.yaml
[g5-summary]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/verification/g5/summary.json
[effects]: https://github.com/Nassar-Coding/invoice_v2/blob/13eb7684a52dc9634c364bf9d9b3ba3087f882c1/verification/g5/decision_effects.json
