package de.cocondo.system.backendcontract;

import java.util.Objects;
import java.util.Set;

/** Complete opt-in authoring contract for one profiled OpenAPI operation. */
public record ApiOperationContract(
        String operationKey,
        String operationId,
        String method,
        String path,
        ApiOperationKind operationKind,
        Set<ApiOperationRole> operationRoles,
        ApiSecurityContract security,
        ApiPreconditionContract precondition,
        ApiResourceSemantics resourceSemantics,
        ApiOperationEffects effects
) {
    private static final Set<String> METHODS = Set.of("GET", "POST", "PUT", "PATCH", "DELETE");

    public ApiOperationContract {
        operationKey = requireText(operationKey, "operationKey");
        operationId = requireText(operationId, "operationId");
        method = requireText(method, "method").toUpperCase();
        path = requireText(path, "path");
        operationKind = Objects.requireNonNull(operationKind, "operationKind");
        operationRoles = Set.copyOf(Objects.requireNonNull(operationRoles, "operationRoles"));
        security = Objects.requireNonNull(security, "security");
        precondition = Objects.requireNonNull(precondition, "precondition");
        resourceSemantics = Objects.requireNonNull(resourceSemantics, "resourceSemantics");
        effects = Objects.requireNonNull(effects, "effects");
        if (!METHODS.contains(method) || !path.startsWith("/api/")) {
            throw new IllegalArgumentException("Invalid technical operation identity");
        }
    }

    private static String requireText(String value, String field) {
        Objects.requireNonNull(value, field);
        if (value.isBlank()) {
            throw new IllegalArgumentException(field + " must not be blank");
        }
        return value;
    }
}
