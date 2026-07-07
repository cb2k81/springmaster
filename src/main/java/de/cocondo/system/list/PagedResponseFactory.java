package de.cocondo.system.list;

import java.util.function.Function;

import de.cocondo.system.dto.PagedResponseDTO;
import org.springframework.data.domain.Page;
import org.springframework.stereotype.Component;

@Component
public class PagedResponseFactory {

    public <S, T> PagedResponseDTO<T> fromPage(Page<S> page, Function<S, T> mapper) {
        PagedResponseDTO<T> response = new PagedResponseDTO<>();
        response.setItems(page.getContent().stream().map(mapper).toList());
        response.setPage(page.getNumber());
        response.setSize(page.getSize());
        response.setTotalElements(page.getTotalElements());
        response.setTotalPages(page.getTotalPages());
        return response;
    }
}
