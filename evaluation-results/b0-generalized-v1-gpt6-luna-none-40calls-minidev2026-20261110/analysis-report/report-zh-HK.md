# generalized-v1 達到 63.8% EX，但語義錯誤與歷史退步仍須處理



分析範圍：BIRD Mini-Dev 2026，完整 Dev 400／Local Test 100；採用已批准 Q60 重跑後記錄。資料截止：Q60 替換及重新評分完成後。報告語言：繁體中文（香港）。



## 1. Executive Summary



**本輪 319／500 題正確（63.80%）**；Dev 255／400（63.75%），Test 64／100（64.00%）。歷史 B0 為 294／500（58.80%）：有66題變正確、41題退步，淨增25題（+5.00個百分點）。歷史B0有不同執行budget及scoring timeout，且本輪Q60經一次基建錯誤重跑，因此此差異不是新matched prompt-only因果實驗。



**主要問題是可執行但語義不符，而非普遍API或語法故障。** 181題失敗中，177題SQL可執行但結果不符；其餘為2題最終SQL執行錯誤、1題parser拒收、1題tool budget用盡。SQL工具成功率約97.2%，但EX只有63.8%；工具執行成功不能當作語義正確。



**R1–R8的改善與退步並存。** 值／缺失語義仍是最大候選失敗組（55題）；量度來源30題、輸出契約／精度27題、粒度23題。Superhero歷史淨增9題，但仍只20／50正確；thrombosis_prediction淨退4題。建議保留generalized-v1作研究候選，暫不宣布為已驗證的通用替代baseline。



