package de.cocondo.platform.demo.catalog.api;

public class CatalogApiViolation {

    private String field;
    private String message;
    private String messageKey;

    public CatalogApiViolation() {
    }

    public CatalogApiViolation(String field, String message, String messageKey) {
        this.field = field;
        this.message = message;
        this.messageKey = messageKey;
    }

    public String getField() {
        return field;
    }

    public void setField(String field) {
        this.field = field;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getMessageKey() {
        return messageKey;
    }

    public void setMessageKey(String messageKey) {
        this.messageKey = messageKey;
    }
}
