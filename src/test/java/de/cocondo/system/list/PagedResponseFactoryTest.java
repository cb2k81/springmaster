package de.cocondo.system.list;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.List;

import de.cocondo.system.dto.PagedResponseDTO;
import org.junit.jupiter.api.Test;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;

class PagedResponseFactoryTest {

    private final PagedResponseFactory factory = new PagedResponseFactory();

    @Test
    void fromPageMapsContentAndCopiesPaginationMetadata() {
        Page<Integer> page = new PageImpl<>(
                List.of(1, 2),
                PageRequest.of(1, 2),
                5
        );

        PagedResponseDTO<String> response = factory.fromPage(page, value -> "item-" + value);

        assertThat(response.getItems()).containsExactly("item-1", "item-2");
        assertThat(response.getPage()).isEqualTo(1);
        assertThat(response.getSize()).isEqualTo(2);
        assertThat(response.getTotalElements()).isEqualTo(5);
        assertThat(response.getTotalPages()).isEqualTo(3);
    }
}
