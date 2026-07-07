package com.root.controller;

import com.root.entity.ComponentClassification;
import com.root.service.ComponentService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/components")
@CrossOrigin(origins = "http://localhost:4200")
public class ComponentController {

    private final ComponentService componentService;

    public ComponentController(ComponentService componentService) {
        this.componentService = componentService;
    }

    @GetMapping
    public List<ComponentClassification> getComponents() {
        return componentService.getAllComponents();
    }
}