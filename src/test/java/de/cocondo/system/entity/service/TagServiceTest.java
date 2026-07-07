package de.cocondo.system.entity.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.util.HashSet;
import java.util.Set;

import org.junit.jupiter.api.Test;
import org.springframework.stereotype.Service;

import de.cocondo.system.entity.DomainEntity;

class TagServiceTest {

    private final TagService service = new TagService();

    @Test
    void addTagAddsTagToEntity() {
        SampleEntity entity = new SampleEntity();

        service.addTag(entity, "core");

        assertThat(entity.getTags()).containsExactly("core");
        assertThat(service.hasTag(entity, "core")).isTrue();
    }

    @Test
    void addTagNormalizesNullTagSet() {
        SampleEntity entity = new SampleEntity();
        entity.setTags(null);

        service.addTag(entity, "springmaster");

        assertThat(entity.getTags()).containsExactly("springmaster");
    }

    @Test
    void removeTagRemovesExistingTag() {
        SampleEntity entity = new SampleEntity();
        entity.setTags(new HashSet<>(Set.of("core", "obsolete")));

        service.removeTag(entity, "obsolete");

        assertThat(service.getAllTags(entity)).containsExactly("core");
        assertThat(service.hasTag(entity, "obsolete")).isFalse();
    }

    @Test
    void getAllTagsReturnsEmptySetWhenEntityHasNoTags() {
        SampleEntity entity = new SampleEntity();
        entity.setTags(null);

        assertThat(service.getAllTags(entity)).isEmpty();
    }

    @Test
    void methodsRequireEntity() {
        assertThatThrownBy(() -> service.addTag(null, "core"))
            .isInstanceOf(NullPointerException.class)
            .hasMessageContaining("entity");
        assertThatThrownBy(() -> service.removeTag(null, "core"))
            .isInstanceOf(NullPointerException.class)
            .hasMessageContaining("entity");
        assertThatThrownBy(() -> service.getAllTags(null))
            .isInstanceOf(NullPointerException.class)
            .hasMessageContaining("entity");
        assertThatThrownBy(() -> service.hasTag(null, "core"))
            .isInstanceOf(NullPointerException.class)
            .hasMessageContaining("entity");
    }

    @Test
    void serviceIsSpringComponent() {
        assertThat(TagService.class.getAnnotation(Service.class)).isNotNull();
    }

    private static final class SampleEntity extends DomainEntity {
    }
}
