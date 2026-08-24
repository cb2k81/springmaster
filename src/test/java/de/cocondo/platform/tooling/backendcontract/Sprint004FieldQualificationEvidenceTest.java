package de.cocondo.platform.tooling.backendcontract;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.Set;
import org.junit.jupiter.api.Test;

class Sprint004FieldQualificationEvidenceTest {

    private static final Path EVIDENCE = Path.of(
            "contracts/api/evidence/sprint-004/personnel-000248-field-qualification.v1.json"
    );
    private static final Path IMPLEMENTATION_RESULT = Path.of(
            "contracts/api/evidence/sprint-004/sprint-004-implementation-result.v1.json"
    );
    private static final Path FIXTURE_INDEX = Path.of(
            "contracts/api/fixtures/sprint-004/fixture-index.v1.json"
    );
    private static final Set<String> MANDATORY_CASE_IDS = Set.of(
            "RW-01", "RW-02", "RW-03", "RW-04", "RW-05", "RW-06", "RW-07"
    );
    private static final Set<String> TOP_LEVEL_FIELDS = Set.of(
            "schemaVersion",
            "evidenceId",
            "sourceProject",
            "sourceExportSha256",
            "acceptedSourceCommit",
            "acceptedSourcePatch",
            "excludedCandidatePatch",
            "excludedCandidatePaths",
            "cases"
    );
    private static final Set<String> CASE_FIELDS = Set.of(
            "caseId", "sourceReferences", "springmasterMapping", "result"
    );
    private static final Set<String> EXCLUDED_CANDIDATE_PATHS = Set.of(
            "PROJECT_DOCS/ADR/PERS_ADR_0036_PERSON_ORGANISATION_AND_ORGANISATION_LINEAGE.md",
            "PROJECT_DOCS/ADR/PERS_ADR_0045_WORKSPACE_API_CONTRACT.md",
            "PROJECT_DOCS/ADR/PERS_ADR_0046_PLANNED_WORKFORCE_P1A.md",
            "PROJECT_DOCS/PLANNING/PERSONNEL_STAFFING_PLAN_WORKSPACE_BACKEND_IMPLEMENTATION_PLAN.md",
            "PROJECT_DOCS/REGISTERS/PERSONNEL_ARCHITECTURE_DECISION_REGISTER.md",
            "PROJECT_DOCS/REGISTERS/PERSONNEL_CONTRACT_TRACEABILITY_REGISTER.md",
            "PROJECT_DOCS/REGISTERS/PERSONNEL_TEST_TRACEABILITY_REGISTER.md",
            "PROJECT_DOCS/REGISTERS/PERSONNEL_USE_CASE_IMPLEMENTATION_REGISTER.md",
            "PROJECT_DOCS/REQUIREMENTS/PERSONNEL_BUSINESS_TERMS_AND_POLICIES.md",
            "PROJECT_DOCS/REQUIREMENTS/PERSONNEL_FUNCTIONAL_REQUIREMENT_CATALOG.md",
            "PROJECT_DOCS/REQUIREMENTS/PERSONNEL_INVARIANT_AND_CAPACITY_CATALOG.md",
            "PROJECT_DOCS/REQUIREMENTS/PERSONNEL_ROLES_AND_CAPABILITIES.md",
            "PROJECT_DOCS/REQUIREMENTS/PERSONNEL_USE_CASE_ACCEPTANCE_SCENARIOS.md",
            "PROJECT_DOCS/REQUIREMENTS/PERSONNEL_USE_CASE_CATALOG.md",
            "PROJECT_DOCS/index.md",
            "src/main/resources/doc/governance/PERSONNEL_PERMISSION_MATRIX.md",
            "patches/logs/composite/CHANGELOG-PERSONNEL-WORKFORCE-DISCOVERY-CONTRACT-FREEZE.md"
    );

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Test
    void bindsExactlySevenPassingCasesToAcceptedPersonnel000248Evidence() throws Exception {
        JsonNode evidence = objectMapper.readTree(EVIDENCE.toFile());

        assertThat(fieldNames(evidence)).isEqualTo(TOP_LEVEL_FIELDS);
        assertThat(evidence.path("schemaVersion").asText())
                .isEqualTo("cocondo.sprint-004-field-qualification.v1");
        assertThat(evidence.path("evidenceId").asText())
                .isEqualTo("S004-PERSONNEL-000248-FIELD-QUALIFICATION");
        assertThat(evidence.path("sourceProject").asText()).isEqualTo("Personnel");
        assertThat(evidence.path("sourceExportSha256").asText())
                .isEqualTo("541b6f97d22ca6aeb532f6d3f25f6f09fc16591ef7161791b5160a98f6cffb61");
        assertThat(evidence.path("acceptedSourceCommit").asText())
                .isEqualTo("1094199a84aeb809865d2992ef2aab65d8488226");
        assertThat(evidence.path("acceptedSourcePatch").asText())
                .isEqualTo("000248_personnel_workspace_post_wsf2_contract_guardrails");
        assertThat(evidence.path("excludedCandidatePatch").asText())
                .isEqualTo("000249_personnel_workforce_discovery_contract_freeze");

        JsonNode excludedCandidatePaths = evidence.path("excludedCandidatePaths");
        assertThat(excludedCandidatePaths.isArray()).isTrue();
        assertThat(excludedCandidatePaths).hasSize(EXCLUDED_CANDIDATE_PATHS.size());
        Set<String> excludedPaths = textValues(excludedCandidatePaths);
        assertThat(excludedPaths).isEqualTo(EXCLUDED_CANDIDATE_PATHS);

        JsonNode cases = evidence.path("cases");
        assertThat(cases.isArray()).isTrue();
        assertThat(cases).hasSize(7);
        Set<String> observedCaseIds = new HashSet<>();
        for (JsonNode qualificationCase : cases) {
            assertThat(fieldNames(qualificationCase)).isEqualTo(CASE_FIELDS);
            assertThat(observedCaseIds.add(qualificationCase.path("caseId").asText())).isTrue();
            assertThat(qualificationCase.path("result").asText()).isEqualTo("PASS");
            assertThat(qualificationCase.path("springmasterMapping").isObject()).isTrue();
            assertThat(qualificationCase.path("springmasterMapping").isEmpty()).isFalse();
            JsonNode references = qualificationCase.path("sourceReferences");
            assertThat(references.isArray()).isTrue();
            assertThat(references.isEmpty()).isFalse();
            for (JsonNode reference : references) {
                assertThat(reference.asText()).isNotBlank();
                assertThat(excludedPaths).doesNotContain(reference.asText());
            }
        }
        assertThat(observedCaseIds).isEqualTo(MANDATORY_CASE_IDS);
    }

