package de.cocondo.platform.demo.catalog;

import de.cocondo.system.dto.DataTransferObject;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.util.LinkedHashSet;
import java.util.Set;

public class CatalogItemUpdateDTO implements DataTransferObject {

    @NotBlank(message = "Catalog item name must not be blank")
    @Size(max = 255, message = "Catalog item name must not exceed 255 characters")
    private String name;

    @Size(max = 1000, message = "Catalog item description must not exceed 1000 characters")
    private String description;

    private Set<String> tags = new LinkedHashSet<>();

    @Valid
    private CatalogItemAvailabilityDTO availability = new CatalogItemAvailabilityDTO();

    public CatalogItemUpdateDTO() {
    }

    public CatalogItemUpdateDTO(String name, String description) {
        this.name = name;
        this.description = description;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Set<String> getTags() {
        return tags;
    }

    public void setTags(Set<String> tags) {
        this.tags = tags != null ? new LinkedHashSet<>(tags) : new LinkedHashSet<>();
    }

    public CatalogItemAvailabilityDTO getAvailability() {
        return availability;
    }

    public void setAvailability(CatalogItemAvailabilityDTO availability) {
        this.availability = availability != null ? availability : new CatalogItemAvailabilityDTO();
    }
}
