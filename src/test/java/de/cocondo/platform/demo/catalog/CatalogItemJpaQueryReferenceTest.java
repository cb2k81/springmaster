package de.cocondo.platform.demo.catalog;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

class CatalogItemJpaQueryReferenceTest {

    private final Path sourcePath = Path.of(
            "src/main/java/de/cocondo/platform/demo/catalog/CatalogItemJpaQueryReference.java");

    @Test
    void countReferenceUsesDedicatedCriteriaCountQueryAndSharedPredicates() throws IOException {
        String source = Files.readString(sourcePath, StandardCharsets.UTF_8);
        String countRows = methodBody(source, "private long countRows(");

        assertThat(countRows)
                .contains("CriteriaQuery<Long> countQuery = cb.createQuery(Long.class);")
                .contains("Root<CatalogItem> root = countQuery.from(CatalogItem.class);")
                .contains("countQuery.select(cb.count(root));")
                .contains("applyPredicates(countQuery, root, cb, sku, name);")
                .contains("entityManager.createQuery(countQuery).getSingleResult()")
                .doesNotContain("listAll(")
                .doesNotContain("listPaged(")
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
                .contains("applyPredicates(dataQuery, root, cb, sku, name);")
                .contains("applyPredicates(countQuery, root, cb, sku, name);")
                .contains("private List<Predicate> filterPredicates(")
                .contains("cb.upper(root.get(ATTRIBUTE_SKU))")
                .contains("cb.lower(root.get(ATTRIBUTE_NAME))");
    }

    @Test
    void pagingAndSortingStayOutOfCountSemantics() throws IOException {
        String source = Files.readString(sourcePath, StandardCharsets.UTF_8);
        String createDataQuery = methodBody(source, "private TypedQuery<CatalogItem> createDataQuery(");
        String countRows = methodBody(source, "private long countRows(");

        assertThat(createDataQuery)
                .contains("dataQuery.orderBy(stableOrders(root, cb, sortBy, sortDir));");
        assertThat(source)
                .contains(".setFirstResult(query.page() * query.size())")
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
        for (int i = brace; i < source.length(); i++) {
            char current = source.charAt(i);
            if (current == '{') {
                depth++;
            } else if (current == '}') {
                depth--;
                if (depth == 0) {
                    return source.substring(brace, i + 1);
                }
            }
        }
        throw new AssertionError("method body not closed: " + signature);
    }
}
