package de.cocondo.system.query;

import static org.assertj.core.api.Assertions.assertThat;

import de.cocondo.system.dto.CountResponseDTO;
import de.cocondo.system.dto.PagedResponseDTO;
import java.util.List;
import org.junit.jupiter.api.Test;

class ResultSetQueryOperationsTest {

    @Test
    void providesTypedContractsForPagedAllAndCountQueries() {
        ResultSetQueryOperations<PageQuery, AllQuery, CountQuery, String> operations = new SampleOperations();

        PagedResponseDTO<String> page = operations.listPaged(new PageQuery(0, 2));
        List<String> all = operations.listAll(new AllQuery("A"));
        CountResponseDTO count = operations.count(new CountQuery("A"));

        assertThat(page.getItems()).containsExactly("A-1", "A-2");
        assertThat(page.getTotalElements()).isEqualTo(3);
        assertThat(all).containsExactly("A-1", "A-2", "A-3");
        assertThat(count.getTotalElements()).isEqualTo(3);
    }

    private record PageQuery(int page, int size) {
    }

    private record AllQuery(String prefix) {
    }

    private record CountQuery(String prefix) {
    }

    private static final class SampleOperations
            implements ResultSetQueryOperations<PageQuery, AllQuery, CountQuery, String> {

        private final List<String> values = List.of("A-1", "A-2", "A-3", "B-1");

        @Override
        public PagedResponseDTO<String> listPaged(PageQuery query) {
            PagedResponseDTO<String> response = new PagedResponseDTO<>();
            response.setItems(values.stream().filter(value -> value.startsWith("A-")).limit(query.size()).toList());
            response.setPage(query.page());
            response.setSize(query.size());
            response.setTotalElements(3);
            response.setTotalPages(2);
            return response;
        }

        @Override
        public List<String> listAll(AllQuery query) {
            return values.stream().filter(value -> value.startsWith(query.prefix())).toList();
        }

        @Override
        public CountResponseDTO count(CountQuery query) {
            return CountResponseDTO.of(values.stream().filter(value -> value.startsWith(query.prefix())).count());
        }
    }
}
