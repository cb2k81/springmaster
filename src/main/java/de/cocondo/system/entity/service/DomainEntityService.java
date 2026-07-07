package de.cocondo.system.entity.service;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.util.Objects;

import org.springframework.stereotype.Service;

import de.cocondo.system.core.id.IdGeneratorService;
import de.cocondo.system.entity.DomainEntity;

/**
 * Factory-style support service for creating Core domain entities with a technical identifier.
 */
@Service
public class DomainEntityService {

    private final IdGeneratorService idGeneratorService;

    public DomainEntityService(IdGeneratorService idGeneratorService) {
        this.idGeneratorService = Objects.requireNonNull(idGeneratorService, "idGeneratorService must not be null");
    }

    public <T extends DomainEntity> T createNewEntity(Class<T> entityClass) {
        Objects.requireNonNull(entityClass, "entityClass must not be null");

        try {
            Constructor<T> constructor = entityClass.getDeclaredConstructor();
            if (!constructor.canAccess(null)) {
                constructor.setAccessible(true);
            }

            T entity = constructor.newInstance();
            entity.setId(idGeneratorService.generateId());
            return entity;
        } catch (NoSuchMethodException | InstantiationException | IllegalAccessException | InvocationTargetException e) {
            throw new IllegalStateException("Error creating entity of class " + entityClass.getName(), e);
        }
    }
}
