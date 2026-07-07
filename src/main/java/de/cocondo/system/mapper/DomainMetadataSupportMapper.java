package de.cocondo.system.mapper;

import java.util.Collections;
import java.util.Set;

import de.cocondo.system.dto.DomainEntityMetadataDTO;
import de.cocondo.system.entity.DomainEntity;
import de.cocondo.system.entity.metadata.KeyValuePairDTO;

public interface DomainMetadataSupportMapper {

    default DomainEntityMetadataDTO toMetadata(DomainEntity entity) {
        if (entity == null) {
            return null;
        }

        DomainEntityMetadataDTO dto = new DomainEntityMetadataDTO();
        dto.setId(entity.getId());
        dto.setCreatedBy(entity.getCreatedBy());
        dto.setCreatedAt(entity.getCreatedAt());
        dto.setLastModifiedBy(entity.getLastModifiedBy());
        dto.setLastModifiedAt(entity.getLastModifiedAt());
        dto.setTags(entity.getTags());
        dto.setKeyValuePairs(toKeyValuePairDtos(entity));
        return dto;
    }

    default Set<KeyValuePairDTO> toKeyValuePairDtos(DomainEntity entity) {
        return Collections.emptySet();
    }
}
