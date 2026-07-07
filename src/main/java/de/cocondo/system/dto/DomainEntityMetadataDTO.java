package de.cocondo.system.dto;

import java.time.LocalDateTime;
import java.util.Set;

import de.cocondo.system.entity.metadata.KeyValuePairDTO;

public class DomainEntityMetadataDTO {

    private String id;
    private String createdBy;
    private LocalDateTime createdAt;
    private String lastModifiedBy;
    private LocalDateTime lastModifiedAt;
    private Set<String> tags;
    private Set<KeyValuePairDTO> keyValuePairs;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getCreatedBy() {
        return createdBy;
    }

    public void setCreatedBy(String createdBy) {
        this.createdBy = createdBy;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public String getLastModifiedBy() {
        return lastModifiedBy;
    }

    public void setLastModifiedBy(String lastModifiedBy) {
        this.lastModifiedBy = lastModifiedBy;
    }

    public LocalDateTime getLastModifiedAt() {
        return lastModifiedAt;
    }

    public void setLastModifiedAt(LocalDateTime lastModifiedAt) {
        this.lastModifiedAt = lastModifiedAt;
    }

    public Set<String> getTags() {
        return tags;
    }

    public void setTags(Set<String> tags) {
        this.tags = tags;
    }

    public Set<KeyValuePairDTO> getKeyValuePairs() {
        return keyValuePairs;
    }

    public void setKeyValuePairs(Set<KeyValuePairDTO> keyValuePairs) {
        this.keyValuePairs = keyValuePairs;
    }
}
