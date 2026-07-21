package de.cocondo.platform.demo.catalog;

import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CatalogItemRepository extends JpaRepository<CatalogItem, String> {

    boolean existsBySkuIgnoreCase(String sku);

    Optional<CatalogItem> findBySkuIgnoreCase(String sku);
}
