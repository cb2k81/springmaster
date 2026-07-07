package de.cocondo.system.entity.metadata;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.Serializable;

import org.junit.jupiter.api.Test;

class CoreMetadataDtoTypesTest {

    @Test
    void keyValuePairDtoCarriesKeyAndValueAndIsSerializable() {
        KeyValuePairDTO dto = new KeyValuePairDTO();

        dto.setKey("key");
        dto.setValue("value");

        assertThat(dto).isInstanceOf(Serializable.class);
        assertThat(dto.getKey()).isEqualTo("key");
        assertThat(dto.getValue()).isEqualTo("value");
    }

    @Test
    void keyValuePairPayloadCarriesKeyAndValue() {
        KeyValuePairPayload payload = new KeyValuePairPayload();

        payload.setKey("key");
        payload.setValue("value");

        assertThat(payload.getKey()).isEqualTo("key");
        assertThat(payload.getValue()).isEqualTo("value");
    }
}
