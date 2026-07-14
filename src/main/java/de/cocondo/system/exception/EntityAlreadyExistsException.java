package de.cocondo.system.exception;

public class EntityAlreadyExistsException extends RuntimeException {

    private final String messageKey;

    public EntityAlreadyExistsException(String message) {
        this(message, "springmaster.resource.conflict");
    }

    public EntityAlreadyExistsException(String message, String messageKey) {
        super(message);
        this.messageKey = messageKey;
    }

    public String getMessageKey() {
        return messageKey;
    }
}
