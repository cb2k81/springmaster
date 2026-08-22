package de.cocondo.system.backendcontract;

import java.util.List;
import java.util.Objects;

/** Backend-visible effects, intentionally limited to affected resource keys. */
public record ApiOperationEffects(List<String> affectedResourceKeys) {
    public ApiOperationEffects {
        affectedResourceKeys = List.copyOf(Objects.requireNonNull(affectedResourceKeys, "affectedResourceKeys"));
        if (affectedResourceKeys.stream().anyMatch(value -> value == null || value.isBlank())) {
            throw new IllegalArgumentException("Affected resource keys must be non-blank");
        }
    }
}
