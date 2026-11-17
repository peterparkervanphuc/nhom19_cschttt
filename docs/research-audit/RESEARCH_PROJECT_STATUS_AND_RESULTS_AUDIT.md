# Kiểm toán tình trạng và kết quả nghiên cứu · Round 1–4

## Tóm tắt điều hành

Ảnh chụp ngày 17/11/2026, giờ Việt Nam. **PARTIALLY COMPLETE** theo cổng tái lập Round 4. Repo độc lập đã có pipeline từ event log tới prediction, ba pre-study, Backward Explainer (BE), Attention Exploration (AE), đánh giá giải thích và xuất đồ thị. Đã xác minh 12/12 baseline dự báo và 12/12 đồ thị BE. Phạm vi pre-study chính đã hoàn tất là **E1 9/12, E2 9/12, E3 11/12**. Helpdesk, Sequence và Long-Dist-Dep có E1–E3, BE và AE vét cạn, cùng đánh giá cặp cả hai phương pháp. Sequence còn có kết quả lặp lại qua lệnh pipeline tích hợp. BPIC12_WC E2 là kết quả mới so với bàn giao cũ, đủ **184.720 cặp model–prefix**, 10 mô hình. Biên bản kiểm tra xác nhận đủ 18.472 prefix cho mỗi mô hình và SHA của manifest cũng như ledger. Nguồn `artifacts/bpic12-wc-v1/e2-record-audit.json`. BPIC12 đầy đủ có đủ 73.742 prefix và 53 cạnh BE đã xác minh.

Ba mức cần đọc riêng là mã đã triển khai, cohort đã chạy và mức khớp nghiên cứu công bố. Phần lớn chênh lệch định lượng chưa có đối chứng cùng split, checkpoint và cách xử lý. Các lượt dở dang có thống kê từ dữ liệu thật và giới hạn toán học bên dưới. Báo cáo học thuật chưa được soạn trong tài liệu này.

Nguồn A là **DIRECTLY OBSERVED** trong thực thi độc lập. B là **RECONSTRUCTED / DERIVED** từ bằng chứng độc lập. C là **ESTIMATED / PREDICTED**. D là **PAPER-REPORTED**. E là **REFERENCE-REPOSITORY RESULT**, gồm artifact bổ sung của tác giả nhưng ghi rõ xuất xứ archive thay vì gán cho Git tree. F là **UNRESOLVED**. Các kiểm thử fixture dùng kiểm tra phần mềm. Mọi số liệu benchmark chính đều có nguồn cấp log hoặc cấp run.

## Lịch sử Round 1–4

| Round | Mục tiêu ban đầu | Công việc có bằng chứng | Quyết định chính | Bằng chứng | Khoảng trống | Trạng thái |
|---|---|---|---|---|---|---|
| 1 | Tách bài thành research map, evidence matrix và sơ đồ | Có bản Markdown/PDF, XLSX và ZIP Mermaid. Các tài liệu tạo cơ sở truy vết câu hỏi, thuật toán và kết quả | Đặt ID E01–E24 để nối nhận định với nguồn | Thư mục sản phẩm Round 1/2, các file không có hậu tố R2 | Bản đầu mang các lỗi công thức và diễn giải được đưa vào vòng kiểm tra sau | VERIFIED COMPLETE cho bộ hiện vật, phụ thuộc Round 2 với các nhận định đã sửa |
| 2 | Kiểm tra trực quan và số học, sửa blueprint | Có map R2 Markdown/PDF, workbook và ZIP R2, validation report. Người dùng cung cấp workbook QA Corrected sau R2 | Head n×dᵥ, concat n×hdᵥ, Wᴼ về n×dₘ. Phân biệt cosine distance và similarity, giữ bất định Hình 5, NaN và thứ tự AE/BE | Round_2_Validation_Report.md và Research_Evidence_Matrix_Dao_Ngoc_Duy_R2_QA_Corrected.xlsx | Việc workbook tồn tại không chứng minh mọi số của phiên bản đầu chính xác. Dùng reconciliation cho Table 2 và 3 | VERIFIED COMPLETE cho bộ kiểm định đã lưu, bất định cấp bài báo còn mở |
| 3 | Lập thiết kế độc lập, mapping, lịch chạy và tiêu chí | Blueprint, kiến trúc, experimental design, ma trận và register trong docs/round3 | Repo độc lập dùng nguồn tác giả để giải nghĩa. Xác định primary và diagnostic, khóa seed, split và metric | ROUND_3_FINAL_BLUEPRINT.md, IMPLEMENTATION_ARCHITECTURE.md, EXPERIMENTAL_DESIGN.md, RESEARCH_TO_CODE_MAPPING.xlsx, EXPERIMENTAL_RUN_MATRIX.xlsx | Trạng thái trong XLSX chủ yếu phản ánh kế hoạch lúc lập | VERIFIED COMPLETE trong phạm vi lập kế hoạch |
| 3.5–3.6 | Rewind và khóa các quyết định trước khi code | Có preflight và hợp đồng triển khai. Người dùng xác nhận uv CPython 3.11.15 riêng, không dùng gói ở Python Store | D02 bốn head × 9, D05 zero sau softmax, quy ước E1 DFG/cosine, E2-FC với các diagnostic riêng, floor bộ nhớ/đĩa và checkpoint | docs/round4_preflight/decision_closure, S0 receipts | Khác biệt bài, mã, checkpoint lịch sử vẫn có ý nghĩa | VERIFIED COMPLETE cho hợp đồng nội bộ |
| 4 | Triển khai, thực nghiệm thật, đánh giá, đối chiếu | Đủ C01–C12 trong repo. 12 baseline, 12 BE, pre-study 9/9/11, AE cặp ba benchmark, BE-only bốn benchmark | Tiếp tục từ snapshot đúng hash. Lưu SQLite có seal, phân biệt full schedule, pilot và cận. Mọi sai khác với phiên bản lịch sử được giữ trong phân tích | docs/round4, artifacts trên D và locators ở C, bảng dưới | Một số study chưa đủ, AE không khả thi ở nhiều cohort, đối chiếu lịch sử còn lệch | PARTIALLY COMPLETE |

Thư mục hiện vật Round 1–2 là `C:/Users/Ngoc Duy/.codex/visualizations/2026/11/16/01a1e37a-016e-71f0-b6c4-78acd306dba7/`. Bản QA corrected nằm trong Downloads theo thông tin người dùng. Lịch sử trước phần cuộc trò chuyện khả dụng được khôi phục qua tài liệu và Git, vì vậy những quyết định chỉ tồn tại trong trao đổi chưa lưu không được xác nhận. Đọc thêm [Round 3 blueprint](../round3/ROUND_3_FINAL_BLUEPRINT.md) và [hợp đồng Round 3.6](../round4_preflight/decision_closure/ROUND4_IMPLEMENTATION_CONTRACTS.md).

## Kiểm toán triển khai và quan hệ pipeline

| Thành phần | Kỳ vọng và hành vi độc lập | Mã và kiểm tra | Bằng chứng thực thi | Trạng thái |
|---|---|---|---|---|
| C01 · Tiền xử lý | XES/CSV và prefix theo case. Sắp timestamp rồi ordinal, vocab học từ train, giữ nhãn chưa thấy khi chấm | data/pipeline.py, data/preparation.py, test_data.py, test_preparation.py | 12 dataset configs và provenance, mỗi log có prepared và identity trong checkpoint | VERIFIED COMPLETE |
| C02–C04 · Model/train/inference | Activity + position embeddings, self-attention QKᵀ/√9, 4×9, Wᴼ về width 36, FFN 64, normalization, pooling, softmax next activity. Training theo 10 epoch, Adam, batch12, lr .001, seed1729. | model/transformer.py, training.py, predictor.py. test_model.py, test_training.py kiểm tra số học bốn head, mask, resume | 12 run.json, checkpoint.pt và predictions.json. Receipt kiểm tra finite FP32, shape, optimizer và epoch ở artifacts/s0/twelve-baseline-checkpoint-audit.json | VERIFIED COMPLETE cho baseline độc lập |
| C05 · E1 | Perturb prefix qua DFG/mask, dùng cosine distance của vector dự đoán để lấy common importance, tổng hợp theo hoạt động, so attention importance qua Kendall tau-b | experiments/studies.py, perturbations.py, e1_streaming.py. test_experiments.py, test_e1_streaming.py | 9 manifest hoàn tất. Sepsis ledger thật dở dang. Full BPIC12 và Complex có cận hoặc count | IMPLEMENTED, NOT FULLY EXECUTED |
| C06 · E2 | So năm BASE với năm FC, khóa prefix/label, JSD trên attention flatten L1 và TVD trên dự đoán. Raw max và L1 max được giữ riêng | experiments/studies.py e2_pair, streaming.py. test_experiments.py, test_streaming.py | 9 FC full, Helpdesk AC full. Fixture AC/UNI có phạm vi riêng | IMPLEMENTED, NOT FULLY EXECUTED |
| C07 · E3 | Cùng checkpoint, lần lượt mask một occurrence ở đầu vào và zero attention hàng/cột sau softmax. So vector hai arm bằng TVD | experiments/studies.py e3_prefix, streaming.py. test_experiments.py, test_e3_attention_audit.py | 11 full, 1 partial. Audit đối chiếu ID và TVD từ vector, bảy log có đối chiếu tensor lưu trong cache BE | IMPLEMENTED, NOT FULLY EXECUTED |
| C08 · BE | Giữ hoạt động liên quan và output vượt ngưỡng, tạo cạnh local, hợp nhất rồi loại shortcut theo quy tắc đã khóa | explain/algorithms.py backward, explain/runner.py. test_explainers.py, test_explainer_runner.py | 12 đồ thị full, audit cohort và merge/pruning | VERIFIED COMPLETE |
| C09 · AE | Xét power set của các vị trí liên quan, hai chế độ mask, phiếu signed, tổng hợp và chuẩn hóa hàng, threshold và OR. Cạnh hướng từ hoạt động giải thích tới lớp dự đoán | explain/algorithms.py ae_contexts/ae_matrices và runner.py. Fixture kiểm tra vị trí lặp, resume và matrix | Ba benchmark baseline + candidate vét cạn. CP có một context primary, Sepsis/CP pilots tách riêng | IMPLEMENTED, NOT FULLY EXECUTED. Một số lịch BLOCKED bởi tài nguyên |
| C10–C11 · Đánh giá | Phân loại dự đoán trên next event. Đánh giá XAI chín trường xuất từ sáu nhóm, gồm completeness P/R/F1, correctness, consistency, continuity, contrastivity, compactness rules/RHS | evaluate/metrics.py, xai.py. test_xai.py, test_xai_audit.py, test_metrics_graphs.py | 12 predictive, 3 paired benchmark, 4 BE-only. Seed404 lấy 80% prefix, Co03 chọn từ năm candidate | VERIFIED COMPLETE predictive. IMPLEMENTED, NOT FULLY EXECUTED XAI |
| C12 · Đồ thị và tích hợp | Xuất directed JSON/GraphML/SVG, so quan hệ BPMN đã chọn. Entry point CLI và workflow nối các stage | graphs/relations.py, export.py, workflow.py, __main__.py. test_workflow.py, test_graph_export.py | Sequence nine-stage + receipt resume, ba full paired benchmarks, bốn kiểm toán BPMN chọn lọc | VERIFIED COMPLETE cho tích hợp và export đã kiểm, PARTIALLY COMPLETE cho đối chiếu mọi log |

Đường dẫn mã trong bảng bắt đầu tại `src/nhom19_process_xai/`. Receipt gần nhất ghi 93 tests và 0 lỗi tại `artifacts/s0/round4-evaluation-cache-policy-suite.xml`. Môi trường độc lập uv CPython 3.11.15 và torch 2.6.0+cpu, CPU FP32, một thread mỗi training config. Split case độc lập 70/30 seed42. XAI chọn trong seed3001–3005, cohort seed404. E2 dùng seed2001–2005 BASE, 2006–2010 cho arm thay đổi. Các trường seal của manifest gắn prefix support, source hash, dataset và checkpoint cụ thể. [Traceability](../round4/REQUIREMENTS_TRACEABILITY.md) · [Dataset provenance](../round4/DATASET_PROVENANCE.md) · [Commands](../round4/COMMANDS.md)

Quan hệ thực nghiệm có thể dùng để khôi phục:

- Event log + split → prefix và target → Transformer. Prediction JSON cho phép khôi phục metric dự báo và phân bố lỗi theo lớp. Kiểm toán trước đối chiếu tất cả prefix IDs, target và sklearn. Không suy attention từ class probabilities.
- Transformer và DFG train → E1. Chỉ prefix có đủ perturbation mới cho một tau hợp lệ. Không trộn biến thể còn thiếu vào mean. E1 trên candidate cần inference riêng. E1 baseline không tự tạo XAI correctness, vì còn cần tập cạnh do explainer sinh.
- Transformer theo seed → E2. Một arm/seed đủ prefix có thể tổng hợp độc lập từ ledger. Không thể suy mean JSD của seed chưa train từ baseline. Raw và L1 max có mẫu số khác nhau. Audit bins và TVD filter nằm trong receipt từng log.
- Transformer baseline → E3. Ba vector đã lưu cho phép tính lại cả TVD input/score, input/base và score/base. Chỉ số attention half-L1, mass bị loại, row-renormalized TVD còn nằm trong từng payload. Mean occurrence không đồng nhất mean prefix. Cache BE gắn tensor gốc qua identity, không thay thế vector E3 bị thiếu.
- BE → tập vị trí thỏa điều kiện AE → lịch 2×2ᵏ mỗi prefix. Lịch có thể tính chính xác từ BE đầy đủ. BE edge count không suy được AE edges vì thiếu signed votes và chuẩn hóa. Một phần lịch duyệt theo thứ tự số không phải mẫu ngẫu nhiên.
- Hai đồ thị baseline/candidate → XAI theo prefix và phép so AE−BE trên giao hợp lệ. Co03 cần đúng candidate và cohort. GraphML cho phép kiểm chứng cạnh và chỉ số cấu trúc, nhưng không tự tạo continuity hoặc contrastivity. BPMN đánh giá alignment, còn fidelity và khả năng hiểu của người dùng cần bằng chứng riêng.

Ảnh chụp repo độc lập trước audit là `2230195`, với các thư mục dự án untracked đã có. Repo tác giả read-only clean tại `494b315a555e713bdd61f0edd7d033c31d5850bf`. D: còn khoảng 10,92 GB và C: 37,99 GB ở lần lấy mẫu. Windows không liệt kê worker Python của project hay auditor tại thời điểm 22:23. Các progress file mang active_session cũ được xem là checkpoint chưa đóng, trạng thái thực tế lấy từ OS và ledger. Hai run BPIC12 đầy đủ trên C dùng locators `artifacts/bpic12-v1/E2-location.json` và `E3-location.json`.


## Kiểm kê toàn bộ benchmark độc lập

Mỗi hàng dưới đây lấy từ artifact đã seal của đúng log. Các cột metric dự báo và XAI là số cấp run đã ghi (A). Mean theo nhóm mô hình và median E1 là phép tổng hợp lại (B). Các định nghĩa, seed, mẫu số và receipts kiểm chứng nằm trong phần phương pháp bên trên. Dấu — là giá trị không xác định hoặc không áp dụng.

### Dự báo bước kế tiếp

Precision và F1 có trọng số theo support. Recall có trọng số bằng accuracy trên bài toán một nhãn. JSON nguồn còn có support, precision, recall, F1 và cờ mẫu số 0 theo lớp.

| Log | Test prefixes | Precision | Accuracy / recall | F1 | Epoch | Nguồn A |
|---|---|---|---|---|---|---|
| BPIC12 | 73742 | 0.83316857 | 0.82977137 | 0.80261221 | 10 | `artifacts/bpic12-v1/predictions.json` |
| BPIC12_O | 7763 | 0.82493242 | 0.81914208 | 0.79936372 | 10 | `artifacts/bpic12-o-v1/predictions.json` |
| BPIC12_W | 47280 | 0.88403514 | 0.88212775 | 0.88037399 | 10 | `artifacts/bpic12-w-v1/predictions.json` |
| BPIC12_WC | 18472 | 0.77702496 | 0.78773278 | 0.77041969 | 10 | `artifacts/bpic12-wc-v1/predictions.json` |
| BPIC13_CP | 1574 | 0.49161169 | 0.56543837 | 0.5217794 | 10 | `artifacts/bpic13-cp-v1/predictions.json` |
| BPIC13-I | 17402 | 0.70931383 | 0.69710378 | 0.66938279 | 10 | `artifacts/bpic13-i-v1/predictions.json` |
| Helpdesk | 4983 | 0.81640582 | 0.79670881 | 0.75161428 | 10 | `artifacts/helpdesk-v1/predictions.json` |
| Sepsis | 4479 | 0.64455625 | 0.60705515 | 0.57506341 | 10 | `artifacts/sepsis-v1/predictions.json` |
| Complex Model | 21555 | 0.59040409 | 0.59489678 | 0.55640397 | 10 | `artifacts/synthetic-complex-model/predictions.json` |
| LDD | 1957 | 1 | 1 | 1 | 10 | `artifacts/synthetic-long-dist-dep/predictions.json` |
| Looped And | 10873 | 0.74336829 | 0.65575278 | 0.60763834 | 10 | `artifacts/synthetic-looped-and/predictions.json` |
| Sequence | 3300 | 1 | 1 | 1 | 10 | `artifacts/synthetic-sequence/predictions.json` |



### E1 · Kendall tau-b

| Log | Prefix | Variant | Tau hợp lệ | Mean | SD | Median B | Nguồn |
|---|---|---|---|---|---|---|---|
| BPIC12_O | 7763 | 67722 | 6197 | 0.7124415 | 0.37015422 | 1 | `artifacts/bpic12-o-v1/E1-stream.json` |
| BPIC12_W | 47280 | 1334973 | 35019 | 0.10709424 | 0.80040589 | 0.33333333 | `artifacts/bpic12-w-v1/E1-stream.json` |
| BPIC12_WC | 18472 | 280907 | 13370 | 0.78029419 | 0.37793808 | 1 | `artifacts/bpic12-wc-v1/E1-stream.json` |
| BPIC13_CP | 1574 | 15569 | 856 | 0.2453271 | 0.94007118 | 1 | `artifacts/bpic13-cp-v1/E1-stream.json` |
| BPIC13-I | 17402 | 304355 | 12498 | 0.69949859 | 0.64444957 | 1 | `artifacts/bpic13-i-v1/E1-stream.json` |
| Helpdesk | 4983 | 390254 | 3497 | 0.90313602 | 0.23644075 | 1 | `artifacts/helpdesk-v1/E1-stream.json` |
| LDD | 1957 | 9356 | 1657 | 0.81477714 | 0.25030482 | 1 | `artifacts/synthetic-long-dist-dep/E1-stream.json` |
| Looped And | 10873 | 734926 | 10408 | 0.7627402 | 0.21358164 | 0.8 | `artifacts/synthetic-looped-and/E1-stream.json` |
| Sequence | 3300 | 19800 | 3000 | 0.45036268 | 0.22739876 | 0.36111111 | `artifacts/synthetic-sequence/E1-stream.json` |



### E2 · JSD attention và TVD dự đoán

| Log | Protocol | Arm | Cặp | Mean JSD B | Mean TVD B | Nguồn |
|---|---|---|---|---|---|---|
| BPIC12_O | E2-FC | BASE | 38815 | 0.0031517027 | 0.036889605 | `artifacts/bpic12-o-v1/E2-stream.json` |
| BPIC12_O | E2-FC | E2-FC | 38815 | 0.0016354234 | 0.034041227 | `artifacts/bpic12-o-v1/E2-stream.json` |
| BPIC12_WC | E2-FC | BASE | 92360 | 0.19537038 | 0.045725292 | `artifacts/bpic12-wc-v1/E2-stream.json` |
| BPIC12_WC | E2-FC | E2-FC | 92360 | 0.23471934 | 0.052314541 | `artifacts/bpic12-wc-v1/E2-stream.json` |
| BPIC13_CP | E2-FC | BASE | 7870 | 0.013598214 | 0.065364167 | `artifacts/bpic13-cp-v1/E2-stream.json` |
| BPIC13_CP | E2-FC | E2-FC | 7870 | 0.0048247172 | 0.06521573 | `artifacts/bpic13-cp-v1/E2-stream.json` |
| BPIC13-I | E2-FC | BASE | 87010 | 0.19749551 | 0.054719885 | `artifacts/bpic13-i-v1/E2-stream.json` |
| BPIC13-I | E2-FC | E2-FC | 87010 | 0.21339357 | 0.093162774 | `artifacts/bpic13-i-v1/E2-stream.json` |
| Helpdesk | E2-FC | BASE | 24915 | 0.026802626 | 0.040435163 | `artifacts/helpdesk-v1/E2-stream.json` |
| Helpdesk | E2-FC | E2-FC | 24915 | 0.078434188 | 0.0435974 | `artifacts/helpdesk-v1/E2-stream.json` |
| Helpdesk | E2-AC | BASE | 24915 | 0.026802626 | 0.040435163 | `artifacts/helpdesk-v1/E2-AC-stream.json` |
| Helpdesk | E2-AC | E2-AC | 24915 | 0.078389895 | 0.041529327 | `artifacts/helpdesk-v1/E2-AC-stream.json` |
| Sepsis | E2-FC | BASE | 22395 | 0.030866119 | 0.12735422 | `artifacts/sepsis-v1/E2-stream.json` |
| Sepsis | E2-FC | E2-FC | 22395 | 0.020680372 | 0.14864371 | `artifacts/sepsis-v1/E2-stream.json` |
| LDD | E2-FC | BASE | 9785 | 0.00029324677 | 1.5627539e-05 | `artifacts/synthetic-long-dist-dep/E2-stream.json` |
| LDD | E2-FC | E2-FC | 9785 | 0.00010381145 | 9.9726679e-05 | `artifacts/synthetic-long-dist-dep/E2-stream.json` |
| Looped And | E2-FC | BASE | 54365 | 0.0007783857 | 0.042614481 | `artifacts/synthetic-looped-and/E2-stream.json` |
| Looped And | E2-FC | E2-FC | 54365 | 0.00064218816 | 0.044711858 | `artifacts/synthetic-looped-and/E2-stream.json` |
| Sequence | E2-FC | BASE | 16500 | 0.0067964141 | 1.9513893e-05 | `artifacts/synthetic-sequence/E2-stream.json` |
| Sequence | E2-FC | E2-FC | 16500 | 0.0047403402 | 3.5815242e-05 | `artifacts/synthetic-sequence/E2-stream.json` |



