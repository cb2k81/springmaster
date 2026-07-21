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
class CatalogItemOpenApiWriteContractTest {

    private static final String COLLECTION_PATH = "/api/demo/catalog/items";
    private static final String ITEM_PATH = "/api/demo/catalog/items/{id}";

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void openApiDocumentsCatalogItemCreateUpdateAndBodylessDeleteContract() throws Exception {
        JsonNode openApi = readOpenApi();

        JsonNode postOperation = operation(openApi, COLLECTION_PATH, "post");
        JsonNode putOperation = operation(openApi, ITEM_PATH, "put");
        JsonNode deleteOperation = operation(openApi, ITEM_PATH, "delete");

        assertRequestBodySchema(openApi, postOperation, "CatalogItemCreateDTO");
        assertRequestBodySchema(openApi, putOperation, "CatalogItemUpdateDTO");
        assertNoDeleteRequestBody(deleteOperation);

        assertThat(pathParameterNames(postOperation))
                .isEmpty();
        assertThat(pathParameterNames(putOperation))
                .containsExactly("id");
        assertThat(pathParameterNames(deleteOperation))
                .containsExactly("id");

        assertThat(queryParameterNames(postOperation))
                .doesNotContain("page", "size", "sortBy", "sortDir", "arg0", "arg1");
        assertThat(queryParameterNames(putOperation))
                .doesNotContain("page", "size", "sortBy", "sortDir", "arg0", "arg1");
        assertThat(queryParameterNames(deleteOperation))
                .doesNotContain("page", "size", "sortBy", "sortDir", "arg0", "arg1");

        assertCatalogItemResponseSchema(openApi, postOperation);
        assertCatalogItemResponseSchema(openApi, putOperation);
        assertNoRepositoryVocabulary(postOperation);
        assertNoRepositoryVocabulary(putOperation);
        assertNoRepositoryVocabulary(deleteOperation);
    }

    private JsonNode readOpenApi() throws Exception {
        String json = mockMvc.perform(get("/api-docs"))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();
        return objectMapper.readTree(json);
    }

    private JsonNode operation(JsonNode openApi, String path, String method) {
        JsonNode operation = openApi.path("paths").path(path).path(method);
        assertThat(operation.isMissingNode())
                .as("OpenAPI %s operation must exist for %s", method.toUpperCase(), path)
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

    private void assertRequestBodySchema(JsonNode openApi, JsonNode operation, String expectedSchemaName) {
        JsonNode schema = firstRequestBodySchema(operation);
        assertThat(schema.isMissingNode())
                .as("OpenAPI request body schema must be present for %s", operation.path("operationId").asText())
                .isFalse();
        JsonNode resolved = resolveSchema(openApi, schema);
        String ref = schema.path("$ref").asText("");
        assertThat(ref + resolved.toString())
                .as("Write endpoint must expose %s request-body evidence", expectedSchemaName)
                .contains(expectedSchemaName);
    }

    private JsonNode firstRequestBodySchema(JsonNode operation) {
        JsonNode content = operation.path("requestBody").path("content");
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

    private void assertNoDeleteRequestBody(JsonNode deleteOperation) {
        assertThat(deleteOperation.has("requestBody"))
                .as("Single-resource DELETE must not expose an OpenAPI requestBody")
                .isFalse();
    }

    private void assertCatalogItemResponseSchema(JsonNode openApi, JsonNode operation) {
        JsonNode schema = first2xxResponseSchema(operation);
        assertThat(schema.isMissingNode())
                .as("OpenAPI 2xx response schema must be present for %s", operation.path("operationId").asText())
                .isFalse();

        JsonNode resolved = resolveSchema(openApi, schema);
        String ref = schema.path("$ref").asText("");
        assertThat(ref + resolved.toString())
                .as("Create/update endpoints must expose CatalogItemDTO response evidence")
                .contains("CatalogItemDTO");
    }

    private JsonNode first2xxResponseSchema(JsonNode operation) {
        JsonNode responses = operation.path("responses");
        for (String status : Set.of("201", "200")) {
            JsonNode schema = firstResponseSchema(responses.path(status));
            if (!schema.isMissingNode()) {
                return schema;
            }
        }
        return responses.path("default").path("content").path("application/json").path("schema");
    }

    private JsonNode firstResponseSchema(JsonNode response) {
        JsonNode content = response.path("content");
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
                .doesNotContain("saveAndFlush")
                .doesNotContain("deleteAll")
                .doesNotContain("deleteInBatch")
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
