package de.cocondo.system.list;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

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
    }

    @Test
    void resolveSortDirectionRejectsUnsupportedDirection() {
        assertThatThrownBy(() -> support.resolveSortDirection("sideways"))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("Unsupported sortDir: sideways");
    }
}
