package de.cocondo.system.http;

import de.cocondo.system.dto.DataTransferObject;

public class ApiViolationDTO implements DataTransferObject {

    private String field;
    private String object;
    private String message;
    private String code;
    private String messageKey;
    private Object rejectedValue;

    public ApiViolationDTO() {
    }

    public ApiViolationDTO(String field, String message, String code, String messageKey) {
        this.field = field;
        this.message = message;
        this.code = code;
        this.messageKey = messageKey;
    }

    public String getField() {
        return field;
    }

    public void setField(String field) {
        this.field = field;
    }

    public String getObject() {
        return object;
    }

    public void setObject(String object) {
        this.object = object;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getMessageKey() {
        return messageKey;
    }

    public void setMessageKey(String messageKey) {
        this.messageKey = messageKey;
    }

    public Object getRejectedValue() {
        return rejectedValue;
    }

    public void setRejectedValue(Object rejectedValue) {
        this.rejectedValue = rejectedValue;
    }
}
