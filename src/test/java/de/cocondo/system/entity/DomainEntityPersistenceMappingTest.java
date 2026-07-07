package de.cocondo.system.entity;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.Set;
import java.util.UUID;

import jakarta.persistence.ElementCollection;
import jakarta.persistence.EntityListeners;
import jakarta.persistence.FetchType;
import jakarta.persistence.Id;
import jakarta.persistence.MappedSuperclass;
import jakarta.persistence.Version;
import org.junit.jupiter.api.Test;

class DomainEntityPersistenceMappingTest {

    @Test
    void domainEntityIsMappedSuperclassWithTechnicalListeners() throws NoSuchFieldException {
        assertNotNull(DomainEntity.class.getAnnotation(MappedSuperclass.class));
        EntityListeners listeners = DomainEntity.class.getAnnotation(EntityListeners.class);
        assertNotNull(listeners);
        assertArrayEquals(new Class<?>[] {DomainEntityListener.class, AuditingEntityListener.class}, listeners.value());

        assertNotNull(DomainEntity.class.getDeclaredField("id").getAnnotation(Id.class));
        assertNotNull(DomainEntity.class.getDeclaredField("persistenceVersion").getAnnotation(Version.class));

        ElementCollection tags = DomainEntity.class.getDeclaredField("tags").getAnnotation(ElementCollection.class);
        assertNotNull(tags);
        assertEquals(FetchType.EAGER, tags.fetch());
    }

    @Test
    void domainEntityInitializesIdVersionAndTags() {
        TestEntity entity = new TestEntity();

        assertNotNull(entity.getId());
        assertFalse(entity.getId().isBlank());
        assertNotNull(UUID.fromString(entity.getId()));
        assertEquals(0L, entity.getPersistenceVersion());
        assertNotNull(entity.getTags());
        assertTrue(entity.getTags().isEmpty());
    }

    @Test
    void setTagsNormalizesNullToEmptySet() {
        TestEntity entity = new TestEntity();

        entity.setTags(null);

        assertNotNull(entity.getTags());
        assertTrue(entity.getTags().isEmpty());
    }

    @Test
    void equalityUsesConcreteClassAndIdentifier() {
        TestEntity first = new TestEntity();
        TestEntity second = new TestEntity();
        second.setId(first.getId());
        OtherTestEntity otherType = new OtherTestEntity();
        otherType.setId(first.getId());

        assertEquals(first, second);
        assertEquals(first.hashCode(), second.hashCode());
        assertNotEquals(first, otherType);
        assertTrue(first.toString().contains(first.getId()));
    }

    @Test
    void tagsRemainMutableForJpaAndDomainUsage() {
        TestEntity entity = new TestEntity();
        entity.setTags(Set.of("demo", "core"));

        assertEquals(Set.of("demo", "core"), entity.getTags());
    }

    private static final class TestEntity extends DomainEntity {
    }

    private static final class OtherTestEntity extends DomainEntity {
    }
}
