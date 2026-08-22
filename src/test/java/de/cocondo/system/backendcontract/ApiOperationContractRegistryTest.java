package de.cocondo.system.backendcontract;

import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.util.List;
import java.util.Set;
import org.junit.jupiter.api.Test;

class ApiOperationContractRegistryTest {

    @Test
    void rejectsDuplicateOperationKeyAndTechnicalIdentity() {
        ApiOperationContractRegistry registry = new ApiOperationContractRegistry();
        ApiOperationContract first = contract("demo.items.list", "listItems", "/api/demo/items");
        registry.register(first);

        assertThatThrownBy(() -> registry.register(contract("demo.items.list", "other", "/api/demo/other")))
                .isInstanceOf(IllegalStateException.class)
                .hasMessageContaining("Duplicate operationKey");
        assertThatThrownBy(() -> registry.register(contract("demo.items.other", "listItems", "/api/demo/items")))
                .isInstanceOf(IllegalStateException.class)
                .hasMessageContaining("Duplicate technical operation identity");
    }

    @Test
    void rejectsStructurallyIncompleteEntries() {
        assertThatThrownBy(() -> contract("", "listItems", "/api/demo/items"))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("operationKey");
    }

    private ApiOperationContract contract(String key, String operationId, String path) {
        return new ApiOperationContract(
                key,
                operationId,
                "GET",
                path,
                ApiOperationKind.QUERY,
                Set.of(ApiOperationRole.ENTITY_LIST),
                new ApiSecurityContract("MANAGEMENT", Set.of("demo:item:read"), "NONE"),
                ApiPreconditionContract.none(),
                new ApiResourceSemantics("item", "NONE", null, null),
                new ApiOperationEffects(List.of())
        );
    }
}
