package com.root.controller;

import com.root.dto.ComponentSentimentResponse;
import com.root.service.ComponentSentimentService;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/component-sentiment")
@CrossOrigin(origins = "http://localhost:4200")
public class ComponentSentimentController {

    private final ComponentSentimentService service;

    public ComponentSentimentController(ComponentSentimentService service) {
        this.service = service;
    }

    @GetMapping("/{componentId}")
    public ComponentSentimentResponse getSentiment(
            @PathVariable int componentId) {

        return service.getComponentSentiment(componentId);
    }
}