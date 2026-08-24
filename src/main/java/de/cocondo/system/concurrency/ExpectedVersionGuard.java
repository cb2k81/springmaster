package de.cocondo.system.concurrency;

import de.cocondo.system.exception.ExpectedVersionConflictException;

/**
 * Validates one caller-supplied expected version without persistence or HTTP coupling.
 */
public final class ExpectedVersionGuard {

    public void requireMatch(
            String resourceType,
            String resourceId,
            Long actualVersion,
            Long expectedVersion
    ) {
        requireNonBlank(resourceType, "resourceType");
        requireNonBlank(resourceId, "resourceId");
        if (expectedVersion == null) {
            throw new IllegalArgumentException("expectedVersion must not be null");
        }
        if (expectedVersion < 0) {
            throw new IllegalArgumentException("expectedVersion must not be negative");
        }
        if (actualVersion == null || !actualVersion.equals(expectedVersion)) {
            throw new ExpectedVersionConflictException();
        }
    }

    private void requireNonBlank(String value, String name) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " must not be blank");
        }
    }
}