    @Test
    void validatesSprint004FixturesWithExistingBackendContractTool() throws Exception {
        Process process = new ProcessBuilder(
                "python3",
                "bin/backend-contract.py",
                "validate",
                "--fixture-index",
                FIXTURE_INDEX.toString(),
                "--format",
                "json"
        ).redirectErrorStream(true).start();
        String output = new String(process.getInputStream().readAllBytes(), StandardCharsets.UTF_8);

        assertThat(process.waitFor()).describedAs(output).isZero();
        JsonNode result = objectMapper.readTree(output);
        assertThat(result.path("status").asText()).isEqualTo("PASS");
        assertThat(result.path("fixtureCount").asInt()).isEqualTo(5);
    }

    @Test
    void keepsImplementationResultNonTerminalUntilTrustedHostQualification() throws Exception {
        JsonNode result = objectMapper.readTree(IMPLEMENTATION_RESULT.toFile());

        assertThat(result.path("taskId").asText()).isEqualTo("S004-FIELD-PROVEN-CONTRACTS-A002");
        assertThat(result.path("status").asText()).isEqualTo("IMPLEMENTATION_COMPLETE");
        assertThat(result.path("qualificationBoundary").asText()).isEqualTo("TRUSTED_HOST_PENDING");
        assertThat(result.path("sprintResult").asText()).isEqualTo("NOT_YET_QUALIFIED");
        assertThat(result.path("overallStatus").asText()).isEqualTo("active");
        assertThat(result.path("closureStatus").asText()).isEqualTo("OPEN");
    }

    private Set<String> fieldNames(JsonNode node) {
        Set<String> names = new HashSet<>();
        node.fieldNames().forEachRemaining(names::add);
        return names;
    }

    private Set<String> textValues(JsonNode array) {
        Set<String> values = new HashSet<>();
        array.forEach(value -> values.add(value.asText()));
        return values;
    }
}