<details><summary>Thông số từng seed E2, gồm mean và SD giữa các prefix</summary>


| Log | Protocol | Arm | Seed | n | JSD mean | JSD SD | TVD mean | TVD SD |
|---|---|---|---|---|---|---|---|---|
| BPIC12_O | E2-FC | BASE | 2001 | 7763 | 0.0037132892 | 0.0042616793 | 0.055303498 | 0.11213345 |
| BPIC12_O | E2-FC | BASE | 2002 | 7763 | 0.0026676048 | 0.0023446524 | 0.033383122 | 0.067259865 |
| BPIC12_O | E2-FC | BASE | 2003 | 7763 | 0.0031225693 | 0.0035685171 | 0.032906123 | 0.06571127 |
| BPIC12_O | E2-FC | BASE | 2004 | 7763 | 0.0028971184 | 0.0038220371 | 0.025135853 | 0.05450907 |
| BPIC12_O | E2-FC | BASE | 2005 | 7763 | 0.0033579316 | 0.0040883466 | 0.03771943 | 0.068550973 |
| BPIC12_O | E2-FC | E2-FC | 2006 | 7763 | 0.0016354739 | 0.0016720506 | 0.039663425 | 0.080277226 |
| BPIC12_O | E2-FC | E2-FC | 2007 | 7763 | 0.0016354706 | 0.0016720375 | 0.037470534 | 0.065740179 |
| BPIC12_O | E2-FC | E2-FC | 2008 | 7763 | 0.0016354851 | 0.0016719947 | 0.036222892 | 0.066957184 |
| BPIC12_O | E2-FC | E2-FC | 2009 | 7763 | 0.0016352086 | 0.0016712052 | 0.029980612 | 0.060483668 |
| BPIC12_O | E2-FC | E2-FC | 2010 | 7763 | 0.0016354789 | 0.0016720545 | 0.026868674 | 0.058359387 |
| BPIC12_WC | E2-FC | BASE | 2001 | 18472 | 0.20593873 | 0.12657836 | 0.045234178 | 0.056906678 |
| BPIC12_WC | E2-FC | BASE | 2002 | 18472 | 0.1957065 | 0.12353823 | 0.039666761 | 0.049940636 |
| BPIC12_WC | E2-FC | BASE | 2003 | 18472 | 0.19538969 | 0.11930507 | 0.052989368 | 0.063739083 |
| BPIC12_WC | E2-FC | BASE | 2004 | 18472 | 0.2061811 | 0.12442666 | 0.043804118 | 0.039641728 |
| BPIC12_WC | E2-FC | BASE | 2005 | 18472 | 0.17363586 | 0.13094568 | 0.046932037 | 0.048903691 |
| BPIC12_WC | E2-FC | E2-FC | 2006 | 18472 | 0.2347215 | 0.14233448 | 0.050147312 | 0.071149847 |
| BPIC12_WC | E2-FC | E2-FC | 2007 | 18472 | 0.23471884 | 0.1423334 | 0.051509142 | 0.072269867 |
| BPIC12_WC | E2-FC | E2-FC | 2008 | 18472 | 0.23471871 | 0.14233338 | 0.06662014 | 0.071482309 |
| BPIC12_WC | E2-FC | E2-FC | 2009 | 18472 | 0.23471886 | 0.1423333 | 0.045847213 | 0.083654207 |
| BPIC12_WC | E2-FC | E2-FC | 2010 | 18472 | 0.23471878 | 0.14233371 | 0.047448898 | 0.066513234 |
| BPIC13_CP | E2-FC | BASE | 2001 | 1574 | 0.024900869 | 0.017678819 | 0.082762965 | 0.050604363 |
| BPIC13_CP | E2-FC | BASE | 2002 | 1574 | 0.011635469 | 0.0092453128 | 0.058634368 | 0.048311829 |
| BPIC13_CP | E2-FC | BASE | 2003 | 1574 | 0.010244253 | 0.0081311183 | 0.048891196 | 0.039062212 |
| BPIC13_CP | E2-FC | BASE | 2004 | 1574 | 0.0074048327 | 0.0082623001 | 0.07932071 | 0.059587815 |
| BPIC13_CP | E2-FC | BASE | 2005 | 1574 | 0.013805647 | 0.010085068 | 0.057211595 | 0.043295717 |
| BPIC13_CP | E2-FC | E2-FC | 2006 | 1574 | 0.0048247969 | 0.0037733025 | 0.059280564 | 0.049264495 |
| BPIC13_CP | E2-FC | E2-FC | 2007 | 1574 | 0.0048247404 | 0.0037732741 | 0.05000148 | 0.049208209 |
| BPIC13_CP | E2-FC | E2-FC | 2008 | 1574 | 0.0048247544 | 0.0037732832 | 0.095071426 | 0.070304045 |
| BPIC13_CP | E2-FC | E2-FC | 2009 | 1574 | 0.0048246405 | 0.0037732177 | 0.051169438 | 0.042453492 |
| BPIC13_CP | E2-FC | E2-FC | 2010 | 1574 | 0.0048246541 | 0.0037732214 | 0.070555739 | 0.069369658 |
| BPIC13-I | E2-FC | BASE | 2001 | 17402 | 0.17153724 | 0.091111509 | 0.053337483 | 0.062476293 |
| BPIC13-I | E2-FC | BASE | 2002 | 17402 | 0.21532357 | 0.13235535 | 0.057158198 | 0.057902771 |
| BPIC13-I | E2-FC | BASE | 2003 | 17402 | 0.16921981 | 0.081524669 | 0.054044026 | 0.064953274 |
| BPIC13-I | E2-FC | BASE | 2004 | 17402 | 0.21563736 | 0.11088784 | 0.056680469 | 0.065079776 |
| BPIC13-I | E2-FC | BASE | 2005 | 17402 | 0.21575958 | 0.10135711 | 0.052379247 | 0.057263494 |
| BPIC13-I | E2-FC | E2-FC | 2006 | 17402 | 0.21339381 | 0.10306959 | 0.089959694 | 0.10879595 |
| BPIC13-I | E2-FC | E2-FC | 2007 | 17402 | 0.21339364 | 0.10306943 | 0.10477465 | 0.10872358 |
| BPIC13-I | E2-FC | E2-FC | 2008 | 17402 | 0.21339352 | 0.10306963 | 0.093450638 | 0.11218132 |
| BPIC13-I | E2-FC | E2-FC | 2009 | 17402 | 0.21339337 | 0.10306921 | 0.092516128 | 0.10247042 |
| BPIC13-I | E2-FC | E2-FC | 2010 | 17402 | 0.21339354 | 0.1030695 | 0.085112757 | 0.093909792 |
| Helpdesk | E2-FC | BASE | 2001 | 4983 | 0.027776197 | 0.031574859 | 0.027443691 | 0.025719824 |
| Helpdesk | E2-FC | BASE | 2002 | 4983 | 0.02580776 | 0.036184346 | 0.043890196 | 0.039040206 |
| Helpdesk | E2-FC | BASE | 2003 | 4983 | 0.0224448 | 0.018098543 | 0.026770479 | 0.031779441 |
| Helpdesk | E2-FC | BASE | 2004 | 4983 | 0.028445637 | 0.03031713 | 0.072432573 | 0.040662668 |
| Helpdesk | E2-FC | BASE | 2005 | 4983 | 0.029538734 | 0.024239727 | 0.031638877 | 0.056242718 |
| Helpdesk | E2-FC | E2-FC | 2006 | 4983 | 0.078433547 | 0.077751531 | 0.042176489 | 0.063315475 |
| Helpdesk | E2-FC | E2-FC | 2007 | 4983 | 0.078433889 | 0.077751984 | 0.027586054 | 0.055843819 |
| Helpdesk | E2-FC | E2-FC | 2008 | 4983 | 0.07843444 | 0.077752199 | 0.03999045 | 0.059278352 |
| Helpdesk | E2-FC | E2-FC | 2009 | 4983 | 0.078434581 | 0.077751647 | 0.051476443 | 0.054763061 |
| Helpdesk | E2-FC | E2-FC | 2010 | 4983 | 0.078434486 | 0.077752525 | 0.056757563 | 0.058693462 |
| Helpdesk | E2-AC | BASE | 2001 | 4983 | 0.027776197 | 0.031574859 | 0.027443691 | 0.025719824 |
| Helpdesk | E2-AC | BASE | 2002 | 4983 | 0.02580776 | 0.036184346 | 0.043890196 | 0.039040206 |
| Helpdesk | E2-AC | BASE | 2003 | 4983 | 0.0224448 | 0.018098543 | 0.026770479 | 0.031779441 |
| Helpdesk | E2-AC | BASE | 2004 | 4983 | 0.028445637 | 0.03031713 | 0.072432573 | 0.040662668 |
| Helpdesk | E2-AC | BASE | 2005 | 4983 | 0.029538734 | 0.024239727 | 0.031638877 | 0.056242718 |
| Helpdesk | E2-AC | E2-AC | 2006 | 4983 | 0.078270881 | 0.077832173 | 0.045177931 | 0.060373517 |
| Helpdesk | E2-AC | E2-AC | 2007 | 4983 | 0.078309334 | 0.077482663 | 0.022883266 | 0.053135277 |
| Helpdesk | E2-AC | E2-AC | 2008 | 4983 | 0.078388054 | 0.077663559 | 0.039078917 | 0.05083645 |
| Helpdesk | E2-AC | E2-AC | 2009 | 4983 | 0.078461788 | 0.077851894 | 0.051414849 | 0.054819521 |
| Helpdesk | E2-AC | E2-AC | 2010 | 4983 | 0.078519418 | 0.077823416 | 0.049091672 | 0.053268568 |
| Sepsis | E2-FC | BASE | 2001 | 4479 | 0.026493667 | 0.016580723 | 0.13348177 | 0.10241532 |
| Sepsis | E2-FC | BASE | 2002 | 4479 | 0.03746656 | 0.021824041 | 0.1329095 | 0.099917757 |
| Sepsis | E2-FC | BASE | 2003 | 4479 | 0.03309661 | 0.027460568 | 0.14104695 | 0.10249668 |
| Sepsis | E2-FC | BASE | 2004 | 4479 | 0.030476159 | 0.023413258 | 0.11998867 | 0.094424004 |
| Sepsis | E2-FC | BASE | 2005 | 4479 | 0.026797599 | 0.020184479 | 0.10934421 | 0.079747013 |
| Sepsis | E2-FC | E2-FC | 2006 | 4479 | 0.020680122 | 0.01080117 | 0.15800221 | 0.11791346 |
| Sepsis | E2-FC | E2-FC | 2007 | 4479 | 0.020680377 | 0.010801448 | 0.13150364 | 0.11086673 |
| Sepsis | E2-FC | E2-FC | 2008 | 4479 | 0.020680344 | 0.010801614 | 0.11972052 | 0.11019235 |
| Sepsis | E2-FC | E2-FC | 2009 | 4479 | 0.020680367 | 0.010801501 | 0.16454164 | 0.11173148 |
| Sepsis | E2-FC | E2-FC | 2010 | 4479 | 0.02068065 | 0.010801679 | 0.16945052 | 0.13262333 |
| LDD | E2-FC | BASE | 2001 | 1957 | 0.00013761685 | 0.00012921992 | 1.2655633e-05 | 5.3832048e-05 |
| LDD | E2-FC | BASE | 2002 | 1957 | 0.0003532727 | 0.00034762869 | 2.6389517e-05 | 9.1465512e-05 |
| LDD | E2-FC | BASE | 2003 | 1957 | 0.00037796333 | 0.00030998112 | 1.4003065e-05 | 4.7377749e-05 |
| LDD | E2-FC | BASE | 2004 | 1957 | 0.00024953754 | 0.00017427559 | 1.2606864e-05 | 5.3966948e-05 |
| LDD | E2-FC | BASE | 2005 | 1957 | 0.00034784345 | 0.00027418415 | 1.2482616e-05 | 5.1147623e-05 |
| LDD | E2-FC | E2-FC | 2006 | 1957 | 0.00010379293 | 0.00011920758 | 6.8488724e-05 | 0.00019967122 |
| LDD | E2-FC | E2-FC | 2007 | 1957 | 0.00010382218 | 0.00011925269 | 5.313712e-05 | 0.00015297987 |
| LDD | E2-FC | E2-FC | 2008 | 1957 | 0.00010380962 | 0.00011922163 | 9.5244844e-05 | 0.00027838579 |
| LDD | E2-FC | E2-FC | 2009 | 1957 | 0.00010381529 | 0.00011920437 | 0.00017462272 | 0.00056731803 |
| LDD | E2-FC | E2-FC | 2010 | 1957 | 0.00010381722 | 0.00011921838 | 0.00010713999 | 0.00043688139 |
| Looped And | E2-FC | BASE | 2001 | 10873 | 0.00065409515 | 0.00021688785 | 0.03645462 | 0.042924475 |
| Looped And | E2-FC | BASE | 2002 | 10873 | 0.00068796659 | 0.00022133714 | 0.050431241 | 0.081945519 |
| Looped And | E2-FC | BASE | 2003 | 10873 | 0.00068531227 | 0.0002143365 | 0.042926638 | 0.065582635 |
| Looped And | E2-FC | BASE | 2004 | 10873 | 0.0011573865 | 0.0003641934 | 0.049643353 | 0.089819795 |
| Looped And | E2-FC | BASE | 2005 | 10873 | 0.00070716795 | 0.00023161341 | 0.033616551 | 0.0520065 |
| Looped And | E2-FC | E2-FC | 2006 | 10873 | 0.00064216477 | 0.00021531259 | 0.036643511 | 0.050624105 |
| Looped And | E2-FC | E2-FC | 2007 | 10873 | 0.00064211729 | 0.00021531597 | 0.045123863 | 0.059423866 |
| Looped And | E2-FC | E2-FC | 2008 | 10873 | 0.0006420879 | 0.00021529812 | 0.051596477 | 0.061275323 |
| Looped And | E2-FC | E2-FC | 2009 | 10873 | 0.0006424041 | 0.00021545373 | 0.06221644 | 0.074968367 |
| Looped And | E2-FC | E2-FC | 2010 | 10873 | 0.00064216672 | 0.00021529524 | 0.027978999 | 0.056555298 |
| Sequence | E2-FC | BASE | 2001 | 3300 | 0.0082695244 | 0.014052424 | 5.1496957e-07 | 5.1477596e-07 |
| Sequence | E2-FC | BASE | 2002 | 3300 | 0.0041782407 | 0.0064879363 | 1.6987183e-07 | 7.0925038e-08 |
| Sequence | E2-FC | BASE | 2003 | 3300 | 0.0054424226 | 0.0068293109 | 1.1902038e-06 | 8.3451394e-07 |
| Sequence | E2-FC | BASE | 2004 | 3300 | 0.0080402379 | 0.010055858 | 9.5104066e-05 | 0.00010703531 |
| Sequence | E2-FC | BASE | 2005 | 3300 | 0.0080516451 | 0.010018949 | 5.9035377e-07 | 3.9661883e-07 |
| Sequence | E2-FC | E2-FC | 2006 | 3300 | 0.0047403269 | 0.0085189216 | 4.518695e-05 | 5.4929958e-05 |
| Sequence | E2-FC | E2-FC | 2007 | 3300 | 0.004740375 | 0.0085189322 | 3.793685e-05 | 4.905459e-05 |
| Sequence | E2-FC | E2-FC | 2008 | 3300 | 0.0047403312 | 0.008518853 | 2.3822435e-05 | 2.8570248e-05 |
| Sequence | E2-FC | E2-FC | 2009 | 3300 | 0.0047403667 | 0.0085189315 | 5.4875487e-05 | 6.9399487e-05 |
| Sequence | E2-FC | E2-FC | 2010 | 3300 | 0.0047403011 | 0.0085188653 | 1.7254488e-05 | 1.7968051e-05 |



</details>


### E3 · TVD giữa input masking và score masking

Mean và SD prefix tính mỗi prefix một trọng số. Thống kê occurrence tính mỗi vị trí một trọng số. Các giá trị occurrence tái tổng hợp từ ledger là B.

| Log | Prefix | Mean prefix | SD prefix | Occurrence | Mean occurrence | Median occurrence | Nguồn |
|---|---|---|---|---|---|---|---|
| BPIC12_O | 7763 | 0.38432882 | 0.30903885 | 31039 | 0.23081322 | 0.071676653 | `artifacts/bpic12-o-v1/E3-stream.json` + `artifacts/bpic12-o-v1/e3-occurrence-audit.json` |
| BPIC12_W | 47280 | 0.087629418 | 0.1833537 | 774557 | 0.02246507 | 0.0035837554 | `artifacts/bpic12-w-v1/E3-stream.json` + `artifacts/bpic12-w-v1/e3-record-audit.json` |
| BPIC12_WC | 18472 | 0.11146411 | 0.17974848 | 143848 | 0.037742898 | 0.011057654 | `artifacts/bpic12-wc-v1/E3-stream.json` + `artifacts/bpic12-wc-v1/e3-occurrence-audit.json` |
| BPIC13_CP | 1574 | 0.22218988 | 0.17823399 | 6243 | 0.11203369 | 0.055524649 | `artifacts/bpic13-cp-v1/E3-stream.json` + `artifacts/bpic13-cp-v1/e3-occurrence-audit.json` |
| BPIC13-I | 17402 | 0.15261745 | 0.15870137 | 146211 | 0.053956432 | 0.017057467 | `artifacts/bpic13-i-v1/E3-stream.json` + `artifacts/bpic13-i-v1/e3-occurrence-audit.json` |
| Helpdesk | 4983 | 0.3106061 | 0.22700232 | 12547 | 0.20558711 | 0.12961973 | `artifacts/helpdesk-v1/E3-stream.json` + `artifacts/helpdesk-v1/e3-occurrence-audit.json` |
| Sepsis | 4479 | 0.15701017 | 0.17439002 | 60338 | 0.053076127 | 0.022247419 | `artifacts/sepsis-v1/E3-stream.json` + `artifacts/sepsis-v1/e3-occurrence-audit.json` |
| Complex Model | 21555 | 0.13595861 | 0.24071134 | 196047 | 0.052625321 | 0.016653824 | `artifacts/synthetic-complex-model/E3-stream.json` + `artifacts/synthetic-complex-model/e3-occurrence-audit.json` |
| LDD | 1957 | 0.14128428 | 0.27150689 | 7399 | 0.063359049 | 0.00023773192 | `artifacts/synthetic-long-dist-dep/E3-stream.json` + `artifacts/synthetic-long-dist-dep/e3-occurrence-audit.json` |
| Looped And | 10873 | 0.078024647 | 0.11534041 | 164829 | 0.035457544 | 0.0095204439 | `artifacts/synthetic-looped-and/E3-stream.json` + `artifacts/synthetic-looped-and/e3-occurrence-audit.json` |
| Sequence | 3300 | 0.086949521 | 0.25969971 | 19800 | 0.016089232 | 6.4517623e-06 | `artifacts/synthetic-sequence/E3-stream.json` + `artifacts/synthetic-sequence/e3-occurrence-audit.json` |



### BE và AE · Đồ thị baseline

| Log | BE prefix | BE cạnh | AE đã ghi | AE lịch đầy đủ | Coverage receipt |
|---|---|---|---|---|---|
| BPIC12 | 73742 | 53 | 0 | 10702726289412151069607326686972248928176 | `artifacts/bpic12-v1/be-only-v1/coverage.json` |
| BPIC12_O | 7763 | 12 | 0 | 113657644 | `artifacts/bpic12-o-v1/be-only-v1/coverage.json` |
| BPIC12_W | 47280 | 15 | 0 | 21778466076276744583975495191531994354998 | `artifacts/bpic12-w-v1/be-only-v1/coverage.json` |
| BPIC12_WC | 18472 | 13 | 0 | 56330420007228581540 | `artifacts/bpic12-wc-v1/be-only-v1/coverage.json` |
| BPIC13_CP | 1574 | 5 | 1 | 809189178 | `artifacts/bpic13-cp-v1/explain-v1/coverage.json` |
| BPIC13-I | 17402 | 6 | 0 | 15950735951275900776544602750118088858 | `artifacts/bpic13-i-v1/be-only-v1/coverage.json` |
| Helpdesk | 4983 | 19 | 107602 | 107602 | `artifacts/helpdesk-v1/evaluation-paired/baseline-graphs/coverage.json` |
| Sepsis | 4479 | 16 | 0 | 95780971304118054312010688327443415449914092552292282 | `artifacts/sepsis-v1/be-only-v1/coverage.json` |
| Complex Model | 21555 | 26 | 0 | 405840441072787719568 | `artifacts/synthetic-complex-model/explain/coverage.json` |
| LDD | 1957 | 11 | 67290 | 67290 | `artifacts/synthetic-long-dist-dep/explain/coverage.json` |
| Looped And | 10873 | 10 | 0 | 1219192350409752944173595276 | `artifacts/synthetic-looped-and/explain/coverage.json` |
| Sequence | 3300 | 13 | 137344 | 137344 | `artifacts/synthetic-sequence/explain/coverage.json` |



### Đánh giá XAI · Chín đầu ra, có mẫu số và paired delta

Delta AE − BE dùng giao các prefix hợp lệ cho từng metric. Dòng BE-only chỉ có thống kê BE.

