package de.cocondo.platform.demo.teammembership;

import jakarta.validation.constraints.NotBlank;

public record TeamMembershipCapabilityRequestDTO(@NotBlank String personId) {
}
