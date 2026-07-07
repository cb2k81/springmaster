package de.cocondo.system.entity;

import java.util.UUID;

import jakarta.persistence.PrePersist;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DomainEntityListener {

    private static final Logger log = LoggerFactory.getLogger(DomainEntityListener.class);

    @PrePersist
    public void prePersist(DomainEntity entity) {
        if (entity == null) {
            throw new IllegalArgumentException("DomainEntity must not be null");
        }
        if (entity.getId() == null || entity.getId().isBlank()) {
            entity.setId(UUID.randomUUID().toString());
            log.warn("DomainEntity without ID detected during PrePersist: entityClass={}", entity.getClass().getSimpleName());
            return;
        }
        log.debug("PrePersist check passed: entityClass={}, id={}", entity.getClass().getSimpleName(), entity.getId());
    }
}
