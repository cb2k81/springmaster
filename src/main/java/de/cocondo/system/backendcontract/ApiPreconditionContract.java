package de.cocondo.system.backendcontract;

import java.util.Objects;
import java.util.Set;

/** Mutation precondition metadata; it does not implement a locking runtime. */
public record ApiPreconditionContract(
        String type,
        boolean required,
        String binding,
        Integer conflictStatus
) {
    private static final Set<String> TYPES = Set.of(
            "NONE", "EXPECTED_VERSION", "EXPECTED_VERSION_SET", "SNAPSHOT_TOKEN", "ETAG"
    );
    private static final Set<String> BINDINGS = Set.of("NONE", "BODY", "HEADER", "QUERY");

    public ApiPreconditionContract {
        type = Objects.requireNonNull(type, "type");
        binding = Objects.requireNonNull(binding, "binding");
        conflictStatus = Objects.requireNonNull(conflictStatus, "conflictStatus");
        if (!TYPES.contains(type) || !BINDINGS.contains(binding)) {
            throw new IllegalArgumentException("Unknown precondition classification");
        }
        if (!Set.of(409, 412, 428).contains(conflictStatus)) {
            throw new IllegalArgumentException("Unsupported precondition status: " + conflictStatus);
        }
        if ("NONE".equals(type) && (required || !"NONE".equals(binding))) {
            throw new IllegalArgumentException("NONE precondition must be optional and unbound");
        }
    }

    public static ApiPreconditionContract none() {
        return new ApiPreconditionContract("NONE", false, "NONE", 409);
    }
}
