package com.root.controller;

import com.root.dto.ComponentSentimentDTO;
import com.root.dto.ProductDashboardDTO;
import com.root.dto.SourceSentimentDTO;
import com.root.service.DashboardService;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/dashboard")
@CrossOrigin(origins = "http://localhost:4200")
public class DashboardController {

    private final DashboardService service;

    public DashboardController(DashboardService service){
        this.service = service;
    }

    @GetMapping("/{productId}")
    public ProductDashboardDTO getDashboard(
            @PathVariable Integer productId){

        return service.getDashboard(productId);

    }

    @GetMapping("/{productId}/components")
    public Map<String, ComponentSentimentDTO> getComponentSentiment(
            @PathVariable Integer productId){
        return service.getComponentSentiment(productId);
    }

    @GetMapping("/{productId}/sources")
    public Map<String, SourceSentimentDTO> getSourceSentiment(
            @PathVariable Integer productId){

        return service.getSourceSentiment(productId);
    }

    @GetMapping("/{productId}/countries")
    public Map<String,Integer> getCountryReviewCounts(
            @PathVariable Integer productId){

        return service.getCountryReviewCounts(productId);
    }
}
