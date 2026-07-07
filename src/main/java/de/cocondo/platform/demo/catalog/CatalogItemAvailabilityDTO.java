package de.cocondo.platform.demo.catalog;

import com.fasterxml.jackson.annotation.JsonIgnore;
import de.cocondo.system.dto.DataTransferObject;
import jakarta.validation.constraints.AssertTrue;
import java.time.LocalDateTime;

public class CatalogItemAvailabilityDTO implements DataTransferObject {

    private LocalDateTime validFrom;
    private LocalDateTime validTo;

    public CatalogItemAvailabilityDTO() {
    }

    public CatalogItemAvailabilityDTO(LocalDateTime validFrom, LocalDateTime validTo) {
        this.validFrom = validFrom;
        this.validTo = validTo;
    }

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

    @JsonIgnore
    @AssertTrue(message = "Catalog item availability validFrom must not be after validTo")
    public boolean isChronological() {
        return validFrom == null || validTo == null || !validFrom.isAfter(validTo);
    }
}
