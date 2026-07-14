package de.cocondo.system.http;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

class ApiErrorIdGeneratorTest {

    @Test
    void nextErrorIdCreatesOpaquePrefixedIdentifier() {
        ApiErrorIdGenerator generator = new ApiErrorIdGenerator();

        String first = generator.nextErrorId();
        String second = generator.nextErrorId();

        assertThat(first).startsWith("err-");
        assertThat(second).startsWith("err-");
        assertThat(first).isNotEqualTo(second);
    }
}
