package de.cocondo.system.backendcontract;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.Operation;
import io.swagger.v3.oas.models.PathItem;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springdoc.core.customizers.OpenApiCustomizer;
import org.springframework.stereotype.Component;

/** Adds the single namespaced profile container to explicitly registered operations. */
@Component
public final class ApiOperationContractCustomizer implements OpenApiCustomizer {
    public static final String EXTENSION_NAME = "x-cocondo-operation-profile";

    private final ApiOperationContractRegistry registry;

    public ApiOperationContractCustomizer(ApiOperationContractRegistry registry) {
        this.registry = registry;
    }

    @Override
    public void customise(OpenAPI openApi) {
        if (openApi.getPaths() == null) {
            return;
        }
        openApi.getPaths().forEach((path, pathItem) -> pathItem.readOperationsMap().forEach((method, operation) -> {
            ApiOperationContract contract = registry.find(method.name(), path, operation.getOperationId());
            if (contract != null) {
                operation.addExtension(EXTENSION_NAME, profile(contract));
            }
        }));
    }

    private Map<String, Object> profile(ApiOperationContract contract) {
        LinkedHashMap<String, Object> profile = new LinkedHashMap<>();
        profile.put("operationKey", contract.operationKey());
        profile.put("operationId", contract.operationId());
        profile.put("operationKind", contract.operationKind().name());
        profile.put("operationRoles", contract.operationRoles().stream().map(Enum::name).sorted().toList());
        profile.put("security", Map.of(
                "classification", contract.security().classification(),
                "permissions", contract.security().permissions().stream().sorted().toList(),
                "targetAuthorization", contract.security().targetAuthorization()
        ));
        profile.put("precondition", Map.of(
                "type", contract.precondition().type(),
                "required", contract.precondition().required(),
                "binding", contract.precondition().binding(),
                "conflictStatus", contract.precondition().conflictStatus()
        ));
        profile.put("resource", Map.of(
                "resourceKey", contract.resourceSemantics().resourceKey(),
                "historyModel", contract.resourceSemantics().historyModel()
        ));
        profile.put("effects", Map.of("affectedResourceKeys", List.copyOf(contract.effects().affectedResourceKeys())));
        return Map.copyOf(profile);
    }
}
