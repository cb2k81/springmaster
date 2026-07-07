package de.cocondo.platform.demo.catalog;

import de.cocondo.system.entity.DomainEntity;
import de.cocondo.system.entity.Range;
import jakarta.persistence.Column;
import jakarta.persistence.Embedded;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;

@Entity
@Table(name = "demo_catalog_item")
public class CatalogItem extends DomainEntity {

    @Column(nullable = false, unique = true, length = 128)
    private String sku;

    @Column(nullable = false, length = 255)
    private String name;

    @Column(length = 1000)
    private String description;

    @Embedded
    private Range availability = new Range();

    protected CatalogItem() {
        super();
    }

    public CatalogItem(String sku, String name, String description) {
        this();
        this.sku = normalize(sku);
        this.name = normalize(name);
        this.description = normalizeNullable(description);
    }

    public String getSku() {
        return sku;
    }

    public void setSku(String sku) {
        this.sku = normalize(sku);
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = normalize(name);
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = normalizeNullable(description);
    }

    public Range getAvailability() {
        return availability;
    }

    public void setAvailability(Range availability) {
        this.availability = availability != null ? availability : new Range();
    }

    private static String normalize(String value) {
        return value != null ? value.trim() : null;
    }

    private static String normalizeNullable(String value) {
        String normalized = normalize(value);
        return normalized != null && !normalized.isBlank() ? normalized : null;
    }
}
