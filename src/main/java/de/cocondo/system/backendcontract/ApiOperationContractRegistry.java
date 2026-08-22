package de.cocondo.system.backendcontract;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Component;

/** Fail-closed registry used only to author opted-in OpenAPI operation profiles. */
@Component
public final class ApiOperationContractRegistry {
    private final Map<String, ApiOperationContract> byOperationKey = new LinkedHashMap<>();
    private final Map<String, ApiOperationContract> byTechnicalIdentity = new LinkedHashMap<>();

    public synchronized void register(ApiOperationContract contract) {
        if (byOperationKey.containsKey(contract.operationKey())) {
            throw new IllegalStateException("Duplicate operationKey: " + contract.operationKey());
        }
        String technicalIdentity = technicalIdentity(contract.method(), contract.path(), contract.operationId());
        if (byTechnicalIdentity.containsKey(technicalIdentity)) {
            throw new IllegalStateException("Duplicate technical operation identity: " + technicalIdentity);
        }
        byOperationKey.put(contract.operationKey(), contract);
        byTechnicalIdentity.put(technicalIdentity, contract);
    }

    public synchronized List<ApiOperationContract> entries() {
        ArrayList<ApiOperationContract> entries = new ArrayList<>(byOperationKey.values());
        entries.sort(Comparator.comparing(ApiOperationContract::operationKey));
        return List.copyOf(entries);
    }

    public synchronized ApiOperationContract find(String method, String path, String operationId) {
        return byTechnicalIdentity.get(technicalIdentity(method, path, operationId));
    }

    private String technicalIdentity(String method, String path, String operationId) {
        return method.toUpperCase() + " " + path + " " + operationId;
    }
}