| Log | Method | Metric | Mean | SD | Valid/scheduled | Delta | Paired n | Nguồn A |
|---|---|---|---|---|---|---|---|---|
| BPIC12_O | BE | correctness | 0.30037944 | 0.53733362 | 4989/6210 | — | — | `artifacts/bpic12-o-v1/evaluation-be/evaluation.json` |
| BPIC12_O | BE | completeness_precision | 0.25824822 | 0.18343812 | 6210/6210 | — | — | `artifacts/bpic12-o-v1/evaluation-be/evaluation.json` |
| BPIC12_O | BE | completeness_recall | 0.72431562 | 0.3967499 | 6210/6210 | — | — | `artifacts/bpic12-o-v1/evaluation-be/evaluation.json` |
| BPIC12_O | BE | completeness_f1 | 0.35801073 | 0.21830845 | 6210/6210 | — | — | `artifacts/bpic12-o-v1/evaluation-be/evaluation.json` |
| BPIC12_O | BE | consistency | 0.35259601 | 0.079037185 | 4073/6210 | — | — | `artifacts/bpic12-o-v1/evaluation-be/evaluation.json` |
| BPIC12_O | BE | continuity | 0.71899817 | 0.14767094 | 4988/6210 | — | — | `artifacts/bpic12-o-v1/evaluation-be/evaluation.json` |
| BPIC12_O | BE | contrastivity | 0.50375204 | 0.19650522 | 6210/6210 | — | — | `artifacts/bpic12-o-v1/evaluation-be/evaluation.json` |
| BPIC12_O | BE | compactness_rules | 2.9304348 | 1.2890977 | 6210/6210 | — | — | `artifacts/bpic12-o-v1/evaluation-be/evaluation.json` |
| BPIC12_O | BE | compactness_rhs | 2.0895813 | 0.18056474 | 6210/6210 | — | — | `artifacts/bpic12-o-v1/evaluation-be/evaluation.json` |
| BPIC13_CP | BE | correctness | -0.09382571 | 0.97998802 | 643/1259 | — | — | `artifacts/bpic13-cp-v1/evaluation-be/evaluation.json` |
| BPIC13_CP | BE | completeness_precision | 0.86338364 | 0.23589289 | 1259/1259 | — | — | `artifacts/bpic13-cp-v1/evaluation-be/evaluation.json` |
| BPIC13_CP | BE | completeness_recall | 0.74212338 | 0.19869396 | 1259/1259 | — | — | `artifacts/bpic13-cp-v1/evaluation-be/evaluation.json` |
| BPIC13_CP | BE | completeness_f1 | 0.7770188 | 0.17718173 | 1259/1259 | — | — | `artifacts/bpic13-cp-v1/evaluation-be/evaluation.json` |
| BPIC13_CP | BE | consistency | 0.98843733 | 0.022997988 | 1207/1259 | — | — | `artifacts/bpic13-cp-v1/evaluation-be/evaluation.json` |
| BPIC13_CP | BE | continuity | 0.60851441 | 0.40409629 | 1259/1259 | — | — | `artifacts/bpic13-cp-v1/evaluation-be/evaluation.json` |
| BPIC13_CP | BE | contrastivity | 0.61495869 | 0.26310236 | 779/1259 | — | — | `artifacts/bpic13-cp-v1/evaluation-be/evaluation.json` |
| BPIC13_CP | BE | compactness_rules | 1.5853852 | 0.57336973 | 1259/1259 | — | — | `artifacts/bpic13-cp-v1/evaluation-be/evaluation.json` |
| BPIC13_CP | BE | compactness_rhs | 1.7374901 | 0.25607169 | 1259/1259 | — | — | `artifacts/bpic13-cp-v1/evaluation-be/evaluation.json` |
| BPIC13-I | BE | correctness | 0.24724226 | 0.93149826 | 9387/13921 | — | — | `artifacts/bpic13-i-v1/evaluation-be/evaluation.json` |
| BPIC13-I | BE | completeness_precision | 0.73399899 | 0.30368617 | 13921/13921 | — | — | `artifacts/bpic13-i-v1/evaluation-be/evaluation.json` |
| BPIC13-I | BE | completeness_recall | 0.98768048 | 0.080022089 | 13921/13921 | — | — | `artifacts/bpic13-i-v1/evaluation-be/evaluation.json` |
| BPIC13-I | BE | completeness_f1 | 0.79919546 | 0.22649847 | 13921/13921 | — | — | `artifacts/bpic13-i-v1/evaluation-be/evaluation.json` |
| BPIC13-I | BE | consistency | 0.83763792 | 0.10841022 | 13551/13921 | — | — | `artifacts/bpic13-i-v1/evaluation-be/evaluation.json` |
| BPIC13-I | BE | continuity | 0.78636011 | 0.29581204 | 13921/13921 | — | — | `artifacts/bpic13-i-v1/evaluation-be/evaluation.json` |
| BPIC13-I | BE | contrastivity | 0.58904617 | 0.19865483 | 13049/13921 | — | — | `artifacts/bpic13-i-v1/evaluation-be/evaluation.json` |
| BPIC13-I | BE | compactness_rules | 1.8692623 | 0.64148139 | 13921/13921 | — | — | `artifacts/bpic13-i-v1/evaluation-be/evaluation.json` |
| BPIC13-I | BE | compactness_rhs | 2.2467854 | 0.47558333 | 13921/13921 | — | — | `artifacts/bpic13-i-v1/evaluation-be/evaluation.json` |
| Helpdesk | BE | correctness | 0.84007998 | 0.34678981 | 2784/3986 | — | — | `artifacts/helpdesk-v1/evaluation-paired/evaluation.json` |
| Helpdesk | BE | completeness_precision | 0.48127613 | 0.35355667 | 3986/3986 | — | — | `artifacts/helpdesk-v1/evaluation-paired/evaluation.json` |
| Helpdesk | BE | completeness_recall | 0.86803813 | 0.21974172 | 3986/3986 | — | — | `artifacts/helpdesk-v1/evaluation-paired/evaluation.json` |
| Helpdesk | BE | completeness_f1 | 0.56146752 | 0.30628319 | 3986/3986 | — | — | `artifacts/helpdesk-v1/evaluation-paired/evaluation.json` |
| Helpdesk | BE | consistency | 0.64012076 | 0.26028402 | 3958/3986 | — | — | `artifacts/helpdesk-v1/evaluation-paired/evaluation.json` |
| Helpdesk | BE | continuity | 0.59493209 | 0.088938014 | 2874/3986 | — | — | `artifacts/helpdesk-v1/evaluation-paired/evaluation.json` |
| Helpdesk | BE | contrastivity | 0.66875181 | 0.18059135 | 3981/3986 | — | — | `artifacts/helpdesk-v1/evaluation-paired/evaluation.json` |
| Helpdesk | BE | compactness_rules | 2.2172604 | 1.0051127 | 3986/3986 | — | — | `artifacts/helpdesk-v1/evaluation-paired/evaluation.json` |
| Helpdesk | BE | compactness_rhs | 2.3396411 | 0.29551549 | 3986/3986 | — | — | `artifacts/helpdesk-v1/evaluation-paired/evaluation.json` |
| Helpdesk | AE | correctness | -0.13745811 | 0.93129581 | 2784/3986 | -0.97753809 | 2784 | `artifacts/helpdesk-v1/evaluation-paired/evaluation.json` |
| Helpdesk | AE | completeness_precision | 0.31342078 | 0.11116614 | 3986/3986 | -0.16785535 | 3986 | `artifacts/helpdesk-v1/evaluation-paired/evaluation.json` |
| Helpdesk | AE | completeness_recall | 0.99987456 | 0.0079195655 | 3986/3986 | 0.13183643 | 3986 | `artifacts/helpdesk-v1/evaluation-paired/evaluation.json` |
| Helpdesk | AE | completeness_f1 | 0.46678155 | 0.12533593 | 3986/3986 | -0.094685964 | 3986 | `artifacts/helpdesk-v1/evaluation-paired/evaluation.json` |
| Helpdesk | AE | consistency | 0.61190217 | 0.088499816 | 3958/3986 | -0.028218589 | 3958 | `artifacts/helpdesk-v1/evaluation-paired/evaluation.json` |
| Helpdesk | AE | continuity | 0.64518768 | 0.16360177 | 2874/3986 | 0.050255592 | 2874 | `artifacts/helpdesk-v1/evaluation-paired/evaluation.json` |
| Helpdesk | AE | contrastivity | 0.53897763 | 0.2649537 | 3981/3986 | -0.12977418 | 3981 | `artifacts/helpdesk-v1/evaluation-paired/evaluation.json` |
| Helpdesk | AE | compactness_rules | 2.2137481 | 0.99935821 | 3986/3986 | -0.003512293 | 3986 | `artifacts/helpdesk-v1/evaluation-paired/evaluation.json` |
| Helpdesk | AE | compactness_rhs | 4.3864359 | 0.75491123 | 3986/3986 | 2.0467947 | 3986 | `artifacts/helpdesk-v1/evaluation-paired/evaluation.json` |
| LDD | BE | correctness | -0.40963796 | 0.46457457 | 1322/1565 | — | — | `artifacts/synthetic-long-dist-dep/evaluation-paired/evaluation.json` |
| LDD | BE | completeness_precision | 0.22511943 | 0.1487791 | 1565/1565 | — | — | `artifacts/synthetic-long-dist-dep/evaluation-paired/evaluation.json` |
| LDD | BE | completeness_recall | 0.84472843 | 0.36227913 | 1565/1565 | — | — | `artifacts/synthetic-long-dist-dep/evaluation-paired/evaluation.json` |
| LDD | BE | completeness_f1 | 0.34377301 | 0.19763796 | 1565/1565 | — | — | `artifacts/synthetic-long-dist-dep/evaluation-paired/evaluation.json` |
| LDD | BE | consistency | 0.29010891 | 0.17719956 | 1209/1565 | — | — | `artifacts/synthetic-long-dist-dep/evaluation-paired/evaluation.json` |
| LDD | BE | continuity | 0.55868482 | 0.2948911 | 1565/1565 | — | — | `artifacts/synthetic-long-dist-dep/evaluation-paired/evaluation.json` |
| LDD | BE | contrastivity | 0.34428419 | 0.14882346 | 1565/1565 | — | — | `artifacts/synthetic-long-dist-dep/evaluation-paired/evaluation.json` |
| LDD | BE | compactness_rules | 3.7654952 | 1.9011601 | 1565/1565 | — | — | `artifacts/synthetic-long-dist-dep/evaluation-paired/evaluation.json` |
| LDD | BE | compactness_rhs | 1.3190126 | 0.26361659 | 1565/1565 | — | — | `artifacts/synthetic-long-dist-dep/evaluation-paired/evaluation.json` |
| LDD | AE | correctness | -0.067322239 | 0.61718763 | 1322/1565 | 0.34231572 | 1322 | `artifacts/synthetic-long-dist-dep/evaluation-paired/evaluation.json` |
| LDD | AE | completeness_precision | 0.14440895 | 0.045284892 | 1565/1565 | -0.080710482 | 1565 | `artifacts/synthetic-long-dist-dep/evaluation-paired/evaluation.json` |
| LDD | AE | completeness_recall | 1 | 0 | 1565/1565 | 0.15527157 | 1565 | `artifacts/synthetic-long-dist-dep/evaluation-paired/evaluation.json` |
| LDD | AE | completeness_f1 | 0.24982606 | 0.064405179 | 1565/1565 | -0.093946955 | 1565 | `artifacts/synthetic-long-dist-dep/evaluation-paired/evaluation.json` |
| LDD | AE | consistency | 0.92036505 | 0.1015126 | 1209/1565 | 0.63025615 | 1209 | `artifacts/synthetic-long-dist-dep/evaluation-paired/evaluation.json` |
| LDD | AE | continuity | 0.60451275 | 0.27428139 | 1565/1565 | 0.04582793 | 1565 | `artifacts/synthetic-long-dist-dep/evaluation-paired/evaluation.json` |
| LDD | AE | contrastivity | 0.35152645 | 0.19994389 | 1565/1565 | 0.0072422522 | 1565 | `artifacts/synthetic-long-dist-dep/evaluation-paired/evaluation.json` |
| LDD | AE | compactness_rules | 3.7654952 | 1.9011601 | 1565/1565 | 0 | 1565 | `artifacts/synthetic-long-dist-dep/evaluation-paired/evaluation.json` |
| LDD | AE | compactness_rhs | 5.0569664 | 0.5735653 | 1565/1565 | 3.7379538 | 1565 | `artifacts/synthetic-long-dist-dep/evaluation-paired/evaluation.json` |
| Looped And | BE | correctness | -0.49068067 | 0.43214584 | 8330/8698 | — | — | `artifacts/synthetic-looped-and/evaluation-be/evaluation.json` |
| Looped And | BE | completeness_precision | 0.41666667 | 0.12463456 | 8698/8698 | — | — | `artifacts/synthetic-looped-and/evaluation-be/evaluation.json` |
| Looped And | BE | completeness_recall | 0.91649613 | 0.16164902 | 8698/8698 | — | — | `artifacts/synthetic-looped-and/evaluation-be/evaluation.json` |
| Looped And | BE | completeness_f1 | 0.55284293 | 0.12443272 | 8698/8698 | — | — | `artifacts/synthetic-looped-and/evaluation-be/evaluation.json` |
| Looped And | BE | consistency | 0.68069361 | 0.15652292 | 8646/8698 | — | — | `artifacts/synthetic-looped-and/evaluation-be/evaluation.json` |
| Looped And | BE | continuity | 0.91223375 | 0.09997505 | 8330/8698 | — | — | `artifacts/synthetic-looped-and/evaluation-be/evaluation.json` |
| Looped And | BE | contrastivity | 0.41685782 | 0.16944026 | 8698/8698 | — | — | `artifacts/synthetic-looped-and/evaluation-be/evaluation.json` |
| Looped And | BE | compactness_rules | 4.5709358 | 1.0485913 | 8698/8698 | — | — | `artifacts/synthetic-looped-and/evaluation-be/evaluation.json` |
| Looped And | BE | compactness_rhs | 2.0244309 | 0.094839297 | 8698/8698 | — | — | `artifacts/synthetic-looped-and/evaluation-be/evaluation.json` |
| Sequence | BE | correctness | 0.049301448 | 0.36946934 | 2158/2640 | — | — | `artifacts/synthetic-sequence/evaluation-paired/evaluation.json` |
| Sequence | BE | completeness_precision | 0.18581845 | 0.12866071 | 2640/2640 | — | — | `artifacts/synthetic-sequence/evaluation-paired/evaluation.json` |
| Sequence | BE | completeness_recall | 0.90606061 | 0.29179965 | 2640/2640 | — | — | `artifacts/synthetic-sequence/evaluation-paired/evaluation.json` |
| Sequence | BE | completeness_f1 | 0.29517291 | 0.16960633 | 2640/2640 | — | — | `artifacts/synthetic-sequence/evaluation-paired/evaluation.json` |
| Sequence | BE | consistency | 0.56062646 | 0.26347513 | 1944/2640 | — | — | `artifacts/synthetic-sequence/evaluation-paired/evaluation.json` |
| Sequence | BE | continuity | 0.80511106 | 0.11597855 | 2392/2640 | — | — | `artifacts/synthetic-sequence/evaluation-paired/evaluation.json` |
| Sequence | BE | contrastivity | 0.25498877 | 0.20737159 | 2640/2640 | — | — | `artifacts/synthetic-sequence/evaluation-paired/evaluation.json` |
| Sequence | BE | compactness_rules | 6.0075758 | 3.1901853 | 2640/2640 | — | — | `artifacts/synthetic-sequence/evaluation-paired/evaluation.json` |
| Sequence | BE | compactness_rhs | 1.205007 | 0.10838189 | 2640/2640 | — | — | `artifacts/synthetic-sequence/evaluation-paired/evaluation.json` |
| Sequence | AE | correctness | -0.77422683 | 0.13463065 | 2392/2640 | -0.79904685 | 2158 | `artifacts/synthetic-sequence/evaluation-paired/evaluation.json` |
| Sequence | AE | completeness_precision | 0.11163654 | 0.013628662 | 2640/2640 | -0.074181917 | 2640 | `artifacts/synthetic-sequence/evaluation-paired/evaluation.json` |
| Sequence | AE | completeness_recall | 1 | 0 | 2640/2640 | 0.093939394 | 2640 | `artifacts/synthetic-sequence/evaluation-paired/evaluation.json` |
| Sequence | AE | completeness_f1 | 0.20057928 | 0.022154909 | 2640/2640 | -0.094593637 | 2640 | `artifacts/synthetic-sequence/evaluation-paired/evaluation.json` |
| Sequence | AE | consistency | 0.96619876 | 0.019800852 | 1944/2640 | 0.40557229 | 1944 | `artifacts/synthetic-sequence/evaluation-paired/evaluation.json` |
| Sequence | AE | continuity | 0.7843843 | 0.13090678 | 2392/2640 | -0.020726761 | 2392 | `artifacts/synthetic-sequence/evaluation-paired/evaluation.json` |
| Sequence | AE | contrastivity | 0.19841931 | 0.20406966 | 2640/2640 | -0.056569454 | 2640 | `artifacts/synthetic-sequence/evaluation-paired/evaluation.json` |
| Sequence | AE | compactness_rules | 6.0075758 | 3.1901853 | 2640/2640 | 0 | 2640 | `artifacts/synthetic-sequence/evaluation-paired/evaluation.json` |
| Sequence | AE | compactness_rhs | 5.8283409 | 1.2459476 | 2640/2640 | 4.6233339 | 2640 | `artifacts/synthetic-sequence/evaluation-paired/evaluation.json` |



## Kết quả khôi phục từ các lượt dở dang

Tất cả đọc từ SQLite mở chỉ đọc. Các worker nêu trong cập nhật trước không xuất hiện ở thời điểm chụp, nên các lượt này là PARTIALLY COMPLETE. Không coi active session trong JSON là bằng chứng đang chạy.

| Log | Study | Đã ghi | Lịch đầy đủ | % đơn vị | Ledger |
|---|---|---|---|---|---|
| BPIC12_W | E2 | 5300 | 472800 | 1.1209814 | `artifacts/bpic12-w-v1/E2-stream-run/records.sqlite` |
| Complex Model | E2 | 170974 | 215550 | 79.319879 | `artifacts/synthetic-complex-model/E2-stream-run/records.sqlite` |
| BPIC12 | E2 | 54952 | 737420 | 7.451927 | `C:/Users/Ngoc Duy/AppData/Local/nhom19_cschttt/round4/bpic12-v1/E2-stream-run/records.sqlite` |
| BPIC12 | E3 | 10690 | 73742 | 14.496488 | `C:/Users/Ngoc Duy/AppData/Local/nhom19_cschttt/round4/bpic12-v1/E3-stream-run/records.sqlite` |
| Sepsis | E1 | 15000 | 2425371457 | 0.00061846197 | `artifacts/sepsis-v1/E1-stream-e1-run/records.sqlite` |



### E2 · Mean quan sát và khoảng mean toàn cohort

B với độ tin cậy HIGH cho phép tính trên hàng lưu. Khoảng là giới hạn tất định từ tổng quan sát S, N đơn vị dự kiến, K thiếu, và metric thuộc [0,M]. Khoảng [S/N,(S+KM)/N] với M=ln(2) cho JSD, M=1 cho TVD. Các khoảng giả định hàng đã ghi thuộc đúng lịch của arm/seed, không phải khoảng tin cậy lấy mẫu. Khi n=N, mean seed khôi phục chính xác theo ledger và vẫn cần audit nhận diện toàn cohort trước khi công bố cấp study. Những seed chưa có hàng giữ F, giới hạn lý thuyết là toàn miền. Thứ tự hash prefix và dừng giữa arm không bảo đảm đại diện theo case, chiều dài hoặc lớp.

| Log | Arm | Seed | n | N | Mean JSD phần lưu | Mean TVD phần lưu | JSD toàn seed | TVD toàn seed | Nguồn |
|---|---|---|---|---|---|---|---|---|---|
| BPIC12_W | BASE | 2001 | 5300 | 47280 | 0.1328971 | 0.050820539 | [0.014898, 0.630344] | [0.005697, 0.893599] | `artifacts/bpic12-w-v1/E2-stream-run/records.sqlite` |
| Complex Model | BASE | 2001 | 21555 | 21555 | 0.043021197 | 0.07284448 | [0.043021, 0.043021] | [0.072844, 0.072844] | `artifacts/synthetic-complex-model/E2-stream-run/records.sqlite` |
| Complex Model | BASE | 2002 | 21555 | 21555 | 0.048494871 | 0.068937286 | [0.048495, 0.048495] | [0.068937, 0.068937] | `artifacts/synthetic-complex-model/E2-stream-run/records.sqlite` |
| Complex Model | BASE | 2003 | 21555 | 21555 | 0.046003295 | 0.092689514 | [0.046003, 0.046003] | [0.092690, 0.092690] | `artifacts/synthetic-complex-model/E2-stream-run/records.sqlite` |
| Complex Model | BASE | 2004 | 21555 | 21555 | 0.049362729 | 0.092605583 | [0.049363, 0.049363] | [0.092606, 0.092606] | `artifacts/synthetic-complex-model/E2-stream-run/records.sqlite` |
| Complex Model | BASE | 2005 | 21555 | 21555 | 0.041573438 | 0.084182609 | [0.041573, 0.041573] | [0.084183, 0.084183] | `artifacts/synthetic-complex-model/E2-stream-run/records.sqlite` |
| Complex Model | E2-FC | 2006 | 21555 | 21555 | 0.031773197 | 0.084884297 | [0.031773, 0.031773] | [0.084884, 0.084884] | `artifacts/synthetic-complex-model/E2-stream-run/records.sqlite` |
| Complex Model | E2-FC | 2007 | 21555 | 21555 | 0.031773062 | 0.072674319 | [0.031773, 0.031773] | [0.072674, 0.072674] | `artifacts/synthetic-complex-model/E2-stream-run/records.sqlite` |
| Complex Model | E2-FC | 2008 | 20089 | 21555 | 0.031791232 | 0.069878277 | [0.029629, 0.076771] | [0.065126, 0.133138] | `artifacts/synthetic-complex-model/E2-stream-run/records.sqlite` |
| BPIC12 | BASE | 2001 | 54952 | 73742 | 0.18705349 | 0.047082128 | [0.139391, 0.316010] | [0.035085, 0.289893] | `C:/Users/Ngoc Duy/AppData/Local/nhom19_cschttt/round4/bpic12-v1/E2-stream-run/records.sqlite` |



