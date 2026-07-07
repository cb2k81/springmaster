package de.cocondo.platform.demo.catalog;

import static org.assertj.core.api.Assertions.assertThat;

import de.cocondo.platform.app.SpringmasterApplication;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest(classes = SpringmasterApplication.class)
class CatalogItemServiceSpringContextTest {

    @Autowired
    private CatalogItemService service;

    @BeforeEach
    void resetService() {
        service.clear();
    }

    @Test
    void demoServiceIsDiscoveredBySpringApplicationScan() {
        CatalogItemDTO created = service.create(new CatalogItemCreateDTO("SCAN-1", "Scanned Demo Item", null));

        assertThat(created.getSku()).isEqualTo("SCAN-1");
        assertThat(service.findBySku("scan-1")).isPresent();
    }
}
