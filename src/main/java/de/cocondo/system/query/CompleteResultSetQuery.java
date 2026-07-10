package de.cocondo.system.query;

import java.util.List;

/**
 * Fachfreier Service contract for a complete result-set query operation.
 *
 * @param <Q> query criteria type owned by the fachliche slice
 * @param <T> public list item DTO type
 */
public interface CompleteResultSetQuery<Q, T> {

    List<T> listAll(Q query);
}
