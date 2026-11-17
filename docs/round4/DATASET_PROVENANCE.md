# Dataset provenance

## Sepsis version 1 · acquired 2026-11-17

Felix Mannhardt (2016), Sepsis Cases – Event Log, 4TU.ResearchData, version 1. The official metadata API resolves the paper's DOI and supplies a directly downloadable XES file and publisher checksum. [Dataset DOI](https://doi.org/10.4121/uuid:915d2bfb-7e84-49ad-a286-dc35f063a460) · [Official API record](https://data.4tu.nl/v2/articles/33632f3c-5c48-40cf-8d8f-2db57f5a6ce7)

Acquisition evidence is retained locally under data/raw/sepsis-v1/ as metadata.json, acquisition.json, readme.txt, DATA.xml, original XES.GZ and General_terms_of_use.pdf. The publisher MD5 b5671166ac71eb20680d3c74616c43d2 matched the downloaded archive. SHA-256 is 709c52340306415952811b9b9c5dc6bcc8f8d47d583eba39df9a538459dc543a. Input remains activity-only using concept:name and time:timestamp with source ordinal tie-breaking. No event filters or lifecycle composition are applied.

The independent loader counted 1,050 cases, 15,214 events, 16 activities and maximum trace length 185, matching the paper inventory. There were no empty or duplicate trace identifiers. These checks establish a verified public dataset for independent runs. Exact historical run/split identity remains unavailable. No BPMN ground truth is claimed for Sepsis.

The dataset's August2016 terms permit noncommercial reuse with source acknowledgement and impose citation/publication-notification and attribution conditions for publication or redistribution. The local work is academic research. Cite the creator and DOI in results using this log, and carry the publication/redistribution requirements into the final report handoff. This turn performs no external publication or notification. The public README describes anonymized attributes and shifted timestamps, with within-case timing retained. [Applicable terms](https://doi.org/10.4121/resource:terms_of_use)

Preparation config is configs/datasets/sepsis.json. Split seed42 is an independent design choice, with actual IDs and hash emitted by prepare. Dataset outputs and model results remain local under ignored data/ and artifacts/. Helpdesk candidate and synthetic historical-provenance issues from Round3.6 remain open.

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

Eight of twelve log variants now have official raw/count evidence or event-level provenance against an official release. The four synthetic logs remain unresolved. The publisher's [Materials availability](https://link.springer.com/article/10.1007/s44311-025-00018-4#data-availability) points to the author repository without identifying a separate verified XES/BPMN bundle.
