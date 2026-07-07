package de.cocondo.system.entity;

import java.time.LocalDateTime;

import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AuditingEntityListener {

    private static final Logger log = LoggerFactory.getLogger(AuditingEntityListener.class);
    private static final String SYSTEM_USER = "SYSTEM";

    @PrePersist
    public void prePersist(Object entity) {
        if (entity instanceof Auditable auditable) {
            setCreationAttributes(auditable);
            setLastModifiedAttributes(auditable, auditable.getCreatedAt(), auditable.getCreatedBy());
            log.debug("Auditing attributes initialized for entityClass={}", entity.getClass().getSimpleName());
        }
    }

    @PreUpdate
    public void preUpdate(Object entity) {
        if (entity instanceof Auditable auditable) {
            setLastModifiedAttributes(auditable, LocalDateTime.now(), SYSTEM_USER);
            log.debug("Auditing attributes updated for entityClass={}", entity.getClass().getSimpleName());
        }
    }

    private void setCreationAttributes(Auditable auditable) {
        if (auditable.getCreatedBy() == null || auditable.getCreatedBy().isBlank()) {
            auditable.setCreatedBy(SYSTEM_USER);
        }
        if (auditable.getCreatedAt() == null) {
            auditable.setCreatedAt(LocalDateTime.now());
        }
    }

    private void setLastModifiedAttributes(Auditable auditable, LocalDateTime timestamp, String username) {
        auditable.setLastModifiedAt(timestamp != null ? timestamp : LocalDateTime.now());
        auditable.setLastModifiedBy(username != null && !username.isBlank() ? username : SYSTEM_USER);
    }
}
