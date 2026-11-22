# 05 · Data Audit and Limitations

## Which JSON was used and why

| Candidate | Size | Parses? | Mayor's Permit record |
|---|---|---|---|
| Old repaired app JSON (previous handover) | 45,761 bytes | Yes | 4 bring items, **0 requirements, 0 steps**, 0 links |
| `juan-and-done/data/documents.json` (design reference) | 47,703 bytes | Yes | 5 bring items, 6 requirements, 7 steps, 0 links |
| Original raw team database | — | **No** (cut off mid-record) | Truncated; **never used and not shipped** |

A field-by-field comparison showed the two valid files are **identical for records 1–15**. The only difference is the Mayor's Permit record. The 47,703-byte file was chosen because it is the more complete valid file. Its rebuilt Mayor's Permit requirements and steps match, almost word for word, the *LGU Business Permitting and Licensing* section of the team's own research notes. They were **not invented for this build**.

**Changes made in this build (no government facts added or altered):** two records gained the optional fields `"dataStatus": "needs-verification"` and a `dataNote`, and the file was re-saved with 2-space indentation (now 48,448 bytes). A script confirmed every other value equals the 47,703-byte source exactly.

## Record status (16 records)

| # | ID | Document | Bring | Reqs | Steps | Links | Last verified | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | `dfa-passport` | Philippine Regular ePassport | 7 | 6 | 7 | 1 | 2026-10-14 | Complete in dataset |
| 2 | `nbi-clearance` | NBI Multi-Purpose Clearance | 5 | 6 | 7 | 2 | 2026-10-14 | Complete in dataset |
| 3 | `philsys-national-id` | PhilSys National ID (PhilID / ePhilID) | 3 | 4 | 5 | 1 | 2026-10-14 | Complete in dataset |
| 4 | `lto-student-permit` | Student-Driver's Permit | 9 | 6 | 7 | 2 | 2026-10-14 | Complete in dataset |
| 5 | `lto-drivers-license` | Non-Professional Driver's License | 6 | 6 | 7 | 2 | 2026-10-14 | Complete in dataset |
| 6 | `pnp-police-clearance` | National Police Clearance | 5 | 5 | 6 | 1 | 2026-10-14 | Complete in dataset |
| 7 | `bir-tin` | Taxpayer Identification Number (TIN) | 7 | 4 | 5 | 2 | 2026-10-14 | Complete in dataset |
| 8 | `sss-number` | Social Security (SS) Number | 4 | 3 | 6 | 1 | 2026-10-14 | Complete in dataset |
| 9 | `philhealth-number` | PhilHealth Identification Number (PIN) & MDR | 6 | 4 | 4 | 1 | 2026-10-14 | Complete in dataset |
| 10 | `pagibig-mid` | Pag-IBIG Member Identification (MID) Number | 4 | 3 | 5 | 1 | 2026-10-14 | Complete in dataset |
| 11 | `psa-civil-certificates` | PSA Civil Registry Certificates | 7 | 5 | 5 | 1 | 2026-10-14 | Complete in dataset |
| 12 | `comelec-voters-certification` | Voter's Certification | 4 | 3 | 6 | 1 | 2026-10-14 | Complete in dataset |
| 13 | `phlpost-postal-id` | Digitized Postal Identity Card | 6 | 5 | 6 | 1 | 2026-10-14 | Complete in dataset |
| 14 | `dti-business-name` | Certificate of Business Name Registration | 2 | 5 | 6 | 1 | 2026-10-14 | Complete in dataset |
| 15 | `lgu-barangay-clearance` | Barangay Clearance & Certificate of Residency | 6 | 5 | 6 | **0** | 2026-10-14 | **Needs verification** |
| 16 | `lgu-mayors-permit` | Mayor's Permit and Barangay Business Clearance | 5 | 6 | 7 | **0** | 2026-10-14 | **Needs verification** |

Totals: 86 bring items (Original 40, Photocopy 16, Original & Photocopy 15, Original/Printed 13, Original/Digital 2), 76 requirements, 95 steps (66 in-person, 29 online), 18 links.

"Complete in dataset" means no field is empty. It does **not** mean the content was checked against today's official rules.

## The two flagged LGU records

**`lgu-mayors-permit`**
- The original database file stopped in the middle of this record's 5th item.
- The 5th item (*Comprehensive General Liability Insurance (CGLI) policy for the business premises*, type *Original & Photocopy*), the 6 requirements and the 7 steps were rebuilt from the team's research notes. The research lists CGLI as a requirement, but the exact item wording and its type were filled in during the rebuild, not copied from a source.
- No official link (rules are per city/municipality).
- App behaviour: red badge, reasons + note shown on Details and Checklist, "Ready ka na!" blocked (`ready-unverified` state), exports named `…-REFERENCE-ONLY`.

**`lgu-barangay-clearance`**
- Full content exists, but no official link, and fees/validity/requirements differ per barangay. The original research even suggested skipping it for that reason.
- Same app behaviour as above.

**To clear a flag:** pick a specific city/municipality and barangay, check its Citizen's Charter or BPLO/BOSS page, correct the record, add the official `https://` link, update `lastVerified`, then delete `dataStatus` and `dataNote`. Run `python tools\check_project.py`.

## Links that need a second look

All 18 links use `https://`. Two are not `.gov.ph` addresses and are labelled "double-check" in the app:

- `https://pnpclearance.ph` (PNP clearance)
- `https://pagibigfundservices.com` (Virtual Pag-IBIG)

These may well be the agencies' real portals, but confirm them from the agency's own `.gov.ph` site before the demo.

## What this build did NOT verify

- No fee, processing time, validity, accepted-ID list, requirement or step was checked against live government websites. All `lastVerified` values are **2026-10-14** as recorded by the team.
- Links were syntax-checked only; none were opened (the build environment had no internet access).
- Conditional rules (minors, married applicants, representatives, first-time jobseekers under RA 11261) are shown as tagged optional items, not as a decision tree.

## Rules for anyone editing the data

1. Never add a fee, requirement, date or link you did not read on the official source. Write the source URL and date in your team log.
2. Keep exact type labels: `Original`, `Photocopy`, `Original & Photocopy`, `Original/Printed`, `Original/Digital`.
3. Changing an item's wording unticks that one item for users (stable keys come from the text). Reordering is safe.
4. Never replace `data/documents.json` with the old truncated raw file.
5. Run `python tools\check_project.py` after every edit.
