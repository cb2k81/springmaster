package de.cocondo.platform.demo.catalog;

import static org.assertj.core.api.Assertions.assertThat;

import de.cocondo.system.entity.DomainEntity;
import org.junit.jupiter.api.Test;

class CatalogItemTest {

    @Test
    void createsDomainEntityWithIdAndNormalizedFields() {
        CatalogItem item = new CatalogItem("  SKU-1  ", "  Demo Item  ", "  Description  ");

        assertThat(item).isInstanceOf(DomainEntity.class);
        assertThat(item.getId()).isNotBlank();
        assertThat(item.getSku()).isEqualTo("SKU-1");
        assertThat(item.getName()).isEqualTo("Demo Item");
        assertThat(item.getDescription()).isEqualTo("Description");
        assertThat(item.getTags()).isEmpty();
        assertThat(item.getAvailability()).isNotNull();
    }
}
