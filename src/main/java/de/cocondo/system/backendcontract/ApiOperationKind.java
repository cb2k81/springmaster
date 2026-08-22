package de.cocondo.system.backendcontract;

/** Classifies the externally observable purpose of a profiled API operation. */
public enum ApiOperationKind {
    QUERY,
    COMMAND,
    PRECHECK,
    CAPABILITY_EVALUATION
}
