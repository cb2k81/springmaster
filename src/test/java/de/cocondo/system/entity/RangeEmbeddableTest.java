package de.cocondo.system.entity;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import java.time.LocalDateTime;

import jakarta.persistence.Embeddable;
import org.junit.jupiter.api.Test;

class RangeEmbeddableTest {

    @Test
    void rangeIsEmbeddableAndStoresValidityWindow() {
        assertNotNull(Range.class.getAnnotation(Embeddable.class));

        LocalDateTime from = LocalDateTime.of(2026, 1, 1, 0, 0);
        LocalDateTime to = LocalDateTime.of(2026, 12, 31, 23, 59);
        Range range = new Range();

        range.setValidFrom(from);
        range.setValidTo(to);

        assertEquals(from, range.getValidFrom());
        assertEquals(to, range.getValidTo());
    }
}
