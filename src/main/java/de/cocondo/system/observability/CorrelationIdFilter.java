package de.cocondo.system.observability;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import org.slf4j.MDC;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

/**
 * Establishes one validated correlation identifier for every HTTP request.
 */
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public final class CorrelationIdFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain
    ) throws ServletException, IOException {
        String previous = MDC.get(CorrelationIdSupport.MDC_KEY);
        String correlationId = CorrelationIdSupport.inboundOrGenerated(
                request.getHeader(CorrelationIdSupport.HEADER_NAME)
        );
        request.setAttribute(CorrelationIdSupport.REQUEST_ATTRIBUTE, correlationId);
        response.setHeader(CorrelationIdSupport.HEADER_NAME, correlationId);
        MDC.put(CorrelationIdSupport.MDC_KEY, correlationId);
        try {
            filterChain.doFilter(request, response);
        } finally {
            if (previous == null) {
                MDC.remove(CorrelationIdSupport.MDC_KEY);
            } else {
                MDC.put(CorrelationIdSupport.MDC_KEY, previous);
            }
        }
    }
}