BPIC12 E3 (B, HIGH cho tập đã lưu) có **10,690 prefix** và **212,879 occurrence**. Mean cùng trọng số prefix **0.10120052**, median occurrence **0.00391139**, mean occurrence **0.02030644**. Đã đối chiếu seal từng hàng và mean từng prefix. Mean toàn bộ 73.742 prefix thuộc **[0.014671, 0.869706]**, với giả định duy nhất TVD trong [0,1]. Nguồn `C:/Users/Ngoc Duy/AppData/Local/nhom19_cschttt/round4/bpic12-v1/E3-stream-run/records.sqlite`.


Sepsis E1 (B, HIGH cho ledger) có 15,000 variant, 2 prefix hoàn tất, 1 tau-b hữu hạn. Mean tau-b của phần hữu hạn là 1. Denominator toàn log là 2.425.371.457 variant. Một vài prefix đầu không tạo mẫu đại diện, mean toàn log giữ F. Nguồn `artifacts/sepsis-v1/E1-stream-e1-run/records.sqlite`.


## Đối chiếu Table 2 và Table 3

Table 2 dùng ba số in trong bài (D), delta là kết quả độc lập trừ số in. Thành phần tương đối dùng F1 in làm mẫu số. Member ghi nơi kiểm tra chéo trong archive (E).

| Log | D Precision | D Accuracy | D F1 | Δ Precision | Δ Accuracy | Δ F1 | Δ F1 % | Member archive E |
|---|---|---|---|---|---|---|---|---|
| BPIC12 | 0.8 | 0.83 | 0.8 | 0.033168571 | -0.00022863497 | 0.0026122138 | +0.33% | `Supplementary_Material/Trained_Models/training_bpic12_GPU/metrics.json` |
| BPIC12_O | 0.96 | 0.93 | 0.93 | -0.13506758 | -0.11085792 | -0.13063628 | -14.05% | `Supplementary_Material/Trained_Models/training_bpic12_o_GPU/metrics.json` |
| BPIC12_W | 0.88 | 0.87 | 0.87 | 0.0040351369 | 0.01212775 | 0.010373987 | +1.19% | `Supplementary_Material/Trained_Models/training_bpic12_w_GPU/metrics.json` |
| BPIC12_WC | 0.75 | 0.78 | 0.75 | 0.027024962 | 0.0077327848 | 0.020419695 | +2.72% | `Supplementary_Material/Trained_Models/training_bpic12_wc_GPU/metrics.json` |
| BPIC13_CP | 0.69 | 0.83 | 0.76 | -0.19838831 | -0.26456163 | -0.2382206 | -31.34% | `Supplementary_Material/Trained_Models/training_bpic13_closed_problems_GPU/metrics.json` |
| BPIC13-I | 0.5 | 0.69 | 0.57 | 0.20931383 | 0.0071037812 | 0.099382792 | +17.44% | `Supplementary_Material/Trained_Models/training_bpic13_incidents_GPU/metrics.json` |
| Helpdesk | 0.74 | 0.79 | 0.76 | 0.076405822 | 0.00670881 | -0.0083857169 | -1.10% | `Supplementary_Material/Trained_Models/training_helpdesk_GPU/metrics.json` |
| Sepsis | 0.49 | 0.51 | 0.46 | 0.15455625 | 0.097055146 | 0.11506341 | +25.01% | `Supplementary_Material/Trained_Models/training_sepsis_GPU/metrics.json` |
| Complex Model | 0.52 | 0.57 | 0.51 | 0.070404088 | 0.024896776 | 0.04640397 | +9.10% | `Supplementary_Material/Trained_Models/training_complex_model/metrics.json` |
| LDD | 0.88 | 0.92 | 0.89 | 0.12 | 0.08 | 0.11 | +12.36% | `Supplementary_Material/Trained_Models/training_long_dist_dep/metrics.json` |
| Looped And | 0.76 | 0.65 | 0.64 | -0.016631715 | 0.0057527821 | -0.032361663 | -5.06% | `Supplementary_Material/Trained_Models/training_looped_and/metrics.json` |
| Sequence | 1 | 1 | 1 | 0 | 0 | 0 | +0.00% | `Supplementary_Material/Trained_Models/training_sequence/metrics.json` |



Table 3 lấy cột printed (D) và so với các cohort XAI đã hoàn thành trong bảng kiểm kê. Đây là đối chiếu mô tả do metric, cohort và checkpoint không luôn tương đương. Tỷ lệ với correlation hoặc baseline gần 0 bị lược bỏ.

| Log | Method | Metric | D mean | A mean | Δ | \|Δ\| | Δ tương đối % |
|---|---|---|---|---|---|---|---|
| BPIC12_O | BE | correctness | 0.48 | 0.30037944 | -0.17962056 | 0.17962056 | — |
| BPIC12_O | BE | completeness_precision | 0.11 | 0.25824822 | 0.14824822 | 0.14824822 | 134.77111 |
| BPIC12_O | BE | completeness_recall | 0.18 | 0.72431562 | 0.54431562 | 0.54431562 | 302.39757 |
| BPIC12_O | BE | completeness_f1 | 0.13 | 0.35801073 | 0.22801073 | 0.22801073 | 175.39287 |
| BPIC12_O | BE | consistency | 0.65 | 0.35259601 | -0.29740399 | 0.29740399 | -45.75446 |
| BPIC12_O | BE | continuity | 0.95 | 0.71899817 | -0.23100183 | 0.23100183 | -24.315982 |
| BPIC12_O | BE | contrastivity | 0.07 | 0.50375204 | 0.43375204 | 0.43375204 | 619.64578 |
| BPIC12_O | BE | compactness_rules | 4.61 | 2.9304348 | -1.6795652 | 1.6795652 | -36.433085 |
| BPIC12_O | BE | compactness_rhs | 2.56 | 2.0895813 | -0.47041868 | 0.47041868 | -18.37573 |
| BPIC13_CP | BE | correctness | 0.75 | -0.09382571 | -0.84382571 | 0.84382571 | — |
| BPIC13_CP | BE | completeness_precision | 0.74 | 0.86338364 | 0.12338364 | 0.12338364 | 16.673465 |
| BPIC13_CP | BE | completeness_recall | 0.46 | 0.74212338 | 0.28212338 | 0.28212338 | 61.331169 |
| BPIC13_CP | BE | completeness_f1 | 0.5 | 0.7770188 | 0.2770188 | 0.2770188 | 55.40376 |
| BPIC13_CP | BE | consistency | 0.59 | 0.98843733 | 0.39843733 | 0.39843733 | 67.531751 |
| BPIC13_CP | BE | continuity | 0.49 | 0.60851441 | 0.11851441 | 0.11851441 | 24.186615 |
| BPIC13_CP | BE | contrastivity | 0.05 | 0.61495869 | 0.56495869 | 0.56495869 | 1129.9174 |
| BPIC13_CP | BE | compactness_rules | 2.16 | 1.5853852 | -0.57461477 | 0.57461477 | -26.602536 |
| BPIC13_CP | BE | compactness_rhs | 0.6 | 1.7374901 | 1.1374901 | 1.1374901 | 189.58168 |
| BPIC13-I | BE | correctness | — | 0.24724226 | — | — | — |
| BPIC13-I | BE | completeness_precision | 0.35 | 0.73399899 | 0.38399899 | 0.38399899 | 109.714 |
| BPIC13-I | BE | completeness_recall | 0.26 | 0.98768048 | 0.72768048 | 0.72768048 | 279.87711 |
| BPIC13-I | BE | completeness_f1 | 0.29 | 0.79919546 | 0.50919546 | 0.50919546 | 175.58464 |
| BPIC13-I | BE | consistency | 0.01 | 0.83763792 | 0.82763792 | 0.82763792 | 8276.3792 |
| BPIC13-I | BE | continuity | 0.19 | 0.78636011 | 0.59636011 | 0.59636011 | 313.87374 |
| BPIC13-I | BE | contrastivity | 0.04 | 0.58904617 | 0.54904617 | 0.54904617 | 1372.6154 |
| BPIC13-I | BE | compactness_rules | 1.38 | 1.8692623 | 0.48926227 | 0.48926227 | 35.453787 |
| BPIC13-I | BE | compactness_rhs | 0.19 | 2.2467854 | 2.0567854 | 2.0567854 | 1082.5186 |
| Helpdesk | BE | correctness | 0.91 | 0.84007998 | -0.069920015 | 0.069920015 | — |
| Helpdesk | BE | completeness_precision | 0.54 | 0.48127613 | -0.058723867 | 0.058723867 | -10.87479 |
| Helpdesk | BE | completeness_recall | 0.3 | 0.86803813 | 0.56803813 | 0.56803813 | 189.34604 |
| Helpdesk | BE | completeness_f1 | 0.36 | 0.56146752 | 0.20146752 | 0.20146752 | 55.963199 |
| Helpdesk | BE | consistency | 0.11 | 0.64012076 | 0.53012076 | 0.53012076 | 481.92797 |
| Helpdesk | BE | continuity | 0.73 | 0.59493209 | -0.13506791 | 0.13506791 | -18.502454 |
| Helpdesk | BE | contrastivity | 0.08 | 0.66875181 | 0.58875181 | 0.58875181 | 735.93977 |
| Helpdesk | BE | compactness_rules | 3.32 | 2.2172604 | -1.1027396 | 1.1027396 | -33.215048 |
| Helpdesk | BE | compactness_rhs | 1.99 | 2.3396411 | 0.34964112 | 0.34964112 | 17.569906 |
| Helpdesk | AE | correctness | 0.73 | -0.13745811 | -0.86745811 | 0.86745811 | — |
| Helpdesk | AE | completeness_precision | 0.5 | 0.31342078 | -0.18657922 | 0.18657922 | -37.315844 |
| Helpdesk | AE | completeness_recall | 0.25 | 0.99987456 | 0.74987456 | 0.74987456 | 299.94982 |
| Helpdesk | AE | completeness_f1 | 0.3 | 0.46678155 | 0.16678155 | 0.16678155 | 55.593851 |
| Helpdesk | AE | consistency | 0.09 | 0.61190217 | 0.52190217 | 0.52190217 | 579.8913 |
| Helpdesk | AE | continuity | 0.85 | 0.64518768 | -0.20481232 | 0.20481232 | -24.095567 |
| Helpdesk | AE | contrastivity | 0.2 | 0.53897763 | 0.33897763 | 0.33897763 | 169.48882 |
| Helpdesk | AE | compactness_rules | 2.45 | 2.2137481 | -0.23625188 | 0.23625188 | -9.6429339 |
| Helpdesk | AE | compactness_rhs | 2.55 | 4.3864359 | 1.8364359 | 1.8364359 | 72.017093 |
| LDD | BE | correctness | 0.68 | -0.40963796 | -1.089638 | 1.089638 | — |
| LDD | BE | completeness_precision | 0.3 | 0.22511943 | -0.074880572 | 0.074880572 | -24.960191 |
| LDD | BE | completeness_recall | 0.17 | 0.84472843 | 0.67472843 | 0.67472843 | 396.89908 |
| LDD | BE | completeness_f1 | 0.18 | 0.34377301 | 0.16377301 | 0.16377301 | 90.985006 |
| LDD | BE | consistency | 0.45 | 0.29010891 | -0.15989109 | 0.15989109 | -35.531354 |
| LDD | BE | continuity | 0.57 | 0.55868482 | -0.011315179 | 0.011315179 | -1.9851191 |
| LDD | BE | contrastivity | 0.42 | 0.34428419 | -0.075715807 | 0.075715807 | -18.027573 |
| LDD | BE | compactness_rules | 3.94 | 3.7654952 | -0.17450479 | 0.17450479 | -4.4290556 |
| LDD | BE | compactness_rhs | 2.76 | 1.3190126 | -1.4409874 | 1.4409874 | -52.209687 |
| LDD | AE | correctness | 0.68 | -0.067322239 | -0.74732224 | 0.74732224 | — |
| LDD | AE | completeness_precision | 0.1 | 0.14440895 | 0.044408946 | 0.044408946 | 44.408946 |
| LDD | AE | completeness_recall | 0.14 | 1 | 0.86 | 0.86 | 614.28571 |
| LDD | AE | completeness_f1 | 0.12 | 0.24982606 | 0.12982606 | 0.12982606 | 108.18838 |
| LDD | AE | consistency | 0.27 | 0.92036505 | 0.65036505 | 0.65036505 | 240.87595 |
| LDD | AE | continuity | 0.57 | 0.60451275 | 0.034512751 | 0.034512751 | 6.0548686 |
| LDD | AE | contrastivity | 0.42 | 0.35152645 | -0.068473554 | 0.068473554 | -16.303227 |
| LDD | AE | compactness_rules | 3.75 | 3.7654952 | 0.015495208 | 0.015495208 | 0.41320554 |
| LDD | AE | compactness_rhs | 1.89 | 5.0569664 | 3.1669664 | 3.1669664 | 167.56436 |
| Looped And | BE | correctness | — | -0.49068067 | — | — | — |
| Looped And | BE | completeness_precision | 0 | 0.41666667 | 0.41666667 | 0.41666667 | — |
| Looped And | BE | completeness_recall | 0.05 | 0.91649613 | 0.86649613 | 0.86649613 | 1732.9923 |
| Looped And | BE | completeness_f1 | 0.01 | 0.55284293 | 0.54284293 | 0.54284293 | 5428.4293 |
| Looped And | BE | consistency | 0.99 | 0.68069361 | -0.30930639 | 0.30930639 | -31.24307 |
| Looped And | BE | continuity | 0.93 | 0.91223375 | -0.017766246 | 0.017766246 | -1.910349 |
| Looped And | BE | contrastivity | 0.4 | 0.41685782 | 0.016857818 | 0.016857818 | 4.2144546 |
| Looped And | BE | compactness_rules | 4 | 4.5709358 | 0.57093585 | 0.57093585 | 14.273396 |
| Looped And | BE | compactness_rhs | 1 | 2.0244309 | 1.0244309 | 1.0244309 | 102.44309 |
| Sequence | BE | correctness | 0.32 | 0.049301448 | -0.27069855 | 0.27069855 | — |
| Sequence | BE | completeness_precision | 0.32 | 0.18581845 | -0.13418155 | 0.13418155 | -41.931734 |
| Sequence | BE | completeness_recall | 0.14 | 0.90606061 | 0.76606061 | 0.76606061 | 547.18615 |
| Sequence | BE | completeness_f1 | 0.15 | 0.29517291 | 0.14517291 | 0.14517291 | 96.781943 |
| Sequence | BE | consistency | 0.53 | 0.56062646 | 0.030626462 | 0.030626462 | 5.7785778 |
| Sequence | BE | continuity | 0.78 | 0.80511106 | 0.025111058 | 0.025111058 | 3.2193664 |
| Sequence | BE | contrastivity | 0.33 | 0.25498877 | -0.075011232 | 0.075011232 | -22.730676 |
| Sequence | BE | compactness_rules | 7.08 | 6.0075758 | -1.0724242 | 1.0724242 | -15.147235 |
| Sequence | BE | compactness_rhs | 1.96 | 1.205007 | -0.75499303 | 0.75499303 | -38.520053 |
| Sequence | AE | correctness | 0.17 | -0.77422683 | -0.94422683 | 0.94422683 | — |
| Sequence | AE | completeness_precision | 0.11 | 0.11163654 | 0.0016365358 | 0.0016365358 | 1.4877598 |
| Sequence | AE | completeness_recall | 0.11 | 1 | 0.89 | 0.89 | 809.09091 |
| Sequence | AE | completeness_f1 | 0.1 | 0.20057928 | 0.10057928 | 0.10057928 | 100.57928 |
| Sequence | AE | consistency | 0.42 | 0.96619876 | 0.54619876 | 0.54619876 | 130.04732 |
| Sequence | AE | continuity | 0.78 | 0.7843843 | 0.0043842969 | 0.0043842969 | 0.56208935 |
| Sequence | AE | contrastivity | 0.32 | 0.19841931 | -0.12158069 | 0.12158069 | -37.993964 |
| Sequence | AE | compactness_rules | 5.08 | 6.0075758 | 0.92757576 | 0.92757576 | 18.259365 |
| Sequence | AE | compactness_rhs | 2.06 | 5.8283409 | 3.7683409 | 3.7683409 | 182.92917 |




## Kết quả suy ra, ước lượng và giới hạn

| Hạng mục | Bằng chứng độc lập | Suy ra hoặc ước lượng | Tin cậy và bất định |
|---|---|---|---|
| E1 Sepsis | 15.000 variant đã lưu, 22.151.168 byte. Session thứ hai thêm 5.000 trong 2,891 s | C. Nếu giữ tốc độ đầu và byte/hàng quan sát, khoảng 16 ngày và 3,6 TB. Dùng làm bậc độ lớn cho kế hoạch, không dùng dự báo metric | LOW. Độ dài prefix, số query và tranh chấp CPU/đĩa thay đổi. Không có khoảng xác suất từ hai session. Nguồn sepsis-v1/E1-stream-e1-run/{progress,workload-estimate}.json |
| E1 BPIC12, Complex | Bộ đếm DFG với split đã khóa | B. BPIC12 ≥2.440.580.925 variants và >312 GB text tối thiểu. Complex có 15.755.268.423 variants | HIGH cho cận hoặc lịch, F cho tau. Nguồn bpic12-v1/E1-workload-lower-bound-v2.json, synthetic-complex-model/E1-workload-counter.json |
| AE BPIC12_O và CP | Số vị trí đủ điều kiện, SHA/ID và các occurrence bắt buộc lưu | B. Payload text tối thiểu 47.502.862.092 byte và 240.980.201.722 byte tương ứng. Cả hai cao hơn chỗ trống từng ổ trong ảnh chụp | HIGH cho cận của schema hiện tại. Chưa gồm cache và overhead. Nguồn ae-storage-bound.json trong mỗi log |
| AE các cohort k lớn | Lịch đã xác minh bằng BE | B. BPIC12 khoảng 1,07027×10^40 contexts, Sepsis khoảng 9,578×10^52. Graph và metric của AE thiếu giữ F | HIGH cho số lịch, NOT ESTIMABLE cho metric hoặc thời điểm hoàn tất thực tế |
| XAI chỉ BE trên BPIC12, Sepsis, Complex | Seed404 và cận variant ID 64 byte | B. Tối thiểu lần lượt 124,91 GB, 120,38 GB, 808,33 GB chỉ cho ID một phương pháp | HIGH với schema và cohort hiện tại. Đồ thị BE hoàn tất không cung cấp biến thể đã chấm. Nguồn xai-evaluation-workload-v2.json từng log |
| E2 còn thiếu, full BPIC12 E3 | Các ledger và giới hạn trong phần trên | B. Khôi phục mean quan sát và giới hạn toàn cohort. F cho point estimate toàn run đáng tin | HIGH cho khoảng toán học có điều kiện. Không có chọn mẫu xác suất, không lấy trung bình log khác để nội suy. ETA từ tốc độ ghi cặp sẽ bỏ qua train các seed và các lần dừng bộ nhớ |
| XAI BPIC12_W và WC | Đồ thị BE và baseline đã có | F cho metric cuối. Cần chọn candidate thật, xuất cạnh và đánh giá perturbation trên mẫu khóa | NOT ESTIMABLE. Có thể tính độ gọn cấu trúc cho graph hiện tại, nhưng thống kê Co06 theo prefix cần projection đúng cohort |

## Kiểm kê nguồn công bố và nguồn tác giả

| Kết quả cần | Nguồn D trong bài | Nguồn E và định nghĩa tham chiếu | So sánh được với dữ liệu độc lập |
|---|---|---|---|
| Kiến trúc, dữ liệu | Figure 1 pp.7–8, Table 1 và Appendix PL1 | Git processtransformer/models/transformer.py, multi_head_attention.py và configs. Kho cấu hình archive gắn thực tế mỗi model | Cùng họ kiến trúc, khác width từng head. Số case/event/label và filter có trong DATASET_PROVENANCE.md |
| E1 | Figure 3, p.16. Median phần lớn hơi trên .5, BPIC12/WC/Sepsis thấp hơn | Git processtransformer/xai/metrics/attn_feature_importance.py. Archive attn_feature_importance.csv và summary, 12 log | So median đúng thống kê, có mẫu số. Cách tạo biến thể, distance/gate và sampled sequences khác |
| E2 | Figures 4–5, pp.18–19. Mười điểm seed mỗi log, JSD tối đa ln2, đường TVD .1, phân bố raw/normalized chưa giải thích đầy đủ | Git processtransformer/xai/metrics/attn_uniform_weights.py. Archive attn_uniform_weights_jsd_tvd.csv, attn_uniform_weights_attn.csv và summaries | So nhóm tương ứng và giữ FC/AC riêng. Bins cần cùng đối tượng, TVD filter và phân mẫu |
| E3 | Figures 6–7, pp.20–21. Histogram tập trung gần 0 ở đa số log | Git processtransformer/xai/metrics/attn_masking.py. Archive attn_masking.csv và summary | So theo occurrence. Chênh semantics pre-softmax và hậu softmax giới hạn diễn giải |
| Dự báo Table 2 | p.30, 12×3 giá trị in | Archive Trained_Models/training_*/metrics.json và SavedModel. Reconciliation ghi từng member, SHA và exact aggregate | Đủ 36 số in và delta độc lập trong audit. Label alignment khác theo lịch sử |
| XAI Table 3, đồ thị | pp.30–35, sáu nhóm chín trường | Git trace_backward_explainer.py, attn_exploration_explainer.py trong processtransformer/xai, metrics/correctness_co01.py. Archive Detailed_Results chứa CSV và reference BPMN | 216 cặp mean/SD archive khớp số in sau làm tròn. Delta chỉ trên log/method có audit độc lập |

