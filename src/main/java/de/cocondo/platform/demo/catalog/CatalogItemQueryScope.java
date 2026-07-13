package de.cocondo.platform.demo.catalog;

import java.util.Locale;
import java.util.Objects;
import java.util.Set;
import java.util.TreeSet;

/**
 * Query-time read permission and data-scope reference for CatalogItem.
 *
 * <p>The type is intentionally framework-free. Future secured runtime services
 * may adapt it from Spring Security, JWT claims, IDM assignments or tenant data,
 * but list, /all and /count must receive the same resolved scope.</p>
 */
public record CatalogItemQueryScope(boolean readAllowed, Set<String> allowedSkus) {

    public static final String READ_PERMISSION = "catalog:item:read";

    public CatalogItemQueryScope {
        allowedSkus = normalizeAllowedSkus(allowedSkus);
    }

    public static CatalogItemQueryScope unrestrictedRead() {
        return new CatalogItemQueryScope(true, Set.of());
    }

    public static CatalogItemQueryScope restrictedRead(Set<String> allowedSkus) {
        return new CatalogItemQueryScope(true, allowedSkus);
    }

    public static CatalogItemQueryScope denied() {
        return new CatalogItemQueryScope(false, Set.of());
    }

    public boolean canSee(CatalogItem item) {
        Objects.requireNonNull(item, "item must not be null");
        if (!readAllowed) {
            return false;
        }
        if (allowedSkus.isEmpty()) {
            return true;
        }
        String sku = item.getSku();
        return sku != null && allowedSkus.contains(normalizeSku(sku));
    }

    private static Set<String> normalizeAllowedSkus(Set<String> source) {
        if (source == null || source.isEmpty()) {
            return Set.of();
        }
        TreeSet<String> normalized = new TreeSet<>();
        for (String value : source) {
            if (value != null && !value.isBlank()) {
                normalized.add(normalizeSku(value));
            }
        }
        return Set.copyOf(normalized);
    }

    private static String normalizeSku(String value) {
        return value.trim().toUpperCase(Locale.ROOT);
    }
}
