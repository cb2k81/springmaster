package de.cocondo.system.observability;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.slf4j.MDC;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

class CorrelationIdFilterTest {

    private final CorrelationIdFilter filter = new CorrelationIdFilter();

    @AfterEach
    void clearMdc() {
        MDC.clear();
    }

    @Test
    void propagatesValidInboundCorrelationId() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/api/platform/info");
        request.addHeader(CorrelationIdSupport.HEADER_NAME, "corr-valid_123");
        MockHttpServletResponse response = new MockHttpServletResponse();
        AtomicReference<String> observed = new AtomicReference<>();

        filter.doFilter(request, response, (servletRequest, servletResponse) ->
                observed.set(MDC.get(CorrelationIdSupport.MDC_KEY))
        );

        assertThat(observed.get()).isEqualTo("corr-valid_123");
        assertThat(request.getAttribute(CorrelationIdSupport.REQUEST_ATTRIBUTE)).isEqualTo("corr-valid_123");
        assertThat(response.getHeader(CorrelationIdSupport.HEADER_NAME)).isEqualTo("corr-valid_123");
        assertThat(MDC.get(CorrelationIdSupport.MDC_KEY)).isNull();
    }

    @Test
    void generatesUuidWhenHeaderIsMissing() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/api/platform/info");
        MockHttpServletResponse response = new MockHttpServletResponse();

        filter.doFilter(request, response, (servletRequest, servletResponse) -> { });

        String value = response.getHeader(CorrelationIdSupport.HEADER_NAME);
        assertThat(value).isNotBlank();
        assertThat(CorrelationIdSupport.isValid(value)).isTrue();
        assertThat(value).matches("[0-9a-f-]{36}");
    }

    @Test
    void replacesInvalidInboundValueAndRestoresPreviousMdc() throws Exception {
        MDC.put(CorrelationIdSupport.MDC_KEY, "outer-correlation");
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/api/platform/info");
        request.addHeader(CorrelationIdSupport.HEADER_NAME, "invalid value with spaces");
        MockHttpServletResponse response = new MockHttpServletResponse();

        filter.doFilter(request, response, (servletRequest, servletResponse) -> { });

        assertThat(response.getHeader(CorrelationIdSupport.HEADER_NAME))
                .isNotEqualTo("invalid value with spaces")
                .matches("[0-9a-f-]{36}");
        assertThat(MDC.get(CorrelationIdSupport.MDC_KEY)).isEqualTo("outer-correlation");
    }
}
