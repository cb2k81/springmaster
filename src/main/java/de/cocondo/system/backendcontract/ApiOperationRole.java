package de.cocondo.system.backendcontract;

/** Additive roles used to describe how an operation is consumed. */
public enum ApiOperationRole {
    ENTITY_LIST,
    ENTITY_DETAIL,
    ENTITY_CREATE,
    ENTITY_UPDATE,
    ENTITY_DELETE,
    REFERENCE_LOOKUP,
    RELATION_LIST,
    CANDIDATE_LIST,
    OVERVIEW_LIST,
    HISTORY_LIST,
    PROJECTION_READ,
    TEMPORAL_READ,
    BULK_COMMAND,
    BULK_STATUS,
    EXPORT,
    AGGREGATION,
    DELTA_READ
}
