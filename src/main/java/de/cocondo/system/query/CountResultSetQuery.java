package de.cocondo.system.query;

import de.cocondo.system.dto.CountResponseDTO;

/**
 * Fachfreier Service contract for a count-only result-set query operation.
 *
 * @param <Q> query criteria type owned by the fachliche slice
 */
public interface CountResultSetQuery<Q> {

    CountResponseDTO count(Q query);
}
