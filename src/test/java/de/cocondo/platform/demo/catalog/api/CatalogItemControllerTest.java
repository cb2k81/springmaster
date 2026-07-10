package de.cocondo.platform.demo.catalog.api;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.blankOrNullString;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import de.cocondo.platform.app.SpringmasterApplication;
import de.cocondo.platform.demo.catalog.CatalogItemCreateDTO;
import de.cocondo.platform.demo.catalog.CatalogItemDTO;
import de.cocondo.platform.demo.catalog.CatalogItemService;
import de.cocondo.platform.demo.catalog.CatalogItemUpdateDTO;
import de.cocondo.platform.demo.catalog.CatalogItemAvailabilityDTO;
import java.time.LocalDateTime;
import java.util.LinkedHashSet;
import java.util.Set;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

@SpringBootTest(classes = SpringmasterApplication.class)
@AutoConfigureMockMvc
class CatalogItemControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private CatalogItemService service;

    @BeforeEach
    void resetService() {
        service.clear();
    }

    @Test
    void listsCatalogItemsWithPagedEnvelopeAndSortBy() throws Exception {
        service.create(new CatalogItemCreateDTO("SKU-2", "Beta Item", null));
        service.create(new CatalogItemCreateDTO("SKU-1", "Alpha Item", null));

        mockMvc.perform(get("/api/demo/catalog/items")
                        .param("page", "0")
                        .param("size", "10")
                        .param("sortBy", "sku")
                        .param("sortDir", "ASC"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.items", hasSize(2)))
                .andExpect(jsonPath("$.items[0].sku").value("SKU-1"))
                .andExpect(jsonPath("$.items[1].sku").value("SKU-2"))
                .andExpect(jsonPath("$.page").value(0))
                .andExpect(jsonPath("$.size").value(10))
                .andExpect(jsonPath("$.totalElements").value(2))
                .andExpect(jsonPath("$.totalPages").value(1));
    }

    @Test
    void listsCatalogItemsWithFiltersAndFilteredTotalElements() throws Exception {
        service.create(new CatalogItemCreateDTO("SKU-1", "Alpha Item", null));
        service.create(new CatalogItemCreateDTO("SKU-2", "Alphabetic Item", null));
        service.create(new CatalogItemCreateDTO("SKU-3", "Beta Item", null));

        mockMvc.perform(get("/api/demo/catalog/items")
                        .param("page", "0")
                        .param("size", "1")
                        .param("sortBy", "sku")
                        .param("sortDir", "ASC")
                        .param("name", "alpha"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.items", hasSize(1)))
                .andExpect(jsonPath("$.items[0].sku").value("SKU-1"))
                .andExpect(jsonPath("$.page").value(0))
                .andExpect(jsonPath("$.size").value(1))
                .andExpect(jsonPath("$.totalElements").value(2))
                .andExpect(jsonPath("$.totalPages").value(2));
    }

    @Test
    void listsAllCatalogItemsWithSameFiltersAndSortWithoutPagingEnvelope() throws Exception {
        service.create(new CatalogItemCreateDTO("SKU-2", "Alpha Item", null));
        service.create(new CatalogItemCreateDTO("SKU-1", "Alphabetic Item", null));
        service.create(new CatalogItemCreateDTO("SKU-3", "Beta Item", null));

        mockMvc.perform(get("/api/demo/catalog/items/all")
                        .param("sortBy", "sku")
                        .param("sortDir", "ASC")
                        .param("name", "alpha"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(2)))
                .andExpect(jsonPath("$[0].sku").value("SKU-1"))
                .andExpect(jsonPath("$[1].sku").value("SKU-2"));
    }

    @Test
    void returnsEmptyPagedAndAllResponsesForFiltersWithoutMatches() throws Exception {
        service.create(new CatalogItemCreateDTO("SKU-1", "Alpha Item", null));

        mockMvc.perform(get("/api/demo/catalog/items")
                        .param("sku", "SKU-DOES-NOT-EXIST"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.items", hasSize(0)))
                .andExpect(jsonPath("$.totalElements").value(0))
                .andExpect(jsonPath("$.totalPages").value(0));

        mockMvc.perform(get("/api/demo/catalog/items/all")
                        .param("sku", "SKU-DOES-NOT-EXIST"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(0)));

        mockMvc.perform(get("/api/demo/catalog/items/count")
                        .param("sku", "SKU-DOES-NOT-EXIST"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalElements").value(0));
    }

    @Test
    void countsCatalogItemsWithSameFiltersAsPagedAndAllQueries() throws Exception {
        service.create(new CatalogItemCreateDTO("SKU-1", "Alpha Item", null));
        service.create(new CatalogItemCreateDTO("SKU-2", "Alphabetic Item", null));
        service.create(new CatalogItemCreateDTO("SKU-3", "Beta Item", null));

        mockMvc.perform(get("/api/demo/catalog/items/count"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalElements").value(3));

        mockMvc.perform(get("/api/demo/catalog/items/count")
                        .param("name", "alpha"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalElements").value(2));

        mockMvc.perform(get("/api/demo/catalog/items/count")
                        .param("sku", "SKU-2"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalElements").value(1));
    }

    @Test
    void rejectsPagingAndSortParametersForCountEndpoint() throws Exception {
        mockMvc.perform(get("/api/demo/catalog/items/count")
                        .param("page", "0"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errorType").value("INVALID_REQUEST"))
                .andExpect(jsonPath("$.message", containsString("Unsupported count query parameter")))
                .andExpect(jsonPath("$.message", containsString("page")));

        mockMvc.perform(get("/api/demo/catalog/items/count")
                        .param("sortBy", "sku"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errorType").value("INVALID_REQUEST"))
                .andExpect(jsonPath("$.message", containsString("sortBy")));
    }

    @Test
    void createsCatalogItemWithOpaqueIdLocation() throws Exception {
        CatalogItemCreateDTO payload = new CatalogItemCreateDTO(" SKU-1 ", "Demo Item", "Description");
        payload.setTags(new LinkedHashSet<>(Set.of("demo", "catalog")));

        mockMvc.perform(post("/api/demo/catalog/items")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(payload)))
                .andExpect(status().isCreated())
                .andExpect(header().string(HttpHeaders.LOCATION, containsString("/api/demo/catalog/items/")))
                .andExpect(header().string(HttpHeaders.LOCATION, not("/api/demo/catalog/items/SKU-1")))
                .andExpect(jsonPath("$.id").isNotEmpty())
                .andExpect(jsonPath("$.sku").value("SKU-1"))
                .andExpect(jsonPath("$.name").value("Demo Item"))
                .andExpect(jsonPath("$.description").value("Description"))
                .andExpect(jsonPath("$.tags", hasSize(2)))
                .andExpect(jsonPath("$.persistenceVersion").value(0));
    }

    @Test
    void findsCatalogItemByOpaqueId() throws Exception {
        CatalogItemDTO created = service.create(new CatalogItemCreateDTO("SKU-1", "Demo Item", null));

        mockMvc.perform(get("/api/demo/catalog/items/{id}", created.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(created.getId()))
                .andExpect(jsonPath("$.sku").value("SKU-1"));
    }

    @Test
    void findsCatalogItemBySkuCaseInsensitivelyThroughBusinessKeyLookup() throws Exception {
        service.create(new CatalogItemCreateDTO("SKU-1", "Demo Item", null));

        mockMvc.perform(get("/api/demo/catalog/items/by-sku/sku-1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.sku").value("SKU-1"));
    }

    @Test
    void updatesCatalogItemByOpaqueId() throws Exception {
        CatalogItemDTO created = service.create(new CatalogItemCreateDTO("SKU-1", "Demo Item", null));
        CatalogItemUpdateDTO payload = new CatalogItemUpdateDTO("Updated Item", "Updated Description");
        payload.setTags(new LinkedHashSet<>(Set.of("updated")));

        mockMvc.perform(put("/api/demo/catalog/items/{id}", created.getId())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(payload)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(created.getId()))
                .andExpect(jsonPath("$.sku").value("SKU-1"))
                .andExpect(jsonPath("$.name").value("Updated Item"))
                .andExpect(jsonPath("$.description").value("Updated Description"))
                .andExpect(jsonPath("$.tags", hasSize(1)));
    }


    @Test
    void returnsBadRequestForInvalidUpdatePayload() throws Exception {
        CatalogItemDTO created = service.create(new CatalogItemCreateDTO("SKU-1", "Demo Item", null));
        CatalogItemUpdateDTO payload = new CatalogItemUpdateDTO(" ", "Updated Description");

        mockMvc.perform(put("/api/demo/catalog/items/{id}", created.getId())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(payload)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errorType").value("VALIDATION_FAILED"))
                .andExpect(jsonPath("$.violations[0].field").value("name"));
    }

    @Test
    void returnsBadRequestForInvalidAvailabilityPayload() throws Exception {
        CatalogItemDTO created = service.create(new CatalogItemCreateDTO("SKU-1", "Demo Item", null));
        CatalogItemUpdateDTO payload = new CatalogItemUpdateDTO("Updated Item", "Updated Description");
        payload.setAvailability(new CatalogItemAvailabilityDTO(
                LocalDateTime.of(2026, 12, 31, 0, 0),
                LocalDateTime.of(2026, 1, 1, 0, 0)
        ));

        mockMvc.perform(put("/api/demo/catalog/items/{id}", created.getId())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(payload)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errorType").value("VALIDATION_FAILED"))
                .andExpect(jsonPath("$.violations[0].field").value("availability.chronological"));
    }

    @Test
    void deletesCatalogItemByOpaqueIdBodylessly() throws Exception {
        CatalogItemDTO created = service.create(new CatalogItemCreateDTO("SKU-1", "Demo Item", null));

        mockMvc.perform(delete("/api/demo/catalog/items/{id}", created.getId()))
                .andExpect(status().isNoContent());

        mockMvc.perform(get("/api/demo/catalog/items/{id}", created.getId()))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.errorId").value(not(blankOrNullString())))
                .andExpect(jsonPath("$.errorType").value("RESOURCE_NOT_FOUND"));
    }

    @Test
    void returnsNotFoundErrorBodyForUnknownId() throws Exception {
        mockMvc.perform(get("/api/demo/catalog/items/UNKNOWN-ID"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.errorId").value(not(blankOrNullString())))
                .andExpect(jsonPath("$.status").value(404))
                .andExpect(jsonPath("$.error").value("Not Found"))
                .andExpect(jsonPath("$.errorType").value("RESOURCE_NOT_FOUND"))
                .andExpect(jsonPath("$.path").value("/api/demo/catalog/items/UNKNOWN-ID"))
                .andExpect(jsonPath("$.method").value("GET"));
    }

    @Test
    void returnsNotFoundErrorBodyForUnknownSku() throws Exception {
        mockMvc.perform(get("/api/demo/catalog/items/by-sku/UNKNOWN"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.errorType").value("RESOURCE_NOT_FOUND"));
    }

    @Test
    void returnsBadRequestForInvalidPayloadWithViolations() throws Exception {
        CatalogItemCreateDTO payload = new CatalogItemCreateDTO(" ", "Demo Item", null);

        mockMvc.perform(post("/api/demo/catalog/items")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(payload)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errorId").value(not(blankOrNullString())))
                .andExpect(jsonPath("$.status").value(400))
                .andExpect(jsonPath("$.errorType").value("VALIDATION_FAILED"))
                .andExpect(jsonPath("$.message").value("Validation failed"))
                .andExpect(jsonPath("$.path").value("/api/demo/catalog/items"))
                .andExpect(jsonPath("$.method").value("POST"))
                .andExpect(jsonPath("$.violations", hasSize(1)))
                .andExpect(jsonPath("$.violations[0].field").value("sku"));
    }

    @Test
    void returnsBadRequestForInvalidSortBy() throws Exception {
        mockMvc.perform(get("/api/demo/catalog/items")
                        .param("sortBy", "createdAt"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errorId").value(not(blankOrNullString())))
                .andExpect(jsonPath("$.errorType").value("INVALID_REQUEST"))
                .andExpect(jsonPath("$.message", containsString("sortBy")));
    }

    @Test
    void returnsBadRequestForInvalidPagingAndSortDirection() throws Exception {
        mockMvc.perform(get("/api/demo/catalog/items")
                        .param("page", "-1"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errorType").value("INVALID_REQUEST"))
                .andExpect(jsonPath("$.message", containsString("page")));

        mockMvc.perform(get("/api/demo/catalog/items")
                        .param("size", "0"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errorType").value("INVALID_REQUEST"))
                .andExpect(jsonPath("$.message", containsString("size")));

        mockMvc.perform(get("/api/demo/catalog/items/all")
                        .param("sortDir", "sideways"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errorType").value("INVALID_REQUEST"))
                .andExpect(jsonPath("$.message", containsString("sortDir")));
    }

    @Test
    void returnsConflictForDuplicateSkuWithStandardErrorBody() throws Exception {
        service.create(new CatalogItemCreateDTO("SKU-1", "Demo Item", null));
        CatalogItemCreateDTO payload = new CatalogItemCreateDTO("sku-1", "Other Item", null);

        mockMvc.perform(post("/api/demo/catalog/items")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(payload)))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.errorId").value(not(blankOrNullString())))
                .andExpect(jsonPath("$.status").value(409))
                .andExpect(jsonPath("$.errorType").value("CONFLICT"))
                .andExpect(jsonPath("$.message", containsString("SKU")));
    }

    @Test
    void createLocationCanBeUsedForDetailLookup() throws Exception {
        CatalogItemCreateDTO payload = new CatalogItemCreateDTO("SKU-1", "Demo Item", null);

        MvcResult result = mockMvc.perform(post("/api/demo/catalog/items")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(payload)))
                .andExpect(status().isCreated())
                .andReturn();

        JsonNode body = objectMapper.readTree(result.getResponse().getContentAsString());
        String location = result.getResponse().getHeader(HttpHeaders.LOCATION);

        mockMvc.perform(get(location))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(body.get("id").asText()))
                .andExpect(jsonPath("$.sku").value("SKU-1"));
    }
}
