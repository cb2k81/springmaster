package de.cocondo.system.dto;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Set;

import de.cocondo.system.entity.metadata.KeyValuePairDTO;
import jakarta.validation.ValidationException;
import org.junit.jupiter.api.Test;

class CoreDtoMarkerTypesTest {

    @Test
    void dtoMarkerIsSerializable() {
        assertThat(DTO.class).isAssignableTo(Serializable.class);
    }

    @Test
    void domainEntityMetadataInboundDtoIsInstantiable() {
        assertThat(new DomainEntityMetadataInboundDTO()).isNotNull();
    }

    @Test
    void dataTransferObjectCanBeUsedAsMarkerInterface() {
        class SampleDataTransferObject implements DataTransferObject {
        }

        assertThat(new SampleDataTransferObject()).isInstanceOf(DataTransferObject.class);
    }

    @Test
    void domainEntityDtoExposesMetadataContract() {
        class SampleDomainEntityDto implements DomainEntityDTO {
            private DomainEntityMetadataDTO metadata;

            @Override
            public DomainEntityMetadataDTO getMetadata() {
                return metadata;
            }

            @Override
            public void setMetadata(DomainEntityMetadataDTO metadata) {
                this.metadata = metadata;
            }
        }

        DomainEntityMetadataDTO metadata = new DomainEntityMetadataDTO();
        SampleDomainEntityDto dto = new SampleDomainEntityDto();

        dto.setMetadata(metadata);

        assertThat(dto.getMetadata()).isSameAs(metadata);
        assertThat(dto).isInstanceOf(DTO.class);
    }

    @Test
    void domainEntityInboundDtoCarriesTagsAndKeyValuePairsAndValidationHook() {
        KeyValuePairDTO keyValuePair = new KeyValuePairDTO();
        keyValuePair.setKey("source");
        keyValuePair.setValue("idm");

        class SampleInboundDto extends DomainEntityInboundDTO {
        }

        SampleInboundDto dto = new SampleInboundDto();
        dto.setTags(Set.of("core"));
        dto.setKeyValuePairs(Set.of(keyValuePair));

        assertThat(dto.getTags()).containsExactly("core");
        assertThat(dto.getKeyValuePairs()).containsExactly(keyValuePair);
        assertThat(dto.isValid()).isTrue();
    }

    @Test
    void domainEntityInboundDtoReportsValidationFailure() {
        class InvalidInboundDto extends DomainEntityInboundDTO {
            @Override
            public void validate() {
                throw new ValidationException("invalid");
            }
        }

        assertThat(new InvalidInboundDto().isValid()).isFalse();
    }

    @Test
    void domainEntityUpdateDtoCarriesIdentifier() {
        DomainEntityUpdateDTO dto = new DomainEntityUpdateDTO();

        dto.setId("entity-1");

        assertThat(dto.getId()).isEqualTo("entity-1");
        assertThat(dto).isInstanceOf(DomainEntityInboundDTO.class);
    }

    @Test
    void domainEntityMetadataDtoCarriesAuditTagsAndKeyValuePairs() {
        LocalDateTime createdAt = LocalDateTime.of(2026, 6, 26, 10, 30);
        LocalDateTime lastModifiedAt = createdAt.plusMinutes(5);
        KeyValuePairDTO keyValuePair = new KeyValuePairDTO();
        keyValuePair.setKey("owner");
        keyValuePair.setValue("platform");

        DomainEntityMetadataDTO dto = new DomainEntityMetadataDTO();
        dto.setId("entity-1");
        dto.setCreatedBy("creator");
        dto.setCreatedAt(createdAt);
        dto.setLastModifiedBy("modifier");
        dto.setLastModifiedAt(lastModifiedAt);
        dto.setTags(Set.of("metadata"));
        dto.setKeyValuePairs(Set.of(keyValuePair));

        assertThat(dto.getId()).isEqualTo("entity-1");
        assertThat(dto.getCreatedBy()).isEqualTo("creator");
        assertThat(dto.getCreatedAt()).isEqualTo(createdAt);
        assertThat(dto.getLastModifiedBy()).isEqualTo("modifier");
        assertThat(dto.getLastModifiedAt()).isEqualTo(lastModifiedAt);
        assertThat(dto.getTags()).containsExactly("metadata");
        assertThat(dto.getKeyValuePairs()).containsExactly(keyValuePair);
    }

    @Test
    void pagedResponseDtoCarriesStablePaginationContract() {
        PagedResponseDTO<String> dto = new PagedResponseDTO<>();

        dto.setItems(List.of("a", "b"));
        dto.setPage(1);
        dto.setSize(2);
        dto.setTotalElements(5);
        dto.setTotalPages(3);

        assertThat(dto.getItems()).containsExactly("a", "b");
        assertThat(dto.getPage()).isEqualTo(1);
        assertThat(dto.getSize()).isEqualTo(2);
        assertThat(dto.getTotalElements()).isEqualTo(5);
        assertThat(dto.getTotalPages()).isEqualTo(3);
    }

    @Test
    void countResponseDtoCarriesStableCountOnlyContract() {
        CountResponseDTO dto = CountResponseDTO.of(12);

        assertThat(dto.getTotalElements()).isEqualTo(12);
    }
}
