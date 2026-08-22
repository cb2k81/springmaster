package de.cocondo.platform.demo.teammembership;

import java.util.List;

public record TeamMembershipCapabilitiesDTO(
        String teamId,
        String personId,
        List<TeamMembershipPrecheckDTO> capabilities
) {
    public TeamMembershipCapabilitiesDTO {
        capabilities = List.copyOf(capabilities);
    }
}
