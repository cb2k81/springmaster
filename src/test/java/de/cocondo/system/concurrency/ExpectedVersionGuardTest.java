package de.cocondo.system.concurrency;

import static org.assertj.core.api.Assertions.assertThatCode;
import static org.assertj.core.api.Assertions.assertThatIllegalArgumentException;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import de.cocondo.system.exception.ExpectedVersionConflictException;
import org.junit.jupiter.api.Test;

class ExpectedVersionGuardTest {

    private final ExpectedVersionGuard guard = new ExpectedVersionGuard();

    @Test
    void acceptsMatchingVersion() {
        assertThatCode(() -> guard.requireMatch("catalog-item", "item-1", 4L, 4L))
                .doesNotThrowAnyException();
    }

    @Test
    void rejectsMissingActualVersionAsConflict() {
        assertConflict(null, 4L);
    }

    @Test
    void rejectsMismatchingVersionAsConflictWithoutDisclosingVersionValues() {
        assertThatThrownBy(() -> guard.requireMatch("catalog-item", "item-1", 5L, 4L))
                .isInstanceOf(ExpectedVersionConflictException.class)
                .hasMessageNotContaining("4")
                .hasMessageNotContaining("5");
    }

    @Test
    void rejectsMissingExpectedVersion() {
        assertThatIllegalArgumentException()
                .isThrownBy(() -> guard.requireMatch("catalog-item", "item-1", 4L, null));
    }

    @Test
    void rejectsNegativeExpectedVersion() {
        assertThatIllegalArgumentException()
                .isThrownBy(() -> guard.requireMatch("catalog-item", "item-1", 4L, -1L));
    }

    @Test
    void rejectsBlankResourceIdentity() {
        assertThatIllegalArgumentException()
                .isThrownBy(() -> guard.requireMatch(" ", "item-1", 4L, 4L));
        assertThatIllegalArgumentException()
                .isThrownBy(() -> guard.requireMatch("catalog-item", " ", 4L, 4L));
        assertThatIllegalArgumentException()
                .isThrownBy(() -> guard.requireMatch(null, "item-1", 4L, 4L));
        assertThatIllegalArgumentException()
                .isThrownBy(() -> guard.requireMatch("catalog-item", null, 4L, 4L));
    }

    private void assertConflict(Long actualVersion, Long expectedVersion) {
        assertThatThrownBy(() -> guard.requireMatch("catalog-item", "item-1", actualVersion, expectedVersion))
                .isInstanceOf(ExpectedVersionConflictException.class);
    }
}
