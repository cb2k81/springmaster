package de.cocondo.platform.tooling.backendcontract;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

class BackendContractToolIntegrationTest {
    private static final Path INDEX = Path.of(
            "contracts/api/fixtures/sprint-003/fixture-index.v1.json"
    );

    private final ObjectMapper objectMapper = new ObjectMapper();

    @TempDir
    private Path tempDirectory;

    @Test
    void validatesAndBuildsDeterministicCatalogAndExport() throws Exception {
        ToolResult validation = run("validate", "--fixture-index", INDEX.toString(), "--format", "json");
        assertThat(validation.exitCode()).isZero();
        assertThat(validation.json().path("status").asText()).isEqualTo("PASS");

        Path firstCatalog = tempDirectory.resolve("catalog-1.json");
        Path secondCatalog = tempDirectory.resolve("catalog-2.json");
        assertPass(run("catalog", "--fixture-index", INDEX.toString(), "--output",
                firstCatalog.toString(), "--format", "json"));
        assertPass(run("catalog", "--fixture-index", INDEX.toString(), "--output",
                secondCatalog.toString(), "--format", "json"));
        assertThat(Files.readAllBytes(firstCatalog)).isEqualTo(Files.readAllBytes(secondCatalog));

        Path firstExport = tempDirectory.resolve("contracts-1.zip");
        Path secondExport = tempDirectory.resolve("contracts-2.zip");
        assertPass(run("export", "--fixture-index", INDEX.toString(), "--output",
                firstExport.toString(), "--format", "json"));
        assertPass(run("export", "--fixture-index", INDEX.toString(), "--output",
                secondExport.toString(), "--format", "json"));
        assertThat(Files.readAllBytes(firstExport)).isEqualTo(Files.readAllBytes(secondExport));
    }

    @Test
    void rejectsCatalogDriftWithStableDiagnostic() throws Exception {
        Path catalog = tempDirectory.resolve("catalog.json");
        Files.writeString(catalog, "{}\n", StandardCharsets.UTF_8);

        ToolResult result = run("verify", "--fixture-index", INDEX.toString(),
                "--catalog", catalog.toString(), "--format", "json");

        assertThat(result.exitCode()).isEqualTo(1);
        assertThat(result.json().path("status").asText()).isEqualTo("FAIL");
        assertThat(result.json().path("diagnosticCode").asText())
                .isEqualTo("BACKEND_CONTRACT_CATALOG_DRIFT");
    }

    private void assertPass(ToolResult result) {
        assertThat(result.exitCode()).isZero();
        assertThat(result.json().path("status").asText()).isEqualTo("PASS");
    }

    private ToolResult run(String... arguments) throws IOException, InterruptedException {
        String[] command = new String[arguments.length + 2];
        command[0] = "python3";
        command[1] = "bin/backend-contract.py";
        System.arraycopy(arguments, 0, command, 2, arguments.length);
        Process process = new ProcessBuilder(command).redirectErrorStream(true).start();
        String output = new String(process.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
        int exitCode = process.waitFor();
        return new ToolResult(exitCode, objectMapper.readTree(output));
    }

    private record ToolResult(int exitCode, JsonNode json) {
    }
}
