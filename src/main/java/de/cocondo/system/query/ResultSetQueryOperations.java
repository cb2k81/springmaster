package de.cocondo.system.query;

/**
 * Composite Service/Application contract for canonical result-set query operations.
 *
 * <p>The Core intentionally does not define Spring MVC mappings, URL paths,
 * fachliche filter fields, security annotations or persistence rules. Those
 * remain owned by the concrete module/controller. This interface only provides
 * a type-safe Java contract for generated and manually implemented query
 * services.</p>
 *
 * @param <P> paged query criteria type
 * @param <A> complete result-set query criteria type
 * @param <C> count-only query criteria type
 * @param <T> public list item DTO type
 */
public interface ResultSetQueryOperations<P, A, C, T>
        extends PagedResultSetQuery<P, T>, CompleteResultSetQuery<A, T>, CountResultSetQuery<C> {
}
