package de.cocondo.system.exception;

/**
 * Signals that a supplied expected version no longer matches the identified resource.
 */
public class ExpectedVersionConflictException extends RuntimeException {

    private static final String MESSAGE_KEY = "springmaster.resource.expected-version-conflict";

    public ExpectedVersionConflictException() {
        super("Expected version conflict");
    }

    public String getMessageKey() {
        return MESSAGE_KEY;
    }
}
