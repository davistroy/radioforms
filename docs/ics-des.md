# ICS Forms Data Encoding Specification (ICS-DES)

## 1. Overview

This specification defines an ultra-compact encoding format for transmitting Incident Command System (ICS) form data via radio or other bandwidth-constrained communication channels. The format implements numeric code substitution, enumeration tables, and field value tokenization to minimize transmission size while maintaining complete information.

## 2. Basic Structure

```
FID{c1~v1|c2~v2|c3~v3|...}
```

Where:
- `FID` is the ICS form number without the "ICS-" prefix (e.g., 213 instead of ICS-213)
- Fields are separated by the pipe character (`|`)
- Numeric codes and values are separated by tilde (`~`)
- Arrays use double square brackets with pipe-separated items (`[[item1]|[item2]]`)

## 3. Numeric Field Codes

All field codes have been replaced with numeric identifiers:

| Code | Field | Description | Original Code |
|------|-------|-------------|---------------|
| `1` | Incident Name | Name assigned to the incident | `in` |
| `2` | Date | Date in format YYYYMMDD or days since 2025-01-01 | `d` |
| `3` | Time | Time in format HHMM or minutes since midnight | `t` |
| `4` | DateTime | Combined date and time | `dt` |
| `5` | Incident Number | Number assigned to the incident | `ino` |
| `6` | Name | Person's name | `n` |
| `7` | Position | ICS position | `p` |
| `8` | Location | Physical location | `l` |
| `9` | Identifier | Resource identifier | `id` |
| `10` | Status | Resource status | `st` |
| `11` | Prepared By | Person who prepared the form | `pc` |
| `12` | Objectives | Incident objectives | `ob` |
| `13` | Operational Period | Time period | `op` |
| `14` | Work Assignments | Tasks assigned | `wa` |
| `15` | Radio Channels | Communication channels | `rc` |
| `16` | Function | Radio function | `fn` |
| `17` | Channel Name | Radio channel name | `cn` |
| `18` | Medical Aid Stations | Medical facilities | `ma` |
| `19` | Organization | Command structure | `og` |
| `20` | Safety Message | Safety information | `sm` |
| `21` | Situation Summary | Incident overview | `ss` |
| `22` | Status Changes | Resource status updates | `sc` |
| `23` | Check-In List | Resource arrivals | `ci` |
| `24` | To | Message recipient | `to` |
| `25` | From | Message sender | `fr` |
| `26` | Message | Message content | `m` |
| `27` | Activity Log | Chronological activities | `al` |
| `28` | Activity | Specific activity | `a` |
| `29` | Resources | Resource information | `rs` |
| `30` | Resource Type | Type of resource | `rt` |
| `31` | Required | Number required | `rq` |
| `32` | Available | Number available | `av` |
| `33` | Hazards | Safety hazards | `hz` |
| `34` | Hazard | Specific hazard | `hd` |
| `35` | Mitigations | Safety measures | `mt` |
| `36` | Vehicles | Vehicle information | `ve` |
| `37` | Type | Resource type | `ty` |
| `38` | Resource Name | Name of resource | `rn` |
| `39` | Aircraft | Aircraft information | `ac` |
| `40` | Assignment | Resource assignment | `as` |
| `41` | Resource Identifier | Resource being released | `ri` |
| `42` | Release Date/Time | Time of resource release | `rd` |
| `43` | Person Name | Name of rated person | `pn` |
| `44` | Rating | Performance rating | `rt` |
| `45` | Comments | Additional information | `cm` |
| `46` | Incident Commander | Name of IC | `ic` |
| `47` | Operations Chief | Name of Operations Section Chief | `ops` |
| `48` | Planning Chief | Name of Planning Section Chief | `pln` |
| `49` | Logistics Chief | Name of Logistics Section Chief | `log` |
| `50` | Finance Chief | Name of Finance Section Chief | `fin` |

## 4. Enumeration Tables

### 4.1. Resource Status Codes
| Code | Status |
|------|--------|
| `A` | Available |
| `B` | Assigned |
| `C` | Out of Service |

### 4.2. ICS Position Codes
| Code | Position |
|------|----------|
| `IC` | Incident Commander |
| `OSC` | Operations Section Chief |
| `PSC` | Planning Section Chief |
| `LSC` | Logistics Section Chief |
| `FSC` | Finance Section Chief |
| `SO` | Safety Officer |
| `LO` | Liaison Officer |
| `PIO` | Public Information Officer |
| `DIVS` | Division Supervisor |
| `TFL` | Task Force Leader |
| `STL` | Strike Team Leader |
| `RUL` | Resources Unit Leader |
| `SUL` | Situation Unit Leader |
| `DOCL` | Documentation Unit Leader |
| `DMOB` | Demobilization Unit Leader |
| `CUL` | Communications Unit Leader |
| `MUL` | Medical Unit Leader |

### 4.3. Performance Rating Codes
| Code | Rating |
|------|--------|
| `1` | Exceeds Expectations |
| `2` | Meets Expectations |
| `3` | Needs Improvement |
| `4` | Unsatisfactory |

