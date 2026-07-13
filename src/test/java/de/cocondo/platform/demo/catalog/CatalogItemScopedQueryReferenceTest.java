package de.cocondo.platform.demo.catalog;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.util.List;
import java.util.Set;
import org.junit.jupiter.api.Test;

class CatalogItemScopedQueryReferenceTest {

    private final CatalogItemScopedQueryReference reference = new CatalogItemScopedQueryReference();

    @Test
    void listAllAndCountUseSamePermissionAndDataScopeAsPagedList() {
        List<CatalogItem> source = List.of(
                new CatalogItem("SKU-1", "Alpha", null),
                new CatalogItem("SKU-2", "Alphabetic", null),
                new CatalogItem("SKU-3", "Beta", null)
        );
        CatalogItemQueryScope scope = CatalogItemQueryScope.restrictedRead(Set.of("sku-1", "SKU-3"));

        var paged = reference.listPaged(source, new CatalogItemPagedQuery(0, 10, "sku", "ASC", null, "alpha"), scope);
        var all = reference.listAll(source, new CatalogItemAllQuery("sku", "ASC", null, "alpha"), scope);
        var count = reference.count(source, new CatalogItemCountQuery(null, "alpha"), scope);

        assertThat(paged.getItems())
                .extracting(CatalogItemListItemDTO::getSku)
                .containsExactly("SKU-1");
        assertThat(paged.getTotalElements()).isEqualTo(1);
        assertThat(all)
                .extracting(CatalogItemListItemDTO::getSku)
                .containsExactly("SKU-1");
        assertThat(count.getTotalElements()).isEqualTo(1);
    }

    @Test
    void countDoesNotBypassDataScopeWhenNoBusinessFilterIsProvided() {
        List<CatalogItem> source = List.of(
                new CatalogItem("SKU-1", "Alpha", null),
                new CatalogItem("SKU-2", "Beta", null),
                new CatalogItem("SKU-3", "Gamma", null)
        );
        CatalogItemQueryScope scope = CatalogItemQueryScope.restrictedRead(Set.of("SKU-1", "SKU-3"));

        var all = reference.listAll(source, new CatalogItemAllQuery("sku", "ASC", null, null), scope);
        var count = reference.count(source, new CatalogItemCountQuery(null, null), scope);

        assertThat(all)
                .extracting(CatalogItemListItemDTO::getSku)
                .containsExactly("SKU-1", "SKU-3");
        assertThat(count.getTotalElements()).isEqualTo(2);
    }

    @Test
    void deniedReadPermissionStopsEveryQueryOperationBeforeReturningRows() {
        List<CatalogItem> source = List.of(new CatalogItem("SKU-1", "Alpha", null));
        CatalogItemQueryScope denied = CatalogItemQueryScope.denied();

        assertThatThrownBy(() -> reference.listPaged(source,
                new CatalogItemPagedQuery(0, 10, "sku", "ASC", null, null), denied))
                .isInstanceOf(SecurityException.class)
                .hasMessageContaining(CatalogItemQueryScope.READ_PERMISSION);
        assertThatThrownBy(() -> reference.listAll(source,
                new CatalogItemAllQuery("sku", "ASC", null, null), denied))
                .isInstanceOf(SecurityException.class)
                .hasMessageContaining(CatalogItemQueryScope.READ_PERMISSION);
        assertThatThrownBy(() -> reference.count(source,
                new CatalogItemCountQuery(null, null), denied))
                .isInstanceOf(SecurityException.class)
                .hasMessageContaining(CatalogItemQueryScope.READ_PERMISSION);
    }
}
