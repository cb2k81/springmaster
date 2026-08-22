package de.cocondo.platform.demo.teammembership;

import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.is;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import de.cocondo.platform.app.SpringmasterApplication;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

@ActiveProfiles("test")
@SpringBootTest(classes = SpringmasterApplication.class)
@AutoConfigureMockMvc
class TeamMembershipApiTest {
    @Autowired
    private MockMvc mockMvc;

    @Test
    void listsMembersAndCandidatesInStableOrder() throws Exception {
        mockMvc.perform(get("/api/demo/teams/alpha/members").header("X-Demo-Actor", "team-lead-alpha"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].membershipId", is("membership-001")));

        mockMvc.perform(get("/api/demo/teams/alpha/members/options").header("X-Demo-Actor", "team-lead-alpha"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(2)))
                .andExpect(jsonPath("$[0].personId", is("person-jordan")))
                .andExpect(jsonPath("$[1].personId", is("person-sam")));
    }

    @Test
    void sharesTargetPolicyAcrossPrecheckCapabilityAndExecution() throws Exception {
        String request = "{\"personId\":\"person-sam\"}";
        mockMvc.perform(post("/api/demo/teams/beta/members/commands/add-member/precheck")
                        .header("X-Demo-Actor", "team-lead-alpha")
                        .contentType(MediaType.APPLICATION_JSON).content(request))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.executable", is(false)))
                .andExpect(jsonPath("$.reasons[0].code", is("TARGET_SCOPE_DENIED")));

        mockMvc.perform(post("/api/demo/teams/beta/members/capabilities/evaluate")
                        .header("X-Demo-Actor", "team-lead-alpha")
                        .contentType(MediaType.APPLICATION_JSON).content(request))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.capabilities", hasSize(2)))
                .andExpect(jsonPath("$.capabilities[0].executable", is(false)));

        mockMvc.perform(post("/api/demo/teams/beta/members")
                        .header("X-Demo-Actor", "team-lead-alpha")
                        .contentType(MediaType.APPLICATION_JSON).content(request))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.errorType", is("FORBIDDEN")));
    }

    @Test
    void addsAndRemovesMembershipWithCanonicalStatuses() throws Exception {
        String request = "{\"personId\":\"person-sam\"}";
        mockMvc.perform(post("/api/demo/teams/alpha/members")
                        .header("X-Demo-Actor", "admin")
                        .contentType(MediaType.APPLICATION_JSON).content(request))
                .andExpect(status().isCreated())
                .andExpect(header().string("Location", "/api/demo/teams/alpha/members/person-sam"))
                .andExpect(jsonPath("$.personId", is("person-sam")));

        mockMvc.perform(delete("/api/demo/teams/alpha/members/person-sam").header("X-Demo-Actor", "admin"))
                .andExpect(status().isNoContent());
    }

    @Test
    void exposesOnlyNamespacedProfilesAndLeavesExistingEndpointUnprofiled() throws Exception {
        mockMvc.perform(get("/api-docs"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.paths['/api/demo/teams/{teamId}/members'].get['x-cocondo-operation-profile'].operationKey",
                        is("demo.teams.members.list")))
                .andExpect(jsonPath("$.paths['/api/demo/teams/{teamId}/members'].post['x-cocondo-operation-profile'].operationKey",
                        is("demo.teams.members.add")))
                .andExpect(jsonPath("$.paths['/api/demo/catalog/items'].get['x-cocondo-operation-profile']").doesNotExist());
    }
}
