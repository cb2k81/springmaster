package de.cocondo.platform.demo.teammembership;

import java.util.List;

public record TeamMembershipPrecheckDTO(
        String commandId,
        String targetType,
        String targetId,
        boolean executable,
        List<TeamMembershipPrecheckReasonDTO> reasons,
        boolean destructive,
        boolean confirmationRequired
) {
    public TeamMembershipPrecheckDTO {
        reasons = List.copyOf(reasons);
    }
}
