package de.cocondo.platform.demo.teammembership;

import org.springframework.stereotype.Component;

@Component
final class TeamMembershipPolicy {

    Decision evaluate(String actorId, String teamId) {
        if (actorId == null || actorId.isBlank()) {
            return new Decision(false, "ACTOR_REQUIRED", "Authentication context is required");
        }
        if ("admin".equals(actorId) || ("team-lead-" + teamId).equals(actorId)) {
            return new Decision(true, null, null);
        }
        return new Decision(false, "TARGET_SCOPE_DENIED", "Actor cannot manage the selected team");
    }

    void requireAllowed(String actorId, String teamId) {
        Decision decision = evaluate(actorId, teamId);
        if (!decision.allowed()) {
            throw new SecurityException(decision.code());
        }
    }

    record Decision(boolean allowed, String code, String message) {
    }
}
