package de.cocondo.system.entity;

import java.time.LocalDateTime;

import jakarta.persistence.Embeddable;

@Embeddable
public class Range {

    private LocalDateTime validFrom;
    private LocalDateTime validTo;

    public LocalDateTime getValidFrom() {
        return validFrom;
    }

    public void setValidFrom(LocalDateTime validFrom) {
        this.validFrom = validFrom;
    }

    public LocalDateTime getValidTo() {
        return validTo;
    }

    public void setValidTo(LocalDateTime validTo) {
        this.validTo = validTo;
    }
}
