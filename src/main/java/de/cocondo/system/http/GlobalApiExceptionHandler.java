package de.cocondo.system.http;

import de.cocondo.system.entity.validation.ValidationException;
import de.cocondo.system.exception.EntityAlreadyExistsException;
import de.cocondo.system.exception.ResourceNotFoundException;
import de.cocondo.system.observability.CorrelationIdSupport;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.ConstraintViolationException;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;

@RestControllerAdvice
public class GlobalApiExceptionHandler {

    private final ApiErrorIdGenerator errorIdGenerator;

    public GlobalApiExceptionHandler(ApiErrorIdGenerator errorIdGenerator) {
        this.errorIdGenerator = errorIdGenerator;
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiErrorResponse> handleMethodArgumentNotValid(
            MethodArgumentNotValidException exception,
            HttpServletRequest request
    ) {
        ApiErrorResponse body = error(
                HttpStatus.BAD_REQUEST,
                ApiErrorType.VALIDATION_FAILED,
                "Validation failed",
                "springmaster.validation.failed",
                request
        );
        body.setViolations(exception.getBindingResult().getFieldErrors().stream()
                .map(this::fieldViolation)
                .toList());
        return ResponseEntity.badRequest().body(body);
    }

    @ExceptionHandler(ConstraintViolationException.class)
    public ResponseEntity<ApiErrorResponse> handleConstraintViolation(
            ConstraintViolationException exception,
            HttpServletRequest request
    ) {
        ApiErrorResponse body = error(
                HttpStatus.BAD_REQUEST,
                ApiErrorType.VALIDATION_FAILED,
                "Validation failed",
                "springmaster.validation.failed",
                request
        );
        body.setViolations(exception.getConstraintViolations().stream()
                .map(this::constraintViolation)
                .toList());
        return ResponseEntity.badRequest().body(body);
    }

    @ExceptionHandler(ValidationException.class)
    public ResponseEntity<ApiErrorResponse> handleValidationException(
            ValidationException exception,
            HttpServletRequest request
    ) {
        return ResponseEntity.badRequest().body(error(
                HttpStatus.BAD_REQUEST,
                ApiErrorType.VALIDATION_FAILED,
                safeClientMessage(exception, "Validation failed"),
                "springmaster.validation.failed",
                request
        ));
    }

    @ExceptionHandler({
            IllegalArgumentException.class,
            MethodArgumentTypeMismatchException.class,
            MissingServletRequestParameterException.class,
            HttpMessageNotReadableException.class
    })
    public ResponseEntity<ApiErrorResponse> handleInvalidRequest(Exception exception, HttpServletRequest request) {
        return ResponseEntity.badRequest().body(error(
                HttpStatus.BAD_REQUEST,
                ApiErrorType.INVALID_REQUEST,
                invalidRequestMessage(exception),
                "springmaster.request.invalid",
                request
        ));
    }

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ApiErrorResponse> handleResourceNotFound(
            ResourceNotFoundException exception,
            HttpServletRequest request
    ) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error(
                HttpStatus.NOT_FOUND,
                ApiErrorType.RESOURCE_NOT_FOUND,
                safeClientMessage(exception, "Resource not found"),
                exception.getMessageKey(),
                request
        ));
    }

    @ExceptionHandler(EntityAlreadyExistsException.class)
    public ResponseEntity<ApiErrorResponse> handleEntityAlreadyExists(
            EntityAlreadyExistsException exception,
            HttpServletRequest request
    ) {
        return ResponseEntity.status(HttpStatus.CONFLICT).body(error(
                HttpStatus.CONFLICT,
                ApiErrorType.CONFLICT,
                safeClientMessage(exception, "Resource conflict"),
                exception.getMessageKey(),
                request
        ));
    }

    @ExceptionHandler(SecurityException.class)
    public ResponseEntity<ApiErrorResponse> handleSecurityException(SecurityException exception, HttpServletRequest request) {
        return ResponseEntity.status(HttpStatus.FORBIDDEN).body(error(
                HttpStatus.FORBIDDEN,
                ApiErrorType.FORBIDDEN,
                "Forbidden",
                "springmaster.security.forbidden",
                request
        ));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiErrorResponse> handleUnexpectedException(Exception exception, HttpServletRequest request) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error(
                HttpStatus.INTERNAL_SERVER_ERROR,
                ApiErrorType.INTERNAL_ERROR,
                "Internal server error",
                "springmaster.internal-error",
                request
        ));
    }

    private ApiErrorResponse error(
            HttpStatus status,
            ApiErrorType errorType,
            String message,
            String messageKey,
            HttpServletRequest request
    ) {
        ApiErrorResponse body = new ApiErrorResponse();
        body.setStatus(status.value());
        body.setError(status.getReasonPhrase());
        body.setErrorType(errorType.name());
        body.setMessage(message);
        body.setMessageKey(messageKey);
        body.setErrorId(errorIdGenerator.nextErrorId());
        body.setPath(request.getRequestURI());
        body.setMethod(request.getMethod());
        body.setCorrelationId(correlationId(request));
        return body;
    }

    private ApiViolationDTO fieldViolation(FieldError error) {
        return new ApiViolationDTO(
                error.getField(),
                safeViolationMessage(error.getDefaultMessage()),
                error.getCode(),
                "springmaster.validation." + error.getField()
        );
    }

    private ApiViolationDTO constraintViolation(ConstraintViolation<?> violation) {
        String path = violation.getPropertyPath() != null ? violation.getPropertyPath().toString() : null;
        return new ApiViolationDTO(
                path,
                safeViolationMessage(violation.getMessage()),
                null,
                path != null ? "springmaster.validation." + path : "springmaster.validation"
        );
    }

    private String invalidRequestMessage(Exception exception) {
        if (exception instanceof HttpMessageNotReadableException) {
            return "Malformed request body";
        }
        if (exception instanceof MethodArgumentTypeMismatchException mismatch) {
            return "Invalid value for parameter: " + mismatch.getName();
        }
        if (exception instanceof MissingServletRequestParameterException missing) {
            return "Missing required parameter: " + missing.getParameterName();
        }
        return safeClientMessage(exception, "Invalid request");
    }

    private String safeClientMessage(Exception exception, String fallback) {
        String message = exception.getMessage();
        if (message == null || message.isBlank()) {
            return fallback;
        }
        return sanitize(message, fallback);
    }

    private String safeViolationMessage(String message) {
        if (message == null || message.isBlank()) {
            return "Validation failed";
        }
        return sanitize(message, "Validation failed");
    }

    private String sanitize(String message, String fallback) {
        List<String> blockedTokens = List.of(
                "java.",
                "jakarta.",
                "org.springframework.",
                "org.hibernate.",
                "SQLException",
                "SQLSyntaxErrorException",
                "NullPointerException",
                "RuntimeException"
        );
        return blockedTokens.stream().anyMatch(message::contains) ? fallback : message;
    }

    private String correlationId(HttpServletRequest request) {
        return CorrelationIdSupport.from(request);
    }
}
