package de.cocondo.platform.demo.teammembership;

import io.swagger.v3.oas.annotations.Operation;
import jakarta.validation.Valid;
import java.net.URI;
import java.util.List;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/demo/teams/{teamId}/members")
public final class TeamMembershipController {
    private final TeamMembershipService service;

    public TeamMembershipController(TeamMembershipService service) {
        this.service = service;
    }

    @GetMapping
    @Operation(operationId = "listTeamMembers")
    public List<TeamMemberDTO> list(
            @RequestHeader("X-Demo-Actor") String actorId,
            @PathVariable("teamId") String teamId
    ) {
        return service.list(actorId, teamId);
    }

    @GetMapping("/options")
    @Operation(operationId = "listTeamMemberOptions")
    public List<TeamMemberOptionDTO> options(
            @RequestHeader("X-Demo-Actor") String actorId,
            @PathVariable("teamId") String teamId
    ) {
        return service.options(actorId, teamId);
    }

    @PostMapping
    @Operation(operationId = "addTeamMember")
    public ResponseEntity<TeamMemberDTO> add(
            @RequestHeader("X-Demo-Actor") String actorId,
            @PathVariable("teamId") String teamId,
            @Valid @RequestBody AddTeamMemberDTO request
    ) {
        TeamMemberDTO created = service.add(actorId, teamId, request.personId());
        URI location = URI.create("/api/demo/teams/" + teamId + "/members/" + created.personId());
        return ResponseEntity.created(location).body(created);
    }

    @DeleteMapping("/{personId}")
    @Operation(operationId = "removeTeamMember")
    public ResponseEntity<Void> remove(
            @RequestHeader("X-Demo-Actor") String actorId,
            @PathVariable("teamId") String teamId,
            @PathVariable("personId") String personId
    ) {
        service.remove(actorId, teamId, personId);
        return ResponseEntity.noContent().build();
    }

    @PostMapping("/commands/add-member/precheck")
    @Operation(operationId = "precheckAddTeamMember")
    public TeamMembershipPrecheckDTO precheckAdd(
            @RequestHeader("X-Demo-Actor") String actorId,
            @PathVariable("teamId") String teamId,
            @Valid @RequestBody AddTeamMemberDTO request
    ) {
        return service.addPrecheck(actorId, teamId, request.personId());
    }

    @PostMapping("/capabilities/evaluate")
    @Operation(operationId = "evaluateTeamMembershipCapabilities")
    public TeamMembershipCapabilitiesDTO evaluateCapabilities(
            @RequestHeader("X-Demo-Actor") String actorId,
            @PathVariable("teamId") String teamId,
            @Valid @RequestBody TeamMembershipCapabilityRequestDTO request
    ) {
        return service.capabilities(actorId, teamId, request.personId());
    }
}
