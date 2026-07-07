package de.cocondo.platform.demo.catalog;

import de.cocondo.system.entity.Range;
import java.util.LinkedHashSet;

public class CatalogItemMapper {

    public CatalogItem toEntity(CatalogItemCreateDTO source) {
        CatalogItem target = new CatalogItem(source.getSku(), source.getName(), source.getDescription());
        target.setTags(new LinkedHashSet<>(source.getTags()));
        target.setAvailability(toRange(source.getAvailability()));
        return target;
    }

    public void updateEntity(CatalogItem target, CatalogItemUpdateDTO source) {
        target.setName(source.getName());
        target.setDescription(source.getDescription());
        target.setTags(new LinkedHashSet<>(source.getTags()));
        target.setAvailability(toRange(source.getAvailability()));
    }

    public CatalogItemDTO toDto(CatalogItem source) {
        CatalogItemDTO target = new CatalogItemDTO();
        target.setId(source.getId());
        target.setSku(source.getSku());
        target.setName(source.getName());
        target.setDescription(source.getDescription());
        target.setTags(new LinkedHashSet<>(source.getTags()));
        target.setPersistenceVersion(source.getPersistenceVersion());
        if (source.getAvailability() != null) {
            target.setValidFrom(source.getAvailability().getValidFrom());
            target.setValidTo(source.getAvailability().getValidTo());
        }
        return target;
    }

    public CatalogItemListItemDTO toListItemDto(CatalogItem source) {
        CatalogItemListItemDTO target = new CatalogItemListItemDTO();
        target.setId(source.getId());
        target.setSku(source.getSku());
        target.setName(source.getName());
        return target;
    }

    private Range toRange(CatalogItemAvailabilityDTO source) {
        Range target = new Range();
        if (source != null) {
            target.setValidFrom(source.getValidFrom());
            target.setValidTo(source.getValidTo());
        }
        return target;
    }
}
