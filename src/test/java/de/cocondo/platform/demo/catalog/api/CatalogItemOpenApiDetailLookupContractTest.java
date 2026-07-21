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
class CatalogItemOpenApiDetailLookupContractTest {

    private static final String DETAIL_PATH = "/api/demo/catalog/items/{id}";
    private static final String BY_SKU_PATH = "/api/demo/catalog/items/by-sku/{sku}";

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void openApiDocumentsCatalogItemDetailAndAlternateKeyLookupContract() throws Exception {
        JsonNode openApi = readOpenApi();

        JsonNode detailOperation = operation(openApi, DETAIL_PATH);
        JsonNode bySkuOperation = operation(openApi, BY_SKU_PATH);

        assertThat(pathParameterNames(detailOperation))
                .containsExactly("id");
        assertThat(pathParameterNames(bySkuOperation))
                .containsExactly("sku");

        assertThat(queryParameterNames(detailOperation))
                .doesNotContain("page", "size", "sortBy", "sortDir", "arg0", "arg1");
        assertThat(queryParameterNames(bySkuOperation))
                .doesNotContain("page", "size", "sortBy", "sortDir", "arg0", "arg1");

        assertCatalogItemResponseSchema(openApi, detailOperation);
        assertCatalogItemResponseSchema(openApi, bySkuOperation);
        assertNoRepositoryVocabulary(detailOperation);
        assertNoRepositoryVocabulary(bySkuOperation);
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

    private Set<String> pathParameterNames(JsonNode operation) {
        Set<String> names = new LinkedHashSet<>();
        for (JsonNode parameter : operation.path("parameters")) {
            if ("path".equals(parameter.path("in").asText())) {
                names.add(parameter.path("name").asText());
            }
        }
        return names;
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

    private void assertCatalogItemResponseSchema(JsonNode openApi, JsonNode operation) {
        JsonNode schema = firstResponseSchema(operation, "200");
        assertThat(schema.isMissingNode())
                .as("OpenAPI 200 response schema must be present for %s", operation.path("operationId").asText())
                .isFalse();

        JsonNode resolved = resolveSchema(openApi, schema);
        String ref = schema.path("$ref").asText("");
        assertThat(ref + resolved.toString())
                .as("Detail/lookup endpoints must expose CatalogItemDTO response evidence")
                .contains("CatalogItemDTO");
    }

    private JsonNode firstResponseSchema(JsonNode operation, String status) {
        JsonNode content = operation.path("responses").path(status).path("content");
        JsonNode jsonSchema = content.path("application/json").path("schema");
        if (!jsonSchema.isMissingNode()) {
            return jsonSchema;
        }
        JsonNode wildcardSchema = content.path("*/*").path("schema");
        if (!wildcardSchema.isMissingNode()) {
            return wildcardSchema;
        }
        return content.path("schema");
    }

    private void assertNoRepositoryVocabulary(JsonNode operation) {
        String operationId = operation.path("operationId").asText("");
        assertThat(operationId)
                .doesNotContain("findOne")
                .doesNotContain("findFirst")
                .doesNotContain("findAny");
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
