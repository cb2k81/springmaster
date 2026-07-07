package de.cocondo.system.entity;

import java.time.LocalDateTime;

public interface Auditable extends Identifyable {

    String getCreatedBy();

    void setCreatedBy(String createdBy);

    LocalDateTime getCreatedAt();

    void setCreatedAt(LocalDateTime createdAt);

    String getLastModifiedBy();

    void setLastModifiedBy(String lastModifiedBy);

    LocalDateTime getLastModifiedAt();

    void setLastModifiedAt(LocalDateTime lastModifiedAt);
}
