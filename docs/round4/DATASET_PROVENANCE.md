# Dataset provenance

## Sepsis version 1 · acquired 2026-11-17

Felix Mannhardt (2016), Sepsis Cases – Event Log, 4TU.ResearchData, version 1. The official metadata API resolves the paper's DOI and supplies a directly downloadable XES file and publisher checksum. [Dataset DOI](https://doi.org/10.4121/uuid:915d2bfb-7e84-49ad-a286-dc35f063a460) · [Official API record](https://data.4tu.nl/v2/articles/33632f3c-5c48-40cf-8d8f-2db57f5a6ce7)

Acquisition evidence is retained locally under data/raw/sepsis-v1/ as metadata.json, acquisition.json, readme.txt, DATA.xml, original XES.GZ and General_terms_of_use.pdf. The publisher MD5 b5671166ac71eb20680d3c74616c43d2 matched the downloaded archive. SHA-256 is 709c52340306415952811b9b9c5dc6bcc8f8d47d583eba39df9a538459dc543a. Input remains activity-only using concept:name and time:timestamp with source ordinal tie-breaking. No event filters or lifecycle composition are applied.

The independent loader counted 1,050 cases, 15,214 events, 16 activities and maximum trace length 185, matching the paper inventory. There were no empty or duplicate trace identifiers. These checks establish a verified public dataset for independent runs. Exact historical run/split identity remains unavailable. No BPMN ground truth is claimed for Sepsis.

The dataset's August2016 terms permit noncommercial reuse with source acknowledgement and impose citation/publication-notification and attribution conditions for publication or redistribution. The local work is academic research. Cite the creator and DOI in results using this log, and carry the publication/redistribution requirements into the final report handoff. This turn performs no external publication or notification. The public README describes anonymized attributes and shifted timestamps, with within-case timing retained. [Applicable terms](https://doi.org/10.4121/resource:terms_of_use)

Preparation config is configs/datasets/sepsis.json. Split seed42 is an independent design choice, with actual IDs and hash emitted by prepare. Dataset outputs and model results remain local under ignored data/ and artifacts/.

## BPIC12 and BPIC13 · acquired 2026-11-17

Three further official original archives and their DATA.xml files were downloaded without transforming them. Each has an acquisition.json recording UTC retrieval, official API URL, version1, file size, publisher MD5 and computed SHA-256. The metadata for all three points to the same 4TU General Terms of Use already reviewed above. Files remain local; no event-level uploads or redistribution occurred.

