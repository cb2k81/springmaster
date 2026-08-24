package de.cocondo.system.time;

import java.time.Clock;
import java.time.LocalDate;
import java.util.Objects;

/**
 * Derives the current business date from an explicitly supplied technical clock.
 */
public final class ClockBusinessDateProvider implements BusinessDateProvider {

    private final Clock clock;

    public ClockBusinessDateProvider(Clock clock) {
        this.clock = Objects.requireNonNull(clock, "clock must not be null");
    }

    @Override
    public LocalDate currentDate() {
        return LocalDate.now(clock);
    }
}
