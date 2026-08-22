package de.cocondo.system.backendcontract;

import java.util.Objects;
import java.util.Set;

/** Security classification and operation permissions for a profiled operation. */
public record ApiSecurityContract(
        String classification,
        Set<String> permissions,
        String targetAuthorization
) {
    private static final Set<String> CLASSIFICATIONS = Set.of(
            "PUBLIC", "AUTHENTICATED", "MANAGEMENT", "TECHNICAL", "SYSTEM"
    );
    private static final Set<String> TARGET_AUTHORIZATIONS = Set.of(
            "NONE", "REQUEST_CONTEXT", "EACH_TARGET"
    );

    public ApiSecurityContract {
        classification = Objects.requireNonNull(classification, "classification");
        permissions = Set.copyOf(Objects.requireNonNull(permissions, "permissions"));
        targetAuthorization = Objects.requireNonNull(targetAuthorization, "targetAuthorization");
        if (!CLASSIFICATIONS.contains(classification)) {
            throw new IllegalArgumentException("Unknown security classification: " + classification);
        }
        if (!TARGET_AUTHORIZATIONS.contains(targetAuthorization)) {
            throw new IllegalArgumentException("Unknown target authorization: " + targetAuthorization);
        }
        if ("MANAGEMENT".equals(classification) && permissions.isEmpty()) {
            throw new IllegalArgumentException("Management operations require a permission");
        }
    }
}