[500題分析CSV](question-analysis-500.csv) · [181題根因表](failure-root-causes-181.csv) · [107題歷史轉變表](historical-transitions-107.csv) · [500題trace索引](../reproduce.md#local-traces) · [互動流程圖](../reproduce.md#local-traces)



## 2. Experiment Configuration



| 項目 | 本輪設定 |
|---|---|
| Dataset | BIRD Mini-Dev 2026；annotation revision 5b256b5a9c17478f06ed6912612e9a14d17065c8 |
| Provider／Model | chatgpt-siwc／gpt-6-luna |
| System prompt | generalized-v1；原有baseline instructions加凍結R1–R8 addendum |
| Requested reasoning effort | none；回覆metadata均報none，reasoning tokens報0 |
| Budgets | 40 model calls／40 total tool calls／40 SQL attempts cap；SQL共用總tool上限 |
| Preview／Seed | 20 rows／42；seed控制選題，不代表provider推理可重現 |
| SQL／Model timeout | 300秒／每次model request 300秒 |
| Recursion limit | 200 |
| 有效題目 | 500唯一IDs；原有400／100 split逐項核對 |
| 推理次數 | 501題目attempts：完整500＋Q60重跑1；不是501個不同題目 |
| 程式差異 | 已批准40/40/40及runner sha256 import修正；本輪分析無新增推理、無改prompt／scorer／predictions |



所有Gold SQL只用於離線評分／診斷，沒有送入runtime agent。已核對prediction與selection SHA256、manifest設定、IDs及Q60替換前後差異；其他499題原prediction／trace未變。來源檢查詳見 [../provenance.json](../provenance.json) 及 [../checksums.sha256](../checksums.sha256)。



原scorer只要收到`--question-ids`就標`is_full_split=false`並印SMOKE警告。本次runner把完整400／100 IDs傳入，因此旗標文字與實際coverage不一致；經獨立比對所有ID與dataset split，本報告確認為完整split。沒有改寫原旗標或scorer。



## 3. Overall EX Comparison



| 範圍 | 歷史B0 | 本輪generalized-v1 | 修正 | 退步 | 淨變化 |
|---|---|---|---|---|---|
| dev | 235/400 (58.75%) | 255/400 (63.75%) | 53 | 33 | +20題／+5.00pp |
| test | 59/100 (59.00%) | 64/100 (64.00%) | 13 | 8 | +5題／+5.00pp |
| overall | 294/500 (58.80%) | 319/500 (63.80%) | 66 | 41 | +25題／+5.00pp |



Overall的253題兩次都正確、140題兩次都錯、66題修正、41題退步。歷史正確294題中約13.9%退步；歷史錯誤206題中約32.0%修正。這是同一ID配對的描述，不是把歷史archive重新跑一次。



歷史configuration頂層目前寫40/40/40，但`execution_budget_history`記錄498題原SQL cap為20，只有Dev Q421／Test Q107以40重跑；歷史scoring timeout為600秒，本輪300秒。比較時保留這些實際差異，不能因metadata對齊就當歷史全500題都在40 SQL cap下產生。



## 4. Development vs Local Test Results



| 範圍 | EX | Wilson 95%區間 | 題目數 |
|---|---|---|---|
| dev | 63.75% | [58.93, 68.31]% | 400 |
| test | 64.00% | [54.24, 72.73]% | 100 |
| overall | 63.80% | [59.50, 67.89]% | 500 |



Dev與Test點估計接近，但Test只有100題，區間較闊。Difficulty由官方annotation繼承：460題challenging、32題moderate、8題simple；不是由本輪模型表現重新分難度。小組別不可作穩健優劣結論。



| Difficulty | 本輪正確／總數 | EX |
|---|---|---|
| simple | 6/8 | 75.00% |
| moderate | 24/32 | 75.00% |
| challenging | 289/460 | 62.83% |



## 5. Database and Query Category Analysis



| Database | N | 歷史EX | 本輪EX | 修正／退步 | 淨pp |
|---|---|---|---|---|---|
| california_schools | 49 | 51.02% | 65.31% | 9/2 | +14.29 |
| card_games | 69 | 56.52% | 63.77% | 12/7 | +7.25 |
| codebase_community | 31 | 61.29% | 54.84% | 1/3 | -6.45 |
| debit_card_specializing | 14 | 64.29% | 78.57% | 2/0 | +14.29 |
| european_football_2 | 31 | 67.74% | 64.52% | 1/2 | -3.23 |
| financial | 46 | 47.83% | 54.35% | 6/3 | +6.52 |
| formula_1 | 55 | 70.91% | 76.36% | 7/4 | +5.45 |
| student_club | 37 | 72.97% | 72.97% | 6/6 | +0.00 |
| superhero | 50 | 22.00% | 40.00% | 9/0 | +18.00 |
| thrombosis_prediction | 86 | 73.26% | 68.60% | 7/11 | -4.65 |
| toxicology | 32 | 59.38% | 68.75% | 6/3 | +9.38 |



Superhero增加18pp仍只有40% EX，顯示部分placeholder修正有效，但大量未量度身高／體重仍被當成0納入平均。Thrombosis_prediction由63／86降至59／86，主要退步例子包含額外Thrombosis事件篩選、診斷字串、年齡邊界及輸出標籤。Student_club淨變0，但6修正／6退步互相抵銷，不能理解為SQL行為沒有改變。



Query category依Gold SQL作可重現的**多標籤正則特徵**，不是官方語義分類或可靠AST解析；例如window、recursive CTE、日期函式、ratio `/`。同一題可屬多組，以下分母不可相加。精確規則存於重現程式及CSV。



| Gold SQL特徵 | N | 本輪正確 | EX | 歷史淨pp |
|---|---|---|---|---|
| aggregation | 442 | 275 | 62.22% | +5.66 |
| cte | 150 | 91 | 60.67% | +2.67 |
| date_or_age | 93 | 57 | 61.29% | +0.00 |
| distinct | 181 | 118 | 65.19% | +6.63 |
| exists_or_antijoin | 52 | 28 | 53.85% | -5.77 |
| grouping | 174 | 107 | 61.49% | +7.47 |
| join | 388 | 256 | 65.98% | +7.22 |
| ordering_or_topk | 184 | 118 | 64.13% | +4.89 |
| ratio_or_percentage | 99 | 68 | 68.69% | +6.06 |
| recursive_cte | 9 | 3 | 33.33% | -11.11 |
| window_function | 25 | 14 | 56.00% | -12.00 |



Window（25題）及recursive CTE（9題）歷史差異較差，只屬探索訊號；樣本小且類別重疊，不應憑此刪除某個工具或宣稱某種SQL結構造成錯誤。



## 6. Corrected and Regressed Case Investigation



全部181題失敗與66題歷史修正均已逐題審閱問題、Gold／Agent SQL，並重執行離線Gold與最終SQL；41題歷史退步包含於181題失敗。共247個重點個案：243個兩邊可執行的結果比較全部重現原EX；2個sql_error重現原生錯誤；2個missing_sql保留缺失。診斷每個query上限15秒，僅供本輪離線分析；沒有改正式300秒scorer設定，也沒有回寫任何prediction。



對候選原因另外做75次小幅SQL改寫，68次改寫結果符合Gold，涉及不同題目的對應情況見 [sql-interventions.csv](sql-interventions.csv)。同題可有多次改寫，不能把68次當作68個獨立修復，也不能當成prompt的預期增益。失敗的改寫亦保留，避免只展示成功修正。



### 已驗證的具體機制



**[Q7](failure-case-review.md#q7) · california_schools · 兩次均錯**：Agent 輸出 district code、percentage，Gold 次序為 percentage、district code。

診斷：`swap_output_columns` 改寫後與Gold結果一致；只驗證該資料上的SQL機制，未套用到本輪成績。



**[Q36](failure-case-review.md#q36) · california_schools · 兩次均錯**：printf('%.4f') 回傳文字，Gold ROUND 回傳數值；school name 來源及 NULL 判定亦不同。

診斷：`numeric_round_instead_of_text_printf` 改寫後與Gold結果一致；只驗證該資料上的SQL機制，未套用到本輪成績。



**[Q46](failure-case-review.md#q46) · california_schools · 兩次均錯**：精確比對 Provision 2 漏掉 Breakfast Provision 2（Washington Elementary／Santa Barbara）；資料探查顯示這是唯一額外Gold行，非混合provision字串。

Gold sample：`[["Los Angeles", 48], ["San Diego", 12], ["Stockton", 8], ["South Gate", 6]]`；Agent sample：`[["Arleta", 1], ["Bell", 2], ["Canoga Park", 1], ["Carson", 1]]`。



**[Q81](failure-case-review.md#q81) · card_games · 歷史啱→本輪錯**：先 DISTINCT name,artist，將 printing 計數改為卡名計數，與 Gold COUNT(*) 不同。

診斷：`remove_name_deduplication` 改寫後與Gold結果一致；只驗證該資料上的SQL機制，未套用到本輪成績。



**[Q92](failure-case-review.md#q92) · card_games · 歷史啱→本輪錯**：題目要求 Foil id alphabetical order，Agent 改用 CAST(... AS INTEGER) 排序。

診斷：`alphabetical_not_integer_id` 改寫後與Gold結果一致；只驗證該資料上的SQL機制，未套用到本輪成績。



**[Q155](failure-case-review.md#q155) · debit_card_specializing · 兩次均錯**：同一首末時間端點，julianday差*1440=3669.9999998509884，CAST截成3669；unix秒差整除為3670。

Gold sample：`[[3670]]`；Agent sample：`[[3669]]`。



**[Q194](failure-case-review.md#q194) · financial · 歷史啱→本輪錯**：把平均薪金欄 A11 錯認為 A12，影響地區選擇及差額。

診斷：`salary_A11_not_A12` 改寫後與Gold結果一致；只驗證該資料上的SQL機制，未套用到本輪成績。



**[Q218](failure-case-review.md#q218) · financial · 兩次均錯**：人口用 district.A8 而非 A4。

診斷：`population_A4_not_A8` 改寫後與Gold結果一致；只驗證該資料上的SQL機制，未套用到本輪成績。



**[Q245](failure-case-review.md#q245) · formula_1 · 兩次均錯**：1952年winner時間總毫秒88492680／8=11061585，平均11061.585秒；Agent浮點ROUND給11061.58，精確half-away規則應11061.59。

Gold sample：`[[1950, 9712.6], [1951, 10870.53], [1952, 11061.59], [1953, 10828.48]]`；Agent sample：`[[1950, 9712.6], [1951, 10870.53], [1952, 11061.58], [1953, 10828.48]]`。



**[Q279](failure-case-review.md#q279) · formula_1 · 歷史啱→本輪錯**：相同driver選擇及first win正確，career COUNT(*)=8，改COUNT(DISTINCT raceId)=7即與Gold吻合。

診斷：`distinct_race_ids` 改寫後與Gold結果一致；只驗證該資料上的SQL機制，未套用到本輪成績。



**[Q393](failure-case-review.md#q393) · thrombosis_prediction · 兩次均錯**：將RNP原始文字titer改為CAST INTEGER聚合後輸出；Gold回傳原始RNP。

診斷：`refined_targeted_diagnostic` 改寫後與Gold結果一致；只驗證該資料上的SQL機制，未套用到本輪成績。



**[Q418](failure-case-review.md#q418) · thrombosis_prediction · 兩次均錯**：輸出CAST INTEGER的MAX RNP，Gold輸出原始RNP字串；值比較以REAL。

診斷：`refined_targeted_diagnostic` 改寫後與Gold結果一致；只驗證該資料上的SQL機制，未套用到本輪成績。



**[Q441](failure-case-review.md#q441) · thrombosis_prediction · 歷史啱→本輪錯**：最後測試SQL可執行；最終改以replace拼JSON交json_each，原生SQLite報 malformed JSON。

原生錯誤：`malformed JSON`。

Gold sample：`[[250391, "F"], [1673252, "F"], [2308236, "F"], [2315140, "F"]]`；Agent sample：`null`。



**[Q442](failure-case-review.md#q442) · thrombosis_prediction · 兩次均錯**：care_setting改首字母大寫，Gold精確小寫標籤；年齡計法亦須對照。

診斷：`exact_label_case` 改寫後與Gold結果一致；只驗證該資料上的SQL機制，未套用到本輪成績。



**[Q466](failure-case-review.md#q466) · thrombosis_prediction · 歷史啱→本輪錯**：工具測試SQL成功，最終別名改為未引用women's_percentage，單引號破壞SQL，parser拒收。

診斷：`quote_free_alias` 改寫後與Gold結果一致；只驗證該資料上的SQL機制，未套用到本輪成績。



**[Q467](failure-case-review.md#q467) · thrombosis_prediction · 歷史啱→本輪錯**：age BETWEEN0 AND49額外排除負年齡記錄，Gold只要求age<50；日期上界及TRIM亦不同。

診斷：`remove_extra_nonnegative_age` 改寫後與Gold結果一致；只驗證該資料上的SQL機制，未套用到本輪成績。



**[Q494](failure-case-review.md#q494) · toxicology · 兩次均錯**：原生SQLite報 ambiguous column name: element；GROUP BY element改GROUP BY1後即與Gold四行結果一致。

原生錯誤：`ambiguous column name: element`。

診斷：`unambiguous_group_by` 改寫後與Gold結果一致；只驗證該資料上的SQL機制，未套用到本輪成績。



### Trace揭示的最終修訂風險



Q466最後一次工具SQL返回 group_count=414、women=353、85.3%，但最終alias被改成未引用的`women's_percentage`，parser才拒收。Q441工具最後測的是較寬鬆LIKE查詢，最終新增json_each字串拆解後沒有再測，離線報malformed JSON。Q494最後工具在探查element表，最終CASE alias與兩個element欄位的GROUP BY歧義未被實測發現。三者均支持「最終SQL驗證」作下一步工程候選；本次沒有自動補寫答案。



Q404有29次模型回覆、41次tool attempts、37次SQL attempts，其中36次SQL有成功結果；第41個總tool attempt被middleware阻止，並不是執行了41個成功工具。Trace後段反覆查Examination.Thrombosis，雖題目只要求女性registry患者的RNP比例，顯示探索及額外cohort條件沒有收斂。增加budget本身未證明能解決定義錯誤。



### 修正個案並非全部代表可泛化的推理改善



Q367排除measurement=0、Q236按district去重、Q224正確採用as-of交易、Q325移除SQLite不支援的ALL、Q487正確限定nitrogen端點，均有清楚SQL差異。相反Q253由字串MAX改MIN剛好取得16:42.640；同資料字串MAX是1:48.289。該題EX雖正確，字串MIN不是一般最慢時間算法，不能視作時間語義已解決。



退步亦有相反方向：Q81過度DISTINCT把printing變card name；Q92把要求alphabetical IDs改成INTEGER排序；Q132／Q313／Q365等把單行多欄改為群組多行；Q392／Q407／Q439／Q445加入額外確診cohort條件。這些現象與R1–R8相關，但沒有可觀察證據能證明是模型「因為某規則」才決定改寫。



全部107個歷史轉變個案均附歷史／本輪SQL、diff、兩輪observable trace與具體變化註記，見 [歷史轉變案例](historical-case-review.md)。



### 題意／參考需裁決，而非自動改Gold



Q205同時要求五區資料及最高平均地區，Gold列五區，Agent只列最高；Q303問題寫「majors it offers／majors held」，Gold要數量，Agent列名稱清單。兩題暫列QA，沒有改Gold或分數。Q46原先疑似provision政策衝突，資料探查後已釐清：唯一漏行為Santa Barbara的Breakfast Provision 2，故改列類別值匹配，未保留未證實的Gold錯誤指控。



## 7. R1–R8 Effectiveness Analysis



下表是人工主候選類別。每個失敗只指定一個主類別；次要差異保留於逐題說明。修正／退步的分類是SQL變化的候選關聯，不是單條規則的因果效果。



| 規則／分類 | 說明 | 失敗主類別N | 修正關聯N | 退步關聯N |
|---|---|---|---|---|
| R1 | 值／編碼／缺失語義 | 55 | 20 | 9 |
| R2 | 量度及權威欄位 | 30 | 6 | 6 |
| R3 | 實體粒度及重複加權 | 23 | 8 | 7 |
| R4 | 篩選對齊 | 20 | 8 | 7 |
| R5 | 時間／年齡／as-of | 9 | 3 | 1 |
| R6 | 關係與包含範圍 | 10 | 4 | 3 |
| R7 | 輸出契約／精度 | 27 | 13 | 6 |
| R8 | 最終SQL一致性 | 4 | 4 | 2 |
| QA | 題意／參考待釐清 | 2 | 0 | 0 |
| BUDGET | 工具探索未收斂 | 1 | 0 | 0 |



R1仍有55題失敗：NULL與0／佔位值、元素大小寫、地點token、數字字串都反覆出現。Q367等有改善，但多個superhero平均仍未排0。R2的30題主要涉及權威欄位（例如A11薪金、A4人口、A16犯罪）和totalSetSize與cards列數不等價。R3的23題涉及DISTINCT放錯位置、join weighting和零次實體被排除；Q81亦展示DISTINCT可能使原正確結果退步。



R7有27題，並非全部推理失敗：欄位次序、文字與數字、標籤大小寫和單行／多行均會被tuple-set scorer判錯。R8的4題（Q259、Q441、Q466、Q494）涉及SQLite方言／最終改寫風險，工具曾成功不代表最終版本被驗證。沒有ablation或新matched baseline，故不計算「每條規則帶來幾pp」。



## 8. Token Usage and Agent Efficiency



### 最終採用500題的記錄用量



| Metric | 歷史500題記錄合計 | 本輪500題記錄合計 | 本輪平均／題 | 本輪P50／P95 |
|---|---|---|---|---|
| input_tokens | 10,486,812 | 12,795,143 | 25590.29 | 20846.50 / 51527.85 |
| cached_input_tokens | 5,556,096 | 6,723,200 | 13446.40 | 11648.00 / 25120.00 |
| output_tokens | 219,521 | 233,182 | 466.36 | 388.50 / 1027.05 |
| reasoning_tokens | 0 | 0 | 0.00 | 0.00 / 0.00 |
| model_calls | 2,842 | 3,043 | 6.09 | 5.00 / 11.00 |
| tool_calls | 3,227 | 3,677 | 7.35 | 7.00 / 13.00 |
| sql_calls | 1,301 | 1,689 | 3.38 | 3.00 / 8.00 |
| latency_ms | 12,047,537 | 12,599,540 | 25199.08 | 20483.50 / 44909.65 |



本輪input tokens比歷史多約22.0%、output多6.2%、model replies多7.1%、tool attempts多13.9%、SQL attempts多29.8%、推理時間合計多4.6%。這些都是記錄到的頂層usage比較，不是費用估算或prompt唯一造成的增量。Cached input為input子集（本輪約52.5%）；reasoning為output子集，不可重複相加。成本USD未回報，維持未知而非0。



本輪採用結果的推理時間合計 12,599.54 秒（3.500小時），平均25.20秒、P50 20.48秒、P95 44.91秒。這不是實驗牆鐘耗時：不包括兩次score、控制程序中斷等待或離線診斷。P95用線性插值，可能與原scorer的nearest-rank略有差別。



所有3043個已記錄頂層模型回覆都有token細項；reasoning tokens均報0，effort均報none。這不代表可讀取隱藏思考，也不證明服務內部完全沒有推理。失敗HTTP請求及Deep Agents巢狀活動可能沒有usage記錄。



### 重試與attempt／execution分開



| Metric | 採用500題 | 含Q60原504的501題attempts記錄 |
|---|---|---|
| input_tokens | 12,795,143 | 12,806,124 |
| cached_input_tokens | 6,723,200 | 6,727,040 |
| output_tokens | 233,182 | 233,367 |
| model_calls | 3,043 | 3,046 |
| tool_calls | 3,677 | 3,682 |
| sql_calls | 1,689 | 1,690 |
| latency_ms | 12,599,540 | 12,611,246 |



Q60原504 attempt已有3次成功模型回覆的usage，但失敗HTTP request本身沒有response usage。因此501欄是可觀察合計，不保證等於供應商所有計費用量。最初被用戶停止並刪除的9題原prompt試跑不在本分析成本範圍，也不能還原其完整用量。



本輪3677 tool attempts只有3676個tool results；1689 SQL attempts只有1688個SQL結果（1641成功、47錯誤），差1就是Q404最後被budget阻擋的嘗試。185次SQL結果被preview截斷；這只限制agent看見的列，不是正式EX scorer截斷。



### 慢題與效能瓶頸



| Question | Split | EX | Latency秒 | Agent SQL秒 | SQL attempts |
|---|---|---|---|---|---|
| [Q193](question-analysis-500.csv) | test | 1 | 329.228 | 300.252 | 4 |
| [Q58](historical-case-review.md#q58) | test | 1 | 324.386 | 300.286 | 3 |
| [Q126](question-analysis-500.csv) | dev | 1 | 318.708 | 300.152 | 2 |
| [Q171](question-analysis-500.csv) | dev | 1 | 210.454 | 114.897 | 1 |
| [Q404](failure-case-review.md#q404) | test | 0 | 136.899 | 0.084 | 37 |
| [Q174](failure-case-review.md#q174) | dev | 0 | 96.735 | 67.086 | 2 |
| [Q40](question-analysis-500.csv) | test | 1 | 91.043 | 0.164 | 19 |
| [Q184](question-analysis-500.csv) | dev | 1 | 82.336 | 0.048 | 11 |



Q193／Q58／Q126的SQL工具時間接近300秒，主導長尾；不是單純模型生成慢。正確題平均25.86秒、失敗題24.04秒，與難度、資料庫及工具timeout混雜，不能推論多花時間會提升或降低正確率。



Trace逐字規範化比對只在33／500題觀察到最終SQL曾原樣出現於工具呼叫。其餘不等於全部有缺陷：alias、排版、輸出投影可合理改變；但Q441／Q466／Q494顯示最後修訂未驗證確有風險。另觀察到8次完全相同SQL重複呼叫，需與語義相近但字串不同的探索分開。



## 9. Limitations and Statistical Confidence



| 範圍 | 歷史ΔEX pp | 配對bootstrap 95% pp | Exact McNemar雙側p |
|---|---|---|---|
| dev | +5.00 | [0.50, 9.50] | 0.03985 |
| test | +5.00 | [-4.00, 14.00] | 0.38331 |
| overall | +5.00 | [1.00, 9.00] | 0.01990 |



Bootstrap固定seed42、20,000次，在Dev／Test內重抽完整paired question outcomes；McNemar只用corrected/regressed discordant pairs。Overall區間[+1,+9]pp及p≈0.0199描述此固定benchmark上的配對差異，不消除歷史budget／timeout／retry混雜。Test區間[-4,+14]pp跨0，單獨不足以支持穩健改善。



這些區間假設question-level抽樣足以代表不確定性，未處理同database題目相關性、跨模型重跑變異或prompt研發的選擇偏差。11個資料庫的小分組及多個重疊SQL特徵屬探索，沒有多重比較校正；不要據單一小組p值作rollout決策。



R1–R8本來由歷史Dev失敗案例提煉，Dev不是獨立prompt驗證集。Local Test亦曾被查看，因此不稱為全新unseen hidden test。每題只採用一個生成結果，Q60按基建錯誤政策重跑一次；未對語義錯誤「重抽直到答對」。本輪Q60替換後63.8%與替換前63.6%分開保存，沒有刪除失敗題分母。



RCA是可觀察SQL／trace分析，沒有模型私有chain-of-thought。診斷改寫符合Gold能驗證資料上的具體SQL差異，不證明模型的內部決策原因；沒有修復成功的個案保留候選程度或QA狀態。Gold本身亦可能與自然語言有多種合理解讀；不得自行修訂參考答案。



## 10. Conclusion and Recommended Next Improvements



**建議保留generalized-v1作研究候選；目前不以這次歷史比較宣布它已是通用最佳prompt。** EX有正向描述訊號，但41題歷史退步、輸入及工具用量增加、若干領域下降，都要求更精確的工程與驗證。



1. **優先處理最終SQL一致性。** 設計最後輸出之前的parser／SQLite檢查及一次有上限修復；先用Q441、Q466、Q494作離線回歸案例。這是未來agent政策變更，今次沒有實作或回寫成績。

2. **優先補足schema／value語義。** 對opaque欄位（A4／A11／A16）、zero measurement、字串數字、NULL與佔位值提供可審核說明；不要把所有0一律排除，也不要用DISTINCT萬用修復。

3. **收緊輸出契約及保護原正確個案。** 區分欄位順序、標籤值、數值型別、群組形狀；將41個歷史退步案例及代表性原正確案例納入離線regression評估。這些case-specific答案只供離線測試，不進runtime prompt。

4. **改善基建錯誤與探索預算。** 對可重試5xx加入有限次backoff並記錄request ID、UTC、retry次數；預留finalization空間，避免Q404耗盡budget。先版本化政策，分開報原始與重試後結果。

5. **下一次確認性比較需重新批准。** 若要把提升歸因prompt，需相同source、SQL budget、timeout、retry policy及可用model版本的新matched baseline；如要驗證R1–R8單獨效果，另設ablation。本次依用戶要求沒有新增這些推理。



## 附錄：審閱範圍與重現



主報告由現有500題結果、歷史archive、現有trace、離線SQLite診斷產生。所有181題失敗均有獨立根因註記；全部107題歷史轉變均有比較頁；500題都有可搜尋trace頁。75次診斷改寫中68次符合Gold，屬分析artifact，非模型預測、非新的EX成績。



- [全部失敗個案審閱](failure-case-review.md)

- [全部歷史轉變個案審閱](historical-case-review.md)

- [SQL診斷原始結果](sql-diagnostics.jsonl)

- [額外數值／類別probe](additional-probes.json)

- [完整metrics與區間](metrics.json)

- [來源檢查](../provenance.json)

- [來源SHA256](../checksums.sha256)



沒有commit、push、修改agent／prompt／scorer或新增模型推理。所有輸出均只保存在本地。


> Repository archive: raw traces and local HTML viewers are intentionally excluded. Trace links above point to local-reproduction guidance; full local review artifacts remain preserved separately.
