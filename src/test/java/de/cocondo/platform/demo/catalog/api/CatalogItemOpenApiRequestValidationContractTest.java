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
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest(classes = SpringmasterApplication.class)
@AutoConfigureMockMvc
class CatalogItemOpenApiRequestValidationContractTest {

    private static final String COLLECTION_PATH = "/api/demo/catalog/items";
    private static final String ITEM_PATH = "/api/demo/catalog/items/{id}";

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void openApiRequiredFieldsMatchCatalogItemBeanValidationBoundary() throws Exception {
        JsonNode openApi = readOpenApi();

        JsonNode createOperation = operation(openApi, COLLECTION_PATH, "post");
        JsonNode updateOperation = operation(openApi, ITEM_PATH, "put");

        assertRequestBodySchemaName(openApi, createOperation, "CatalogItemCreateDTO");
        assertRequestBodySchemaName(openApi, updateOperation, "CatalogItemUpdateDTO");

        JsonNode createSchema = componentSchema(openApi, "CatalogItemCreateDTO");
        JsonNode updateSchema = componentSchema(openApi, "CatalogItemUpdateDTO");

        assertRequiredFields(createSchema, "sku", "name");
        assertRequiredFields(updateSchema, "name");
        assertOptionalFields(createSchema, "description", "tags", "availability");
        assertOptionalFields(updateSchema, "description", "tags", "availability");

        assertMaxLength(createSchema, "sku", 128);
        assertMaxLength(createSchema, "name", 255);
        assertMaxLength(createSchema, "description", 1000);
        assertMaxLength(updateSchema, "name", 255);
        assertMaxLength(updateSchema, "description", 1000);
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

    private void assertRequestBodySchemaName(JsonNode openApi, JsonNode operation, String expectedSchemaName) {
        JsonNode schema = firstRequestBodySchema(operation);
        assertThat(schema.isMissingNode())
                .as("OpenAPI request body schema must be present for %s", operation.path("operationId").asText())
                .isFalse();
        String ref = schema.path("$ref").asText("");
        JsonNode resolved = resolveSchema(openApi, schema);
        assertThat(ref + resolved.toString())
                .as("Request body must expose %s", expectedSchemaName)
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

    private JsonNode componentSchema(JsonNode openApi, String schemaName) {
        JsonNode schema = openApi.path("components").path("schemas").path(schemaName);
        assertThat(schema.isMissingNode())
                .as("OpenAPI component schema must exist: %s", schemaName)
                .isFalse();
        return schema;
    }

    private void assertRequiredFields(JsonNode schema, String... expectedFields) {
        assertThat(requiredFieldNames(schema))
                .containsExactlyInAnyOrder(expectedFields);
    }

    private void assertOptionalFields(JsonNode schema, String... optionalFields) {
        assertThat(requiredFieldNames(schema))
                .doesNotContain(optionalFields);
    }

    private Set<String> requiredFieldNames(JsonNode schema) {
        Set<String> fields = new LinkedHashSet<>();
        for (JsonNode item : schema.path("required")) {
            fields.add(item.asText());
        }
        return fields;
    }

    private void assertMaxLength(JsonNode schema, String property, int expectedMaxLength) {
        JsonNode maxLength = schema.path("properties").path(property).path("maxLength");
        assertThat(maxLength.isMissingNode())
                .as("OpenAPI maxLength must be present for %s", property)
                .isFalse();
        assertThat(maxLength.asInt())
                .as("OpenAPI maxLength for %s", property)
                .isEqualTo(expectedMaxLength);
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
        return componentSchema(openApi, schemaName);
    }
}
