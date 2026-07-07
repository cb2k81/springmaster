package de.cocondo.system.entity;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.Set;

import org.junit.jupiter.api.Test;

class CoreEntityMarkerTypesTest {

    @Test
    void taggableExtendsIdentifyableContract() {
        Taggable taggable = new Taggable() {
            @Override
            public String getId() {
                return "sample-id";
            }

            @Override
            public Set<String> getTags() {
                return Set.of("core", "test");
            }
        };

        assertThat(taggable).isInstanceOf(Identifyable.class);
        assertThat(taggable.getId()).isEqualTo("sample-id");
        assertThat(taggable.getTags()).containsExactlyInAnyOrder("core", "test");
    }
}
