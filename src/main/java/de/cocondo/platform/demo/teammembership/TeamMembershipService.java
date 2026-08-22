package de.cocondo.platform.demo.teammembership;

import de.cocondo.system.exception.EntityAlreadyExistsException;
import de.cocondo.system.exception.ResourceNotFoundException;
import java.util.List;
import java.util.Locale;
import org.springframework.stereotype.Service;

@Service
public final class TeamMembershipService {
    private final TeamMembershipPolicy policy;
    private final TeamMembershipRepository repository;

    public TeamMembershipService(TeamMembershipPolicy policy, TeamMembershipRepository repository) {
        this.policy = policy;
        this.repository = repository;
    }

    public synchronized List<TeamMemberDTO> list(String actorId, String teamId) {
        requireTeam(teamId);
        policy.requireAllowed(actorId, teamId);
        return repository.findMembers(teamId);
    }

    public synchronized List<TeamMemberOptionDTO> options(String actorId, String teamId) {
        requireTeam(teamId);
        policy.requireAllowed(actorId, teamId);
        return repository.findCandidates(teamId);
    }

    public synchronized TeamMemberDTO add(String actorId, String teamId, String personId) {
        requireTeam(teamId);
        requirePerson(personId);
        policy.requireAllowed(actorId, teamId);
        if (repository.membershipExists(teamId, personId)) {
            throw new EntityAlreadyExistsException(
                    "Team membership already exists", "team-membership.already-exists"
            );
        }
        return repository.add(teamId, personId);
    }

    public synchronized void remove(String actorId, String teamId, String personId) {
        requireTeam(teamId);
        policy.requireAllowed(actorId, teamId);
        if (!repository.remove(teamId, personId)) {
            throw notFound("Team member not found", "team-membership.not-found");
        }
    }

    public synchronized TeamMembershipPrecheckDTO addPrecheck(String actorId, String teamId, String personId) {
        requireTeam(teamId);
        requirePerson(personId);
        TeamMembershipPolicy.Decision decision = policy.evaluate(actorId, teamId);
        if (!decision.allowed()) {
            return blocked("add-member", personId, decision, false);
        }
        if (repository.membershipExists(teamId, personId)) {
            return blocked("add-member", personId,
                    new TeamMembershipPolicy.Decision(false, "MEMBERSHIP_EXISTS", "Person is already a member"), false);
        }
        return allowed("add-member", personId, false);
    }

    public synchronized TeamMembershipPrecheckDTO removePrecheck(String actorId, String teamId, String personId) {
        requireTeam(teamId);
        TeamMembershipPolicy.Decision decision = policy.evaluate(actorId, teamId);
        if (!decision.allowed()) {
            return blocked("remove-member", personId, decision, true);
        }
        if (!repository.membershipExists(teamId, personId)) {
            return blocked("remove-member", personId,
                    new TeamMembershipPolicy.Decision(false, "MEMBERSHIP_MISSING", "Person is not a member"), true);
        }
        return allowed("remove-member", personId, true);
    }

    public synchronized TeamMembershipCapabilitiesDTO capabilities(String actorId, String teamId, String personId) {
        requireTeam(teamId);
        requirePerson(personId);
        return new TeamMembershipCapabilitiesDTO(
                teamId, personId, List.of(addPrecheck(actorId, teamId, personId), removePrecheck(actorId, teamId, personId))
        );
    }

    private TeamMembershipPrecheckDTO allowed(String commandId, String personId, boolean destructive) {
        return new TeamMembershipPrecheckDTO(
                commandId, "team-membership", personId, true, List.of(), destructive, destructive
        );
    }

    private TeamMembershipPrecheckDTO blocked(
            String commandId,
            String personId,
            TeamMembershipPolicy.Decision decision,
            boolean destructive
    ) {
        TeamMembershipPrecheckReasonDTO reason = new TeamMembershipPrecheckReasonDTO(
                decision.code(), "policy", "blocking",
                "team-membership." + decision.code().toLowerCase(Locale.ROOT), decision.message()
        );
        return new TeamMembershipPrecheckDTO(
                commandId, "team-membership", personId, false, List.of(reason), destructive, destructive
        );
    }

    private void requireTeam(String teamId) {
        if (!repository.teamExists(teamId)) {
            throw notFound("Team not found", "team.not-found");
        }
    }

    private void requirePerson(String personId) {
        if (!repository.personExists(personId)) {
            throw notFound("Person not found", "person.not-found");
        }
    }

    private ResourceNotFoundException notFound(String message, String messageKey) {
        return new ResourceNotFoundException(message, messageKey);
    }
}
