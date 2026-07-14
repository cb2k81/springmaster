package de.cocondo.system.http;

import de.cocondo.system.dto.DataTransferObject;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

public class ApiErrorResponse implements DataTransferObject {

    private String timestamp = Instant.now().toString();
    private int status;
    private String error;
    private String errorType;
    private String message;
    private String messageKey;
    private String localMessage;
    private String errorId;
    private String correlationId;
    private String traceId;
    private String path;
    private String method;
    private List<ApiViolationDTO> violations = new ArrayList<>();

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

    public String getMessageKey() {
        return messageKey;
    }

    public void setMessageKey(String messageKey) {
        this.messageKey = messageKey;
    }

    public String getLocalMessage() {
        return localMessage;
    }

    public void setLocalMessage(String localMessage) {
        this.localMessage = localMessage;
    }

    public String getErrorId() {
        return errorId;
    }

    public void setErrorId(String errorId) {
        this.errorId = errorId;
    }

    public String getCorrelationId() {
        return correlationId;
    }

    public void setCorrelationId(String correlationId) {
        this.correlationId = correlationId;
    }

    public String getTraceId() {
        return traceId;
    }

    public void setTraceId(String traceId) {
        this.traceId = traceId;
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

    public List<ApiViolationDTO> getViolations() {
        return violations;
    }

    public void setViolations(List<ApiViolationDTO> violations) {
        this.violations = violations != null ? new ArrayList<>(violations) : new ArrayList<>();
    }
}
