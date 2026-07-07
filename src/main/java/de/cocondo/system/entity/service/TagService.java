package de.cocondo.system.entity.service;

import java.util.HashSet;
import java.util.Objects;
import java.util.Set;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import de.cocondo.system.entity.DomainEntity;

/**
 * Small tag helper for entities that use the Core {@link DomainEntity} tag collection.
 */
@Service
public class TagService {

    private static final Logger LOGGER = LoggerFactory.getLogger(TagService.class);

    public void addTag(DomainEntity entity, String tag) {
        Objects.requireNonNull(entity, "entity must not be null");
        LOGGER.debug("Adding tag='{}' to {}", tag, entity.getClass().getSimpleName());

        if (entity.getTags() == null) {
            entity.setTags(new HashSet<>());
        }
        entity.getTags().add(tag);
    }

    public void removeTag(DomainEntity entity, String tag) {
        Objects.requireNonNull(entity, "entity must not be null");
        LOGGER.debug("Removing tag='{}' from {}", tag, entity.getClass().getSimpleName());

        if (entity.getTags() != null) {
            entity.getTags().remove(tag);
        }
    }

    public Set<String> getAllTags(DomainEntity entity) {
        Objects.requireNonNull(entity, "entity must not be null");
        LOGGER.debug("Retrieving all tags for {}", entity.getClass().getSimpleName());
        return entity.getTags() != null ? entity.getTags() : new HashSet<>();
    }

    public boolean hasTag(DomainEntity entity, String tag) {
        Objects.requireNonNull(entity, "entity must not be null");
        LOGGER.debug("Checking if tag='{}' exists in {}", tag, entity.getClass().getSimpleName());
        return entity.getTags() != null && entity.getTags().contains(tag);
    }
}
