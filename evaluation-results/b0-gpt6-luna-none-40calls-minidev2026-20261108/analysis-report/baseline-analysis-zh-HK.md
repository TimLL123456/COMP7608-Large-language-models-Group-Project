# KORA B0 — Mini-Dev 2026 Performance & Failure Analysis (繁體中文)

> **Current setting (10 November 2026):** B0 now uses 40 model calls, 40 total tool calls and 40 SQL executions for both prompt variants; the current requested evaluation runs only `generalized-v1`. The earlier Mini-Dev 2026 B0 configuration metadata also lists 40/40/40. Historical execution limits and scores below remain as originally recorded; this note does not regenerate predictions or convert the archive into a matched control.


> **日期：** 2026-11-09 · **Provider / Model：** `chatgpt-siwc / gpt-6-luna` · **Requested reasoning effort：** `none`  
> **固定資料版本：** BIRD Mini-Dev 2026 SQLite，annotation revision `5b256b5a9c17478f06ed6912612e9a14d17065c8`  
> **口徑：** 本地 Dev 400 / Local Test 100；Dev 用於診斷，Local Test 僅供描述性確認。**本報告未重跑 inference 或 SQLite scoring。**

本研究把歸檔 Score、Question/Evidence、官方同版本 Gold SQL、Predicted SQL、structured trace 作交叉分析，目的不是只找出「錯了多少」，而是找出**為何 SQL 執行成功仍然得到錯誤結果**，以及最值得優先驗證的修復方案。**EX（Execution Accuracy）是結果準確率，並非 SQL 能否執行的成功率。**

