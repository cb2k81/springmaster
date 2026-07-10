package de.cocondo.system.dto;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import org.junit.jupiter.api.Test;

class CountResponseDTOTest {

    @Test
    void defaultConstructorInitializesZeroTotalElements() {
        CountResponseDTO dto = new CountResponseDTO();

        assertThat(dto.getTotalElements()).isZero();
    }

    @Test
    void constructorCarriesTotalElements() {
        CountResponseDTO dto = new CountResponseDTO(42);

        assertThat(dto.getTotalElements()).isEqualTo(42);
    }

    @Test
    void factoryCarriesTotalElements() {
        CountResponseDTO dto = CountResponseDTO.of(7);

        assertThat(dto.getTotalElements()).isEqualTo(7);
    }

    @Test
    void setterCarriesTotalElements() {
        CountResponseDTO dto = new CountResponseDTO();

        dto.setTotalElements(3);

        assertThat(dto.getTotalElements()).isEqualTo(3);
    }

    @Test
    void constructorRejectsNegativeTotalElements() {
        assertThatThrownBy(() -> new CountResponseDTO(-1))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("totalElements must be non-negative");
    }

    @Test
    void setterRejectsNegativeTotalElements() {
        CountResponseDTO dto = new CountResponseDTO();

        assertThatThrownBy(() -> dto.setTotalElements(-1))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("totalElements must be non-negative");
    }
}
