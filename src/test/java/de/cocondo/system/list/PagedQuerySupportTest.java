package de.cocondo.system.list;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.junit.jupiter.api.Test;
import org.springframework.data.domain.Sort;

class PagedQuerySupportTest {

    private final PagedQuerySupport support = new PagedQuerySupport();

    @Test
    void validatePagingAcceptsValidArguments() {
        support.validatePaging(0, 200);
    }

    @Test
    void validatePagingRejectsInvalidPageAndSizeArguments() {
        assertThatThrownBy(() -> support.validatePaging(-1, 10))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("page must be >= 0");

        assertThatThrownBy(() -> support.validatePaging(0, 0))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("size must be > 0");

        assertThatThrownBy(() -> support.validatePaging(0, 201))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("size must be <= 200");
    }

    @Test
    void resolveSortDirectionDefaultsToAscendingAndSupportsAscDesc() {
        assertThat(support.resolveSortDirection(null)).isEqualTo(Sort.Direction.ASC);
        assertThat(support.resolveSortDirection(" ")).isEqualTo(Sort.Direction.ASC);
        assertThat(support.resolveSortDirection("asc")).isEqualTo(Sort.Direction.ASC);
        assertThat(support.resolveSortDirection("DESC")).isEqualTo(Sort.Direction.DESC);
        assertThat(support.resolveSortDirection(" desc ")).isEqualTo(Sort.Direction.DESC);
    }

    @Test
    void resolveSortDirectionRejectsUnsupportedDirection() {
        assertThatThrownBy(() -> support.resolveSortDirection("sideways"))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("Unsupported sortDir: sideways");
    }

    @Test
    void resolveSortByDefaultsAndAcceptsOnlyAllowedFields() {
        Set<String> allowed = Set.of("sku", "name");

        assertThat(support.resolveSortBy(null, allowed, "sku")).isEqualTo("sku");
        assertThat(support.resolveSortBy(" ", allowed, "sku")).isEqualTo("sku");
        assertThat(support.resolveSortBy("name", allowed, "sku")).isEqualTo("name");
    }

    @Test
    void resolveSortByRejectsUnsupportedFieldsAndInvalidConfiguration() {
        assertThatThrownBy(() -> support.resolveSortBy("createdAt", Set.of("sku", "name"), "sku"))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("Unsupported sortBy: createdAt");

        assertThatThrownBy(() -> support.resolveSortBy(null, Set.of("sku", "name"), "id"))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("defaultSortBy must be part of allowed sort fields: id");

        assertThatThrownBy(() -> support.resolveSortBy(null, Set.of(), "sku"))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("allowedSortFields must not be empty");
    }

    @Test
    void stableSortAddsAscendingTieBreakerWhenDifferentFromPrimarySort() {
        Sort sort = support.stableSort("name", "desc", Set.of("sku", "name"), "sku", "id");

        List<Sort.Order> orders = sort.stream().toList();
        assertThat(orders).hasSize(2);
        assertThat(orders.get(0).getProperty()).isEqualTo("name");
        assertThat(orders.get(0).getDirection()).isEqualTo(Sort.Direction.DESC);
        assertThat(orders.get(1).getProperty()).isEqualTo("id");
        assertThat(orders.get(1).getDirection()).isEqualTo(Sort.Direction.ASC);
    }

    @Test
    void stableSortDoesNotDuplicateTieBreakerWhenPrimarySortIsTieBreaker() {
        Sort sort = support.stableSort("id", "asc", Set.of("id", "name"), "id", "id");

        List<Sort.Order> orders = sort.stream().toList();
        assertThat(orders).hasSize(1);
        assertThat(orders.getFirst().getProperty()).isEqualTo("id");
        assertThat(orders.getFirst().getDirection()).isEqualTo(Sort.Direction.ASC);
    }

    @Test
    void stableComparatorAppliesRequestedDirectionAndAscendingTieBreaker() {
        Map<String, Comparator<Row>> allowedComparators = Map.of(
                "name", Comparator.comparing(Row::name, String.CASE_INSENSITIVE_ORDER),
                "sku", Comparator.comparing(Row::sku, String.CASE_INSENSITIVE_ORDER)
        );
        List<Row> rows = new ArrayList<>(List.of(
                new Row("2", "B-002", "Beta"),
                new Row("3", "A-001", "Alpha"),
                new Row("1", "B-001", "Beta")
        ));

        rows.sort(support.stableComparator(
                "name",
                "desc",
                allowedComparators,
                "sku",
                Comparator.comparing(Row::id)
        ));

        assertThat(rows).extracting(Row::id).containsExactly("1", "2", "3");
    }

    @Test
    void stableComparatorRejectsInvalidConfiguration() {
        assertThatThrownBy(() -> support.stableComparator(
                "name",
                "asc",
                Map.<String, Comparator<Row>>of(),
                "name",
                Comparator.comparing(Row::id)
        ))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("allowedComparators must not be empty");
    }

    private record Row(String id, String sku, String name) {
    }
}
