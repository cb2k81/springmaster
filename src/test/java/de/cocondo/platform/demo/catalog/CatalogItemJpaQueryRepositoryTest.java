package de.cocondo.platform.demo.catalog;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

class CatalogItemJpaQueryRepositoryTest {

    private final Path sourcePath = Path.of(
            "src/main/java/de/cocondo/platform/demo/catalog/CatalogItemJpaQueryRepository.java");

    @Test
    void countQueryUsesDedicatedCriteriaCountAndSharedPredicates() throws IOException {
        String source = Files.readString(sourcePath, StandardCharsets.UTF_8);
        String countRows = methodBody(source, "private long countRows(");

        assertThat(countRows)
                .contains("CriteriaQuery<Long> countQuery = criteriaBuilder.createQuery(Long.class);")
                .contains("Root<CatalogItem> root = countQuery.from(CatalogItem.class);")
                .contains("countQuery.select(criteriaBuilder.count(root));")
                .contains("applyPredicates(countQuery, root, criteriaBuilder, sku, name);")
                .contains("entityManager.createQuery(countQuery).getSingleResult()")
                .doesNotContain("findAll(")
                .doesNotContain("findPage(")
                .doesNotContain("getResultList()")
                .doesNotContain(".size()")
                .doesNotContain("setFirstResult")
                .doesNotContain("setMaxResults")
                .doesNotContain("orderBy");
    }

    @Test
    void pagedAndAllQueriesReuseSamePredicateFamilyAsCount() throws IOException {
        String source = Files.readString(sourcePath, StandardCharsets.UTF_8);

        assertThat(source)
                .contains("applyPredicates(dataQuery, root, criteriaBuilder, sku, name);")
                .contains("applyPredicates(countQuery, root, criteriaBuilder, sku, name);")
                .contains("private List<Predicate> filterPredicates(")
                .contains("criteriaBuilder.upper(root.get(CatalogItemQuerySupport.ATTRIBUTE_SKU))")
                .contains("criteriaBuilder.lower(root.get(CatalogItemQuerySupport.ATTRIBUTE_NAME))");
    }

    @Test
    void pagingAndSortingStayOutOfCountSemantics() throws IOException {
        String source = Files.readString(sourcePath, StandardCharsets.UTF_8);
        String createDataQuery = methodBody(source, "private TypedQuery<CatalogItem> createDataQuery(");
        String countRows = methodBody(source, "private long countRows(");

        assertThat(createDataQuery)
                .contains("dataQuery.orderBy(stableOrders(root, criteriaBuilder, sortBy, sortDir));");
        assertThat(source)
                .contains(".setFirstResult(CatalogItemQuerySupport.validatedOffset(query.page(), query.size()))")
                .contains(".setMaxResults(query.size())");
        assertThat(countRows)
                .doesNotContain("stableOrders")
                .doesNotContain("sortBy")
                .doesNotContain("sortDir");
    }

    private String methodBody(String source, String signature) {
        int start = source.indexOf(signature);
        assertThat(start).as("method signature must exist: %s", signature).isGreaterThanOrEqualTo(0);
        int brace = source.indexOf('{', start);
        assertThat(brace).as("method opening brace must exist: %s", signature).isGreaterThanOrEqualTo(0);

        int depth = 0;
        for (int index = brace; index < source.length(); index++) {
            char current = source.charAt(index);
            if (current == '{') {
                depth++;
            } else if (current == '}') {
                depth--;
                if (depth == 0) {
                    return source.substring(brace, index + 1);
                }
            }
        }
        throw new AssertionError("method body not closed: " + signature);
    }
}
