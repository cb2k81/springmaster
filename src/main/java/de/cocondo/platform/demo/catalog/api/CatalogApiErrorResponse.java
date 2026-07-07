package de.cocondo.platform.demo.catalog.api;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class CatalogApiErrorResponse {

    private String timestamp = Instant.now().toString();
    private int status;
    private String error;
    private String errorType;
    private String message;
    private String errorId = UUID.randomUUID().toString();
    private String path;
    private String method;
    private String messageKey;
    private List<CatalogApiViolation> violations = new ArrayList<>();

    public String getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }

    public int getStatus() {
        return status;
    }

    public void setStatus(int status) {
        this.status = status;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    public String getErrorType() {
        return errorType;
    }

    public void setErrorType(String errorType) {
        this.errorType = errorType;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getErrorId() {
        return errorId;
    }

    public void setErrorId(String errorId) {
        this.errorId = errorId;
    }

    public String getPath() {
        return path;
    }

    public void setPath(String path) {
        this.path = path;
    }

    public String getMethod() {
        return method;
    }

    public void setMethod(String method) {
        this.method = method;
    }

    public String getMessageKey() {
        return messageKey;
    }

    public void setMessageKey(String messageKey) {
        this.messageKey = messageKey;
    }

    public List<CatalogApiViolation> getViolations() {
        return violations;
    }

    public void setViolations(List<CatalogApiViolation> violations) {
        this.violations = violations != null ? new ArrayList<>(violations) : new ArrayList<>();
    }
}
