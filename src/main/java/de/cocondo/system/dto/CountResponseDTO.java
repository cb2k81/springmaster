package de.cocondo.system.dto;

/**
 * Fachfreier Core-DTO contract for count-only API responses.
 *
 * <p>The public JSON shape is intentionally minimal:</p>
 *
 * <pre>{ "totalElements": 0 }</pre>
 *
 * <p>Count-only endpoints must calculate the value from the same filter,
 * security and data-scope predicates as the corresponding list or complete
 * result-set endpoint. Sorting, page and size parameters are not part of the
 * count semantics.</p>
 */
public class CountResponseDTO {

    private long totalElements;

    public CountResponseDTO() {
        this(0);
    }

    public CountResponseDTO(long totalElements) {
        setTotalElements(totalElements);
    }

    public static CountResponseDTO of(long totalElements) {
        return new CountResponseDTO(totalElements);
    }

    public long getTotalElements() {
        return totalElements;
    }

    public void setTotalElements(long totalElements) {
        if (totalElements < 0) {
            throw new IllegalArgumentException("totalElements must be non-negative");
        }
        this.totalElements = totalElements;
    }
}
