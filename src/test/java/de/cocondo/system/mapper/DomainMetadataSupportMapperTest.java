package de.cocondo.system.mapper;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.LocalDateTime;
import java.util.Set;

import de.cocondo.system.dto.DomainEntityMetadataDTO;
import de.cocondo.system.entity.DomainEntity;
import de.cocondo.system.entity.metadata.KeyValuePairDTO;
import org.junit.jupiter.api.Test;

class DomainMetadataSupportMapperTest {

    private final DomainMetadataSupportMapper mapper = new DomainMetadataSupportMapper() {
    };

    @Test
    void toMetadataReturnsNullForNullEntity() {
        assertThat(mapper.toMetadata(null)).isNull();
    }

    @Test
    void toMetadataMapsDomainEntityAuditAndTags() {
        LocalDateTime createdAt = LocalDateTime.of(2026, 6, 26, 10, 0);
        LocalDateTime lastModifiedAt = createdAt.plusMinutes(10);
        TestEntity entity = new TestEntity();
        entity.setId("entity-1");
        entity.setCreatedBy("creator");
        entity.setCreatedAt(createdAt);
        entity.setLastModifiedBy("modifier");
        entity.setLastModifiedAt(lastModifiedAt);
        entity.setTags(Set.of("core", "metadata"));

        DomainEntityMetadataDTO metadata = mapper.toMetadata(entity);

        assertThat(metadata.getId()).isEqualTo("entity-1");
        assertThat(metadata.getCreatedBy()).isEqualTo("creator");
        assertThat(metadata.getCreatedAt()).isEqualTo(createdAt);
        assertThat(metadata.getLastModifiedBy()).isEqualTo("modifier");
        assertThat(metadata.getLastModifiedAt()).isEqualTo(lastModifiedAt);
        assertThat(metadata.getTags()).containsExactlyInAnyOrder("core", "metadata");
        assertThat(metadata.getKeyValuePairs()).isEmpty();
    }

    @Test
    void toMetadataCanBeExtendedWithKeyValuePairMapping() {
        KeyValuePairDTO pair = new KeyValuePairDTO();
        pair.setKey("source");
        pair.setValue("idm");

        DomainMetadataSupportMapper customMapper = new DomainMetadataSupportMapper() {
            @Override
            public Set<KeyValuePairDTO> toKeyValuePairDtos(DomainEntity entity) {
                return Set.of(pair);
            }
        };

        DomainEntityMetadataDTO metadata = customMapper.toMetadata(new TestEntity());

        assertThat(metadata.getKeyValuePairs()).containsExactly(pair);
    }

    private static final class TestEntity extends DomainEntity {
    }
}
