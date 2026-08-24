package de.cocondo.system.time;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatNullPointerException;

import java.time.Clock;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneId;
import java.time.ZoneOffset;
import org.junit.jupiter.api.Test;

class ClockBusinessDateProviderTest {

    private static final Instant CONTROLLED_INSTANT = Instant.parse("2026-08-23T00:30:00Z");

    @Test
    void derivesCurrentDateFromInjectedClock() {
        BusinessDateProvider provider = new ClockBusinessDateProvider(
                Clock.fixed(CONTROLLED_INSTANT, ZoneOffset.UTC)
        );

        assertThat(provider.currentDate()).isEqualTo(LocalDate.of(2026, 8, 23));
    }

    @Test
    void honorsTheInjectedClockZone() {
        BusinessDateProvider provider = new ClockBusinessDateProvider(
                Clock.fixed(CONTROLLED_INSTANT, ZoneId.of("America/Los_Angeles"))
        );

        assertThat(provider.currentDate()).isEqualTo(LocalDate.of(2026, 8, 22));
    }

    @Test
    void rejectsNullClock() {
        assertThatNullPointerException()
                .isThrownBy(() -> new ClockBusinessDateProvider(null))
                .withMessage("clock must not be null");
    }
}