## 5. Data Structure Encodings

### Arrays
```
27~[[3~0800|28~Arrived]|[3~0900|28~Briefing]]
```

### Objects in Arrays
```
15~[[16~Command|17~CMD1]|[16~Tactical|17~TAC2]]
```

## 6. Character Escaping

- Replace pipes (`|`) in text with `\/`
- Replace tildes (`~`) in text with `\:`
- Replace square brackets (`[` or `]`) with `\(` or `\)`

## 7. Examples for Each ICS Form

### ICS-201 (Incident Briefing)

```
201{1~Mountain Wildfire|5~WF-2025-042|11~John Smith}
```

### ICS-202 (Incident Objectives)

```
202{1~Mountain Wildfire|12~1. Protect residential areas\/ 2. Establish fire lines\/ 3. Monitor weather conditions|13~20250423~20250424}
```

### ICS-204 (Assignment List)

```
204{1~Mountain Wildfire|14~Clear access routes to north ridge\/ Establish staging area at ranger station}
```

### ICS-205 (Incident Radio Communications Plan)

```
205{1~Mountain Wildfire|15~[[16~Command|17~CMD1]|[16~Tactical|17~TAC2]|[16~Medical|17~MED1]]}
```

### ICS-206 (Medical Plan)

```
206{1~Mountain Wildfire|18~[[6~Aid Station Alpha|8~Base Camp]|[6~Aid Station Bravo|8~Ridge Point]]}
```

### ICS-207 (Incident Organization Chart)

```
207{1~Mountain Wildfire|46~Sarah Johnson|47~Mark Williams|48~David Chen|49~Lisa Garcia|50~Robert Taylor}
```

### ICS-208 (Safety Message/Plan)

```
208{1~Mountain Wildfire|20~All personnel must wear full PPE at all times\/ Report weather changes immediately\/ Maintain communications with team leader}
```

### ICS-209 (Incident Status Summary)

```
209{1~Mountain Wildfire|21~Fire currently 40% contained\/ 120 personnel on scene\/ Expected containment in 48 hours\/ Weather conditions stable}
```

### ICS-210 (Resource Status Change)

```
210{1~Mountain Wildfire|22~[[9~Engine 3|10~A]|[9~Crew 7|10~C]|[9~Helicopter 2|10~B]]}
```

### ICS-211 (Incident Check-In List)

```
211{1~Mountain Wildfire|23~[[9~Engine 3|3~0800]|[9~Crew 7|3~0830]|[9~Helicopter 2|3~0915]]}
```

### ICS-213 (General Message)

```
213{24~OSC|25~PSC|26~Request additional resources for north sector\/ Fire line needs reinforcement\/ Wind shift expected at 1600|2~20250423|3~1145}
```

### ICS-214 (Activity Log)

```
214{1~Mountain Wildfire|6~James Wilson|7~DIVS|27~[[3~0800|28~Arrived at command post]|[3~0900|28~Briefing with team]|[3~1200|28~Established fire line]|[3~1700|28~End of shift]]}
```

### ICS-215 (Operational Planning Worksheet)

```
215{1~Mountain Wildfire|29~[[30~Engine|31~5|32~3]|[30~Hand Crew|31~8|32~6]|[30~Helicopter|31~2|32~1]]}
```

### ICS-215A (Incident Action Plan Safety Analysis)

```
215A{1~Mountain Wildfire|33~[[34~Steep Terrain|35~Use proper footwear\/ Work in teams]|[34~Heat Exposure|35~Hydration schedule\/ Rotate crews]|[34~Smoke Inhalation|35~Use respirators\/ Monitor air quality]]}
```

### ICS-218 (Support Vehicle/Equipment Inventory)

```
218{1~Mountain Wildfire|36~[[37~Pickup|9~V-01|8~Base Camp]|[37~Water Tender|9~WT-03|8~North Ridge]|[37~ATV|9~A-07|8~Staging Area]]}
```

### ICS-219 (Resource Status Card)

```
219{38~Engine 42|10~B|8~North Division}
```

### ICS-220 (Air Operations Summary)

```
220{1~Mountain Wildfire|39~[[37~Type 1 Helicopter|9~H-65|40~Water drops]|[37~Fixed Wing|9~A-12|40~Reconnaissance]|[37~Drone|9~D-03|40~Thermal imaging]]}
```

### ICS-221 (Demobilization Check-Out)

```
221{1~Mountain Wildfire|41~Engine 42|42~202504251400}
```

### ICS-225 (Incident Personnel Performance Rating)

```
225{1~Mountain Wildfire|43~Michael Johnson|44~2|45~Showed good leadership\/ Maintained crew safety\/ Completed assignments efficiently}
```

## 8. Form Field Requirement Matrix

To further optimize transmission, this table shows which numeric codes apply to which forms. Only transmit fields relevant to the specific form:

