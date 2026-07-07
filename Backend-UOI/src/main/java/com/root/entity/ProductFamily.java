package com.root.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "product_family")
public class ProductFamily {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "family_name")
    private String familyName;

    public Integer getId() {
        return id;
    }

    public String getFamilyName() {
        return familyName;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public void setFamilyName(String familyName) {
        this.familyName = familyName;
    }
}