Bài PDF gốc nằm ở `C:/Users/Ngoc Duy/Downloads/s44311-025-00018-4.pdf`. Trang 16/18/21 được kiểm tra trực quan trong `artifacts/paper-r4-page16.png`, `paper-r4-page18.png`, `paper-r4-page21.png`. Figures 3, 4 và 7 không in đầy đủ các giá trị số chính xác theo log. Các thống kê chi tiết lấy từ supplement E và có SHA member tại `artifacts/author-runtime/prestudy-archive-audit.json`. Inventory Git tracked không thấy file .pt/.h5/.pb/.csv/.xes/.zip/.pkl. Các artifact E xác minh trong `data/raw/author-supplement/Supplementary_Material.zip`, dung lượng 148.506.909 byte, SHA-256 b1b88b2d7797fbe3369dccc5c4fe8d9a96af5d52293954279d4bab2f0bcc169e. Xem `data/raw/author-supplement/inventory.json`, `table2-reconciliation.json`, `table3-reconciliation.json` và `artifacts/author-runtime/table2-replay-comparison.json`. [Bài gốc](https://doi.org/10.1007/s44311-025-00018-4) · [Git tác giả tại SHA đã kiểm](https://github.com/mkaep/transformer-explainability/tree/494b315a555e713bdd61f0edd7d033c31d5850bf)

## Sai khác thực nghiệm và mức tái lập

| Mục | Phân loại và bằng chứng | Đánh giá tái lập |
|---|---|---|
| E1 | EVIDENCE-SUPPORTED HYPOTHESIS. DFG path/mask, điều kiện similarity và split có thể đổi thứ hạng. BPIC12_WC độc lập median 1.0, xung đột với mô tả thấp trong Figure 3. Không có can thiệp chỉ thay một biến để gán nguyên nhân | PARTIALLY REPRODUCED |
| E2 JSD/TVD | VERIFIED CAUSE cho khác biệt protocol: head width 9 so với key_dim 36, và FC constant so với initializer đóng băng của mã. EVIDENCE-SUPPORTED HYPOTHESIS cho ảnh hưởng của chúng lên độ lệch số. Helpdesk AC−FC JSD −0,00004429 và TVD −0,00206807 trên cùng cohort và BASE, chưa khôi phục archive uniform. Nguồn helpdesk-v1/e2-ac-fc-comparison.json | PARTIALLY REPRODUCED |
| E2 Figure 5 normalized | VERIFIED CAUSE cho mâu thuẫn support. Với H=4 và n query hợp lệ, L1 tối đa 1/(4n), nên các bin cao không có support. Pinned code lấy raw max và lọc TVD≤.1. Không biết mọi điểm in đã chọn đúng cohort nào | NOT REPRODUCED với định nghĩa normalized đã in |
| E3 | VERIFIED CAUSE cho khác biệt toán tử. Bản độc lập zero query/key sau softmax, source thực hiện trước softmax. Tách occurrence và prefix. Sequence/LDD gần 0 ở median occurrence, Helpdesk .129620 so với archive .056731. Nguyên nhân định lượng của độ lệch còn EVIDENCE-SUPPORTED HYPOTHESIS | PARTIALLY REPRODUCED |
| BE, AE và Table 3 | Mã và artifact xác lập đồ thị fidelity đối với checkpoint. Simultaneous pruning và vote semantics, cohort, null handling và Jaccard/cosine dựa trên consequence khác nhau. Đánh giá mức alignment dựa trên 4 BPMN có chọn lọc. Paper nói AE precision luôn cao hơn nhưng Table 3 có bốn log ngược lại, đây là VERIFIED CAUSE của mâu thuẫn phát biểu và bảng | PARTIALLY REPRODUCED trên cohort có kết quả. UNABLE TO ASSESS cho full AE bị thiếu |
| Table 2 | VERIFIED CAUSE cho gap target conventions trong replay BPIC13_CP. Cùng checkpoint archive đạt accuracy .831763 với last prefix, .538358 với next event. Author CPU replay khớp 10/12 kết quả archive theo last prefix, lệch ở Helpdesk và Sepsis. Mốc lịch sử chính xác, CPU/GPU và pipeline chưa tách được ở hai log này, nguyên nhân UNKNOWN | PARTIALLY REPRODUCED độc lập. Replay archive thuộc E |

Khác biệt split theo case, vocab train-only, hyperparameter khi chạy lịch sử và seed/cấu hình có bằng chứng trong run.json hoặc acquisition logs. Chúng là khác biệt quan sát được. Mức đóng góp nhân quả của từng yếu tố tới metric tổng hợp chưa định lượng được. Ưu tiên thuật ngữ “đối chiếu mô tả” cho các cohort khác nhau. Xem [bảng đối chiếu Round 4 trước WC](../round4/REPRODUCTION_COMPARISON.md) và ma trận bổ sung dưới đây.

## Checklist phần còn thiếu

| Mục | Vì sao cần, bằng chứng hiện có | Cách xử lý | Cần chạy thêm | Ưu tiên |
|---|---|---|---|---|
| E2 BPIC12/W/Complex | Results theo seed và checkpoint có nhưng thiếu cặp toàn cohort | Dùng số liệu đã ghi trong audit này. Tiếp tục đúng snapshot sau audit khi có RAM và dung lượng | Có để đủ mẫu | CRITICAL |
| E3 BPIC12 | 10.690 prefix lưu được, cận chưa đủ kết luận | Dùng cận và phần đo có điều kiện. Tiếp tục đúng checkpoint và C locator sau audit | Có | CRITICAL |
| E1 Sepsis/BPIC12/Complex | Số biến thể xác lập chi phí, thiếu tau toàn log | Giữ F cho mean. Cân nhắc schema lưu lossless và compute riêng trước khi cam kết lịch | Có nếu giữ full protocol | CRITICAL |
| AE và XAI thiếu | 3 full paired, 4 BE-only, còn 5 log không có đủ XAI. Phần lớn AE có lịch vượt tài nguyên | Công bố workload, mẫu số thực và phạm vi phương pháp. Cap phải khai protocol riêng nếu được duyệt | Có nếu cần kết quả mới | CRITICAL |
| Source historical parity | Archive có Table 2/3, nguồn mã pin và replay. Hai checkpoint lệch, chưa có lịch chính xác Figure 5 | Ưu tiên đối chiếu config, target order và artifacts gốc. Ghi UNKNOWN nếu thiếu linkage | Có thể cần diagnostic, chưa đủ cơ sở | IMPORTANT |
| Hình thiếu | Có figures cho O, CP, incidents, Helpdesk và ba synthetic đủ E1–E3, có graph QA riêng | Dựng Figure-style từ manifest cho WC sau audit này. W/Complex/full BPIC12 thiếu một hoặc nhiều study nên vẽ theo phạm vi xác nhận | Không cần train để vẽ dữ liệu hiện có | IMPORTANT |
| Đọc hiểu của người dùng | Chưa có human study hoặc thống kê suy luận thiết kế trước | Giữ claim fidelity và BPMN riêng. Đề xuất đánh giá người dùng sau | Có | OPTIONAL |

## Cơ hội nghiên cứu sơ bộ

| ID và loại | Hạn chế quan sát | Đề xuất, lợi ích kỳ vọng | Cách xác thực | Độ phức tạp / ưu tiên |
|---|---|---|---|---|
| P1 · IMPLEMENTATION CORRECTION | Head width, checkpoint và masking historical khác | Profile đối chiếu cùng data, width và masking, có thể quy phần chênh riêng | Kiểm Q/K/V shapes, support, chạy một log có archive và seed kiểm soát | Trung bình / IMPORTANT |
| P2 · METHODOLOGICAL IMPROVEMENT | E1 và AE có số context tăng mạnh. Bộ nhớ và I/O dừng thật | Lưu ledger nén/lossless hoặc suy luận microbatch với lịch không đổi, kỳ vọng giảm I/O và peak RSS | Kiểm mọi mask và vote, graph, metric và hash canonical trên cohort hoàn chỉnh | Trung bình / IMPORTANT |
| P3 · METHODOLOGICAL IMPROVEMENT | Báo cáo Figure 5 dễ trộn raw và L1 | Ghi rõ statistic, mẫu số lọc và support, kiểm toán bins theo arm và chiều dài | Bất biến 1/(Hn), đối chiếu raw bins đã lưu và TVD gate | Thấp / CRITICAL cho diễn giải |
| P4 · RESEARCH EXTENSION | AE exhaustive quá lớn, đã có exact graph trên 3 log | Thử approximation có ngân sách ghi riêng, kỳ vọng mở rộng phạm vi | Accuracy edge, weighted metric error, time/memory và độ ổn định theo seed so exact | Cao / OPTIONAL |
| P5 · RESEARCH EXTENSION | Fidelity không đồng nhất BPMN hoặc khả năng hiểu | Đánh giá mù các truy vấn nghiệp vụ trên đồ thị/BPMN và baseline | Định trước nhiệm vụ, split theo case, liên giám khảo và sai số theo log | Cao / OPTIONAL |

## Dùng tài liệu này cho báo cáo sau

Khóa lại snapshot số liệu sát ngày nộp. Trích nguồn A/B cùng cohort, trạng thái audit, null và profile. Dùng Table 2/3 và Figures 3/4/5/7 làm nguồn D, supplement và replay làm E. Nêu E2/BE đã đủ dữ liệu ở các phạm vi xác nhận và các thí nghiệm đang thiếu cấp log. Bảng khoảng ở đây có thể dùng trong phần giới hạn hoặc feasibility. Chỉ chuyển một dòng từ F thành kết quả sau khi đủ artifact và audit cùng cohort. Báo cáo kết quả đúng theo phạm vi đã kiểm chứng, tránh quy chiếu từ fidelity sang năng lực giải thích của mọi Transformer.

Các hiện vật công khai và log cục bộ truy vết qua [Results](../round4/EXPERIMENTAL_RESULTS.md), [Technical report](../round4/TECHNICAL_REPORT.md), [Source decisions](../round4_preflight/decision_closure/TECHNICAL_DECISION_CLOSURE.md), và [Progress](../round4/PROGRESS.md). Mọi đường dẫn repo không tuyệt đối trong các bảng có gốc `D:/nhom19_cschttt`. Log/tham số chi tiết chứa trong manifest và ledger của từng stage. Kiểm toán này sử dụng kết quả thực thi và kiểm thử trước đó, cùng đọc seal, trích ledger và tính toán độc lập trong phiên hiện tại.



## Ma trận đối chiếu E1–E3 theo log

Có 67 dòng từ 63 dòng đối chiếu đã lưu và 4 dòng BPIC12_WC mới đã audit. Bài chỉ công bố đồ thị cho các giá trị trong bảng. Cột E lấy từ supplement, cột B lấy từ kết quả độc lập, gồm tổng hợp mean/median. Δ = B − E. Cột % là Δ/|E|, để trống khi tỷ lệ không có nghĩa. Các dòng đều là đối chiếu mô tả và trạng thái cấp experiment xem bảng sai khác. Cột nguồn ghi theo thứ tự B rồi E.

| Log | E | Metric | Nguồn D | E value | B value | Δ | \|Δ\| | Δ % | n E / B | Nguồn B và E |
|---|---|---|---|---|---|---|---|---|---|---|
| bpic12-o-v1 | E1 | median_tau_b | Fig 3 | 0.57635398 | 1 | 0.42364602 | 0.42364602 | — | 411/6197 | artifacts/bpic12-o-v1/E1-stream.json · Supplementary_Material/Trained_Models/training_bpic12_o_GPU/metrics/attn_feature_importance.csv |
| bpic12-o-v1 | E2 | BASE_five_model_mean_jsd | Fig 4 | 0.27531204 | 0.0031517027 | -0.27216034 | 0.27216034 | -98.855225 | 5/5 | artifacts/bpic12-o-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_bpic12_o_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| bpic12-o-v1 | E2 | BASE_five_model_mean_tvd | Fig 4 | 0.062103173 | 0.036889605 | -0.025213568 | 0.025213568 | -40.599484 | 5/5 | artifacts/bpic12-o-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_bpic12_o_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| bpic12-o-v1 | E2 | E2-FC_five_model_mean_jsd | Fig 4 | 0.39117348 | 0.0016354234 | -0.38953805 | 0.38953805 | -99.581919 | 5/5 | artifacts/bpic12-o-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_bpic12_o_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| bpic12-o-v1 | E2 | E2-FC_five_model_mean_tvd | Fig 4 | 0.10635655 | 0.034041227 | -0.072315325 | 0.072315325 | -67.993295 | 5/5 | artifacts/bpic12-o-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_bpic12_o_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| bpic12-o-v1 | E3 | occurrence_mean_tvd | Fig 7 | 0.05734369 | 0.23081322 | 0.17346953 | 0.17346953 | 302.5085 | 6376/31039 | artifacts/bpic12-o-v1/e3-attention-reference-audit.json · Supplementary_Material/Trained_Models/training_bpic12_o_GPU/metrics/attn_masking.csv |
| bpic12-o-v1 | E3 | occurrence_median_tvd | Fig 7 | 0.0030903437 | 0.071676653 | 0.06858631 | 0.06858631 | 2219.3748 | 6376/31039 | artifacts/bpic12-o-v1/e3-attention-reference-audit.json · Supplementary_Material/Trained_Models/training_bpic12_o_GPU/metrics/attn_masking.csv |
| bpic12-w-v1 | E1 | median_tau_b | Fig 3 | 0.56736651 | 0.33333333 | -0.23403318 | 0.23403318 | — | 2000/35019 | artifacts/bpic12-w-v1/E1-stream.json · Supplementary_Material/Trained_Models/training_bpic12_w_GPU/metrics/attn_feature_importance.csv |
| bpic12-w-v1 | E3 | occurrence_mean_tvd | Fig 7 | 0.014074944 | 0.02246507 | 0.0083901258 | 0.0083901258 | 59.610367 | 81777/774557 | artifacts/bpic12-w-v1/e3-record-audit.json · Supplementary_Material/Trained_Models/training_bpic12_w_GPU/metrics/attn_masking.csv |
| bpic12-w-v1 | E3 | occurrence_median_tvd | Fig 7 | 0.0065510548 | 0.0035837554 | -0.0029672994 | 0.0029672994 | -45.294986 | 81777/774557 | artifacts/bpic12-w-v1/e3-record-audit.json · Supplementary_Material/Trained_Models/training_bpic12_w_GPU/metrics/attn_masking.csv |
| bpic12-wc-v1 | E1 | median_tau_b | Fig 3 | 0.19245009 | 1 | 0.80754991 | 0.80754991 | — | 2000/13370 | artifacts/bpic12-wc-v1/E1-stream.json · Supplementary_Material/Trained_Models/training_bpic12_wc_GPU/metrics/attn_feature_importance.csv |
| bpic12-wc-v1 | E3 | occurrence_mean_tvd | Fig 7 | 0.014611874 | 0.037742898 | 0.023131024 | 0.023131024 | 158.30293 | 39060/143848 | artifacts/bpic12-wc-v1/e3-occurrence-audit.json · Supplementary_Material/Trained_Models/training_bpic12_wc_GPU/metrics/attn_masking.csv |
| bpic12-wc-v1 | E3 | occurrence_median_tvd | Fig 7 | 0.0017880967 | 0.011057654 | 0.0092695569 | 0.0092695569 | 518.40355 | 39060/143848 | artifacts/bpic12-wc-v1/e3-occurrence-audit.json · Supplementary_Material/Trained_Models/training_bpic12_wc_GPU/metrics/attn_masking.csv |
| bpic13-cp-v1 | E1 | median_tau_b | Fig 3 | 0.4454354 | 1 | 0.5545646 | 0.5545646 | — | 585/856 | artifacts/bpic13-cp-v1/E1-stream.json · Supplementary_Material/Trained_Models/training_bpic13_closed_problems_GPU/metrics/attn_feature_importance.csv |
| bpic13-cp-v1 | E2 | BASE_five_model_mean_jsd | Fig 4 | 0.044072321 | 0.013598214 | -0.030474107 | 0.030474107 | -69.145682 | 5/5 | artifacts/bpic13-cp-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_bpic13_closed_problems_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| bpic13-cp-v1 | E2 | BASE_five_model_mean_tvd | Fig 4 | 0.036729592 | 0.065364167 | 0.028634575 | 0.028634575 | 77.960503 | 5/5 | artifacts/bpic13-cp-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_bpic13_closed_problems_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| bpic13-cp-v1 | E2 | E2-FC_five_model_mean_jsd | Fig 4 | 0.44658974 | 0.0048247172 | -0.44176502 | 0.44176502 | -98.919653 | 5/5 | artifacts/bpic13-cp-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_bpic13_closed_problems_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| bpic13-cp-v1 | E2 | E2-FC_five_model_mean_tvd | Fig 4 | 0.14609688 | 0.06521573 | -0.080881151 | 0.080881151 | -55.361313 | 5/5 | artifacts/bpic13-cp-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_bpic13_closed_problems_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| bpic13-cp-v1 | E3 | occurrence_mean_tvd | Fig 7 | 0.032735123 | 0.11203369 | 0.079298563 | 0.079298563 | 242.24306 | 5955/6243 | artifacts/bpic13-cp-v1/e3-attention-reference-audit.json · Supplementary_Material/Trained_Models/training_bpic13_closed_problems_GPU/metrics/attn_masking.csv |
| bpic13-cp-v1 | E3 | occurrence_median_tvd | Fig 7 | 0.00392047 | 0.055524649 | 0.051604179 | 0.051604179 | 1316.2753 | 5955/6243 | artifacts/bpic13-cp-v1/e3-attention-reference-audit.json · Supplementary_Material/Trained_Models/training_bpic13_closed_problems_GPU/metrics/attn_masking.csv |
| bpic13-i-v1 | E1 | median_tau_b | Fig 3 | 0.67357531 | 1 | 0.32642469 | 0.32642469 | — | 2000/12498 | artifacts/bpic13-i-v1/E1-stream.json · Supplementary_Material/Trained_Models/training_bpic13_incidents_GPU/metrics/attn_feature_importance.csv |
| bpic13-i-v1 | E2 | BASE_five_model_mean_jsd | Fig 4 | 0.37166495 | 0.19749551 | -0.17416944 | 0.17416944 | -46.861948 | 5/5 | artifacts/bpic13-i-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_bpic13_incidents_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| bpic13-i-v1 | E2 | BASE_five_model_mean_tvd | Fig 4 | 0.077607752 | 0.054719885 | -0.022887867 | 0.022887867 | -29.491728 | 5/5 | artifacts/bpic13-i-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_bpic13_incidents_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| bpic13-i-v1 | E2 | E2-FC_five_model_mean_jsd | Fig 4 | 0.3381879 | 0.21339357 | -0.12479433 | 0.12479433 | -36.900885 | 5/5 | artifacts/bpic13-i-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_bpic13_incidents_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| bpic13-i-v1 | E2 | E2-FC_five_model_mean_tvd | Fig 4 | 0.18253058 | 0.093162774 | -0.089367807 | 0.089367807 | -48.960457 | 5/5 | artifacts/bpic13-i-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_bpic13_incidents_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| bpic13-i-v1 | E3 | occurrence_mean_tvd | Fig 7 | 0.017179326 | 0.053956432 | 0.036777106 | 0.036777106 | 214.0777 | 41902/146211 | artifacts/bpic13-i-v1/e3-occurrence-audit.json · Supplementary_Material/Trained_Models/training_bpic13_incidents_GPU/metrics/attn_masking.csv |
| bpic13-i-v1 | E3 | occurrence_median_tvd | Fig 7 | 0.0036883647 | 0.017057467 | 0.013369103 | 0.013369103 | 362.46693 | 41902/146211 | artifacts/bpic13-i-v1/e3-occurrence-audit.json · Supplementary_Material/Trained_Models/training_bpic13_incidents_GPU/metrics/attn_masking.csv |
| helpdesk-v1 | E1 | median_tau_b | Fig 3 | 0.63976328 | 1 | 0.36023672 | 0.36023672 | — | 500/3497 | artifacts/helpdesk-v1/E1-stream.json · Supplementary_Material/Trained_Models/training_helpdesk_GPU/metrics/attn_feature_importance.csv |
| helpdesk-v1 | E2 | BASE_five_model_mean_jsd | Fig 4 | 0.34404921 | 0.026802626 | -0.31724658 | 0.31724658 | -92.209653 | 5/5 | artifacts/helpdesk-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_helpdesk_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| helpdesk-v1 | E2 | BASE_five_model_mean_tvd | Fig 4 | 0.13161972 | 0.040435163 | -0.091184554 | 0.091184554 | -69.278795 | 5/5 | artifacts/helpdesk-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_helpdesk_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| helpdesk-v1 | E2 | E2-FC_five_model_mean_jsd | Fig 4 | 7.1713058e-08 | 0.078434188 | 0.078434117 | 0.078434117 | — | 5/5 | artifacts/helpdesk-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_helpdesk_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| helpdesk-v1 | E2 | E2-FC_five_model_mean_tvd | Fig 4 | 0.097284464 | 0.0435974 | -0.053687064 | 0.053687064 | -55.18565 | 5/5 | artifacts/helpdesk-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_helpdesk_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| helpdesk-v1 | E3 | occurrence_mean_tvd | Fig 7 | 0.1298035 | 0.20558711 | 0.075783609 | 0.075783609 | 58.383331 | 2918/12547 | artifacts/helpdesk-v1/e3-attention-reference-audit.json · Supplementary_Material/Trained_Models/training_helpdesk_GPU/metrics/attn_masking.csv |
| helpdesk-v1 | E3 | occurrence_median_tvd | Fig 7 | 0.056730903 | 0.12961973 | 0.072888826 | 0.072888826 | 128.4817 | 2918/12547 | artifacts/helpdesk-v1/e3-attention-reference-audit.json · Supplementary_Material/Trained_Models/training_helpdesk_GPU/metrics/attn_masking.csv |
| sepsis-v1 | E2 | BASE_five_model_mean_jsd | Fig 4 | 0.48606371 | 0.030866119 | -0.45519759 | 0.45519759 | -93.649779 | 5/5 | artifacts/sepsis-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_sepsis_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| sepsis-v1 | E2 | BASE_five_model_mean_tvd | Fig 4 | 0.1380855 | 0.12735422 | -0.010731275 | 0.010731275 | -7.7714713 | 5/5 | artifacts/sepsis-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_sepsis_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| sepsis-v1 | E2 | E2-FC_five_model_mean_jsd | Fig 4 | 5.4747232e-06 | 0.020680372 | 0.020674897 | 0.020674897 | 377642.79 | 5/5 | artifacts/sepsis-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_sepsis_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| sepsis-v1 | E2 | E2-FC_five_model_mean_tvd | Fig 4 | 0.074511219 | 0.14864371 | 0.074132487 | 0.074132487 | 99.491711 | 5/5 | artifacts/sepsis-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_sepsis_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| sepsis-v1 | E3 | occurrence_mean_tvd | Fig 7 | 0.020713608 | 0.053076127 | 0.03236252 | 0.03236252 | 156.23797 | 45126/60338 | artifacts/sepsis-v1/e3-attention-reference-audit.json · Supplementary_Material/Trained_Models/training_sepsis_GPU/metrics/attn_masking.csv |
| sepsis-v1 | E3 | occurrence_median_tvd | Fig 7 | 0.006060783 | 0.022247419 | 0.016186636 | 0.016186636 | 267.0717 | 45126/60338 | artifacts/sepsis-v1/e3-attention-reference-audit.json · Supplementary_Material/Trained_Models/training_sepsis_GPU/metrics/attn_masking.csv |
| synthetic-complex-model | E3 | occurrence_mean_tvd | Fig 7 | 0.11512885 | 0.052625321 | -0.062503528 | 0.062503528 | -54.290066 | 29575/196047 | artifacts/synthetic-complex-model/e3-occurrence-audit.json · Supplementary_Material/Trained_Models/training_complex_model/metrics/attn_masking.csv |
| synthetic-complex-model | E3 | occurrence_median_tvd | Fig 7 | 0.0035928726 | 0.016653824 | 0.013060951 | 0.013060951 | 363.52391 | 29575/196047 | artifacts/synthetic-complex-model/e3-occurrence-audit.json · Supplementary_Material/Trained_Models/training_complex_model/metrics/attn_masking.csv |
| synthetic-long-dist-dep | E1 | median_tau_b | Fig 3 | 0.59818923 | 1 | 0.40181077 | 0.40181077 | — | 14/1657 | artifacts/synthetic-long-dist-dep/E1-stream.json · Supplementary_Material/Trained_Models/training_long_dist_dep/metrics/attn_feature_importance.csv |
| synthetic-long-dist-dep | E2 | BASE_five_model_mean_jsd | Fig 4 | 0.20496637 | 0.00029324677 | -0.20467312 | 0.20467312 | -99.856929 | 5/5 | artifacts/synthetic-long-dist-dep/E2-stream.json · Supplementary_Material/Trained_Models/training_long_dist_dep/metrics/attn_uniform_weights_jsd_tvd.csv |
| synthetic-long-dist-dep | E2 | BASE_five_model_mean_tvd | Fig 4 | 0.00013651308 | 1.5627539e-05 | -0.00012088554 | 0.00012088554 | -88.55235 | 5/5 | artifacts/synthetic-long-dist-dep/E2-stream.json · Supplementary_Material/Trained_Models/training_long_dist_dep/metrics/attn_uniform_weights_jsd_tvd.csv |
| synthetic-long-dist-dep | E2 | E2-FC_five_model_mean_jsd | Fig 4 | 0.17070842 | 0.00010381145 | -0.17060461 | 0.17060461 | -99.939188 | 5/5 | artifacts/synthetic-long-dist-dep/E2-stream.json · Supplementary_Material/Trained_Models/training_long_dist_dep/metrics/attn_uniform_weights_jsd_tvd.csv |
| synthetic-long-dist-dep | E2 | E2-FC_five_model_mean_tvd | Fig 4 | 0.00077834598 | 9.9726679e-05 | -0.0006786193 | 0.0006786193 | -87.187359 | 5/5 | artifacts/synthetic-long-dist-dep/E2-stream.json · Supplementary_Material/Trained_Models/training_long_dist_dep/metrics/attn_uniform_weights_jsd_tvd.csv |
| synthetic-long-dist-dep | E3 | occurrence_mean_tvd | Fig 7 | 0.22341436 | 0.063359049 | -0.16005531 | 0.16005531 | -71.640565 | 53/7399 | artifacts/synthetic-long-dist-dep/e3-attention-reference-audit.json · Supplementary_Material/Trained_Models/training_long_dist_dep/metrics/attn_masking.csv |
| synthetic-long-dist-dep | E3 | occurrence_median_tvd | Fig 7 | 0.0014763839 | 0.00023773192 | -0.001238652 | 0.001238652 | -83.89769 | 53/7399 | artifacts/synthetic-long-dist-dep/e3-attention-reference-audit.json · Supplementary_Material/Trained_Models/training_long_dist_dep/metrics/attn_masking.csv |
| synthetic-looped-and | E1 | median_tau_b | Fig 3 | 0.68 | 0.8 | 0.12 | 0.12 | — | 2000/10408 | artifacts/synthetic-looped-and/E1-stream.json · Supplementary_Material/Trained_Models/training_looped_and/metrics/attn_feature_importance.csv |
| synthetic-looped-and | E2 | BASE_five_model_mean_jsd | Fig 4 | 0.55238426 | 0.0007783857 | -0.55160587 | 0.55160587 | -99.859086 | 5/5 | artifacts/synthetic-looped-and/E2-stream.json · Supplementary_Material/Trained_Models/training_looped_and/metrics/attn_uniform_weights_jsd_tvd.csv |
| synthetic-looped-and | E2 | BASE_five_model_mean_tvd | Fig 4 | 0.058214857 | 0.042614481 | -0.015600377 | 0.015600377 | -26.79793 | 5/5 | artifacts/synthetic-looped-and/E2-stream.json · Supplementary_Material/Trained_Models/training_looped_and/metrics/attn_uniform_weights_jsd_tvd.csv |
| synthetic-looped-and | E2 | E2-FC_five_model_mean_jsd | Fig 4 | 0.55773766 | 0.00064218816 | -0.55709547 | 0.55709547 | -99.884858 | 5/5 | artifacts/synthetic-looped-and/E2-stream.json · Supplementary_Material/Trained_Models/training_looped_and/metrics/attn_uniform_weights_jsd_tvd.csv |
| synthetic-looped-and | E2 | E2-FC_five_model_mean_tvd | Fig 4 | 0.1944077 | 0.044711858 | -0.14969584 | 0.14969584 | -77.000984 | 5/5 | artifacts/synthetic-looped-and/E2-stream.json · Supplementary_Material/Trained_Models/training_looped_and/metrics/attn_uniform_weights_jsd_tvd.csv |
| synthetic-looped-and | E3 | occurrence_mean_tvd | Fig 7 | 0.037228634 | 0.035457544 | -0.0017710897 | 0.0017710897 | -4.757332 | 52825/164829 | artifacts/synthetic-looped-and/e3-attention-reference-audit.json · Supplementary_Material/Trained_Models/training_looped_and/metrics/attn_masking.csv |
| synthetic-looped-and | E3 | occurrence_median_tvd | Fig 7 | 8.926845e-05 | 0.0095204439 | 0.0094311754 | 0.0094311754 | 10564.959 | 52825/164829 | artifacts/synthetic-looped-and/e3-attention-reference-audit.json · Supplementary_Material/Trained_Models/training_looped_and/metrics/attn_masking.csv |
| synthetic-sequence | E1 | median_tau_b | Fig 3 | 0.67729621 | 0.36111111 | -0.3161851 | 0.3161851 | — | 11/3000 | artifacts/synthetic-sequence/E1-stream.json · Supplementary_Material/Trained_Models/training_sequence/metrics/attn_feature_importance.csv |
| synthetic-sequence | E2 | BASE_five_model_mean_jsd | Fig 4 | 0.12886738 | 0.0067964141 | -0.12207096 | 0.12207096 | -94.72604 | 5/5 | artifacts/synthetic-sequence/E2-stream.json · Supplementary_Material/Trained_Models/training_sequence/metrics/attn_uniform_weights_jsd_tvd.csv |
| synthetic-sequence | E2 | BASE_five_model_mean_tvd | Fig 4 | 2.087279e-05 | 1.9513893e-05 | -1.3588971e-06 | 1.3588971e-06 | -6.5103759 | 5/5 | artifacts/synthetic-sequence/E2-stream.json · Supplementary_Material/Trained_Models/training_sequence/metrics/attn_uniform_weights_jsd_tvd.csv |
| synthetic-sequence | E2 | E2-FC_five_model_mean_jsd | Fig 4 | 0.23756197 | 0.0047403402 | -0.23282163 | 0.23282163 | -98.004588 | 5/5 | artifacts/synthetic-sequence/E2-stream.json · Supplementary_Material/Trained_Models/training_sequence/metrics/attn_uniform_weights_jsd_tvd.csv |
| synthetic-sequence | E2 | E2-FC_five_model_mean_tvd | Fig 4 | 0.00018191566 | 3.5815242e-05 | -0.00014610042 | 0.00014610042 | -80.312172 | 5/5 | artifacts/synthetic-sequence/E2-stream.json · Supplementary_Material/Trained_Models/training_sequence/metrics/attn_uniform_weights_jsd_tvd.csv |
| synthetic-sequence | E3 | occurrence_mean_tvd | Fig 7 | 0.13511689 | 0.016089232 | -0.11902766 | 0.11902766 | -88.092361 | 61/19800 | artifacts/synthetic-sequence/e3-attention-reference-audit.json · Supplementary_Material/Trained_Models/training_sequence/metrics/attn_masking.csv |
| synthetic-sequence | E3 | occurrence_median_tvd | Fig 7 | 2.8930323e-05 | 6.4517623e-06 | -2.247856e-05 | 2.247856e-05 | -77.698962 | 61/19800 | artifacts/synthetic-sequence/e3-attention-reference-audit.json · Supplementary_Material/Trained_Models/training_sequence/metrics/attn_masking.csv |
| bpic12-wc-v1 | E2 | BASE_five_model_mean_jsd | Fig 4 | 0.23617258 | 0.19537038 | -0.04080221 | 0.04080221 | -17.276438 | 5/5 | artifacts/bpic12-wc-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_bpic12_wc_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| bpic12-wc-v1 | E2 | BASE_five_model_mean_tvd | Fig 4 | 0.056565542 | 0.045725292 | -0.01084025 | 0.01084025 | -19.164051 | 5/5 | artifacts/bpic12-wc-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_bpic12_wc_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| bpic12-wc-v1 | E2 | E2-FC_five_model_mean_jsd | Fig 4 | 0.4494512 | 0.23471934 | -0.21473186 | 0.21473186 | -47.776458 | 5/5 | artifacts/bpic12-wc-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_bpic12_wc_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |
| bpic12-wc-v1 | E2 | E2-FC_five_model_mean_tvd | Fig 4 | 0.11416185 | 0.052314541 | -0.061847305 | 0.061847305 | -54.17511 | 5/5 | artifacts/bpic12-wc-v1/E2-stream.json · Supplementary_Material/Trained_Models/training_bpic12_wc_GPU/metrics/attn_uniform_weights_jsd_tvd.csv |

<details><summary>Kiểm kê toàn bộ Table 3 và số liệu archive đối ứng, 216 hàng</summary>

| Log | Method | Metric | D mean | D SD | E mean | E SD | E valid/total | E member |
|---|---|---|---|---|---|---|---|---|
| BPIC12 | AE | Correctness | 0.65 | 0.15 | 0.65437401 | 0.15428643 | 374/400 | Supplementary_Material/Detailed_Results/bpic12/bpic12-attn_expl_xai/metrics/correctness_co01.csv |
| BPIC12 | BE | Correctness | 0.63 | 0.2 | 0.63290391 | 0.19815409 | 374/400 | Supplementary_Material/Detailed_Results/bpic12/bpic12-trace_backward_xai/metrics/correctness_co01.csv |
| BPIC12_O | AE | Correctness | 0.48 | 0.22 | 0.47625771 | 0.2221113 | 265/400 | Supplementary_Material/Detailed_Results/bpic12_o/bpic12_o-attn_expl_xai/metrics/correctness_co01.csv |
| BPIC12_O | BE | Correctness | 0.48 | 0.22 | 0.47502382 | 0.21911643 | 265/400 | Supplementary_Material/Detailed_Results/bpic12_o/bpic12_o-trace_backward_xai/metrics/correctness_co01.csv |
| BPIC12_W | AE | Correctness | 0.65 | 0.21 | 0.65395656 | 0.20576231 | 396/400 | Supplementary_Material/Detailed_Results/bpic12_w/bpic12_w-attn_expl_xai/metrics/correctness_co01.csv |
| BPIC12_W | BE | Correctness | 0.65 | 0.21 | 0.64973283 | 0.2081659 | 381/400 | Supplementary_Material/Detailed_Results/bpic12_w/bpic12_w-trace_backward_xai/metrics/correctness_co01.csv |
| BPIC12_WC | AE | Correctness | 0.56 | 0.18 | 0.56198184 | 0.18412402 | 399/400 | Supplementary_Material/Detailed_Results/bpic12_wc/bpic12_wc-attn_expl_xai/metrics/correctness_co01.csv |
| BPIC12_WC | BE | Correctness | 0.62 | 0.18 | 0.61816438 | 0.1839931 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_wc/bpic12_wc-trace_backward_xai/metrics/correctness_co01.csv |
| BPIC13_CP | AE | Correctness | 0.6 | 0.28 | 0.59557319 | 0.28303929 | 125/398 | Supplementary_Material/Detailed_Results/bpic13_closed_problems/bpic13_closed_problems-attn_expl_xai/metrics/correctness_co01.csv |
| BPIC13_CP | BE | Correctness | 0.75 | 0.18 | 0.75452136 | 0.1816017 | 397/398 | Supplementary_Material/Detailed_Results/bpic13_closed_problems/bpic13_closed_problems-trace_backward_xai/metrics/correctness_co01.csv |
| BPIC13-I | AE | Correctness | 0.57 | 0.25 | 0.56769819 | 0.25104868 | 31/400 | Supplementary_Material/Detailed_Results/bpic13_incidents/bpic13_incidents-attn_expl_xai/metrics/correctness_co01.csv |
| BPIC13-I | BE | Correctness | — | — | — | — | 0/400 | Supplementary_Material/Detailed_Results/bpic13_incidents/bpic13_incidents-trace_backward_xai/metrics/correctness_co01.csv |
| Sepsis | AE | Correctness | 0.59 | 0.17 | 0.59408232 | 0.16795184 | 397/399 | Supplementary_Material/Detailed_Results/sepsis/sepsis-attn_expl_xai/metrics/correctness_co01.csv |
| Sepsis | BE | Correctness | 0.86 | 0.13 | 0.86159897 | 0.12511894 | 399/399 | Supplementary_Material/Detailed_Results/sepsis/sepsis-trace_backward_xai/metrics/correctness_co01.csv |
| Helpdesk | AE | Correctness | 0.73 | 0.18 | 0.72882577 | 0.17830604 | 390/396 | Supplementary_Material/Detailed_Results/helpdesk/helpdesk-attn_expl_xai/metrics/correctness_co01.csv |
| Helpdesk | BE | Correctness | 0.91 | 0.08 | 0.90708843 | 0.08114564 | 396/396 | Supplementary_Material/Detailed_Results/helpdesk/helpdesk-trace_backward_xai/metrics/correctness_co01.csv |
| Complex Model | AE | Correctness | 0.51 | 0.12 | 0.51360638 | 0.1248243 | 378/400 | Supplementary_Material/Detailed_Results/14_complex_models/complex_model_001/complex_model_001-attn_expl_xai/metrics/correctness_co01.csv |
| Complex Model | BE | Correctness | 0.59 | 0.15 | 0.58639433 | 0.14532589 | 356/400 | Supplementary_Material/Detailed_Results/14_complex_models/complex_model_001/complex_model_001-trace_backward_xai/metrics/correctness_co01.csv |
| LDD | AE | Correctness | 0.68 | 0.22 | 0.6797653 | 0.22006162 | 16/16 | Supplementary_Material/Detailed_Results/long_dist_dep2/long_dist_dep2-attn_expl_xai/metrics/correctness_co01.csv |
| LDD | BE | Correctness | 0.68 | 0.21 | 0.6812487 | 0.20626955 | 16/16 | Supplementary_Material/Detailed_Results/long_dist_dep2/long_dist_dep2-trace_backward_xai/metrics/correctness_co01.csv |
| Looped And | AE | Correctness | 0.31 | 0.36 | 0.30866002 | 0.35578027 | 400/400 | Supplementary_Material/Detailed_Results/15_looped_AND/looped_and-attn_expl_xai/metrics/correctness_co01.csv |
| Looped And | BE | Correctness | — | — | — | — | 0/400 | Supplementary_Material/Detailed_Results/15_looped_AND/looped_and-trace_backward_xai/metrics/correctness_co01.csv |
| Sequence | AE | Correctness | 0.17 | 0.25 | 0.16904615 | 0.25034226 | 11/12 | Supplementary_Material/Detailed_Results/sequence/sequence-attn_expl_xai/metrics/correctness_co01.csv |
| Sequence | BE | Correctness | 0.32 | 0.18 | 0.31944453 | 0.18147886 | 11/12 | Supplementary_Material/Detailed_Results/sequence/sequence-trace_backward_xai/metrics/correctness_co01.csv |
| BPIC12 | AE | Completeness precision | 0.18 | 0.08 | 0.18266837 | 0.082299587 | 100/100 | Supplementary_Material/Detailed_Results/bpic12/bpic12-attn_expl_xai/metrics/completeness_co02_combined.csv |
| BPIC12 | BE | Completeness precision | 0.2 | 0.09 | 0.19747452 | 0.087029776 | 100/100 | Supplementary_Material/Detailed_Results/bpic12/bpic12-trace_backward_xai/metrics/completeness_co02_combined.csv |
| BPIC12_O | AE | Completeness precision | 0.25 | 0.07 | 0.24852612 | 0.067980239 | 100/100 | Supplementary_Material/Detailed_Results/bpic12_o/bpic12_o-attn_expl_xai/metrics/completeness_co02_combined.csv |
| BPIC12_O | BE | Completeness precision | 0.11 | 0.03 | 0.11105875 | 0.025288711 | 100/100 | Supplementary_Material/Detailed_Results/bpic12_o/bpic12_o-trace_backward_xai/metrics/completeness_co02_combined.csv |
| BPIC12_W | AE | Completeness precision | 0.49 | 0.14 | 0.48694458 | 0.13942356 | 100/100 | Supplementary_Material/Detailed_Results/bpic12_w/bpic12_w-attn_expl_xai/metrics/completeness_co02_combined.csv |
| BPIC12_W | BE | Completeness precision | 0.21 | 0.23 | 0.21273223 | 0.23397147 | 100/100 | Supplementary_Material/Detailed_Results/bpic12_w/bpic12_w-trace_backward_xai/metrics/completeness_co02_combined.csv |
| BPIC12_WC | AE | Completeness precision | 0.68 | 0.35 | 0.67906094 | 0.34738989 | 100/100 | Supplementary_Material/Detailed_Results/bpic12_wc/bpic12_wc-attn_expl_xai/metrics/completeness_co02_combined.csv |
| BPIC12_WC | BE | Completeness precision | 0.42 | 0.25 | 0.41820037 | 0.24654898 | 100/100 | Supplementary_Material/Detailed_Results/bpic12_wc/bpic12_wc-trace_backward_xai/metrics/completeness_co02_combined.csv |
| BPIC13_CP | AE | Completeness precision | 0.87 | 0.14 | 0.86837803 | 0.13566569 | 100/100 | Supplementary_Material/Detailed_Results/bpic13_closed_problems/bpic13_closed_problems-attn_expl_xai/metrics/completeness_co02_combined.csv |
| BPIC13_CP | BE | Completeness precision | 0.74 | 0.23 | 0.74042428 | 0.2263648 | 100/100 | Supplementary_Material/Detailed_Results/bpic13_closed_problems/bpic13_closed_problems-trace_backward_xai/metrics/completeness_co02_combined.csv |
| BPIC13-I | AE | Completeness precision | 0.82 | 0.06 | 0.81988447 | 0.055396036 | 100/100 | Supplementary_Material/Detailed_Results/bpic13_incidents/bpic13_incidents-attn_expl_xai/metrics/completeness_co02_combined.csv |
| BPIC13-I | BE | Completeness precision | 0.35 | 0.05 | 0.34513031 | 0.053117487 | 100/100 | Supplementary_Material/Detailed_Results/bpic13_incidents/bpic13_incidents-trace_backward_xai/metrics/completeness_co02_combined.csv |
| Sepsis | AE | Completeness precision | 0.54 | 0.13 | 0.54161354 | 0.12560123 | 100/100 | Supplementary_Material/Detailed_Results/sepsis/sepsis-attn_expl_xai/metrics/completeness_co02_combined.csv |
| Sepsis | BE | Completeness precision | 0.5 | 0.19 | 0.49829842 | 0.1866461 | 100/100 | Supplementary_Material/Detailed_Results/sepsis/sepsis-trace_backward_xai/metrics/completeness_co02_combined.csv |
| Helpdesk | AE | Completeness precision | 0.5 | 0.15 | 0.4979604 | 0.14648591 | 100/100 | Supplementary_Material/Detailed_Results/helpdesk/helpdesk-attn_expl_xai/metrics/completeness_co02_combined.csv |
| Helpdesk | BE | Completeness precision | 0.54 | 0.15 | 0.5427977 | 0.15296376 | 100/100 | Supplementary_Material/Detailed_Results/helpdesk/helpdesk-trace_backward_xai/metrics/completeness_co02_combined.csv |
| Complex Model | AE | Completeness precision | 0.3 | 0.07 | 0.30485047 | 0.067059949 | 100/100 | Supplementary_Material/Detailed_Results/14_complex_models/complex_model_001/complex_model_001-attn_expl_xai/metrics/completeness_co02_combined.csv |
| Complex Model | BE | Completeness precision | 0.19 | 0.03 | 0.18644738 | 0.027866362 | 100/100 | Supplementary_Material/Detailed_Results/14_complex_models/complex_model_001/complex_model_001-trace_backward_xai/metrics/completeness_co02_combined.csv |
| LDD | AE | Completeness precision | 0.1 | 0 | 0.10251323 | 0 | 4/4 | Supplementary_Material/Detailed_Results/long_dist_dep2/long_dist_dep2-attn_expl_xai/metrics/completeness_co02_combined.csv |
| LDD | BE | Completeness precision | 0.3 | 0 | 0.29931973 | 0 | 4/4 | Supplementary_Material/Detailed_Results/long_dist_dep2/long_dist_dep2-trace_backward_xai/metrics/completeness_co02_combined.csv |
| Looped And | AE | Completeness precision | 0.31 | 0.01 | 0.30813127 | 0.014356512 | 100/100 | Supplementary_Material/Detailed_Results/15_looped_AND/looped_and-attn_expl_xai/metrics/completeness_co02_combined.csv |
| Looped And | BE | Completeness precision | 0 | 0 | 0.0033664977 | 0.0024787847 | 100/100 | Supplementary_Material/Detailed_Results/15_looped_AND/looped_and-trace_backward_xai/metrics/completeness_co02_combined.csv |
| Sequence | AE | Completeness precision | 0.11 | — | 0.10556758 | — | 1/1 | Supplementary_Material/Detailed_Results/sequence/sequence-attn_expl_xai/metrics/completeness_co02_combined.csv |
| Sequence | BE | Completeness precision | 0.32 | — | 0.32297332 | — | 1/1 | Supplementary_Material/Detailed_Results/sequence/sequence-trace_backward_xai/metrics/completeness_co02_combined.csv |
| BPIC12 | AE | Completeness recall | 0.05 | 0 | 0.052266158 | 0.0012088082 | 100/100 | Supplementary_Material/Detailed_Results/bpic12/bpic12-attn_expl_xai/metrics/completeness_co02_combined.csv |
| BPIC12 | BE | Completeness recall | 0.04 | 0.01 | 0.04413904 | 0.0083023481 | 100/100 | Supplementary_Material/Detailed_Results/bpic12/bpic12-trace_backward_xai/metrics/completeness_co02_combined.csv |
| BPIC12_O | AE | Completeness recall | 0.2 | 0.01 | 0.1956791 | 0.013851253 | 100/100 | Supplementary_Material/Detailed_Results/bpic12_o/bpic12_o-attn_expl_xai/metrics/completeness_co02_combined.csv |
| BPIC12_O | BE | Completeness recall | 0.18 | 0.03 | 0.17801872 | 0.025316329 | 100/100 | Supplementary_Material/Detailed_Results/bpic12_o/bpic12_o-trace_backward_xai/metrics/completeness_co02_combined.csv |
| BPIC12_W | AE | Completeness recall | 0.22 | 0.03 | 0.21806917 | 0.032480275 | 100/100 | Supplementary_Material/Detailed_Results/bpic12_w/bpic12_w-attn_expl_xai/metrics/completeness_co02_combined.csv |
| BPIC12_W | BE | Completeness recall | 0.09 | 0.05 | 0.085773815 | 0.050231353 | 100/100 | Supplementary_Material/Detailed_Results/bpic12_w/bpic12_w-trace_backward_xai/metrics/completeness_co02_combined.csv |
| BPIC12_WC | AE | Completeness recall | 0.23 | 0.06 | 0.23056682 | 0.063991309 | 100/100 | Supplementary_Material/Detailed_Results/bpic12_wc/bpic12_wc-attn_expl_xai/metrics/completeness_co02_combined.csv |
| BPIC12_WC | BE | Completeness recall | 0.25 | 0.06 | 0.25287281 | 0.063487621 | 100/100 | Supplementary_Material/Detailed_Results/bpic12_wc/bpic12_wc-trace_backward_xai/metrics/completeness_co02_combined.csv |
| BPIC13_CP | AE | Completeness recall | 0.79 | 0.15 | 0.7924735 | 0.14750103 | 100/100 | Supplementary_Material/Detailed_Results/bpic13_closed_problems/bpic13_closed_problems-attn_expl_xai/metrics/completeness_co02_combined.csv |
| BPIC13_CP | BE | Completeness recall | 0.46 | 0.11 | 0.45769231 | 0.1148011 | 100/100 | Supplementary_Material/Detailed_Results/bpic13_closed_problems/bpic13_closed_problems-trace_backward_xai/metrics/completeness_co02_combined.csv |
| BPIC13-I | AE | Completeness recall | 0.77 | 0.08 | 0.7727023 | 0.079796986 | 100/100 | Supplementary_Material/Detailed_Results/bpic13_incidents/bpic13_incidents-attn_expl_xai/metrics/completeness_co02_combined.csv |
| BPIC13-I | BE | Completeness recall | 0.26 | 0.04 | 0.25822572 | 0.041717979 | 100/100 | Supplementary_Material/Detailed_Results/bpic13_incidents/bpic13_incidents-trace_backward_xai/metrics/completeness_co02_combined.csv |
| Sepsis | AE | Completeness recall | 0.11 | 0.01 | 0.10724126 | 0.010924934 | 100/100 | Supplementary_Material/Detailed_Results/sepsis/sepsis-attn_expl_xai/metrics/completeness_co02_combined.csv |
| Sepsis | BE | Completeness recall | 0.04 | 0.02 | 0.037238911 | 0.015999618 | 100/100 | Supplementary_Material/Detailed_Results/sepsis/sepsis-trace_backward_xai/metrics/completeness_co02_combined.csv |
| Helpdesk | AE | Completeness recall | 0.25 | 0.03 | 0.24783498 | 0.031073578 | 100/100 | Supplementary_Material/Detailed_Results/helpdesk/helpdesk-attn_expl_xai/metrics/completeness_co02_combined.csv |
| Helpdesk | BE | Completeness recall | 0.3 | 0.04 | 0.30187341 | 0.044635902 | 100/100 | Supplementary_Material/Detailed_Results/helpdesk/helpdesk-trace_backward_xai/metrics/completeness_co02_combined.csv |
| Complex Model | AE | Completeness recall | 0.1 | 0 | 0.096078055 | 0.0048914172 | 100/100 | Supplementary_Material/Detailed_Results/14_complex_models/complex_model_001/complex_model_001-attn_expl_xai/metrics/completeness_co02_combined.csv |
| Complex Model | BE | Completeness recall | 0.11 | 0.01 | 0.11103771 | 0.014368068 | 100/100 | Supplementary_Material/Detailed_Results/14_complex_models/complex_model_001/complex_model_001-trace_backward_xai/metrics/completeness_co02_combined.csv |
| LDD | AE | Completeness recall | 0.14 | 0 | 0.13888889 | 0 | 4/4 | Supplementary_Material/Detailed_Results/long_dist_dep2/long_dist_dep2-attn_expl_xai/metrics/completeness_co02_combined.csv |
| LDD | BE | Completeness recall | 0.17 | 0 | 0.16666667 | 0 | 4/4 | Supplementary_Material/Detailed_Results/long_dist_dep2/long_dist_dep2-trace_backward_xai/metrics/completeness_co02_combined.csv |
| Looped And | AE | Completeness recall | 0.25 | 0.01 | 0.24932775 | 0.0052051298 | 100/100 | Supplementary_Material/Detailed_Results/15_looped_AND/looped_and-attn_expl_xai/metrics/completeness_co02_combined.csv |
| Looped And | BE | Completeness recall | 0.05 | 0.02 | 0.050185915 | 0.020405837 | 100/100 | Supplementary_Material/Detailed_Results/15_looped_AND/looped_and-trace_backward_xai/metrics/completeness_co02_combined.csv |
| Sequence | AE | Completeness recall | 0.11 | — | 0.11111111 | — | 1/1 | Supplementary_Material/Detailed_Results/sequence/sequence-attn_expl_xai/metrics/completeness_co02_combined.csv |
| Sequence | BE | Completeness recall | 0.14 | — | 0.14102564 | — | 1/1 | Supplementary_Material/Detailed_Results/sequence/sequence-trace_backward_xai/metrics/completeness_co02_combined.csv |
| BPIC12 | AE | Completeness F1 | 0.07 | 0.01 | 0.068052726 | 0.0052991323 | 100/100 | Supplementary_Material/Detailed_Results/bpic12/bpic12-attn_expl_xai/metrics/completeness_co02_combined.csv |
| BPIC12 | BE | Completeness F1 | 0.06 | 0.01 | 0.056015649 | 0.011685082 | 100/100 | Supplementary_Material/Detailed_Results/bpic12/bpic12-trace_backward_xai/metrics/completeness_co02_combined.csv |
| BPIC12_O | AE | Completeness F1 | 0.21 | 0.02 | 0.20915656 | 0.023695494 | 100/100 | Supplementary_Material/Detailed_Results/bpic12_o/bpic12_o-attn_expl_xai/metrics/completeness_co02_combined.csv |
| BPIC12_O | BE | Completeness F1 | 0.13 | 0.02 | 0.1311548 | 0.021905964 | 100/100 | Supplementary_Material/Detailed_Results/bpic12_o/bpic12_o-trace_backward_xai/metrics/completeness_co02_combined.csv |
| BPIC12_W | AE | Completeness F1 | 0.27 | 0.04 | 0.27232898 | 0.041262287 | 100/100 | Supplementary_Material/Detailed_Results/bpic12_w/bpic12_w-attn_expl_xai/metrics/completeness_co02_combined.csv |
| BPIC12_W | BE | Completeness F1 | 0.1 | 0.08 | 0.095235383 | 0.078908212 | 100/100 | Supplementary_Material/Detailed_Results/bpic12_w/bpic12_w-trace_backward_xai/metrics/completeness_co02_combined.csv |
| BPIC12_WC | AE | Completeness F1 | 0.28 | 0.09 | 0.28209522 | 0.093106077 | 100/100 | Supplementary_Material/Detailed_Results/bpic12_wc/bpic12_wc-attn_expl_xai/metrics/completeness_co02_combined.csv |
| BPIC12_WC | BE | Completeness F1 | 0.29 | 0.1 | 0.29347895 | 0.096977448 | 100/100 | Supplementary_Material/Detailed_Results/bpic12_wc/bpic12_wc-trace_backward_xai/metrics/completeness_co02_combined.csv |
| BPIC13_CP | AE | Completeness F1 | 0.79 | 0.15 | 0.79454146 | 0.15077445 | 100/100 | Supplementary_Material/Detailed_Results/bpic13_closed_problems/bpic13_closed_problems-attn_expl_xai/metrics/completeness_co02_combined.csv |
| BPIC13_CP | BE | Completeness F1 | 0.5 | 0.14 | 0.50334845 | 0.13512029 | 100/100 | Supplementary_Material/Detailed_Results/bpic13_closed_problems/bpic13_closed_problems-trace_backward_xai/metrics/completeness_co02_combined.csv |
| BPIC13-I | AE | Completeness F1 | 0.77 | 0.08 | 0.77333799 | 0.077806123 | 100/100 | Supplementary_Material/Detailed_Results/bpic13_incidents/bpic13_incidents-attn_expl_xai/metrics/completeness_co02_combined.csv |
| BPIC13-I | BE | Completeness F1 | 0.29 | 0.04 | 0.29286351 | 0.037735343 | 100/100 | Supplementary_Material/Detailed_Results/bpic13_incidents/bpic13_incidents-trace_backward_xai/metrics/completeness_co02_combined.csv |
| Sepsis | AE | Completeness F1 | 0.15 | 0.02 | 0.14925626 | 0.021177254 | 100/100 | Supplementary_Material/Detailed_Results/sepsis/sepsis-attn_expl_xai/metrics/completeness_co02_combined.csv |
| Sepsis | BE | Completeness F1 | 0.04 | 0.02 | 0.044271568 | 0.023111475 | 100/100 | Supplementary_Material/Detailed_Results/sepsis/sepsis-trace_backward_xai/metrics/completeness_co02_combined.csv |
| Helpdesk | AE | Completeness F1 | 0.3 | 0.04 | 0.30438964 | 0.039792802 | 100/100 | Supplementary_Material/Detailed_Results/helpdesk/helpdesk-attn_expl_xai/metrics/completeness_co02_combined.csv |
| Helpdesk | BE | Completeness F1 | 0.36 | 0.05 | 0.36191926 | 0.051370247 | 100/100 | Supplementary_Material/Detailed_Results/helpdesk/helpdesk-trace_backward_xai/metrics/completeness_co02_combined.csv |
| Complex Model | AE | Completeness F1 | 0.12 | 0.01 | 0.12247081 | 0.0068287636 | 100/100 | Supplementary_Material/Detailed_Results/14_complex_models/complex_model_001/complex_model_001-attn_expl_xai/metrics/completeness_co02_combined.csv |
| Complex Model | BE | Completeness F1 | 0.1 | 0.01 | 0.10194343 | 0.013483317 | 100/100 | Supplementary_Material/Detailed_Results/14_complex_models/complex_model_001/complex_model_001-trace_backward_xai/metrics/completeness_co02_combined.csv |
| LDD | AE | Completeness F1 | 0.12 | 0 | 0.11784512 | 0 | 4/4 | Supplementary_Material/Detailed_Results/long_dist_dep2/long_dist_dep2-attn_expl_xai/metrics/completeness_co02_combined.csv |
| LDD | BE | Completeness F1 | 0.18 | 0 | 0.18225108 | 0 | 4/4 | Supplementary_Material/Detailed_Results/long_dist_dep2/long_dist_dep2-trace_backward_xai/metrics/completeness_co02_combined.csv |
| Looped And | AE | Completeness F1 | 0.27 | 0.01 | 0.26846302 | 0.0058715731 | 100/100 | Supplementary_Material/Detailed_Results/15_looped_AND/looped_and-attn_expl_xai/metrics/completeness_co02_combined.csv |
| Looped And | BE | Completeness F1 | 0.01 | 0 | 0.0062667804 | 0.0044851306 | 100/100 | Supplementary_Material/Detailed_Results/15_looped_AND/looped_and-trace_backward_xai/metrics/completeness_co02_combined.csv |
| Sequence | AE | Completeness F1 | 0.1 | — | 0.10281726 | — | 1/1 | Supplementary_Material/Detailed_Results/sequence/sequence-attn_expl_xai/metrics/completeness_co02_combined.csv |
| Sequence | BE | Completeness F1 | 0.15 | — | 0.14691697 | — | 1/1 | Supplementary_Material/Detailed_Results/sequence/sequence-trace_backward_xai/metrics/completeness_co02_combined.csv |
| BPIC12 | AE | Consistency | 0.19 | 0.06 | 0.19472651 | 0.056163235 | 56/56 | Supplementary_Material/Detailed_Results/bpic12/bpic12-attn_expl_xai/metrics/consistency_co03_complete.csv |
| BPIC12 | BE | Consistency | 0.46 | 0.07 | 0.46252584 | 0.068849548 | 56/56 | Supplementary_Material/Detailed_Results/bpic12/bpic12-trace_backward_xai/metrics/consistency_co03_complete.csv |
| BPIC12_O | AE | Consistency | 0.31 | 0.05 | 0.31332768 | 0.050742045 | 125/125 | Supplementary_Material/Detailed_Results/bpic12_o/bpic12_o-attn_expl_xai/metrics/consistency_co03_complete.csv |
| BPIC12_O | BE | Consistency | 0.65 | 0.07 | 0.65347435 | 0.071939328 | 125/125 | Supplementary_Material/Detailed_Results/bpic12_o/bpic12_o-trace_backward_xai/metrics/consistency_co03_complete.csv |
| BPIC12_W | AE | Consistency | 0.73 | 0.08 | 0.72550968 | 0.07755729 | 177/177 | Supplementary_Material/Detailed_Results/bpic12_w/bpic12_w-attn_expl_xai/metrics/consistency_co03_complete.csv |
| BPIC12_W | BE | Consistency | 0.66 | 0.13 | 0.65598037 | 0.12540566 | 177/177 | Supplementary_Material/Detailed_Results/bpic12_w/bpic12_w-trace_backward_xai/metrics/consistency_co03_complete.csv |
| BPIC12_WC | AE | Consistency | 0.54 | 0.07 | 0.54212134 | 0.074919983 | 272/272 | Supplementary_Material/Detailed_Results/bpic12_wc/bpic12_wc-attn_expl_xai/metrics/consistency_co03_complete.csv |
| BPIC12_WC | BE | Consistency | 0.39 | 0.08 | 0.38850767 | 0.075576936 | 272/272 | Supplementary_Material/Detailed_Results/bpic12_wc/bpic12_wc-trace_backward_xai/metrics/consistency_co03_complete.csv |
| BPIC13_CP | AE | Consistency | 0.99 | 0.09 | 0.98508206 | 0.093812467 | 336/336 | Supplementary_Material/Detailed_Results/bpic13_closed_problems/bpic13_closed_problems-attn_expl_xai/metrics/consistency_co03_complete.csv |
| BPIC13_CP | BE | Consistency | 0.59 | 0.18 | 0.59093473 | 0.17850037 | 336/336 | Supplementary_Material/Detailed_Results/bpic13_closed_problems/bpic13_closed_problems-trace_backward_xai/metrics/consistency_co03_complete.csv |
| BPIC13-I | AE | Consistency | 0.18 | 0.03 | 0.17793465 | 0.025466541 | 178/178 | Supplementary_Material/Detailed_Results/bpic13_incidents/bpic13_incidents-attn_expl_xai/metrics/consistency_co03_complete.csv |
| BPIC13-I | BE | Consistency | 0.01 | 0.02 | 0.014076976 | 0.017144328 | 178/178 | Supplementary_Material/Detailed_Results/bpic13_incidents/bpic13_incidents-trace_backward_xai/metrics/consistency_co03_complete.csv |
| Sepsis | AE | Consistency | 0.1 | 0.02 | 0.10093395 | 0.023965746 | 86/86 | Supplementary_Material/Detailed_Results/sepsis/sepsis-attn_expl_xai/metrics/consistency_co03_complete.csv |
| Sepsis | BE | Consistency | 0.13 | 0.03 | 0.12783502 | 0.025685369 | 86/86 | Supplementary_Material/Detailed_Results/sepsis/sepsis-trace_backward_xai/metrics/consistency_co03_complete.csv |
| Helpdesk | AE | Consistency | 0.09 | 0.05 | 0.090541721 | 0.052378672 | 201/201 | Supplementary_Material/Detailed_Results/helpdesk/helpdesk-attn_expl_xai/metrics/consistency_co03_complete.csv |
| Helpdesk | BE | Consistency | 0.11 | 0.09 | 0.1144444 | 0.08722029 | 201/201 | Supplementary_Material/Detailed_Results/helpdesk/helpdesk-trace_backward_xai/metrics/consistency_co03_complete.csv |
| Complex Model | AE | Consistency | 0.25 | 0.06 | 0.24812446 | 0.060568859 | 91/91 | Supplementary_Material/Detailed_Results/14_complex_models/complex_model_001/complex_model_001-attn_expl_xai/metrics/consistency_co03_complete.csv |
| Complex Model | BE | Consistency | 0.02 | 0.03 | 0.023011808 | 0.029044933 | 91/91 | Supplementary_Material/Detailed_Results/14_complex_models/complex_model_001/complex_model_001-trace_backward_xai/metrics/consistency_co03_complete.csv |
| LDD | AE | Consistency | 0.27 | 0.15 | 0.2654973 | 0.15216453 | 13/13 | Supplementary_Material/Detailed_Results/long_dist_dep2/long_dist_dep2-attn_expl_xai/metrics/consistency_co03_complete.csv |
| LDD | BE | Consistency | 0.45 | 0.22 | 0.4537879 | 0.21834034 | 13/13 | Supplementary_Material/Detailed_Results/long_dist_dep2/long_dist_dep2-trace_backward_xai/metrics/consistency_co03_complete.csv |
| Looped And | AE | Consistency | 0.01 | 0.01 | 0.010775054 | 0.014560067 | 41/41 | Supplementary_Material/Detailed_Results/15_looped_AND/looped_and-attn_expl_xai/metrics/consistency_co03_complete.csv |
| Looped And | BE | Consistency | 0.99 | 0.01 | 0.98922495 | 0.014560067 | 41/41 | Supplementary_Material/Detailed_Results/15_looped_AND/looped_and-trace_backward_xai/metrics/consistency_co03_complete.csv |
| Sequence | AE | Consistency | 0.42 | 0.21 | 0.4234789 | 0.21358703 | 12/12 | Supplementary_Material/Detailed_Results/sequence/sequence-attn_expl_xai/metrics/consistency_co03_complete.csv |
| Sequence | BE | Consistency | 0.53 | 0.2 | 0.52530018 | 0.19632617 | 12/12 | Supplementary_Material/Detailed_Results/sequence/sequence-trace_backward_xai/metrics/consistency_co03_complete.csv |
| BPIC12 | AE | Continuity | 0.93 | 0.05 | 0.93427623 | 0.047541019 | 400/400 | Supplementary_Material/Detailed_Results/bpic12/bpic12-attn_expl_xai/metrics/continuity_co04.csv |
| BPIC12 | BE | Continuity | 0.71 | 0.05 | 0.70752314 | 0.051459125 | 400/400 | Supplementary_Material/Detailed_Results/bpic12/bpic12-trace_backward_xai/metrics/continuity_co04.csv |
| BPIC12_O | AE | Continuity | 0.95 | 0.07 | 0.95334123 | 0.068418637 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_o/bpic12_o-attn_expl_xai/metrics/continuity_co04.csv |
| BPIC12_O | BE | Continuity | 0.95 | 0.07 | 0.95334123 | 0.068418637 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_o/bpic12_o-trace_backward_xai/metrics/continuity_co04.csv |
| BPIC12_W | AE | Continuity | 0.92 | 0.06 | 0.91601436 | 0.060621706 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_w/bpic12_w-attn_expl_xai/metrics/continuity_co04.csv |
| BPIC12_W | BE | Continuity | 0.81 | 0.13 | 0.81312855 | 0.13439566 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_w/bpic12_w-trace_backward_xai/metrics/continuity_co04.csv |
| BPIC12_WC | AE | Continuity | 0.89 | 0.05 | 0.88991614 | 0.049899405 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_wc/bpic12_wc-attn_expl_xai/metrics/continuity_co04.csv |
| BPIC12_WC | BE | Continuity | 0.9 | 0.06 | 0.89502487 | 0.060728717 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_wc/bpic12_wc-trace_backward_xai/metrics/continuity_co04.csv |
| BPIC13_CP | AE | Continuity | 0.98 | 0.1 | 0.97723687 | 0.10146751 | 400/400 | Supplementary_Material/Detailed_Results/bpic13_closed_problems/bpic13_closed_problems-attn_expl_xai/metrics/continuity_co04.csv |
| BPIC13_CP | BE | Continuity | 0.49 | 0.13 | 0.49350093 | 0.13018624 | 400/400 | Supplementary_Material/Detailed_Results/bpic13_closed_problems/bpic13_closed_problems-trace_backward_xai/metrics/continuity_co04.csv |
| BPIC13-I | AE | Continuity | 0.99 | 0.02 | 0.99297816 | 0.01750257 | 400/400 | Supplementary_Material/Detailed_Results/bpic13_incidents/bpic13_incidents-attn_expl_xai/metrics/continuity_co04.csv |
| BPIC13-I | BE | Continuity | 0.19 | 0.24 | 0.19455151 | 0.2407398 | 400/400 | Supplementary_Material/Detailed_Results/bpic13_incidents/bpic13_incidents-trace_backward_xai/metrics/continuity_co04.csv |
| Sepsis | AE | Continuity | 0.92 | 0.13 | 0.9220648 | 0.13003947 | 400/400 | Supplementary_Material/Detailed_Results/sepsis/sepsis-attn_expl_xai/metrics/continuity_co04.csv |
| Sepsis | BE | Continuity | 0.57 | 0.09 | 0.56596053 | 0.091560367 | 400/400 | Supplementary_Material/Detailed_Results/sepsis/sepsis-trace_backward_xai/metrics/continuity_co04.csv |
| Helpdesk | AE | Continuity | 0.85 | 0.19 | 0.85267109 | 0.19448587 | 400/400 | Supplementary_Material/Detailed_Results/helpdesk/helpdesk-attn_expl_xai/metrics/continuity_co04.csv |
| Helpdesk | BE | Continuity | 0.73 | 0.15 | 0.72887811 | 0.14648201 | 400/400 | Supplementary_Material/Detailed_Results/helpdesk/helpdesk-trace_backward_xai/metrics/continuity_co04.csv |
| Complex Model | AE | Continuity | 0.88 | 0.21 | 0.87505527 | 0.21095066 | 400/400 | Supplementary_Material/Detailed_Results/14_complex_models/complex_model_001/complex_model_001-attn_expl_xai/metrics/continuity_co04.csv |
| Complex Model | BE | Continuity | 0.72 | 0.19 | 0.71829147 | 0.19169793 | 400/400 | Supplementary_Material/Detailed_Results/14_complex_models/complex_model_001/complex_model_001-trace_backward_xai/metrics/continuity_co04.csv |
| LDD | AE | Continuity | 0.57 | 0.31 | 0.57001208 | 0.31199388 | 16/16 | Supplementary_Material/Detailed_Results/long_dist_dep2/long_dist_dep2-attn_expl_xai/metrics/continuity_co04.csv |
| LDD | BE | Continuity | 0.57 | 0.32 | 0.57447636 | 0.31613363 | 16/16 | Supplementary_Material/Detailed_Results/long_dist_dep2/long_dist_dep2-trace_backward_xai/metrics/continuity_co04.csv |
| Looped And | AE | Continuity | 0.93 | 0.24 | 0.92830142 | 0.23648004 | 400/400 | Supplementary_Material/Detailed_Results/15_looped_AND/looped_and-attn_expl_xai/metrics/continuity_co04.csv |
| Looped And | BE | Continuity | 0.93 | 0.24 | 0.92830142 | 0.23648004 | 400/400 | Supplementary_Material/Detailed_Results/15_looped_AND/looped_and-trace_backward_xai/metrics/continuity_co04.csv |
| Sequence | AE | Continuity | 0.78 | 0.25 | 0.78207173 | 0.2503563 | 12/12 | Supplementary_Material/Detailed_Results/sequence/sequence-attn_expl_xai/metrics/continuity_co04.csv |
| Sequence | BE | Continuity | 0.78 | 0.25 | 0.77845824 | 0.25157879 | 12/12 | Supplementary_Material/Detailed_Results/sequence/sequence-trace_backward_xai/metrics/continuity_co04.csv |
| BPIC12 | AE | Contrastivity | 0.26 | 0.25 | 0.260497 | 0.24621493 | 400/400 | Supplementary_Material/Detailed_Results/bpic12/bpic12-attn_expl_xai/metrics/contrastivity_co05.csv |
| BPIC12 | BE | Contrastivity | 0.45 | 0.33 | 0.44510667 | 0.32699266 | 400/400 | Supplementary_Material/Detailed_Results/bpic12/bpic12-trace_backward_xai/metrics/contrastivity_co05.csv |
| BPIC12_O | AE | Contrastivity | 0.07 | 0.18 | 0.074098417 | 0.17684767 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_o/bpic12_o-attn_expl_xai/metrics/contrastivity_co05.csv |
| BPIC12_O | BE | Contrastivity | 0.07 | 0.18 | 0.074098417 | 0.17684767 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_o/bpic12_o-trace_backward_xai/metrics/contrastivity_co05.csv |
| BPIC12_W | AE | Contrastivity | 0.16 | 0.26 | 0.15924498 | 0.25910288 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_w/bpic12_w-attn_expl_xai/metrics/contrastivity_co05.csv |
| BPIC12_W | BE | Contrastivity | 0.19 | 0.3 | 0.18652182 | 0.29909877 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_w/bpic12_w-trace_backward_xai/metrics/contrastivity_co05.csv |
| BPIC12_WC | AE | Contrastivity | 0.02 | 0.09 | 0.020547244 | 0.094048767 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_wc/bpic12_wc-attn_expl_xai/metrics/contrastivity_co05.csv |
| BPIC12_WC | BE | Contrastivity | 0.03 | 0.13 | 0.030231333 | 0.12824329 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_wc/bpic12_wc-trace_backward_xai/metrics/contrastivity_co05.csv |
| BPIC13_CP | AE | Contrastivity | 0.05 | 0.19 | 0.050079033 | 0.18638299 | 400/400 | Supplementary_Material/Detailed_Results/bpic13_closed_problems/bpic13_closed_problems-attn_expl_xai/metrics/contrastivity_co05.csv |
| BPIC13_CP | BE | Contrastivity | 0.05 | 0.2 | 0.0528708 | 0.19765281 | 400/400 | Supplementary_Material/Detailed_Results/bpic13_closed_problems/bpic13_closed_problems-trace_backward_xai/metrics/contrastivity_co05.csv |
| BPIC13-I | AE | Contrastivity | 0.03 | 0.12 | 0.026192823 | 0.12374468 | 400/400 | Supplementary_Material/Detailed_Results/bpic13_incidents/bpic13_incidents-attn_expl_xai/metrics/contrastivity_co05.csv |
| BPIC13-I | BE | Contrastivity | 0.04 | 0.18 | 0.039788477 | 0.18120392 | 400/400 | Supplementary_Material/Detailed_Results/bpic13_incidents/bpic13_incidents-trace_backward_xai/metrics/contrastivity_co05.csv |
| Sepsis | AE | Contrastivity | 0.13 | 0.27 | 0.13365279 | 0.26800037 | 400/400 | Supplementary_Material/Detailed_Results/sepsis/sepsis-attn_expl_xai/metrics/contrastivity_co05.csv |
| Sepsis | BE | Contrastivity | 0.17 | 0.33 | 0.171609 | 0.33078555 | 400/400 | Supplementary_Material/Detailed_Results/sepsis/sepsis-trace_backward_xai/metrics/contrastivity_co05.csv |
| Helpdesk | AE | Contrastivity | 0.2 | 0.3 | 0.20286123 | 0.30358998 | 400/400 | Supplementary_Material/Detailed_Results/helpdesk/helpdesk-attn_expl_xai/metrics/contrastivity_co05.csv |
| Helpdesk | BE | Contrastivity | 0.08 | 0.22 | 0.077946466 | 0.21737163 | 400/400 | Supplementary_Material/Detailed_Results/helpdesk/helpdesk-trace_backward_xai/metrics/contrastivity_co05.csv |
| Complex Model | AE | Contrastivity | 0.3 | 0.15 | 0.3027393 | 0.15132965 | 400/400 | Supplementary_Material/Detailed_Results/14_complex_models/complex_model_001/complex_model_001-attn_expl_xai/metrics/contrastivity_co05.csv |
| Complex Model | BE | Contrastivity | 0.58 | 0.17 | 0.58124819 | 0.17371462 | 400/400 | Supplementary_Material/Detailed_Results/14_complex_models/complex_model_001/complex_model_001-trace_backward_xai/metrics/contrastivity_co05.csv |
| LDD | AE | Contrastivity | 0.42 | 0.31 | 0.41503642 | 0.31452251 | 16/16 | Supplementary_Material/Detailed_Results/long_dist_dep2/long_dist_dep2-attn_expl_xai/metrics/contrastivity_co05.csv |
| LDD | BE | Contrastivity | 0.42 | 0.31 | 0.42346896 | 0.31001963 | 16/16 | Supplementary_Material/Detailed_Results/long_dist_dep2/long_dist_dep2-trace_backward_xai/metrics/contrastivity_co05.csv |
| Looped And | AE | Contrastivity | 0.4 | 0.21 | 0.40149734 | 0.20880199 | 400/400 | Supplementary_Material/Detailed_Results/15_looped_AND/looped_and-attn_expl_xai/metrics/contrastivity_co05.csv |
| Looped And | BE | Contrastivity | 0.4 | 0.21 | 0.40029312 | 0.20902685 | 400/400 | Supplementary_Material/Detailed_Results/15_looped_AND/looped_and-trace_backward_xai/metrics/contrastivity_co05.csv |
| Sequence | AE | Contrastivity | 0.32 | 0.34 | 0.32463709 | 0.34054494 | 12/12 | Supplementary_Material/Detailed_Results/sequence/sequence-attn_expl_xai/metrics/contrastivity_co05.csv |
| Sequence | BE | Contrastivity | 0.33 | 0.3 | 0.32944108 | 0.30104461 | 12/12 | Supplementary_Material/Detailed_Results/sequence/sequence-trace_backward_xai/metrics/contrastivity_co05.csv |
| BPIC12 | AE | Compactness số luật | 6.32 | 1.11 | 6.32 | 1.1116156 | 400/400 | Supplementary_Material/Detailed_Results/bpic12/bpic12-attn_expl_xai/metrics/compactness_co07.csv |
| BPIC12 | BE | Compactness số luật | 13.04 | 2.03 | 13.0375 | 2.0288876 | 400/400 | Supplementary_Material/Detailed_Results/bpic12/bpic12-trace_backward_xai/metrics/compactness_co07.csv |
| BPIC12_O | AE | Compactness số luật | 4.61 | 0.55 | 4.6075 | 0.55154715 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_o/bpic12_o-attn_expl_xai/metrics/compactness_co07.csv |
| BPIC12_O | BE | Compactness số luật | 4.61 | 0.55 | 4.6075 | 0.55154715 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_o/bpic12_o-trace_backward_xai/metrics/compactness_co07.csv |
| BPIC12_W | AE | Compactness số luật | 4.05 | 0.78 | 4.0525 | 0.78183881 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_w/bpic12_w-attn_expl_xai/metrics/compactness_co07.csv |
| BPIC12_W | BE | Compactness số luật | 3.28 | 0.57 | 3.2825 | 0.56877281 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_w/bpic12_w-trace_backward_xai/metrics/compactness_co07.csv |
| BPIC12_WC | AE | Compactness số luật | 3.19 | 0.6 | 3.195 | 0.60239705 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_wc/bpic12_wc-attn_expl_xai/metrics/compactness_co07.csv |
| BPIC12_WC | BE | Compactness số luật | 3.97 | 0.89 | 3.9675 | 0.89355461 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_wc/bpic12_wc-trace_backward_xai/metrics/compactness_co07.csv |
| BPIC13_CP | AE | Compactness số luật | 1.88 | 0.34 | 1.8825 | 0.33760731 | 400/400 | Supplementary_Material/Detailed_Results/bpic13_closed_problems/bpic13_closed_problems-attn_expl_xai/metrics/compactness_co07.csv |
| BPIC13_CP | BE | Compactness số luật | 2.16 | 0.53 | 2.1625 | 0.53084673 | 400/400 | Supplementary_Material/Detailed_Results/bpic13_closed_problems/bpic13_closed_problems-trace_backward_xai/metrics/compactness_co07.csv |
| BPIC13-I | AE | Compactness số luật | 1.99 | 0.09 | 1.9925 | 0.086385219 | 400/400 | Supplementary_Material/Detailed_Results/bpic13_incidents/bpic13_incidents-attn_expl_xai/metrics/compactness_co07.csv |
| BPIC13-I | BE | Compactness số luật | 1.38 | 0.49 | 1.38 | 0.49112423 | 400/400 | Supplementary_Material/Detailed_Results/bpic13_incidents/bpic13_incidents-trace_backward_xai/metrics/compactness_co07.csv |
| Sepsis | AE | Compactness số luật | 4.55 | 0.85 | 4.5525 | 0.85091356 | 400/400 | Supplementary_Material/Detailed_Results/sepsis/sepsis-attn_expl_xai/metrics/compactness_co07.csv |
| Sepsis | BE | Compactness số luật | 7.72 | 1.42 | 7.725 | 1.4175325 | 400/400 | Supplementary_Material/Detailed_Results/sepsis/sepsis-trace_backward_xai/metrics/compactness_co07.csv |
| Helpdesk | AE | Compactness số luật | 2.45 | 0.79 | 2.4475 | 0.78663252 | 400/400 | Supplementary_Material/Detailed_Results/helpdesk/helpdesk-attn_expl_xai/metrics/compactness_co07.csv |
| Helpdesk | BE | Compactness số luật | 3.32 | 0.94 | 3.3175 | 0.94016143 | 400/400 | Supplementary_Material/Detailed_Results/helpdesk/helpdesk-trace_backward_xai/metrics/compactness_co07.csv |
| Complex Model | AE | Compactness số luật | 4.19 | 0.98 | 4.1875 | 0.98221975 | 400/400 | Supplementary_Material/Detailed_Results/14_complex_models/complex_model_001/complex_model_001-attn_expl_xai/metrics/compactness_co07.csv |
| Complex Model | BE | Compactness số luật | 7.47 | 2.03 | 7.47 | 2.0296301 | 400/400 | Supplementary_Material/Detailed_Results/14_complex_models/complex_model_001/complex_model_001-trace_backward_xai/metrics/compactness_co07.csv |
| LDD | AE | Compactness số luật | 3.75 | 1.91 | 3.75 | 1.9148542 | 16/16 | Supplementary_Material/Detailed_Results/long_dist_dep2/long_dist_dep2-attn_expl_xai/metrics/compactness_co07.csv |
| LDD | BE | Compactness số luật | 3.94 | 2.17 | 3.9375 | 2.1746647 | 16/16 | Supplementary_Material/Detailed_Results/long_dist_dep2/long_dist_dep2-trace_backward_xai/metrics/compactness_co07.csv |
| Looped And | AE | Compactness số luật | 2 | 0 | 2 | 0 | 400/400 | Supplementary_Material/Detailed_Results/15_looped_AND/looped_and-attn_expl_xai/metrics/compactness_co07.csv |
| Looped And | BE | Compactness số luật | 4 | 0 | 4 | 0 | 400/400 | Supplementary_Material/Detailed_Results/15_looped_AND/looped_and-trace_backward_xai/metrics/compactness_co07.csv |
| Sequence | AE | Compactness số luật | 5.08 | 2.02 | 5.0833333 | 2.0207259 | 12/12 | Supplementary_Material/Detailed_Results/sequence/sequence-attn_expl_xai/metrics/compactness_co07.csv |
| Sequence | BE | Compactness số luật | 7.08 | 3.34 | 7.0833333 | 3.3427896 | 12/12 | Supplementary_Material/Detailed_Results/sequence/sequence-trace_backward_xai/metrics/compactness_co07.csv |
| BPIC12 | AE | Compactness độ dài | 4.12 | 0.77 | 4.1207857 | 0.76801911 | 400/400 | Supplementary_Material/Detailed_Results/bpic12/bpic12-attn_expl_xai/metrics/compactness_co07.csv |
| BPIC12 | BE | Compactness độ dài | 1.66 | 0.2 | 1.6623789 | 0.20131429 | 400/400 | Supplementary_Material/Detailed_Results/bpic12/bpic12-trace_backward_xai/metrics/compactness_co07.csv |
| BPIC12_O | AE | Compactness độ dài | 2.21 | 0.09 | 2.207875 | 0.09342674 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_o/bpic12_o-attn_expl_xai/metrics/compactness_co07.csv |
| BPIC12_O | BE | Compactness độ dài | 2.56 | 0.06 | 2.5625833 | 0.057396341 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_o/bpic12_o-trace_backward_xai/metrics/compactness_co07.csv |
| BPIC12_W | AE | Compactness độ dài | 1.86 | 0.25 | 1.8632917 | 0.25270549 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_w/bpic12_w-attn_expl_xai/metrics/compactness_co07.csv |
| BPIC12_W | BE | Compactness độ dài | 0.9 | 0.14 | 0.89629167 | 0.13779906 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_w/bpic12_w-trace_backward_xai/metrics/compactness_co07.csv |
| BPIC12_WC | AE | Compactness độ dài | 1.89 | 0.15 | 1.89325 | 0.14953374 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_wc/bpic12_wc-attn_expl_xai/metrics/compactness_co07.csv |
| BPIC12_WC | BE | Compactness độ dài | 1.48 | 0.09 | 1.477125 | 0.089366008 | 400/400 | Supplementary_Material/Detailed_Results/bpic12_wc/bpic12_wc-trace_backward_xai/metrics/compactness_co07.csv |
| BPIC13_CP | AE | Compactness độ dài | 2.09 | 0.35 | 2.0925 | 0.34531414 | 400/400 | Supplementary_Material/Detailed_Results/bpic13_closed_problems/bpic13_closed_problems-attn_expl_xai/metrics/compactness_co07.csv |
| BPIC13_CP | BE | Compactness độ dài | 0.6 | 0.2 | 0.59958333 | 0.19923928 | 400/400 | Supplementary_Material/Detailed_Results/bpic13_closed_problems/bpic13_closed_problems-trace_backward_xai/metrics/compactness_co07.csv |
| BPIC13-I | AE | Compactness độ dài | 2 | 0.09 | 2.0025 | 0.08667486 | 400/400 | Supplementary_Material/Detailed_Results/bpic13_incidents/bpic13_incidents-attn_expl_xai/metrics/compactness_co07.csv |
| BPIC13-I | BE | Compactness độ dài | 0.19 | 0.24 | 0.19125 | 0.24330316 | 400/400 | Supplementary_Material/Detailed_Results/bpic13_incidents/bpic13_incidents-trace_backward_xai/metrics/compactness_co07.csv |
| Sepsis | AE | Compactness độ dài | 2.76 | 0.42 | 2.7609167 | 0.42423321 | 400/400 | Supplementary_Material/Detailed_Results/sepsis/sepsis-attn_expl_xai/metrics/compactness_co07.csv |
| Sepsis | BE | Compactness độ dài | 0.83 | 0.16 | 0.82687698 | 0.15982893 | 400/400 | Supplementary_Material/Detailed_Results/sepsis/sepsis-trace_backward_xai/metrics/compactness_co07.csv |
| Helpdesk | AE | Compactness độ dài | 2.55 | 0.62 | 2.5454167 | 0.62393309 | 400/400 | Supplementary_Material/Detailed_Results/helpdesk/helpdesk-attn_expl_xai/metrics/compactness_co07.csv |
| Helpdesk | BE | Compactness độ dài | 1.99 | 0.39 | 1.9915833 | 0.39427114 | 400/400 | Supplementary_Material/Detailed_Results/helpdesk/helpdesk-trace_backward_xai/metrics/compactness_co07.csv |
| Complex Model | AE | Compactness độ dài | 3.6 | 0.64 | 3.5970833 | 0.64185651 | 400/400 | Supplementary_Material/Detailed_Results/14_complex_models/complex_model_001/complex_model_001-attn_expl_xai/metrics/compactness_co07.csv |
| Complex Model | BE | Compactness độ dài | 2.01 | 0.53 | 2.0144006 | 0.52973914 | 400/400 | Supplementary_Material/Detailed_Results/14_complex_models/complex_model_001/complex_model_001-trace_backward_xai/metrics/compactness_co07.csv |
| LDD | AE | Compactness độ dài | 1.89 | 1.13 | 1.8875 | 1.1289376 | 16/16 | Supplementary_Material/Detailed_Results/long_dist_dep2/long_dist_dep2-attn_expl_xai/metrics/compactness_co07.csv |
| LDD | BE | Compactness độ dài | 2.76 | 0.74 | 2.7565476 | 0.74057826 | 16/16 | Supplementary_Material/Detailed_Results/long_dist_dep2/long_dist_dep2-trace_backward_xai/metrics/compactness_co07.csv |
| Looped And | AE | Compactness độ dài | 4 | 0 | 4 | 0 | 400/400 | Supplementary_Material/Detailed_Results/15_looped_AND/looped_and-attn_expl_xai/metrics/compactness_co07.csv |
| Looped And | BE | Compactness độ dài | 1 | 0 | 1 | 0 | 400/400 | Supplementary_Material/Detailed_Results/15_looped_AND/looped_and-trace_backward_xai/metrics/compactness_co07.csv |
| Sequence | AE | Compactness độ dài | 2.06 | 0.4 | 2.0615079 | 0.3990504 | 12/12 | Supplementary_Material/Detailed_Results/sequence/sequence-attn_expl_xai/metrics/compactness_co07.csv |
| Sequence | BE | Compactness độ dài | 1.96 | 0.65 | 1.9551557 | 0.65279607 | 12/12 | Supplementary_Material/Detailed_Results/sequence/sequence-trace_backward_xai/metrics/compactness_co07.csv |

</details>
