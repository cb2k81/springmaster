package de.cocondo.system.backendcontract;

import java.util.Objects;
import java.util.Set;

/** Resource/history/projection binding referenced by a profiled operation. */
public record ApiResourceSemantics(
        String resourceKey,
        String historyModel,
        String temporalContext,
        String projectionResponseSchema
) {
    private static final Set<String> HISTORY_MODELS = Set.of(
            "NONE", "ROOT_VERSION", "PLAN_SNAPSHOT", "APPEND_ONLY", "TEMPORAL_RELATION"
    );

    public ApiResourceSemantics {
        resourceKey = Objects.requireNonNull(resourceKey, "resourceKey");
        historyModel = Objects.requireNonNull(historyModel, "historyModel");
        if (resourceKey.isBlank() || !HISTORY_MODELS.contains(historyModel)) {
            throw new IllegalArgumentException("Invalid resource semantics");
        }
    }
}
