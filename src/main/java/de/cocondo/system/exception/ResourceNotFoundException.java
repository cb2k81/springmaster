package de.cocondo.system.exception;

public class ResourceNotFoundException extends RuntimeException {

    private final String messageKey;

    public ResourceNotFoundException(String message) {
        this(message, "springmaster.resource.not-found");
    }

    public ResourceNotFoundException(String message, String messageKey) {
        super(message);
        this.messageKey = messageKey;
    }

    public String getMessageKey() {
        return messageKey;
    }
}
