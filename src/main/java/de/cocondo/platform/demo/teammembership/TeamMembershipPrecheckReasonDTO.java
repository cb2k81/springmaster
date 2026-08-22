package de.cocondo.platform.demo.teammembership;

public record TeamMembershipPrecheckReasonDTO(
        String code,
        String category,
        String severity,
        String messageKey,
        String defaultMessage
) {
}
