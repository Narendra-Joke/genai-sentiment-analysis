package com.root.service;

import com.root.dto.ProductDTO;
import com.root.dto.ProductFamilyDTO;
import com.root.entity.Product;
import com.root.repository.ProductRepository;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class ProductService {

    private final ProductRepository repository;

    public ProductService(ProductRepository repository) {
        this.repository = repository;
    }

    public List<ProductFamilyDTO> getProductsGroupedByFamily() {

        List<Product> products = repository.findAll();

        Map<String,List<ProductDTO>> grouped =
                products.stream()
                        .collect(Collectors.groupingBy(
                                p -> p.getFamily().getFamilyName(),
                                Collectors.mapping(
                                        p -> new ProductDTO(p.getId(),p.getProductName()),
                                        Collectors.toList()
                                )
                        ));

        List<ProductFamilyDTO> result = new ArrayList<>();

        grouped.forEach((family,productList) -> {
            result.add(new ProductFamilyDTO(family,productList));
        });

        return result;
    }

    public List<ProductFamilyDTO> getProductsGroupedByYear(int year) {

        List<Product> products = repository.findByReleaseYear(year);

        Map<String,List<ProductDTO>> grouped =
                products.stream()
                        .collect(Collectors.groupingBy(
                                p -> p.getFamily().getFamilyName(),
                                Collectors.mapping(
                                        p -> new ProductDTO(p.getId(), p.getProductName()),
                                        Collectors.toList()
                                )
                        ));

        List<ProductFamilyDTO> result = new ArrayList<>();

        grouped.forEach((family, productList) -> {
            result.add(new ProductFamilyDTO(family, productList));
        });

        return result;
    }
}