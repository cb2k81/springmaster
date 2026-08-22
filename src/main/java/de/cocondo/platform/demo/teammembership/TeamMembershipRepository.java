package de.cocondo.platform.demo.teammembership;

import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import org.springframework.stereotype.Repository;

/**
 * In-memory data boundary for the deliberately non-persistent Team-Membership reference slice.
 */
@Repository
class TeamMembershipRepository {
    private final Map<String, String> people = new LinkedHashMap<>();
    private final Map<String, Map<String, TeamMemberDTO>> memberships = new LinkedHashMap<>();
    private final AtomicInteger sequence = new AtomicInteger(3);

    TeamMembershipRepository() {
        people.put("person-alex", "Alex Morgan");
        people.put("person-jordan", "Jordan Lee");
        people.put("person-sam", "Sam Rivera");
        memberships.put("alpha", new LinkedHashMap<>());
        memberships.put("beta", new LinkedHashMap<>());
        memberships.get("alpha").put("person-alex", member("membership-001", "alpha", "person-alex"));
        memberships.get("beta").put("person-jordan", member("membership-002", "beta", "person-jordan"));
    }

    boolean teamExists(String teamId) {
        return memberships.containsKey(teamId);
    }

    boolean personExists(String personId) {
        return people.containsKey(personId);
    }

    boolean membershipExists(String teamId, String personId) {
        return memberships.get(teamId).containsKey(personId);
    }

    List<TeamMemberDTO> findMembers(String teamId) {
        return memberships.get(teamId).values().stream()
                .sorted(Comparator.comparing(TeamMemberDTO::displayName).thenComparing(TeamMemberDTO::personId))
                .toList();
    }

    List<TeamMemberOptionDTO> findCandidates(String teamId) {
        Map<String, TeamMemberDTO> team = memberships.get(teamId);
        return people.entrySet().stream()
                .filter(entry -> !team.containsKey(entry.getKey()))
                .map(entry -> new TeamMemberOptionDTO(entry.getKey(), entry.getValue()))
                .sorted(Comparator.comparing(TeamMemberOptionDTO::displayName)
                        .thenComparing(TeamMemberOptionDTO::personId))
                .toList();
    }

    TeamMemberDTO add(String teamId, String personId) {
        TeamMemberDTO member = member(
                "membership-%03d".formatted(sequence.getAndIncrement()), teamId, personId
        );
        memberships.get(teamId).put(personId, member);
        return member;
    }

    boolean remove(String teamId, String personId) {
        return memberships.get(teamId).remove(personId) != null;
    }

    private TeamMemberDTO member(String membershipId, String teamId, String personId) {
        return new TeamMemberDTO(membershipId, teamId, personId, people.get(personId));
    }
}
