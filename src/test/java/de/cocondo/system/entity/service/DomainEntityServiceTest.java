package de.cocondo.system.entity.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import org.junit.jupiter.api.Test;
import org.springframework.stereotype.Service;

import de.cocondo.system.core.id.IdGeneratorService;
import de.cocondo.system.entity.DomainEntity;

class DomainEntityServiceTest {

    @Test
    void createNewEntityCreatesEntityAndAssignsGeneratedId() {
        DomainEntityService service = new DomainEntityService(new FixedIdGeneratorService("generated-id"));

        SampleEntity entity = service.createNewEntity(SampleEntity.class);

        assertThat(entity).isNotNull();
        assertThat(entity.getId()).isEqualTo("generated-id");
    }

    @Test
    void createNewEntitySupportsNonPublicNoArgConstructors() {
        DomainEntityService service = new DomainEntityService(new FixedIdGeneratorService("private-id"));

        PrivateConstructorEntity entity = service.createNewEntity(PrivateConstructorEntity.class);

        assertThat(entity.getId()).isEqualTo("private-id");
    }

    @Test
    void createNewEntityRejectsMissingNoArgConstructor() {
        DomainEntityService service = new DomainEntityService(new FixedIdGeneratorService("unused"));

        assertThatThrownBy(() -> service.createNewEntity(NoDefaultConstructorEntity.class))
            .isInstanceOf(IllegalStateException.class)
            .hasMessageContaining(NoDefaultConstructorEntity.class.getName());
    }

    @Test
    void serviceIsSpringComponent() {
        assertThat(DomainEntityService.class.getAnnotation(Service.class)).isNotNull();
    }

    private record FixedIdGeneratorService(String id) implements IdGeneratorService {
        @Override
        public String generateId() {
            return id;
        }
    }

    private static final class SampleEntity extends DomainEntity {
    }

    private static final class PrivateConstructorEntity extends DomainEntity {
        private PrivateConstructorEntity() {
        }
    }

    private static final class NoDefaultConstructorEntity extends DomainEntity {
        private NoDefaultConstructorEntity(String ignored) {
        }
    }
}