## 目錄
- [0. Executive Summary](#summary)
- [1. Dataset Provenance & Integrity](#integrity)
- [2. Overall / Difficulty](#overall)
- [3. Database Breakdown](#databases)
- [4. Query Category / SQL Structure](#categories)
- [5. Table / Column / Grain](#tables)
- [6. Agent Inference Trace](#traces)
- [7. Root Cause Taxonomy](#causes)
- [8. In-depth Case Studies](#cases)
- [9. Improvement Priorities](#priorities)
- [10. Controlled Experiment Plan](#experiments)
- [11. Limitations & QA Watchlist](#limitations)
- [12. Sources & Reproduction](#sources)

<a id="summary"></a>
## 0. Executive Summary

| 核心指標 | 研究結果 |
| --- | --- |
| Overall EX | **294/500 = 58.80%** |
| Dev / Local Test | **235/400 = 58.75%** / **59/100 = 59.00%** |
| Failures | **206**：203 `incorrect_result`、3 `sql_error` |
| Dev failures | **165**：163 `incorrect_result`、2 `sql_error` |
| Worst Dev database | `superhero`：**11/40 = 27.5%**，29 failures |
| Superhero numeric sentinel candidates | **15/29 failed**：Gold 有 `height_cm > 0` 或 `weight_kg > 0`，Agent 未完整加入 |
| Dev final SQL 未匹配先前執行 SQL 文字 | **325/400**：128 failures、197 correct |
| Dev 失敗且漏 inspect Gold 引用的物理表（近似） | **9/165**，多數問題不是完全不認識表名 |

**主要發現：** 這個 B0 的主導問題是 SQL **語義正確性**，尤其是 Value Meaning、業務度量來源、資料粒度（grain）、聚合母體、時間語義、題目 Filter 和結果欄數。因而建議先測 **E1: Value/Semantic Grounding** 及 **E2: Query Contract / Granularity**，再考慮更高 thinking effort 或更大型架構。

**嚴謹性：** 15 個 Sentinel 案例是直接觀察到 Gold/Predicted 條件差異且 EX=0 的**候選修復機會**，不是已做過反事實驗證的 15 個 guaranteed fixes。現已為全部 165 題作 Gold/Agent SQL 比較：153 題有單一主要**候選**分類、12 題保留 unresolved。這是便於排序的研究標籤，未逐題做反事實 SQLite rerun，也不代表互斥、已證實的真實原因。

### 更新：165 題完整候選分類（2026-11-09）
已重新核對 **官方 pinned Mini-Dev 2026 question/evidence/database/difficulty 與 Dev+Local Test：500/500 相符**。既有 97 題個案比較保留；另補做 68 題 Question／Gold SQL／Agent final SQL 對照。全部 165 題均在 [failure-inventory.csv](failure-inventory.csv) 中記錄主要候選根因、審核來源及驗證狀態；**153 題有 provisional 候選分類，12 題待進一步比較**。每題在統計表只歸一個主要候選類別，但仍可能同時涉及多個錯因；因此以下不是已確認之因果分佈，亦不能當成修復收益。
| 主要候選根因 | Dev failures | 佔 165 題 |
| --- | ---: | ---: |
| Value Semantics / 編碼值 | 49 | 29.7% |
| Output Contract / 結果形狀 | 22 | 13.3% |
| Metric Source / Grain | 22 | 13.3% |
| Aggregation / Population | 21 | 12.7% |
| Missing / Unsupported Filter | 19 | 11.5% |
| Unresolved / 待比較 | 12 | 7.3% |
| Temporal Semantics | 11 | 6.7% |
| Entity Relationship / Join | 7 | 4.2% |
| SQLite Syntax / Validation | 2 | 1.2% |
**解讀：** 與 SQL syntax（2 個 final execution errors）相比，Value Meaning、Measure Source、Grain、Aggregation Population、Filter 和 Output Schema 更值得優先測試；但錯誤歸因要透過同版 SQLite rerun / paired experiment 才能驗證。官方 Gold SQL、候選分類和修補提示嚴禁加入 Agent runtime、RAG 或 Demo 可檢索資料。

<a id="integrity"></a>
## 1. Dataset Provenance & Integrity

| 驗證 | 結果 |
| --- | --- |
| Official Mini-Dev 2026 annotation | 500 個唯一 Question IDs 0–499 |
| Local question / evidence / database / difficulty | 與官方同版本逐題比對：**0 差異** |
| Score / trace 覆蓋 | Dev 400、Test 100；500 個唯一 IDs，無缺失 Final SQL |
| Gold SQL | 官方 pinned revision `5b256b5a9c17478f06ed6912612e9a14d17065c8` |
| Scoring source | 歸檔結果；本研究未重新執行 500 條 Gold/Agent SQL |

**Mixed-budget 提醒：** `configuration.json` 現列 `max_sql_executions=40`，但同一檔案的 `execution_budget_history` 說明 **498 題實際 SQL budget 為 20**，Dev Q421、Test Q107 重跑才是 40。總 Tool/Model 上限記錄為 40；request timeout 300s；scoring timeout 600s。不可將整套結果描述為「全 500 題均可執行 40 次 SQL」。

Original Mini-Dev 的歷史 EX **299/500 = 59.8%** 與新版本 **294/500 = 58.8%** 使用不同 question/label release；不構成同題 -1pp regression。官方 Gold SQL 屬 scorer/research-only，**不可以放入 Agent prompt 或 Agent 可檢索的工具 context**。

<a id="overall"></a>
## 2. Overall / Difficulty

| Split | Correct | Total | Failures | EX |
| --- | ---: | ---: | ---: | ---: |
| Dev | 235 | 400 | **165** | **58.75%** |
| Local Test | 59 | 100 | 41 | 59.00% |
| **Total** | **294** | **500** | **206** | **58.80%** |

| Difficulty (Overall) | Correct / Total | EX | Failures |
| --- | ---: | ---: | ---: |
| challenging | 267/460 | 58.0% | 193 |
| moderate | 22/32 | 68.8% | 10 |
| simple | 5/8 | 62.5% | 3 |

Dev：Challenging **213/369**、Moderate **17/24**、Simple **5/7**。新版 500 題中 460 題標成 Challenging（**92%**），而 Simple/Moderate 樣本非常少。建議以 Database、Query Type、Gold-required features、Table/Column 與 Trace 取代過份依賴 Difficulty 進行診斷。

<a id="databases"></a>
## 3. Database Breakdown — Dev

| Database | Correct / Total | EX | Failed |
| --- | ---: | ---: | ---: |
| `superhero` | 11/40 | 27.5% | 29 |
| `card_games` | 32/55 | 58.2% | 23 |
| `financial` | 17/37 | 45.9% | 20 |
| `thrombosis_prediction` | 48/68 | 70.6% | 20 |
| `california_schools` | 21/40 | 52.5% | 19 |
| `toxicology` | 13/25 | 52.0% | 12 |
| `formula_1` | 33/44 | 75.0% | 11 |
| `codebase_community` | 16/25 | 64.0% | 9 |
| `european_football_2` | 16/25 | 64.0% | 9 |
| `student_club` | 22/30 | 73.3% | 8 |
| `debit_card_specializing` | 6/11 | 54.5% | 5 |

前五個失敗最多的 Database：`superhero`、`card_games`、`financial`、`thrombosis_prediction`、`california_schools`，合計 **111/165 = 67.3%** failures。

把 Difficulty 固定在 Challenging：`superhero` **10/38 = 26.3%**，`formula_1` **33/43 = 76.7%**。從 `list_tables` trace 可見前者有約 10 張 table、後者約 13 張；因此「table 更多必然較差」不符合這組觀察。合理假設是 schema/value conventions、特定 query grain、join cardinality 與指標來源才是關鍵，仍需 matched-case 實驗確認。

### 候選根因 × Database（單一主要標籤、Dev failures）
| Database | Failures | 主要候選 pattern（案例數） |
| --- | ---: | --- |
| `superhero` | 29 | Value Semantics 20；Relationship 1 |
| `card_games` | 23 | Value Semantics 12；Metric/Grain 6 |
| `financial` | 20 | Aggregation/Population 7；Metric/Grain 3；Temporal 3 |
| `thrombosis_prediction` | 20 | Missing/Unsupported Filters 6；Value Semantics 5 |
| `california_schools` | 19 | Filters 7；Metric/Grain 6 |
| `toxicology` | 12 | Entity/Join 4；Output Contract 3 |
| `formula_1` | 11 | Output Contract 3；Temporal 3 |
| `codebase_community` | 9 | Aggregation/Population 4 |
| `european_football_2` | 9 | Value Semantics 4 |
| `student_club` | 8 | Metric/Grain 3；SQL errors 2 |
| `debit_card_specializing` | 5 | 每個候選類別分散，無明顯單一主因 |
以上分組用嚟找優先診斷方向，並無控制 Database 內部嘅 query mix、難度、schema conventions 或重複錯因。

<a id="categories"></a>
## 4. Query Category / Gold SQL Structure

下表為**非互斥探索性群組**：NL groups 按 Question 文本關鍵字，Gold features 按官方 SQL 結構識別。同一題可被多次計數；分類不是已確認根因，不能將失敗數加總或當成 causality。

| Feature | Dev cases | Fail | EX |
| --- | ---: | ---: | ---: |
| NL: Average/mean/median | 114 | 59 | 48.2% |
| NL: Count/number of | 230 | 111 | 51.7% |
| NL: Top-K/ranking/extremum | 192 | 78 | 59.4% |
| NL: Temporal/date | 190 | 72 | 62.1% |
| NL: Conditions/negation | 183 | 77 | 57.9% |
| NL: Percent/rate/ratio | 56 | 23 | 58.9% |
| Gold: GROUP BY | 145 | 68 | 53.1% |
| Gold: LIMIT | 44 | 22 | 50.0% |
| Gold: CASE | 88 | 43 | 51.1% |
| Gold: COUNT(DISTINCT) | 108 | 46 | 57.4% |
| Gold: CTE | 118 | 50 | 57.6% |
| Gold: Subquery | 247 | 105 | 57.5% |
| Gold: LEFT JOIN | 68 | 24 | 64.7% |

Average/Mean（59 failed，EX 48.2%）與 Count（111 failed，EX 51.7%）值得重點研究。問題可能不是不會用 `AVG`、`COUNT`，而是選錯 population、denominator、NULL/0 排除、Distinct Key、Join duplication 及結果粒度。Gold 使用 `CTE`、`CASE`、`LEFT JOIN` 等形式也不是唯一正確寫法；比較 Agent SQL 時要考慮 SQL 等價改寫。

<a id="tables"></a>
## 5. Table / Column / Data Grain

| Gold 使用的實體表（Dev） | Correct / relevant cases | Fail |
| --- | ---: | ---: |
| `superhero.superhero` | 10/38 | 28 |
| `financial.district` | 13/30 | 17 |
| `financial.account` | 12/29 | 17 |
| `card_games.cards` | 29/44 | 15 |
| `california_schools.frpm` | 10/24 | 14 |
| `toxicology.atom` | 10/22 | 12 |
| `toxicology.connected` | 3/13 | 10 |
| `card_games.set_translations` | 3/12 | 9 |

統計只表示「該 Table 在 Gold query 出現」，同題可包括多 Table，**不代表是單一 Table 導致 EX=0**。

**探索充足度：** 以 Gold FROM/JOIN 的實體表及 Agent `inspect_table` 行為作初步對照，**156/165** Dev failures 已 inspect 所需 Gold 實體表；**9/165** 至少漏 inspect 一張。這個 regex/table-catalog 分析無法完整涵蓋 CTE alias、quoted identifiers 等 SQL 特性，應視為近似。主要推論是：只增加 `inspect_table` 次數很可能不足，還須理解 **每一行代表的粒度、欄位值域與指標真正來源**。

Examples：`superhero.weight_kg` / `height_cm` 需釐清 0 代表未知；`card_games.sets.totalSetSize` 與 `cards` rows 不可等同；`financial.district.A16` 代表犯罪統計，不是 `trans` 次數；`student_club.expense_description` 可包含多件逗號分隔物品；`toxicology.connected` 要認清 Atom/Bond 主鍵及雙端關係。

<a id="traces"></a>
## 6. Agent Inference Trace

| 500 題 Structured Events | Count |
| --- | ---: |
| Model events | **2,842** |
| Tool calls / results | **3,227 / 3,227** |
| `list_tables` / `inspect_table` | 504 / 1,417 |
| `execute_sql` / `grep` | **1,301** / 5 |
| SQL tool errors | 18 |
| Final-validation events | 500 |

Trace 只包括可觀察的 model messages、Tool Args、SQL 結果、錯誤和 Final SQL；**不包含 hidden chain-of-thought**。`requested_reasoning_effort=none`，歸檔 reasoning tokens 為 0，不能由此推斷模型沒有任何內部計算。

**Dev Efficiency：** SQL calls **1,021**（平均 2.55）；Tool calls **2,549**（平均 6.37）；Model calls **2,255**（平均 5.64）；平均 input **20,715.93** tokens、output **433.43**、total **21,149.35**、cached input **11,048.32**；latency 約 **21.94s**。Cached input 已包含在 input，兩者**不可相加**；`cost_usd=null` 表示不可得，不代表免費。

| Dev SQL calls | Cases | Correct | EX |
| --- | ---: | ---: | ---: |
| 1 | 177 | 98 | 55.4% |
| 2–3 | 137 | 86 | 62.8% |
| 4–6 | 61 | 41 | 67.2% |
| 7+ | 25 | 10 | 40.0% |

成功題平均 SQL calls 約 **2.51**、失敗題約 **2.61**。7+ calls 反而較差可能是 case difficulty 的選擇效應，不能推論工具呼叫造成錯誤，亦不能說增加 budget 保證改善。

**Final SQL Text Matching**（case-fold、去註解、正規化空格、結尾分號）：Dev Correct **38/235** 的 Final SQL 與某次已執行 SQL 文字匹配，Failed **37/165** 匹配；換言之 Correct **197**、Failed **128** 不匹配。**文字不匹配比率在成功案例更高**，所以不能把 128 題當成 Final Verification 可修復機會；AST/結果等價性與風險性變更（新 Filter、改 Grain、引入 SQLite dialect）才是適當驗證目標。

### 新增 Trace Findings：Post-execution Decision Regression
- **Q33 (`california_schools`)：** 工具曾算出 572/12 ≈ 47.67；後續加入題目未要求嘅 `SOCType LIKE '%(Public)%'`，改成 519/12 = 43.25，Final SQL 甚至直接寫死 `SELECT 519.0 / 12`。係可以直接觀察到嘅 *exploration-induced predicate drift*。
- **Q354 (`superhero`)：** 一次已執行 SQL 考慮「與 Cryokinesis 持有者分享任意超能力」，回傳 9.1；Final SQL 改成只以 Cryokinesis 本身作分享條件。係 *executed-to-final semantic regression* 候選。
- **Q203 (`financial`)：** 工具曾輸出人口字串 `"1204953"`；官方 Gold 以 `CAST(A4 AS INTEGER)` 回傳。可能涉及結果型別，但必須以 SQLite/scorer 結果確認，**唔能夠只因文字型別差異就確定係根因**。
- **Q497 (`toxicology`)：** Gold 只檢查 `connected.atom_id`、Agent 檢查兩端；加入 Reference QA watchlist，未改官方標籤。
**注意：** `structured_events` 記錄可觀察工具、SQL 同回傳，並無 hidden chain-of-thought。不能從 Final SQL 文字不匹配（325/400；其中 197 correct）推斷 325 題都未經驗證，亦不能推斷 128 failed cases 可全部靠重跑 Final SQL 修復。

<a id="causes"></a>
## 7. Root Cause Taxonomy（證據級別）

| Candidate cause | SQL/Trace Evidence | Cases | Review position |
| --- | --- | --- | --- |
| Sentinel / encoded value | Gold `weight_kg > 0`，Agent 僅 `IS NOT NULL` 或未過濾 | 15-case Superhero pattern | **High-signal candidate；未做補丁重跑** |
| Metric Source / Grain | Set size ≠ Card row count；Crimes ≠ Bank Transactions | Q65、79、162、217、320、321 | 強 SQL 差異，需測修復 |
| Aggregation Population | Per-user vs per-comment；LEFT vs INNER；distinct entity | Q128、379、411、481 | 題意／分母不對 |
| Missing / Unsupported Filter | 額外 Good/Thrombosis 設限；漏 Admission | Q332、398、412、430 | 明確 predicate drift |
| Temporal Semantics | latest valid vs latest any；as-of balance | Q224、251、443、447 | 抽取時間語義需明確 |
| Output Contract | 多輸出列／欄、不同表示形式 | Q2、157、165、335、365 | 結果形狀/排序 |
| Final SQLite Syntax | `>= ALL`、未定義欄位 `item` | Q325、327 | 2 個 Dev SQL error |
| Reference QA candidates | Question/Gold 可能有不同解讀 | Q235、255、325 | **不可視為標註確定錯誤** |

**Superhero 深入：** Dev 的 29 failed cases 中，以下 **15 題** Gold 有 `weight_kg > 0` 或 `height_cm > 0`，Predicted SQL 卻沒有完整相同的有效值條件：

`Q345, Q348, Q350, Q355, Q356, Q357, Q360, Q363, Q366, Q367, Q368, Q370, Q371, Q374, Q380`。

全部 EX=0，佔 Superhero failures **15/29 = 51.7%**、全 Dev failures **15/165 = 9.1%**。Trace 未顯示針對 0 值的專門 SQL 探查。另 Q381 Gold 亦將未知體重視為 `weight_kg = 0 OR IS NULL`，支持 value semantics 需要重視。**反事實理論上限**（假設 15 題全部可修、無 regression）為 **+15/400 = +3.75pp**，不是已實測的 uplift，也不是此類根因已獨立證實造成全部 EX=0。

<a id="cases"></a>
## 8. High-Signal Case Studies（節錄）

### Q345 — Superhero: known weight

Gold：`c.colour='Green' AND s.weight_kg > 0`；Agent：`LOWER(c.colour)='green' AND s.weight_kg IS NOT NULL`。Trace：`list_tables → inspect_table(superhero) → inspect_table(colour) → execute_sql`，成功得到 **967.6** 並提交同一 SQL。問題是非 NULL 並不排除 0；`AVG` 可能把未知測量值計入。**Action：** 先查 Value Profile 再生成有效值 Filter。

### Q33 — California Schools: extra filter changed the answer

Agent 曾按 District Type 找到 **572** 間，計得 **572/12 = 47.6667**；之後自行加入 `SOCType LIKE '%(Public)%'`，縮成 **519**，最後交 `SELECT 519.0 / 12;` = **43.25**。這說明 SQL exploration 可能引入無根據條件；Query Planner 應要求每個 Filter 對應 Question/Evidence。

### Q65/Q79 — Card Games: measure source & output grain

Gold 使用 `sets.totalSetSize`，Agent 使用 `COUNT(cards)`。Q65 更在單一總量問題中 `GROUP BY s.code` 輸出每 Set 一行。屬 Source-of-Truth、粒度與結果 contract 同時出錯。

### Q217 — Financial: wrong metric

Gold 以 `district.A16` 作 1996 Crimes；Agent 用 `COUNT(trans.trans_id)` 代替。需要 Column Meaning / Metric Lineage，而不單是 tables DDL。

### Q379 — Superhero: changed denominator

Gold `LEFT JOIN alignment`，令未知 alignment 英雄仍在 denominator；Agent `INNER JOIN alignment`，漏掉該母體。計算前要寫出 numerator、denominator 各自的 population。

### Q443/Q447 — Thrombosis: latest valid laboratory record

Gold 先按 IgG/RNP **非 NULL** 篩選再找最新日期；Agent 找全部 Lab 的最新日期，兩者不能混為一談。Q447 要求 CPK 來自同一條最新有效 RNP record。

### Q325/Q327 — Student Club: Final SQL validation

Q325 使用 SQLite 不支援的 `>= ALL (...)`；Q327 使用 `json_each` 但引用未宣告的 `item` 欄位。Dev 只有兩條 final SQL errors；Selective SQLite Syntax/Execution Check 值得測試，但不能假定可修復其餘 163 條 incorrect-result cases。

**完整代表性案例（官方 Gold/Agent SQL、trace 摘要）：** [case-studies.md](case-studies.md)。**所有 165 個 Dev failures 的 CSV：** [failure-inventory.csv](failure-inventory.csv)。

### 新補充案例及跨類別現象
- **Q6 / Q7（`california_schools`）：** Agent 直接讀 stored percentage；Gold 按 Question Evidence 用 eligible count / enrollment × 100。應檢查數值尺度同 measure definition。
- **Q67 / Q88（`card_games`）：** Card printings 重複導致 `COUNT(*)` 或 ruling ID 計數同題意要求嘅 distinct ruling content 不同。
- **Q115（`card_games`）：** `sets.totalSetSize` 並非 `COUNT(cards)`；還有 `LIMIT 1` 對 ties 嘅影響。
- **Q131 / Q223 / Q236（跨 DB）：** 用 post/account/loan rows 重複計算 user 或 district-level metric，導致 population 加權錯誤。
- **Q172（`european_football_2`）：** 球員喺多場比賽出現，Agent 按 match appearances 平均身高，Gold 按 distinct players 平均。
- **Q406 / Q420（`thrombosis_prediction`）：** 題目要求兩個 scalar count columns，Agent 卻輸出按類別分組嘅兩行。
- **Q497（`toxicology`）：** Gold 可能只檢查 bond 一端；先做 reference/data QA，唔直接推斷 Agent 正確。
完整 Gold SQL／Predicted SQL／工具 trace 摘要見 [case-studies.md](case-studies.md) 新增 Appendix。

<a id="priorities"></a>
## 9. Improvement Prioritization

| Priority | Improvement | 設計理由與驗證 |
| --- | --- | --- |
| **P0** | E1 Prompt-only Value & Semantic Grounding | 明確處理 NULL / 0 / sentinel / enum；測 15 Sentinel cases、non-sentinel controls |
| **P0** | E2 Query Contract + Granularity Checklist | 強制整理 Population、Measure Source、Grain、Required/Unsupported Filters、Output Schema |
| **P1** | E3 On-demand Value Profiling Tool | 讓 Agent 在必要時取 distinct values、min/max、NULL/0 distribution；獨立比較 E1 |
| **P1** | Temporal/Aggregation Query Planning | latest-valid、as-of、ties、COUNT DISTINCT、JOIN duplication |
| **P1** | E4 Selective Final SQL Verification | 關注高風險 Final edit、新 SQLite syntax，不做盲目 unconditional retry |
| **P2** | E5 Reasoning Effort Ablation | 單獨比較 effort 改變與 tokens/latency；不先假設有效 |
| **P2** | Complex Routing / Planner architecture | 等 E1–E5 的 paired failure evidence 足夠才投入 |

本報告不假定 B1–B4 已實現；E1–E5 係**研究編號/實驗候選**，並非已執行版本或既有 B1–B4 的重新命名。

<a id="experiments"></a>
## 10. Controlled Experiment Plan

固定 **Mini-Dev 2026 revision、400 Dev membership、model/provider、system/tool policy、max calls、time limits、scoring method**，每次只更動一個因素。因本次 archive 的 SQL budget 並不統一，新對比應先跑統一設定 B0 或在比較中明確控制這個差異。

| Experiment | Single change | Target evidence |
| --- | --- | --- |
| B0 | frozen baseline | 235/400 |
| E1 | semantic checklist only | Q345/348/350/363/371/374 + 其餘 Sentinel group |
| E2 | query contract only | Q2/65/79/128/320/365 |
| E3 | value profiling tool only / vs E1 | validate whether observed DB values beat prompt-only reminders |
| E4 | selective final check | Q33/325/327, regression rate |
| E5 | higher reasoning effort only | paired all-Dev EX, SQL/tool calls, token & latency |

**Primary outcome**（同一 400 題）：

`ΔEX = (Corrected Cases - Regressed Cases) / 400`

要同時展示改正個案、退步個案、per-DB/per-category、平均及尾部 latency、input/cached/output tokens 和工具呼叫。沒有 rerun，就不能宣稱 improvement。Local Test 100 已於 repo 可見，不是嚴格未暴露 holdout；只在固定方案後描述性檢查，不對其反覆調參。

### 補充：對應失敗樣本嘅 controlled tests
| Intervention | 目標案例 | Negative controls / Safety |
| --- | --- | --- |
| E1 Semantic Grounding | Q345 / 348 / 363、Q347 / 352、Q69 / 90 | Valid zero/NULL、已正確處理 0 值嘅題目；避免「所有 0 皆排除」 |
| E2 Query Contract | Q6 / 7、Q67 / 88、Q115、Q131 / 172 / 223 / 236、Q406 / 420 | 要求選對 measure、entity grain、denominator、columns；檢查無關 query regression |
| E3 Value Profile | Q309、Q393 / 418 / 423、Q352 | Compare prompt-only E1 vs selective value profiling；限制多餘 tool calls |
| E4 Selective Final Check | Q33、Q354、Q325 / 327 | 只對高風險 final edit / dialect 引入檢查；比較 repaired 與 regressed cases |
| E5 Higher Effort | 固定 400 Dev 題 | 固定 provider、同一 2026 pinned data、統一 budget；記錄 tokens/latency |
**配對評估：** `ΔEX=(newly_correct−regressed)/400`。先統一歷史 20/40 SQL-call mixed-budget 問題；此次只提出設計、**未做實驗**。

<a id="limitations"></a>
## 11. Limitations & Reference QA Watchlist

1. **165 個 Dev failures 逐題做過 Question/Gold/Agent SQL comparison，但不是 165 個獨立驗證根因。** 現有 97 題加新增 68 題，153 題歸 provisional candidate，12 題保留 unresolved。每題可能有多個錯因；Inventory 的 `candidate_root_cause`、`case_evidence`、`review_basis` 同 `counterfactual_verification` 需一併閱讀。
2. **未做 Fresh SQLite execution。** 此研究根據官方 Gold SQL、歸檔 scorer 和可觀察 trace，比較 SQL 邏輯並提出假設；部分 SQL 可能在實際 DB 上等價或還有其他共同錯因。
3. **SQL text matching、FROM/JOIN table extraction、Natural-language categories 是 heuristics。** SQL AST、實際執行結果及 row-level comparisons 更可靠。不同形式的 SQL 可以合法等價。
4. **Reference QA Watchlist，不自動修改官方 Gold/EX：** Q235（題目外部帳戶識別為 bank+account，Gold 使用 `COUNT(DISTINCT t.account)`）、Q255（題目要求列出所有最速並列車手，但 Gold 使用 `LIMIT 1`）、Q325（題目描述日期窗，而 Gold 沒有顯式 Date Filter）、Q497（Gold 只用 bond 關係一端，而 Agent 檢查兩端）。實際資料可能令兩種解讀同結果，不可宣稱一定錯。
5. **Small N 與 confounding：** Simple 8、Moderate 32；Database、題型、難度、schema 和模型呼叫互相關聯。分組 EX 只屬描述統計，並非 causal proof。
6. **Cost metadata 缺失：** `cost_usd=null` 不能讀作 $0。Reasoning tokens 歸檔為 0 不代表可以觀察 hidden reasoning。
7. **污染風險：** 詳細 Case Studies 含官方 Gold SQL，研究文件不得加入 Agent runtime 或 Demo 的 Retrieval corpus。

**最新研究附錄（9 Nov 2026）：** [Case Studies](case-studies.md) 保留原有 97 題，新增 17 個具代表性案例（共 114 條案例條目）；其餘 51 題亦已在 [165-Case Inventory](failure-inventory.csv) 做候選 SQL 差異分類。呢個「reviewed」表示文件分析，**唔係反事實修復已通過**。

<a id="sources"></a>
## 12. Sources, Navigation & Reproduction

- **Frozen run:** [Archive Overview](../README.md)、[Configuration](../configuration.json)、[Dataset Manifest](../dataset_manifest.json)、[Reproduce](../reproduce.md)、[Checksums](../checksums.sha256)。
- **Dev:** [Scores](../dev/scores/per_question.jsonl)、[Predictions](../dev/predictions.jsonl)、[Traces](../dev/traces.jsonl)。
- **Local Test:** [Scores](../test/scores/per_question.jsonl)、[Predictions](../test/predictions.jsonl)、[Traces](../test/traces.jsonl)。
- **Official pinned reference:** [BIRD Mini-Dev 2026 Questions, Evidence and Gold SQL](https://huggingface.co/datasets/birdsql/bird_mini_dev/blob/5b256b5a9c17478f06ed6912612e9a14d17065c8/data/mini_dev_sqlite.jsonl)。[Dataset Version Rules](../../../docs/bird-dataset-versions.md)。
- **Attachments:** [English Report](baseline-analysis-en.md)、[Case Studies](case-studies.md)、[165-Case Dev Failure Inventory](failure-inventory.csv)。
- **Separate historical original dataset:** [Original Mini-Dev Baseline Analysis](../../b0-gpt6-luna-40calls-20261108/analysis-report/baseline-analysis-zh-CN.md)。

**Archive integrity:** Original run `README.md` 被包含於 `checksums.sha256`。本次不變動此 README、任何 raw scores/traces、manifests 或 checksum；研究文件放在獨立 `analysis-report/`，只在 Group Project root README 加連結，避免破壞 `sha256sum -c checksums.sha256` 的重現驗證。
