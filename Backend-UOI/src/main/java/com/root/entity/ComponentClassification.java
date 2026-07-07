package com.root.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "component_classification")
public class ComponentClassification {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "component")
    private String component;

    public ComponentClassification() {}

    public Integer getId() {
        return id;
    }

    public String getComponent() {
        return component;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public void setComponent(String component) {
        this.component = component;
    }
}