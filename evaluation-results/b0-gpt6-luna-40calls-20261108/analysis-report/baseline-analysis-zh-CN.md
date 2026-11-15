# B0 基線效能與失敗原因分析（Performance & Failure Analysis）

> **研究日期：** 2026-11-08　|　**版本：** B0 / `gpt-6-luna` / `chatgpt-siwc` / requested reasoning effort `none`  
> **評估範圍：** BIRD Mini-Dev（原始 SQLite 版本），固定本地 Dev 400 / Test 100；**診斷及改善方案以 Dev 為主**。  
> **狀態：** 既有評估的唯讀分析與後續實驗提案；沒有修改預測、評分、Agent 或模型輸出。

本報告將**已核實的測量結果**、**有 Trace 支持的案例觀察**、**待驗證假設**及**研究限制**分開呈現。EX 是執行結果準確率（Execution Accuracy），而非 SQL 能否成功執行的比率。

## 目錄

- [0. 核心摘要](#executive-summary)
- [1. 評估設定與口徑](#evaluation-setup)
- [2. 整體準確率與難度分析](#overall-performance)
- [3. 資料庫與難度交叉分析](#database-performance)
- [4. SQL 特徵與 Agent Trace](#trace-analysis)
- [5. 失敗原因分類](#root-causes)
- [6. 代表性失敗案例](#case-studies)
- [7. 改善方案與優先次序](#recommendations)
- [8. 對照實驗設計](#experiment-plan)
- [9. 限制、來源與重現方式](#limitations)

<a id="executive-summary"></a>
## 0. 核心摘要（Executive Summary）

| 指標 | 已核實結果 | 解讀 |
| --- | ---: | --- |
| 所有 500 題 EX | **299/500 = 59.8%** | Dev 59.0%，本地 Test 63.0% |
| Dev 失敗 | **164/400** | 其中 Moderate 93、Challenging 41、Simple 30 |
| Dev 中／難題失敗佔比 | **134/164 = 81.7%** | 故主要調查 Moderate/Challenging |
| 全部最終 SQL 執行成功率 | **500/500** | 全部 201 個 EX 失敗均為結果不匹配 |
| Dev 失敗且只有一次 SQL 呼叫 | **113/164 = 68.9%** | 值得測試語義複核，**非**證明應強制重試 |
| Dev 中 Final SQL 與所有已測試 SQL 的正規化文字不同 | **201/400**；其中失敗 **99/164** | 文字差異**不等於**語義差異或已證實的失敗原因 |
| Dev 既有離線 Projection 診斷 | **17 個匹配案例** | 只是使用參考結果的回顧性潛在機會，**非**已實現 +4.25pp |

**主要結論：** 現時更值得優先改善的是**題意／欄位語義理解、Aggregation / Top-K 邏輯、輸出規格及最終 SQL 驗證**，而非增加 Call Budget。最值得先做的小型實驗是「輸出與語義檢查清單」，並將「Final SQL 驗證」設為獨立可選實驗。更高 Reasoning Effort、Query Planner、Schema/Value Grounding 應分開測試；Knowledge Graph / Routing 暫時不應假定有效。

**分析優先次序：** 以 400 題 Dev 為研究對象，簡單題做針對性錯誤抽查，中／難題深入分析；按 Database 的**失敗率和失敗數量**兩個維度選案例。

<a id="evaluation-setup"></a>
## 1. 評估設定與口徑

| 項目 | 歸檔執行設定 |
| --- | --- |
| Provider / Model | `chatgpt-siwc` / `gpt-6-luna` |
| Requested Reasoning Effort | `none`；回應中的可觀察設定保留於 Predictions/Traces |
| Dataset | 原始 BIRD Mini-Dev SQLite，500 題、11 個 Database（非 Mini-Dev V2） |
| Local Split | 400 Dev / 100 Test，seed 42；同一次全新推理 |
| 每題最大預算 | Model 40、總 Tool 40、SQL 20；Graph recursion limit 200 |
| Model request timeout | 每次請求 300 秒 |
| Scorer timeout | 每條參考／預測 SQL 600 秒 |
| Agent SQL tool timeout | 此歸檔執行使用 5 秒；目前程式文件描述較長預設值，未來比較要匹配或明確披露 |
| 執行時間 | 2026-11-08 03:59:35–06:32:14 UTC（約 2 小時 33 分鐘） |

**EX 定義：** 比較預測 SQL 與參考 SQL 執行所得的**完整結果元組集合**；不以列順序或重複列決定正確，但欄數、欄位位置及數值會影響結果。SQL 語法合法或執行成功，不代表答案在語義上正確。Gold SQL、Gold Result 只供診斷／評分，不能輸入正在評估的 Agent。

原始 Scorer 因傳入明確 Question IDs，而標示 `is_full_split: false`／selected subset；但比對 ID 清單確認本地 Dev 400 + Test 100 全部覆蓋，綜合 Summary 記錄 `covers_full_local_split: true`。**這並非 BIRD 官方 Hidden Test 成績**。59% Dev 與 63% Test 是不同問題集合，不能當成改進前後的效果。

<a id="overall-performance"></a>
## 2. 整體準確率與難度分析

### 2.1 整體成績

| Split | 正確 | 總題數 | EX | 失敗 |
| --- | ---: | ---: | ---: | ---: |
| Dev | 236 | 400 | **59.0%** | 164 |
| Local Test | 63 | 100 | **63.0%** | 37 |
| **Overall** | **299** | **500** | **59.8%** | **201** |

推理及評分完成全部題目，沒有遺失最終預測或最終 SQL 執行錯誤。全部 201 個 EX 錯誤均屬 `incorrect_result`，所以首先應研究**語義結果錯誤**。

### 2.2 Dev 按難度分析

| Difficulty | 正確／總數 | EX | 失敗數 | 佔全部 Dev 失敗 |
| --- | ---: | ---: | ---: | ---: |
| Simple | 87/117 | **74.4%** | 30 | 18.3% |
| Moderate | 107/200 | **53.5%** | 93 | 56.7% |
| Challenging | 42/83 | **50.6%** | 41 | 25.0% |
| **合計** | **236/400** | **59.0%** | **164** | **100%** |

Moderate + Challenging 合計 134 題失敗，占 Dev 失敗 **81.7%**。建議將大部分深入 Trace 研究放在這兩組，Simple 僅針對系統性錯誤及回歸風險審查。Simple 仍有 30 題錯誤，不宜完全忽略。

<a id="database-performance"></a>
## 3. 資料庫與難度交叉分析

### 3.1 Dev 完整 Database × Difficulty 矩陣

每格格式為「正確／題數（EX）」；按**失敗題數**排序，協助找出能挽回最多題目的領域。

| Database | 失敗 | Overall EX | Simple | Moderate | Challenging |
| --- | ---: | ---: | --- | --- | --- |
| `formula_1` | **24** | 29/53（54.7%） | 14/22（63.6%） | 11/21（52.4%） | 4/10（40.0%） |
| `thrombosis_prediction` | **21** | 20/41（48.8%） | 4/6（66.7%） | 10/22（45.5%） | 6/13（46.2%） |
| `card_games` | **18** | 23/41（56.1%） | 7/10（70.0%） | 12/26（46.2%） | 4/5（80.0%） |
| `financial` | **16** | 9/25（36.0%） | 1/2（50.0%） | 6/17（35.3%） | 2/6（33.3%） |
| `codebase_community` | **15** | 24/39（61.5%） | 15/17（88.2%） | 8/18（44.4%） | 1/4（25.0%） |
| `european_football_2` | **15** | 26/41（63.4%） | 7/11（63.6%） | 14/20（70.0%） | 5/10（50.0%） |
| `california_schools` | **14** | 10/24（41.7%） | 2/6（33.3%） | 7/14（50.0%） | 1/4（25.0%） |
| `toxicology` | **13** | 19/32（59.4%） | 3/4（75.0%） | 8/14（57.1%） | 8/14（57.1%） |
| `student_club` | **10** | 28/38（73.7%） | 15/17（88.2%） | 10/17（58.8%） | 3/4（75.0%） |
| `debit_card_specializing` | **9** | 15/24（62.5%） | 9/11（81.8%） | 6/10（60.0%） | 0/3（0.0%） |
| `superhero` | **9** | 33/42（78.6%） | 10/11（90.9%） | 15/21（71.4%） | 8/10（80.0%） |

**兩種不同的優先級：** （a）最低準確率：`financial`、`california_schools`；（b）最多失敗題：`formula_1`、`thrombosis_prediction`、`card_games`。只用 EX 排名會忽略題數差異；只用失敗數又會忽略領域的相對困難。

### 3.2 Difficulty-mix-adjusted 描述性比較

用整個 Dev 的難度準確率（Simple 87/117、Moderate 107/200、Challenging 42/83）乘各 Database 的難度題數，估計其難度組成下的預期 EX。這**不是因果歸因或顯著性測試**。

| Database | 實際 Dev EX | 按難度組成預期 EX（約） | 差異 |
| --- | ---: | ---: | ---: |
| `financial` | 36% | 54% | **−18pp** |
| `california_schools` | 42% | 58% | **−17pp** |
| `formula_1` | 55% | 62% | −7pp |
| `thrombosis_prediction` | 49% | 56% | −7pp |
| `student_club` | 74% | 63% | +11pp |
| `superhero` | 79% | 58% | +20pp |

`financial` 和 `california_schools` 的低分不完全由難度分佈解釋，但仍可能受 Schema 規模、問題類型、資料值及樣本波動影響。個別切片只有 2–6 題，必須標註分母。這裏的「Database 類型」是**業務領域與 Schema 特性**；11 個資料庫引擎均為 SQLite，不是 MySQL 與 PostgreSQL 的比較。

### 3.3 後續 Database 研究問題

優先檢查：表／欄數、Foreign Key 是否足夠、需要的 JOIN 層數、含糊欄位命名、特殊值／日期編碼、聚合與答案粒度。按 Database 及這些特徵交叉統計，才可判斷是否值得投入 Knowledge Graph 或 Metadata Grounding。

<a id="trace-analysis"></a>
## 4. SQL 特徵與 Agent Trace 分析

### 4.1 Dev 最終 SQL 結構特徵

按最終**預測 SQL**是否含有關鍵字／模式分組；同一題可出現在多個類別，且預測 SQL 使用某語法不代表題目真正需要它。

| SQL 特徵 | 正確／包含該特徵的題目 | EX | 失敗 |
| --- | ---: | ---: | ---: |
| JOIN | 170/296 | 57.4% | 126 |
| Subquery（`(SELECT`） | 37/90 | 41.1% | 53 |
| DISTINCT（任何位置） | 62/107 | 57.9% | 45 |
| ORDER BY | 44/80 | 55.0% | 36 |
| GROUP BY | 23/57 | 40.4% | 34 |
| CASE | 28/58 | 48.3% | 30 |
| LIMIT | 27/55 | 49.1% | 28 |
| COUNT(DISTINCT …) | 16/43 | 37.2% | 27 |
| CTE（以 WITH 開頭） | 3/16 | 18.8% | 13 |

**觀察：** 複合查詢、GROUP BY、COUNT DISTINCT 等組別準確率偏低，適合作為**進一步審查對象**。由於問題難度及 SQL 特徵高度混雜，不能得出「CTE 導致失敗」等結論；需要結合題意、參考 SQL 與 Trace 判讀。

### 4.2 Agent 實際行為：Dev 400 題

| 可觀察指標 | 結果 | 解讀 |
| --- | ---: | --- |
| 失敗且恰好 1 次 SQL 呼叫 | 113/164（68.9%） | 值得研究第一次查詢後是否欠缺驗證 |
| 失敗且 ≥2 次 SQL 呼叫 | 51/164 | 額外呼叫不代表最終結果正確 |
| Final SQL 與所有已呼叫 SQL 正規化**文字**不一致 | 201/400（50.3%） | 可能只是 Alias、排列或等價重寫 |
| 上述文字不一致且失敗 | 99/164（60.4%） | 候選驗證問題，**非**99 個因果證據 |
| 曾有空結果的 SQL 呼叫 | 24/400；當中失敗 13 | 空結果不一定是錯誤 |
| 至少一次 SQL 預覽截斷（Trace 逐題） | 51/400；當中失敗 23 | 不等於 Scorer 截斷 |
| 沒有呼叫 `inspect_table` | 0/400 | 本次每題至少檢查一張表 |

Trace 文字比較方法：提取 `execute_sql` 的輸入與 `report.final_sql`，移除空白／註解、統一大小寫及結尾分號後做字串比對。**它不是 SQL AST 或語義等價檢驗**；任何不一致均標為「未與已測試 SQL 文字完全對上」，不能稱為已確認的邏輯變化。原始 Trace 中的 Tool Preview 通常只顯示最多 20 行。

### 4.3 Efficiency：保留作次要指標

下表覆蓋所有 500 題，P95 為 nearest-rank。

| Metric | Mean | Median | P95 | Max |
| --- | ---: | ---: | ---: | ---: |
| Model calls | 4.78 | 4.00 | 7.00 | 18 |
| Tool calls | 4.90 | 5.00 | 8.00 | 19 |
| SQL calls | 1.47 | 1.00 | 3.00 | 14 |
| Total tokens | 15,298.74 | 13,573.50 | 26,514 | 81,685 |
| Latency (ms) | 17,093.78 | 15,022 | 29,722 | 80,105 |

總計 736 次 SQL Tool 呼叫、其中 6 次錯誤（涉及 5 題）；66 題至少有一次 SQL 預覽截斷。最大 Model Calls 18 次，遠低於 40 次限制，因此**未觀察到 Call Budget 耗盡這個瓶頸**。失敗題平均使用 5.04 Model Calls、16,889 Tokens、18.35 秒；成功題平均 4.60、14,229、16.25 秒。這些是關聯，不是更多呼叫導致失敗的證據。Cost 未能觀察到，應標為 unknown，不能當作零。

<a id="root-causes"></a>
## 5. 失敗原因分類（Root Cause Taxonomy）

這是待用於**全部 164 個 Dev 失敗案例**的分類框架；目前只對部分案例有足夠證據。**以下不是已完成、互斥的 164 題原因計數**。一題可有多個原因，亦可標記 `uncertain` 或 `reference-review`。

| 分類 | 核對內容 | 已審查例子／狀態 |
| --- | --- | --- |
| Schema / Column Mapping | 選錯實體、欄、Join Key | Q89、Q861：有觀察證據 |
| Value / Evidence Interpretation | 值編碼、欄位定義與 Evidence | Q231：未核實 label 編碼 |
| Join / Row Duplication | JOIN Path、重複計數、One-to-many | Q197：參考 SQL 亦存爭議 |
| Aggregation / Granularity | GROUP BY、COUNT DISTINCT、計算分母 | Q17、Q1322 |
| Ranking / Top-K | LIMIT、排序、Rank、Tie | Q846、Q726、Q728 |
| Date / Filter Logic | Timestamp vs Date、ABS、期間 | Q533、Q82、Q1338 |
| Output Specification | 輸出欄數、欄順序、名稱拆分 | Q1486、Q1381；17 題 Projection 診斷 |
| Final SQL Verification | 測試結果與 Final SQL 不一致／修正未確認 | Q82、Q1322：具體 Trace 案例 |
| Reference / Annotation Ambiguity | 問題、Evidence、Gold SQL 互相矛盾 | Q345、Q197、Q1322：需人工裁決 |

### 5.1 已有離線 Projection 診斷（保留原始研究）

既有報告以唯讀方式在 164 個 Dev 失敗案例重跑 Gold/Predicted SQL，獨立使用**每條查詢 1 秒**及最多 **100,000 Rows**。160 題完成；Q192、Q530、Q595、Q1014 因診斷 Timeout 未完成。160 題中，44 題結果欄數不同；其中 17 題在對預測結果列做選取／重排後，與參考結果集合匹配：

`Q32, Q87, Q125, Q231, Q345, Q402, Q634, Q798, Q829, Q981, Q989, Q1078, Q1145, Q1192, Q1338, Q1486, Q1533`。

難度分佈：Simple **3**、Moderate **8**、Challenging **6**。17/400 相當於 **4.25 個百分點的回顧性上限提示**，**不是**可直接部署的提升規則，也不能證明在其他資料例子上 SQL 等價。44 題包含缺欄與其他情況，不可全部歸類成「多了欄位」。原始 EX 不作修改。

<a id="case-studies"></a>
## 6. 代表性失敗案例（Evidence-based Case Studies）

以下例子來自 [Dev Trace](../dev/traces.jsonl.gz)、[Dev Score](../dev/scores/per_question.jsonl) 及既有離線 Gold 比較。每個解讀區分「實際觀察」與「候選原因」；部分參考答案仍需核對。

### 6.1 Simple：Q82 — 絕對 Longitude 的條件錯誤

- **Question / Evidence：** 找 Longitude **絕對值**最大的學校之 `GSoffered`。
- **Trace：** Agent 先用 `Longitude = MAX(ABS(Longitude))` 得到空結果，其後按 `ABS(Longitude) DESC` 找到學校及 `GSoffered = 'K-8'`；最後交回的 SQL 仍將**原始負 Longitude**與正的 `MAX(ABS(Longitude))` 相比。
- **觀察：** 中途檢查曾取得有效候選結果，但 Final SQL 沒有保留正確的絕對值比較。
- **候選改進：** Filter semantics checklist、Final SQL 重新驗證。

### 6.2 Simple：Q17 / Q861 — 排名與實體欄位

- **Q17（California Schools）：** 對 Charter Number 分組並計算 AVG，未輸出參考答案要求的排名；應核對題意指定的「每行代表甚麼」及 Rank 欄。
- **Q861（Formula 1）：** 選了 `qualifying.number`，參考使用 `drivers.number`；兩個名稱相近但代表不同實體。
- **候選改進：** Output grain / Rank 規格、Column ownership grounding。

### 6.3 Moderate：Q89 — Financial 欄位語義

題意：「East Bohemia 有多少選擇交易後收費／發行頻率的帳戶？」Evidence 涉及 `'POPLATEK PO OBRATU'`。Agent 反覆在 `order.k_symbol`、`trans` 等欄位查值，最後仍用 `order.k_symbol` 過濾，得到 0；既有 Gold 比較指出目標應對應 `account.frequency`。Trace 中還出現一次不存在的欄位及一次多語句 SQL 執行錯誤。

**候選原因：** 相似業務概念分散於不同表，單靠 DDL 難以辨別欄位語義及值；增加 SQL 嘗試次數未必可修復。**改善方向：** 值域驗證、欄位定義／Evidence Grounding。

### 6.4 Moderate：Q846 — Formula 1 的 Top-K

Evidence 明確提到第一段 Qualifying 淘汰的**5 名**車手。Agent 用 `q1 = (SELECT MAX(q1) …)`，Trace 只返回 1 名；問題涉及返回數量及排序邏輯，而不只是正確 JOIN。

**候選改進：** Query Planner 明確列出 `expected cardinality = 5`、Sort / Limit 及 Tie 規則，並檢查結果數量。

### 6.5 Moderate：Q1322 — 已測試計數與 Final SQL 分組不同

Question 要求計算「出席人數超過 10 的 Event 中，有幾個 Meeting？」Trace 中 Agent 已測試過以 Subquery 先篩選 Event，再 `COUNT(*)` 的版本，得到單一數值 **4**；Final SQL 卻改成 `GROUP BY e.event_id HAVING COUNT(...) > 10`，未再次執行。後者可能返回每個 Event 各一行，與要求的單一總數粒度不同。

**候選改進：** Final SQL 再執行、Result Grain 檢查。**限制：** 此題既有報告指出 Gold SQL 本身亦值得複核；不要直接以未裁決的參考語義作完整因果判斷。

### 6.6 Moderate：Q1338 / Q1486 — 日期與多餘欄位

- **Q1338（Student Club）：** 初始用 `event_date = '2019-10-08'` 得到空結果，查到資料實際帶時間後改用 `LIKE '2019-10-08%'`；Final SQL 已修正日期，但多出 `expense_description`，與 Gold 所需輸出不完全一致。
- **Q1486（Debit Card）：** Trace 已求得 CZK 與 EUR SME 人數差為 **23505**；Final SQL 額外返回 Yes/No 欄。這個 Yes/No 對自然語言提問未必不合理，但與參考結果的欄結構不同。故應記為**答案規格／參考口徑問題**，不是單純數學計算失敗。

### 6.7 Challenging：Q28 / Q36 / Q231 / Q1192

- **Q28（California Schools）：** 先求 Enrollment 差異的平均，再挑出高於平均的學校；屬多階段 Aggregation / Filter，具 Planner 檢查價值，但現有證據未足以確定唯一失敗原因。
- **Q36（California Schools）：** Evidence 明確指出學校最多有三名 Administrator，Trace 檢索了多組姓名欄，但 Final SQL 只輸出第一名；需檢查完整性要求。
- **Q231（Toxicology）：** Trace 讀到 `molecule.label = '-'`，Final SQL 卻直接與 `'carcinogenic'` 比較；應先確認 `label` 的實際編碼，不可臆測。
- **Q1192（Thrombosis）：** 使用 `Patient.*` 輸出多個欄；離線 Projection 診斷可從其結果欄選出與參考匹配的子集。可檢查只輸出問題指定患者識別資訊的規格，但具體要求仍以題意和合法 Evidence 為準。

### 6.8 其他既有例子與參考爭議

- **Q533：** 原有 Gold 比對指出應先提取日期，再作日期範圍比較；直接比較 Timestamp 有邊界／粒度風險。
- **Q726 / Q728：** 排序結果與 Gold 預期的顯式 Rank 欄不一致。
- **Q1381：** Agent 合併名字為一欄，Gold 返回 `first_name`、`last_name` 兩欄。
- **Q345：** 問題／Evidence／Gold SQL 在 `type` 與 `types` 上有不一致，應獨立標示。
- **Q197：** Gold SQL 的 Atom/Bond JOIN 可能重複計算 Atom，尚未確認為標註錯誤。
- **Q1322：** Gold Query 的分組與計數設計亦值得複核。

**原則：** 不修改 Gold 或正式 EX；將爭議列入 `reference-review`，需人工核對後才能下最終結論。

<a id="recommendations"></a>
## 7. 改善方案與優先次序

| Priority | 方案 | 對應觀察 | 應如何驗證 |
| --- | --- | --- | --- |
| **P0** | **Output / Semantic Checklist** | 17 題 Projection 診斷、Rank / Grain / Output 欄差異 | Prompt-only opt-in 對照；記錄修正與退步 |
| **P0** | **Final SQL Verification**（獨立 Variant） | Q82、Q1322；99 題失敗有 Final SQL 文字差異 | 選擇性重新執行最終 SQL，檢查語義與空結果；不可假定所有文字差異都有錯 |
| **P1** | Schema / Value Grounding | Q89、Q861、Q231 等欄位／值解讀 | 先確認同類原因反覆出現，才加入 Metadata/Value 提示 |
| **P1** | Explicit Query Planner | Q846、Q28；Aggregation、Top-K / Subquery 低 EX 組別 | 在相同模型及工具預算下比較 Planner 前後 |
| **P1** | Reasoning Effort Ablation | B0 requested `none` | 保持原 Prompt，測更高**實際支援**的 Effort |
| **P2** | Knowledge Graph / Adaptive Routing | 尚無足夠證據顯示為主要瓶頸 | 等測得 Schema Join / Model Choice 根因後再投入 |

**不建議**目前盲目提高 Model/Tool Call 上限，也不應機械刪除多餘欄位、對所有排名題加 Rank、或無條件強制每題二次 SQL 執行。應尊重問題的實際 Output Contract 和現有安全邊界。

<a id="experiment-plan"></a>
## 8. 對照實驗設計（Accuracy First）

### 8.1 第一輪：分離 Prompt 與 Reasoning Effort

| Variant | Prompt / Controller | Reasoning Effort | 目的 |
| --- | --- | --- | --- |
| **B0** | 原始 Prompt | `none` | 歸檔基準 |
| **E1** | Output / Semantic Checklist | `none` | 測 Checklist 獨立影響 |
| **E2** | 原始 Prompt | 較高且受支援的設定（例如 `medium`） | 測 Effort 獨立影響 |
| **E3** | 同 E1 | 同 E2 | 測組合效應 |

不要同時把 Planner、Grounding、Verification 混入 E1，否則無法分辨收益來源。第二輪另設 Final SQL Verification / Query Planner / Grounding 的 opt-in 變體，根據第一輪及人工失敗分類結果決定先後。

### 8.2 評估規則與成功標準

1. 以**同一批 Dev Question IDs**做 paired comparison；固定 Dataset 版本、Evidence Policy、Model/Provider、Scorer、SQL 安全規則，以及可比較的 Tool Budget/Timeout。任何差異都要記錄，歸檔 B0 不覆蓋。
2. 記錄 `EX`、`corrected_count`（B0 錯→新正）、`regressed_count`（B0 正→新錯）、兩者差額、按 Difficulty/Database 分組結果，及 paired uncertainty；不要只看整體提升。
3. Token、Tool Calls、Latency 作**次要指標**，繼續保存而非先行優化。記錄 requested 與 response-reported Reasoning Effort；無法驗證啟用時不作性能歸因。
4. 可先用 Dev 小樣本進行功能 Smoke Test，再固定方案在完整 Dev 測試。若資源許可，重跑 B0 估計 Hosted Model 波動。
5. 選定配置後才在 Local Test 評估；既有 Local Test 基線已被查看，**不可依其逐題錯誤調參**，並在報告披露這點。
6. 不設定無證據的「必達 EX」或「必得 +4.25pp」。報告所有修正與退步例子及 Compute Trade-off。

<a id="limitations"></a>
## 9. 限制、資料來源與重現方式

### 9.1 證據等級與局限

- **確定測量：** 500/400 題 Score、模型呼叫計數、Database/Difficulty 分組與可觀察 Tool Events。
- **探索性 Trace 指標：** Final SQL 的正規化文字比對、SQL Feature Regex、空結果／預覽截斷。不是 SQL 語義等價或因果證明。
- **回顧性 Gold 診斷：** 160/164 完成的 Projection Audit 使用 1 秒時限及本地 Gold 結果；未保存獨立可重跑腳本。與正式 Scorer 600 秒時限不同，必須披露。
- **人工審查未完成：** 代表性例子不足以量化全部 164 個失敗原因的盛行率；不可把候選 Root Cause 視為完整標註。
- **小樣本與混雜：** 個別 Database × Difficulty 切片僅數題；SQL Feature 分析與題目難度相互影響。
- **Usage 觀察限制：** 只有 Provider 回報的部分數據可見；Cached Input 已包含在 Input Tokens，Reasoning Tokens 已包含在 Output Tokens；Hidden Reasoning Text 不可見，Subagent Usage 可能不完整，Cost Unknown。
- **再現性：** 模型 Slug 不代表固定權重版本；新推理可能受模型更新、採樣、環境與 Cache 影響。保存原始 Run IDs / Provenance 和設定。
- **正式結果保護：** 不因 Reference 爭議改 Gold、Predictions、Scores 或原始 EX。

### 9.2 原始檔案及重現入口

| 類別 | 原始檔案 |
| --- | --- |
| Run 概覽 | [README](../README.md)、[Combined Summary](../summary.json)、[Configuration](../configuration.json) |
| 可追溯性 | [Dataset Manifest](../dataset_manifest.json)、[Provenance](../provenance.json)、[Environment](../environment.json) |
| Dev 評分與輸出 | [Per-question Scores](../dev/scores/per_question.jsonl)、[Predictions](../dev/predictions.jsonl)、[Compressed Traces](../dev/traces.jsonl.gz) |
| Test 評分與輸出 | [Per-question Scores](../test/scores/per_question.jsonl)、[Predictions](../test/predictions.jsonl) |
| 重現指引 | [Reproduce](../reproduce.md)、[Checksums](../checksums.sha256) |

**聚合重算：** 依 `split`、`difficulty`、`db_id` 對逐題 `ex` 求和；EX = 正確題數／總題數。SQL Feature 只以 Predicted SQL 的文字模式識別並需容許重疊。Trace 比對須用 `question_id` 與 Split Join，不可把同名 ID 混淆。P95 依 `ceil(0.95 × n) - 1`（從 0 開始）的 nearest-rank 索引。

**本次文檔更新範圍：** 將原有與新增已觀察結果整合成報告；**沒有**新的模型推理、重新評分、獨立 Gold 診斷或 Agent 程式改動。
