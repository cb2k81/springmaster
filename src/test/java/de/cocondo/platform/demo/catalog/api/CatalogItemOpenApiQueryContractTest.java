package de.cocondo.platform.demo.catalog.api;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import de.cocondo.platform.app.SpringmasterApplication;
import java.util.LinkedHashSet;
import java.util.Set;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

@ActiveProfiles("test")
@SpringBootTest(classes = SpringmasterApplication.class)
@AutoConfigureMockMvc
class CatalogItemOpenApiQueryContractTest {

    private static final String LIST_PATH = "/api/demo/catalog/items";
    private static final String ALL_PATH = "/api/demo/catalog/items/all";
    private static final String COUNT_PATH = "/api/demo/catalog/items/count";

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void openApiDocumentsCatalogItemQueryContractEndpointsAndParameters() throws Exception {
        JsonNode openApi = readOpenApi();

        JsonNode listOperation = operation(openApi, LIST_PATH);
        JsonNode allOperation = operation(openApi, ALL_PATH);
        JsonNode countOperation = operation(openApi, COUNT_PATH);

        assertThat(queryParameterNames(listOperation))
                .containsExactlyInAnyOrder("page", "size", "sortBy", "sortDir", "sku", "name");
        assertThat(queryParameterNames(allOperation))
                .containsExactlyInAnyOrder("sortBy", "sortDir", "sku", "name");
        assertThat(queryParameterNames(countOperation))
                .containsExactlyInAnyOrder("sku", "name");

        assertThat(queryParameterNames(allOperation))
                .doesNotContain("page", "size");
        assertThat(queryParameterNames(countOperation))
                .doesNotContain("page", "size", "sortBy", "sortDir", "arg0", "arg1");

        assertJsonResponsePresent(listOperation);
        assertJsonResponsePresent(allOperation);
        assertJsonResponsePresent(countOperation);
        assertCountResponseSchema(openApi, countOperation);
    }

    private JsonNode readOpenApi() throws Exception {
        String json = mockMvc.perform(get("/api-docs"))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();
        return objectMapper.readTree(json);
    }

    private JsonNode operation(JsonNode openApi, String path) {
        JsonNode operation = openApi.path("paths").path(path).path("get");
        assertThat(operation.isMissingNode())
                .as("OpenAPI GET operation must exist for %s", path)
                .isFalse();
        return operation;
    }

    private Set<String> queryParameterNames(JsonNode operation) {
        Set<String> names = new LinkedHashSet<>();
        for (JsonNode parameter : operation.path("parameters")) {
            if ("query".equals(parameter.path("in").asText())) {
                names.add(parameter.path("name").asText());
            }
        }
        return names;
    }

    private void assertJsonResponsePresent(JsonNode operation) {
        JsonNode schema = responseSchema(operation);
        assertThat(schema.isMissingNode())
                .as("OpenAPI 200 application/json response schema must be present for %s", operation.path("operationId").asText())
                .isFalse();
        assertThat(schema.isObject())
                .as("OpenAPI response schema must be an object node for %s", operation.path("operationId").asText())
                .isTrue();
    }

    private JsonNode responseSchema(JsonNode operation) {
        return operation.path("responses")
                .path("200")
                .path("content")
                .path("application/json")
                .path("schema");
    }

    private void assertCountResponseSchema(JsonNode openApi, JsonNode countOperation) {
        JsonNode schema = responseSchema(countOperation);
        JsonNode resolved = resolveSchema(openApi, schema);

        assertThat(schema.path("$ref").asText(""))
                .as("Count endpoint should expose CountResponseDTO as OpenAPI schema reference")
                .contains("CountResponseDTO");
        assertThat(resolved.path("properties").has("totalElements"))
                .as("CountResponseDTO OpenAPI schema must expose totalElements")
                .isTrue();
    }

    private JsonNode resolveSchema(JsonNode openApi, JsonNode schema) {
        String ref = schema.path("$ref").asText();
        if (ref == null || ref.isBlank()) {
            return schema;
        }
        assertThat(ref)
                .as("Only local OpenAPI schema references are supported by this evidence test")
                .startsWith("#/components/schemas/");
        String schemaName = ref.substring("#/components/schemas/".length());
        JsonNode resolved = openApi.path("components").path("schemas").path(schemaName);
        assertThat(resolved.isMissingNode())
                .as("OpenAPI component schema must exist: %s", schemaName)
                .isFalse();
        return resolved;
    }
}
