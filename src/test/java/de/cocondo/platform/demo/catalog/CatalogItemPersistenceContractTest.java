package de.cocondo.platform.demo.catalog;

import static org.assertj.core.api.Assertions.assertThat;

import de.cocondo.platform.app.SpringmasterApplication;
import jakarta.persistence.EntityManager;
import java.util.LinkedHashSet;
import java.util.Set;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

@ActiveProfiles("test")
@SpringBootTest(classes = SpringmasterApplication.class)
class CatalogItemPersistenceContractTest {

    @Autowired
    private CatalogItemService service;

    @Autowired
    private CatalogItemRepository repository;

    @Autowired
    private EntityManager entityManager;

    private final CatalogItemMapper mapper = new CatalogItemMapper();

    @BeforeEach
    void clearRepository() {
        repository.deleteAll();
        repository.flush();
        entityManager.clear();
    }

    @Test
    void persistsReloadsAndVersionsCatalogItemAcrossTransactions() {
        CatalogItemCreateDTO payload = new CatalogItemCreateDTO("SKU-PERSIST-1", "Persistent Item", "Stored");
        payload.setTags(new LinkedHashSet<>(Set.of("persistent", "candidate")));

        CatalogItem transientItem = mapper.toEntity(payload);
        assertThat(transientItem.getPersistenceVersion()).isNull();

        CatalogItemDTO created = service.create(payload);
        assertThat(created.getPersistenceVersion()).isZero();

        entityManager.clear();
        CatalogItemDTO reloadedAfterInsert = service.findById(created.getId()).orElseThrow();
        assertThat(reloadedAfterInsert.getPersistenceVersion()).isZero();
        assertThat(reloadedAfterInsert.getTags()).containsExactlyInAnyOrder("persistent", "candidate");

        CatalogItemDTO updated = service.update(
                created.getId(),
                new CatalogItemUpdateDTO("Persistent Item Updated", "Stored and updated")
        );
        assertThat(updated.getPersistenceVersion()).isEqualTo(1L);

        entityManager.clear();
        CatalogItemDTO reloadedAfterUpdate = service.findById(created.getId()).orElseThrow();
        assertThat(reloadedAfterUpdate.getPersistenceVersion()).isEqualTo(1L);
        assertThat(reloadedAfterUpdate.getName()).isEqualTo("Persistent Item Updated");
    }
}
