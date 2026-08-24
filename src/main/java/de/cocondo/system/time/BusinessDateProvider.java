package de.cocondo.system.time;

import java.time.LocalDate;

/**
 * Supplies the business date used by an application boundary, independently of audit timestamps.
 */
@FunctionalInterface
public interface BusinessDateProvider {

    LocalDate currentDate();
}