| Code | 201 | 202 | 204 | 205 | 206 | 207 | 208 | 209 | 210 | 211 | 213 | 214 | 215 | 215A | 218 | 219 | 220 | 221 | 225 |
|------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|------|-----|-----|-----|-----|-----|
| `1`  | ✓   | ✓   | ✓   | ✓   | ✓   | ✓   | ✓   | ✓   | ✓   | ✓   |     | ✓   | ✓   | ✓    | ✓   |     | ✓   | ✓   | ✓   |
| `2`  | ✓   | ✓   |     |     |     |     |     | ✓   |     | ✓   | ✓   | ✓   |     |      |     |     |     | ✓   |     |
| `3`  | ✓   |     |     |     |     |     |     |     |     |     | ✓   | ✓   |     |      |     |     |     |     |     |
| `5`  | ✓   |     |     |     |     |     |     |     |     |     |     |     |     |      |     |     |     |     |     |
| `6`  |     |     |     |     | ✓   |     |     |     |     |     |     | ✓   |     |      |     |     |     |     |     |
| `7`  |     |     |     |     |     |     |     |     |     |     |     | ✓   |     |      |     |     |     |     |     |
| `8`  |     |     |     |     | ✓   |     |     |     |     |     |     |     |     |      | ✓   | ✓   |     |     |     |
| `9`  |     |     |     |     |     |     |     |     | ✓   | ✓   |     |     |     |      | ✓   |     | ✓   |     |     |
| `10` |     |     |     |     |     |     |     |     | ✓   |     |     |     |     |      |     | ✓   |     |     |     |
| `11` | ✓   |     |     |     |     |     |     |     |     |     |     |     |     |      |     |     |     |     |     |
| `12` |     | ✓   |     |     |     |     |     |     |     |     |     |     |     |      |     |     |     |     |     |
| `13` |     | ✓   |     |     |     |     |     |     |     |     |     | ✓   |     |      |     |     |     |     |     |
| `14` |     |     | ✓   |     |     |     |     |     |     |     |     |     |     |      |     |     |     |     |     |
| `15` |     |     |     | ✓   |     |     |     |     |     |     |     |     |     |      |     |     |     |     |     |
| `18` |     |     |     |     | ✓   |     |     |     |     |     |     |     |     |      |     |     |     |     |     |
| `20` |     |     |     |     |     |     | ✓   |     |     |     |     |     |     |      |     |     |     |     |     |
| `21` |     |     |     |     |     |     |     | ✓   |     |     |     |     |     |      |     |     |     |     |     |
| `22` |     |     |     |     |     |     |     |     | ✓   |     |     |     |     |      |     |     |     |     |     |
| `23` |     |     |     |     |     |     |     |     |     | ✓   |     |     |     |      |     |     |     |     |     |
| `24` |     |     |     |     |     |     |     |     |     |     | ✓   |     |     |      |     |     |     |     |     |
| `25` |     |     |     |     |     |     |     |     |     |     | ✓   |     |     |      |     |     |     |     |     |
| `26` |     |     |     |     |     |     |     |     |     |     | ✓   |     |     |      |     |     |     |     |     |
| `27` |     |     |     |     |     |     |     |     |     |     |     | ✓   |     |      |     |     |     |     |     |
| `29` |     |     |     |     |     |     |     |     |     |     |     |     | ✓   |      |     |     |     |     |     |
| `33` |     |     |     |     |     |     |     |     |     |     |     |     |     | ✓    |     |     |     |     |     |
| `36` |     |     |     |     |     |     |     |     |     |     |     |     |     |      | ✓   |     |     |     |     |
| `38` |     |     |     |     |     |     |     |     |     |     |     |     |     |      |     | ✓   |     |     |     |
| `39` |     |     |     |     |     |     |     |     |     |     |     |     |     |      |     |     | ✓   |     |     |
| `41` |     |     |     |     |     |     |     |     |     |     |     |     |     |      |     |     |     | ✓   |     |
| `42` |     |     |     |     |     |     |     |     |     |     |     |     |     |      |     |     |     | ✓   |     |
| `43` |     |     |     |     |     |     |     |     |     |     |     |     |     |      |     |     |     |     | ✓   |
| `44` |     |     |     |     |     |     |     |     |     |     |     |     |     |      |     |     |     |     | ✓   |
| `45` |     |     |     |     |     |     |     |     |     |     |     |     |     |      |     |     |     |     | ✓   |
| `46` |     |     |     |     |     | ✓   |     |     |     |     |     |     |     |      |     |     |     |     |     |
| `47` |     |     |     |     |     | ✓   |     |     |     |     |     |     |     |      |     |     |     |     |     |
| `48` |     |     |     |     |     | ✓   |     |     |     |     |     |     |     |      |     |     |     |     |     |
| `49` |     |     |     |     |     | ✓   |     |     |     |     |     |     |     |      |     |     |     |     |     |
| `50` |     |     |     |     |     | ✓   |     |     |     |     |     |     |     |      |     |     |     |     |     |
