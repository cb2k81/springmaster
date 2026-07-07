package de.cocondo.system.entity;

import java.util.Set;

public interface Taggable extends Identifyable {
    Set<String> getTags();
}
