package de.cocondo.system.observability;

import jakarta.servlet.http.HttpServletRequest;
import java.util.UUID;
import java.util.regex.Pattern;

/**
 * Canonical correlation identifier names, validation and request lookup.
 */
public final class CorrelationIdSupport {

    public static final String HEADER_NAME = "X-Correlation-Id";
    public static final String REQUEST_ATTRIBUTE = "springmaster.correlationId";
    public static final String MDC_KEY = "correlationId";
    private static final Pattern VALID_VALUE = Pattern.compile("[A-Za-z0-9._-]{1,128}");

    private CorrelationIdSupport() {
    }

    public static String inboundOrGenerated(String candidate) {
        return isValid(candidate) ? candidate : UUID.randomUUID().toString();
    }

    public static boolean isValid(String candidate) {
        return candidate != null && VALID_VALUE.matcher(candidate).matches();
    }

    public static String from(HttpServletRequest request) {
        Object attribute = request.getAttribute(REQUEST_ATTRIBUTE);
        if (attribute instanceof String value && isValid(value)) {
            return value;
        }
        String header = request.getHeader(HEADER_NAME);
        return isValid(header) ? header : null;
    }
}
