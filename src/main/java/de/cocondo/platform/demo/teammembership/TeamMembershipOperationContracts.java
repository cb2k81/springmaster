package de.cocondo.platform.demo.teammembership;

import de.cocondo.system.backendcontract.ApiOperationContract;
import de.cocondo.system.backendcontract.ApiOperationContractRegistry;
import de.cocondo.system.backendcontract.ApiOperationEffects;
import de.cocondo.system.backendcontract.ApiOperationKind;
import de.cocondo.system.backendcontract.ApiOperationRole;
import de.cocondo.system.backendcontract.ApiPreconditionContract;
import de.cocondo.system.backendcontract.ApiResourceSemantics;
import de.cocondo.system.backendcontract.ApiSecurityContract;
import java.util.List;
import java.util.Set;
import org.springframework.stereotype.Component;

@Component
final class TeamMembershipOperationContracts {
    private static final String BASE_PATH = "/api/demo/teams/{teamId}/members";
    private static final ApiResourceSemantics RESOURCE = new ApiResourceSemantics(
            "team-membership", "NONE", null, null
    );

    TeamMembershipOperationContracts(ApiOperationContractRegistry registry) {
        registry.register(contract(
                "demo.teams.members.list", "listTeamMembers", "GET", BASE_PATH,
                ApiOperationKind.QUERY, Set.of(ApiOperationRole.RELATION_LIST), "demo:team-membership:read", List.of()
        ));
        registry.register(contract(
                "demo.teams.members.options", "listTeamMemberOptions", "GET", BASE_PATH + "/options",
                ApiOperationKind.QUERY,
                Set.of(ApiOperationRole.CANDIDATE_LIST, ApiOperationRole.REFERENCE_LOOKUP),
                "demo:team-membership:read", List.of()
        ));
        registry.register(contract(
                "demo.teams.members.add", "addTeamMember", "POST", BASE_PATH,
                ApiOperationKind.COMMAND, Set.of(), "demo:team-membership:create", List.of("team-membership")
        ));
        registry.register(contract(
                "demo.teams.members.remove", "removeTeamMember", "DELETE", BASE_PATH + "/{personId}",
                ApiOperationKind.COMMAND, Set.of(ApiOperationRole.ENTITY_DELETE),
                "demo:team-membership:delete", List.of("team-membership")
        ));
        registry.register(contract(
                "demo.teams.members.add.precheck", "precheckAddTeamMember", "POST",
                BASE_PATH + "/commands/add-member/precheck", ApiOperationKind.PRECHECK, Set.of(),
                "demo:team-membership:create", List.of()
        ));
        registry.register(contract(
                "demo.teams.members.capabilities.evaluate", "evaluateTeamMembershipCapabilities", "POST",
                BASE_PATH + "/capabilities/evaluate", ApiOperationKind.CAPABILITY_EVALUATION, Set.of(),
                "demo:team-membership:read", List.of()
        ));
    }

    private ApiOperationContract contract(
            String operationKey,
            String operationId,
            String method,
            String path,
            ApiOperationKind kind,
            Set<ApiOperationRole> roles,
            String permission,
            List<String> affectedResourceKeys
    ) {
        return new ApiOperationContract(
                operationKey,
                operationId,
                method,
                path,
                kind,
                roles,
                new ApiSecurityContract("MANAGEMENT", Set.of(permission), "REQUEST_CONTEXT"),
                ApiPreconditionContract.none(),
                RESOURCE,
                new ApiOperationEffects(affectedResourceKeys)
        );
    }
}
