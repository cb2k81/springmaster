package de.cocondo.platform.demo.teammembership;

import jakarta.validation.constraints.NotBlank;

public record AddTeamMemberDTO(@NotBlank String personId) {
}
