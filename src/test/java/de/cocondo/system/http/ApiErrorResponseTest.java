package de.cocondo.system.http;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.List;
import org.junit.jupiter.api.Test;

class ApiErrorResponseTest {

    @Test
    void apiErrorResponseCarriesCanonicalFieldsAndViolations() {
        ApiErrorResponse response = new ApiErrorResponse();
        ApiViolationDTO violation = new ApiViolationDTO(
                "name",
                "must not be blank",
                "NotBlank",
                "springmaster.validation.name"
        );

        response.setStatus(400);
        response.setError("Bad Request");
        response.setErrorType(ApiErrorType.VALIDATION_FAILED.name());
        response.setMessage("Validation failed");
        response.setMessageKey("springmaster.validation.failed");
        response.setErrorId("err-0001");
        response.setCorrelationId("corr-0001");
        response.setPath("/api/demo/catalog/items");
        response.setMethod("POST");
        response.setViolations(List.of(violation));

        assertThat(response.getTimestamp()).isNotBlank();
        assertThat(response.getStatus()).isEqualTo(400);
        assertThat(response.getError()).isEqualTo("Bad Request");
        assertThat(response.getErrorType()).isEqualTo("VALIDATION_FAILED");
        assertThat(response.getMessage()).isEqualTo("Validation failed");
        assertThat(response.getMessageKey()).isEqualTo("springmaster.validation.failed");
        assertThat(response.getErrorId()).isEqualTo("err-0001");
        assertThat(response.getCorrelationId()).isEqualTo("corr-0001");
        assertThat(response.getPath()).isEqualTo("/api/demo/catalog/items");
        assertThat(response.getMethod()).isEqualTo("POST");
        assertThat(response.getViolations()).hasSize(1);
        assertThat(response.getViolations().getFirst().getField()).isEqualTo("name");
    }

    @Test
    void setViolationsDefensivelyHandlesNull() {
        ApiErrorResponse response = new ApiErrorResponse();

        response.setViolations(null);

        assertThat(response.getViolations()).isEmpty();
    }
}
