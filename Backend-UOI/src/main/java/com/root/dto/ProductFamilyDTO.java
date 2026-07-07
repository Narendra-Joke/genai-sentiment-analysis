package com.root.dto;

import java.util.List;

public class ProductFamilyDTO {

    private String familyName;
    private List<ProductDTO> products;

    public ProductFamilyDTO(String familyName, List<ProductDTO> products) {
        this.familyName = familyName;
        this.products = products;
    }

    public String getFamilyName() {
        return familyName;
    }

    public List<ProductDTO> getProducts() {
        return products;
    }
}