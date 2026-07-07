package com.root.controller;

import com.root.dto.ProductFamilyDTO;
import com.root.service.ProductService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/products")
@CrossOrigin(origins = "http://localhost:4200")
public class ProductController {

    private final ProductService service;

    public ProductController(ProductService service) {
        this.service = service;
    }

//    @GetMapping("/families")
//    public List<ProductFamilyDTO> getProductsByFamily(){
//        return service.getProductsGroupedByFamily();
//    }

    @GetMapping("/families")
    public List<ProductFamilyDTO> getProductsByFamily(
            @RequestParam(required = false) Integer year
    ) {

        int selectedYear = (year != null)
                ? year
                : java.time.LocalDate.now().getYear();

        return service.getProductsGroupedByYear(selectedYear);
    }
}
