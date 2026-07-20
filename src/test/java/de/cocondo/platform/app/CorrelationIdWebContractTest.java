package de.cocondo.platform.app;

import static org.hamcrest.Matchers.matchesPattern;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import de.cocondo.system.observability.CorrelationIdSupport;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class CorrelationIdWebContractTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void returnsGeneratedCorrelationId() throws Exception {
        mockMvc.perform(get("/api/platform/info"))
                .andExpect(status().isOk())
                .andExpect(header().string(
                        CorrelationIdSupport.HEADER_NAME,
                        matchesPattern("[0-9a-f-]{36}")
                ));
    }

    @Test
    void propagatesValidCorrelationId() throws Exception {
        mockMvc.perform(get("/api/platform/info")
                        .header(CorrelationIdSupport.HEADER_NAME, "corr-web-42"))
                .andExpect(status().isOk())
                .andExpect(header().string(CorrelationIdSupport.HEADER_NAME, "corr-web-42"));
    }
}
