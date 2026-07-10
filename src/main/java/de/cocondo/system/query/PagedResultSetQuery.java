package de.cocondo.system.query;

import de.cocondo.system.dto.PagedResponseDTO;

/**
 * Fachfreier Service contract for a paged result-set query operation.
 *
 * @param <Q> query criteria type owned by the fachliche slice
 * @param <T> public list item DTO type
 */
public interface PagedResultSetQuery<Q, T> {

    PagedResponseDTO<T> listPaged(Q query);
}
