package de.cocondo.platform.app.version;

import org.springframework.boot.actuate.info.Info;
import org.springframework.boot.actuate.info.InfoContributor;
import org.springframework.stereotype.Component;

@Component
public final class PlatformInfoContributor implements InfoContributor {

    private final PlatformVersionProperties versions;

    public PlatformInfoContributor(PlatformVersionProperties versions) {
        this.versions = versions;
    }

    @Override
    public void contribute(Info.Builder builder) {
        builder.withDetail("springmaster", versions.asMap());
    }
}
