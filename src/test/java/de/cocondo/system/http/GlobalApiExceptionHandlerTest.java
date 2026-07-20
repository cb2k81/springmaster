package de.cocondo.system.http;

import static org.assertj.core.api.Assertions.assertThat;

import de.cocondo.system.exception.EntityAlreadyExistsException;
import de.cocondo.system.exception.ResourceNotFoundException;
import de.cocondo.system.observability.CorrelationIdSupport;
import org.junit.jupiter.api.Test;
import org.springframework.http.ResponseEntity;
import org.springframework.mock.web.MockHttpServletRequest;

class GlobalApiExceptionHandlerTest {

    private final GlobalApiExceptionHandler handler = new GlobalApiExceptionHandler(new ApiErrorIdGenerator());

    @Test
    void handlesResourceNotFoundWithCanonicalNotFoundEnvelope() {
        MockHttpServletRequest request = request("GET", "/api/demo/catalog/items/UNKNOWN");

        ResponseEntity<ApiErrorResponse> response = handler.handleResourceNotFound(
                new ResourceNotFoundException("Catalog item not found", "catalog.item.not-found"),
                request
        );

        assertThat(response.getStatusCode().value()).isEqualTo(404);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().getErrorType()).isEqualTo(ApiErrorType.RESOURCE_NOT_FOUND.name());
        assertThat(response.getBody().getMessage()).isEqualTo("Catalog item not found");
        assertThat(response.getBody().getMessageKey()).isEqualTo("catalog.item.not-found");
        assertThat(response.getBody().getErrorId()).startsWith("err-");
        assertThat(response.getBody().getPath()).isEqualTo("/api/demo/catalog/items/UNKNOWN");
        assertThat(response.getBody().getMethod()).isEqualTo("GET");
    }

    @Test
    void handlesEntityAlreadyExistsWithCanonicalConflictEnvelope() {
        MockHttpServletRequest request = request("POST", "/api/demo/catalog/items");

        ResponseEntity<ApiErrorResponse> response = handler.handleEntityAlreadyExists(
                new EntityAlreadyExistsException("Catalog item already exists: SKU=SKU-1", "catalog.item.conflict"),
                request
        );

        assertThat(response.getStatusCode().value()).isEqualTo(409);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().getErrorType()).isEqualTo(ApiErrorType.CONFLICT.name());
        assertThat(response.getBody().getMessage()).contains("SKU");
        assertThat(response.getBody().getMessageKey()).isEqualTo("catalog.item.conflict");
    }

    @Test
    void handlesUnexpectedExceptionWithSafeInternalErrorEnvelope() {
        MockHttpServletRequest request = request("GET", "/api/demo/catalog/items");

        ResponseEntity<ApiErrorResponse> response = handler.handleUnexpectedException(
                new RuntimeException("java.sql.SQLException: secret table name"),
                request
        );

        assertThat(response.getStatusCode().value()).isEqualTo(500);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().getErrorType()).isEqualTo(ApiErrorType.INTERNAL_ERROR.name());
        assertThat(response.getBody().getMessage()).isEqualTo("Internal server error");
        assertThat(response.getBody().getMessage()).doesNotContain("SQLException");
        assertThat(response.getBody().getErrorId()).startsWith("err-");
    }

    @Test
    void propagatesCorrelationIdWhenProvided() {
        MockHttpServletRequest request = request("GET", "/api/demo/catalog/items/UNKNOWN");
        request.setAttribute(CorrelationIdSupport.REQUEST_ATTRIBUTE, "corr-123");

        ResponseEntity<ApiErrorResponse> response = handler.handleResourceNotFound(
                new ResourceNotFoundException("Catalog item not found"),
                request
        );

        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().getCorrelationId()).isEqualTo("corr-123");
    }

    private MockHttpServletRequest request(String method, String uri) {
        return new MockHttpServletRequest(method, uri);
    }
}