| Official dataset | Original SHA-256 | API and DOI |
|---|---|---|
| BPI Challenge 2012 | 5cd9cc16b9bcb20bd4aae45666a5d87479ddbf47e6371618b6ad217174cecdf3 | [API](https://data.4tu.nl/v2/articles/12689204), [DOI](https://doi.org/10.4121/uuid:3926db30-f712-4394-aebc-75976070e91f) |
| BPI Challenge 2013, closed problems | 6d2a6c64666621dd258765cabe38c013b5a8c59cc42b55d4191ddf57b6da072f | [API](https://data.4tu.nl/v2/articles/1987a2a6-9f5b-4b14-8d26-ab7056b17929), [DOI](https://doi.org/10.4121/uuid:c2c3b154-ab26-4b31-a0e8-8f2350ddac11) |
| BPI Challenge 2013, incidents | 6ec2136c607648608655802486df97a866f351668751b7ecbca51e1f8715d522 | [API](https://data.4tu.nl/v2/articles/0fc5c579-e544-4fab-9143-fab1f5192432), [DOI](https://doi.org/10.4121/uuid:500573e6-accc-4b0c-9576-aa5468b10cee) |

The older BPIC12 repository URL returned404; its DOI resolves to numeric article12689204. The prior BPIC13 DOI a7ce5c55-03a7-4583-b855-98b86e1a2b07 identifies the collection, not an incidents file. The official [collection API](https://data.4tu.nl/v2/collections/5065448/articles) distinguishes closed problems, open problems and incidents. Only the two required files were acquired.

Independent streaming XML counts, retained in each raw directory's count-audit.json:

| Log/config | Cases | Events | Activity labels | Transformation |
|---|---:|---:|---:|---|
| bpic12.json | 13,087 | 262,200 | 24 | concept:name only |
| bpic12-o.json | 5,015 | 31,244 | 7 | O_ prefix filter; remove empty cases |
| bpic12-w.json | 9,658 | 170,107 | 7 | W_ prefix filter; remove empty cases |
| bpic12-wc.json | 9,658 | 72,413 | 6 | W_ then literal lifecycle COMPLETE; remove empty cases |
| bpic13-cp.json | 1,487 | 6,660 | 4 | concept:name only |
| bpic13-i.json | 7,554 | 65,533 | 4 | concept:name only |

These match the respective locked Table 1 inventory. BPIC13 lifecycle composition would produce 7 and 13 labels. BPIC12 lifecycle composition would produce 36 labels. The activity-only classifier preserves the paper's counts. The WC config uses uppercase COMPLETE as stored in the archive. BPIC12_O/W/WC count verification used a separate streaming counter. The project CLI has prepared both BPIC13 logs and trained an independent baseline for each.

The project CLI also prepared BPIC12_O from the verified archive. The audit matches the independent count, including 8,072 cases removed by the `O_` filter. Source ordinals still refer to the unfiltered XES. Baseline training and full test prediction completed on this preparation.

The CLI preparation for BPIC12_WC kept 170,107 events out of 262,200 after the `W_` filter and 72,413 after the `COMPLETE` filter. The first filter removed 3,429 cases. The second removed none. All preserved records match both predicates. Baseline training and prediction completed for all 18,472 test prefixes.

## Helpdesk · acquired 2026-11-17

The official 4TU v1 record for Massimiliano Polato's Helpdesk provides finale.csv and a README identifying 4,580 cases, 21,348 events and 14 activities. The files passed the publisher's MD5 and byte-count checks. The CSV SHA-256 is 31024fa6da0a35578643d50f2bea6e90d5ce97628b64851e271b521f005eef1c. The record declares the same 4TU General Terms of Use as the other acquired datasets. The raw files and retrieval receipt remain under ignored data/raw/helpdesk-4tu-v1/. [Dataset DOI](https://doi.org/10.4121/uuid:0c60edf1-6f83-4e75-9367-4c63b3e9d5bb) · [Official metadata](https://data.4tu.nl/v2/articles/12675977)

The CSV has timezone-free timestamps and two headers named Variant. The project uses an independently verified XES encoding from the PM4Py fixture at commit 9a9237d850ff25dcffd884026a7f787049c76ed5. Its bytes hash to fb133a5b70711d523bdbb95279d6bd86d975661ad3d23d23129bfe5121cea453. Comparison to the archived CSV was positional, with source ordinal breaking timestamp ties. It found the same 4,580 case IDs, the same ordered activity sequence in every case, and 226 distinct sequences on both sides. All 21,348 event times matched the CSV clock values when the XES timestamps were converted to UTC. This establishes event-level agreement for the fields used by the model and avoids assigning a timezone to the CSV. Additional attributes are outside this equivalence claim. The pinned XES and comparison receipt remain under ignored data/raw/helpdesk-pm4py/. [Pinned XES fixture](https://github.com/pm4py/pm4py-core/blob/9a9237d850ff25dcffd884026a7f787049c76ed5/tests/input_data/helpdesk.xes.gz)

The verified configs/datasets/helpdesk.json selects the event-equivalent XES encoding. CLI preparation reproduced the expected counts without filtering. Training uses the independent split and retains raw data locally. The paper's precise historical XES bytes, split and checkpoint are still unverified.

## Author supplementary archive · acquired 2026-11-17

The pinned author README links to a Google Drive folder containing `Supplementary_Material.zip`. The downloaded ZIP is 148,506,909 bytes and has SHA-256 `b1b88b2d7797fbe3369dccc5c4fe8d9a96af5d52293954279d4bab2f0bcc169e`. The inventory contains 4,512 entries, including 253 XES and 25 BPMN files, saved models and result files. The ZIP and extracted inputs remain local under ignored `data/raw/author-supplement/`. Acquisition establishes access to the author-linked material for this audit. Redistribution rights for the bundle have not been established. [Pinned README](https://github.com/mkaep/transformer-explainability/blob/494b315a555e713bdd61f0edd7d033c31d5850bf/README.md#L10) · [Author archive](https://drive.google.com/file/d/1p-mbznaXoYI0ofqlzKGPzJ1FVcAX0Pg4/view)

For each Table 1 synthetic log, the `preprocessed.xes`, `train.xes`, `test.xes`, experiment JSON and reference BPMN were extracted by exact member name. The root for the following paths is `Supplementary_Material/Synthetic_Event_Logs/generated_event_logs/`. Cases, events and activity counts match Table 1. Both split files together match the preprocessed case IDs and their activity sequences, with no overlap between train and test.

| Log | Event log directory | Reference BPMN in parent directory | Cases / events / activities | Distinct activity sequences | Archive train / test | Test cases shared with independent split |
|---|---|---|---|---:|---|---:|
| Sequence | `02_sequence/exp_018` | `longer_sequence.bpmn` | 1,000 / 12,000 / 12 | 1 | 700 / 300 | 100 |
| Long-Dist-Dep | `11_long_running_dependency2/exp_015` | `long_running_dependency2.bpmn` | 1,000 / 7,514 / 10 | 4 | 700 / 300 | 95 |
| Complex-Model | `14_complex_models/complex_model_001/exp_022` | `complex_model_001.bpmn` | 5,000 / 76,535 / 15 | 4,192 | 3,500 / 1,500 | 446 |
| Looped-AND | `15_looped_AND/exp_023` | `looped_AND.bpmn` | 1,550 / 38,016 / 6 | 1,550 | 1,085 / 465 | 123 |

Local `inventory.json` and `synthetic-receipt.json` record retrieval, exact paths, member sizes and hashes. Configs `configs/datasets/synthetic-*.json` pin the hashes and expected counts of the four preprocessed XES files. All four archived test memberships match the author's random split with seed 789 on each preprocessed log's source trace order. The independent configs retain the locked seed 42 and sorted case order. All twelve Table 1 log inputs now have provenance and count evidence.

The archived BPIC13 closed-problems test file shares 129 of 447 test cases with the independent split. Taking every event after the first event of its case as a next-activity target yields 1,486 targets: 800 Accepted, 465 Completed, 216 Queued and 5 Unmatched. The independent run has 1,574 held-out targets, with respective counts 839, 477, 255 and 3. The pinned splitter applied with seed 42 to the acquired public XES produces the same membership as the independent split for this log. The archived test file establishes a different actual membership.
