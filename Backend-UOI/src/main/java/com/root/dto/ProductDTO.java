package com.root.dto;

public class ProductDTO {

    private Integer id;
    private String productName;

    public ProductDTO(Integer id, String productName) {
        this.id = id;
        this.productName = productName;
    }

    public Integer getId() {
        return id;
    }

    public String getProductName() {
        return productName;
    }
}