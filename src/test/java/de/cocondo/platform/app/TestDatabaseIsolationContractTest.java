package de.cocondo.platform.app;

import static org.assertj.core.api.Assertions.assertThat;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;
import javax.sql.DataSource;
import org.junit.jupiter.api.Test;
import org.springframework.boot.WebApplicationType;
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.context.ConfigurableApplicationContext;

class TestDatabaseIsolationContractTest {

    @Test
    void testProfileUsesDistinctLiquibaseManagedDatabasePerApplicationContext() throws Exception {
        try (
                ConfigurableApplicationContext first = testContext();
                ConfigurableApplicationContext second = testContext()
        ) {
            DataSource firstDataSource = first.getBean(DataSource.class);
            DataSource secondDataSource = second.getBean(DataSource.class);

            String firstConfiguredUrl = configuredJdbcUrl(first);
            String secondConfiguredUrl = configuredJdbcUrl(second);
            String firstRuntimeUrl = runtimeJdbcUrl(firstDataSource);
            String secondRuntimeUrl = runtimeJdbcUrl(secondDataSource);

            assertConfiguredTestUrl(firstConfiguredUrl);
            assertConfiguredTestUrl(secondConfiguredUrl);
            assertThat(secondConfiguredUrl).isNotEqualTo(firstConfiguredUrl);

            assertThat(firstRuntimeUrl).startsWith("jdbc:h2:mem:springmaster-");
            assertThat(secondRuntimeUrl)
                    .startsWith("jdbc:h2:mem:springmaster-")
                    .isNotEqualTo(firstRuntimeUrl);

            assertLiquibaseInitialized(firstDataSource);
            assertLiquibaseInitialized(secondDataSource);
        }
    }

    private ConfigurableApplicationContext testContext() {
        return new SpringApplicationBuilder(SpringmasterApplication.class)
                .profiles("test")
                .web(WebApplicationType.NONE)
                .properties("spring.main.banner-mode=off")
                .run();
    }

    private String configuredJdbcUrl(ConfigurableApplicationContext context) {
        return context.getEnvironment().getRequiredProperty("spring.datasource.url");
    }

    private void assertConfiguredTestUrl(String jdbcUrl) {
        assertThat(jdbcUrl)
                .startsWith("jdbc:h2:mem:springmaster-")
                .contains(";MODE=MariaDB")
                .contains(";DATABASE_TO_LOWER=TRUE");
    }

    private String runtimeJdbcUrl(DataSource dataSource) throws Exception {
        try (Connection connection = dataSource.getConnection()) {
            return connection.getMetaData().getURL();
        }
    }

    private void assertLiquibaseInitialized(DataSource dataSource) throws Exception {
        try (
                Connection connection = dataSource.getConnection();
                Statement statement = connection.createStatement();
                ResultSet result = statement.executeQuery("select count(*) from databasechangelog")
        ) {
            assertThat(result.next()).isTrue();
            assertThat(result.getInt(1)).isGreaterThan(0);
        }
    }
}
