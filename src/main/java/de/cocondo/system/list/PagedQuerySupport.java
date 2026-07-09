package de.cocondo.system.list;

import java.util.Collection;
import java.util.Comparator;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;

import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Component;

@Component
public class PagedQuerySupport {

    public static final int MAX_PAGE_SIZE = 200;

    public void validatePaging(int page, int size) {
        if (page < 0) {
            throw new IllegalArgumentException("page must be >= 0");
        }
        if (size <= 0) {
            throw new IllegalArgumentException("size must be > 0");
        }
        if (size > MAX_PAGE_SIZE) {
            throw new IllegalArgumentException("size must be <= " + MAX_PAGE_SIZE);
        }
    }

    public Sort.Direction resolveSortDirection(String sortDir) {
        if (sortDir == null || sortDir.isBlank()) {
            return Sort.Direction.ASC;
        }

        return switch (sortDir.trim().toLowerCase(Locale.ROOT)) {
            case "asc" -> Sort.Direction.ASC;
            case "desc" -> Sort.Direction.DESC;
            default -> throw new IllegalArgumentException("Unsupported sortDir: " + sortDir);
        };
    }

    public String resolveSortBy(String sortBy, Collection<String> allowedSortFields, String defaultSortBy) {
        validateAllowedSortFields(allowedSortFields);
        String resolvedDefaultSortBy = requireNonBlank(defaultSortBy, "defaultSortBy");
        if (!allowedSortFields.contains(resolvedDefaultSortBy)) {
            throw new IllegalArgumentException("defaultSortBy must be part of allowed sort fields: " + resolvedDefaultSortBy);
        }

        if (sortBy == null || sortBy.isBlank()) {
            return resolvedDefaultSortBy;
        }

        String normalizedSortBy = sortBy.trim();
        if (allowedSortFields.contains(normalizedSortBy)) {
            return normalizedSortBy;
        }
        throw new IllegalArgumentException("Unsupported sortBy: " + sortBy);
    }

    public Sort stableSort(
            String sortBy,
            String sortDir,
            Collection<String> allowedSortFields,
            String defaultSortBy,
            String tieBreakerSortBy
    ) {
        String resolvedSortBy = resolveSortBy(sortBy, allowedSortFields, defaultSortBy);
        Sort.Direction resolvedDirection = resolveSortDirection(sortDir);
        Sort resolvedSort = Sort.by(new Sort.Order(resolvedDirection, resolvedSortBy));

        if (tieBreakerSortBy == null || tieBreakerSortBy.isBlank()) {
            return resolvedSort;
        }

        String resolvedTieBreakerSortBy = tieBreakerSortBy.trim();
        if (resolvedSortBy.equals(resolvedTieBreakerSortBy)) {
            return resolvedSort;
        }
        return resolvedSort.and(Sort.by(new Sort.Order(Sort.Direction.ASC, resolvedTieBreakerSortBy)));
    }

    public <T> Comparator<T> stableComparator(
            String sortBy,
            String sortDir,
            Map<String, Comparator<T>> allowedComparators,
            String defaultSortBy,
            Comparator<T> tieBreakerComparator
    ) {
        validateAllowedComparators(allowedComparators);
        String resolvedSortBy = resolveSortBy(sortBy, allowedComparators.keySet(), defaultSortBy);
        Comparator<T> primaryComparator = Objects.requireNonNull(
                allowedComparators.get(resolvedSortBy),
                "comparator must exist for resolved sort field: " + resolvedSortBy
        );

        if (resolveSortDirection(sortDir) == Sort.Direction.DESC) {
            primaryComparator = primaryComparator.reversed();
        }

        if (tieBreakerComparator == null) {
            return primaryComparator;
        }
        return primaryComparator.thenComparing(tieBreakerComparator);
    }

    private void validateAllowedSortFields(Collection<String> allowedSortFields) {
        if (allowedSortFields == null || allowedSortFields.isEmpty()) {
            throw new IllegalArgumentException("allowedSortFields must not be empty");
        }
        if (allowedSortFields.stream().anyMatch(field -> field == null || field.isBlank())) {
            throw new IllegalArgumentException("allowedSortFields must not contain blank values");
        }
    }

    private <T> void validateAllowedComparators(Map<String, Comparator<T>> allowedComparators) {
        if (allowedComparators == null || allowedComparators.isEmpty()) {
            throw new IllegalArgumentException("allowedComparators must not be empty");
        }
        if (allowedComparators.keySet().stream().anyMatch(field -> field == null || field.isBlank())) {
            throw new IllegalArgumentException("allowedComparators must not contain blank sort fields");
        }
        if (allowedComparators.values().stream().anyMatch(Objects::isNull)) {
            throw new IllegalArgumentException("allowedComparators must not contain null comparators");
        }
    }

    private String requireNonBlank(String value, String name) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " must not be blank");
        }
        return value.trim();
    }
}
