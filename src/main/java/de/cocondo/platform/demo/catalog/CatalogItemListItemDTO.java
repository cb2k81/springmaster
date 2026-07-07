package de.cocondo.platform.demo.catalog;

import de.cocondo.system.dto.DTO;

public class CatalogItemListItemDTO implements DTO {

    private String id;
    private String sku;
    private String name;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getSku() {
        return sku;
    }

    public void setSku(String sku) {
        this.sku = sku;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}
