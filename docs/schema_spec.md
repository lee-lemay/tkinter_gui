# Logical Schema Specification (Draft)

Defines logical field names decoupled from physical dataframe column names.
A per-dataset mapping `DatasetInfo.schema` may override any logical->physical name.

## Roles
- tracks
- truth
- errors (optional; precomputed per-track errors)

## Logical Fields by Role

### tracks
| Logical | Meaning | Default Physical |
|---------|---------|------------------|
| timestamp | Track measurement time | timestamp |
| lat | Latitude (deg) | lat |
| lon | Longitude (deg) | lon |
| alt | Altitude (m or unit) | alt |
| track_id | Unique track identifier | track_id |

### truth
| Logical | Meaning | Default Physical |
|---------|---------|------------------|
| timestamp | Truth measurement time | timestamp |
| lat | Latitude (deg) | lat |
| lon | Longitude (deg) | lon |
| alt | Altitude | alt |
| truth_id | Unique truth identifier | id |

### errors (optional)
| Logical | Meaning | Default Physical |
|---------|---------|------------------|
| timestamp | Associated track timestamp | timestamp |
| track_id | Track identifier | track_id |
| north_error | North (latitudinal) position error (meters) | north_error |
| east_error | East (longitudinal) position error (meters) | east_error |

## Capabilities
Populate `DatasetInfo.capabilities` with zero or more of:
- precomputed_errors: dataset supplies an `errors` dataframe with north/east errors.

## Access Helpers
Use `schema_access.get_col(schema, role, logical)` to resolve columns and `safe_series` for robust reads.

## Extension
New roles can be added by: 
1. Extending `LOGICAL_DEFAULTS` in `schema_access.py`.
2. Adding role documentation above.
3. Supplying mappings in DatasetInfo.schema per dataset.
